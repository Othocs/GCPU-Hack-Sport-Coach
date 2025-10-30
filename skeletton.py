import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import os
from dotenv import load_dotenv
from gemini_call import call_gemini
from gemini_prompt import GEMINI_PROMPT
from posture_analyzer.exercise_recognizer import ExerciseRecognizer
from posture_analyzer.fatigue import FatigueAnalyzer
from posture_analyzer import analyze_and_summarize, quick_detect_exercise
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

# ---------- Utils: ROI crop & smoothing & confidence ----------
def crop_to_landmarks(frame_bgr, landmarks, pad=0.12):
    h, w = frame_bgr.shape[:2]
    xs = [lm.x for lm in landmarks]
    ys = [lm.y for lm in landmarks]
    if not xs or not ys:
        return frame_bgr
    x1 = max(0.0, min(xs) - pad)
    x2 = min(1.0, max(xs) + pad)
    y1 = max(0.0, min(ys) - pad)
    y2 = min(1.0, max(ys) + pad)
    x1i, x2i = int(x1 * w), int(x2 * w)
    y1i, y2i = int(y1 * h), int(y2 * h)
    if x2i <= x1i or y2i <= y1i:
        return frame_bgr
    return frame_bgr[y1i:y2i, x1i:x2i]

class LandmarkEMA:
    def __init__(self, alpha=0.4):
        self.alpha = alpha
        self.prev = None
    def apply(self, landmarks):
        if self.prev is None:
            self.prev = [(lm.x, lm.y, lm.z) for lm in landmarks]
            return landmarks
        smoothed = []
        out = []
        for (px, py, pz), lm in zip(self.prev, landmarks):
            nx = self.alpha * lm.x + (1 - self.alpha) * px
            ny = self.alpha * lm.y + (1 - self.alpha) * py
            nz = self.alpha * lm.z + (1 - self.alpha) * pz
            smoothed.append((nx, ny, nz))
            lm.x, lm.y, lm.z = nx, ny, nz
            out.append(lm)
        self.prev = smoothed
        return out

def landmarks_confident(landmarks, min_count=20, min_box=0.20):
    if not landmarks:
        return False
    xs = [lm.x for lm in landmarks if np.isfinite(lm.x)]
    ys = [lm.y for lm in landmarks if np.isfinite(lm.y)]
    if len(xs) < min_count or len(ys) < min_count:
        return False
    w = max(xs) - min(xs)
    h = max(ys) - min(ys)
    return (w * h) >= (min_box ** 2)

# ---------- Async JPEG encoder pool ----------
def _encode_jpeg(image_bgr, max_side=512, quality=80):
    h, w = image_bgr.shape[:2]
    scale = min(1.0, max_side / max(h, w))
    if scale < 1.0:
        image_bgr = cv2.resize(image_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".jpg", image_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    return buf if ok else None

class JpegEncoderPool:
    def __init__(self, workers=2):
        self.pool = ThreadPoolExecutor(max_workers=workers)
    def encode(self, frame_bgr, max_side=512, quality=80):
        return self.pool.submit(_encode_jpeg, frame_bgr, max_side, quality)

# ---------- Gemini worker ----------
class GeminiWorker:
    def __init__(self, max_queue_size=4, cooldown_ms=2000, encoder_pool=None):
        self._q = queue.Queue(maxsize=max_queue_size)
        self._cooldown_ms = cooldown_ms
        self._last_call_ms = -1
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._run, daemon=True)
        self._encoder_pool = encoder_pool or JpegEncoderPool(workers=2)
        self._last_llm_ms = None
        self._t.start()

    def enqueue(self, frame_bgr_for_llm, context_text=None):
        try:
            future = self._encoder_pool.encode(frame_bgr_for_llm, max_side=512, quality=80)
            self._q.put_nowait((future, context_text))
        except queue.Full:
            pass

    def _run(self):
        while not self._stop.is_set():
            try:
                future_buf, context_text = self._q.get(timeout=0.1)
            except queue.Empty:
                continue
            now_ms = int(time.time() * 1000)
            if self._last_call_ms >= 0 and (now_ms - self._last_call_ms) < self._cooldown_ms:
                continue
            try:
                t0 = time.time()
                buf = future_buf.result(timeout=2.5)
                if buf is None:
                    continue
                feedback = call_gemini(None, GEMINI_PROMPT, context=context_text, jpeg_buf=buf)
                self._last_call_ms = int(time.time() * 1000)
                self._last_llm_ms = (time.time() - t0) * 1000.0
                if feedback:
                    print(feedback)
            except Exception as e:
                print(f"Gemini worker error: {e}")

    def last_llm_latency_ms(self):
        return self._last_llm_ms

    def stop(self):
        self._stop.set()
        self._t.join(timeout=1.0)

# ---------- MediaPipe pose ----------
_mp_pose_detector = None

def _init_pose_detector():
    global _mp_pose_detector
    if _mp_pose_detector is not None:
        return
    model_path_candidates = [
        'pose_landmarker_lite.task',
        'pose_landmarker_full.task',
        'pose_landmarker_heavy.task',
    ]
    model_path = next((p for p in model_path_candidates if os.path.exists(p)), 'pose_landmarker_lite.task')
    base_options_kwargs = {'model_asset_path': model_path}
    delegate = getattr(python.BaseOptions.Delegate, 'GPU', None)
    if delegate is not None:
        base_options_kwargs['delegate'] = delegate
    base_options = python.BaseOptions(**base_options_kwargs)
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_segmentation_masks=False,
    )
    _mp_pose_detector = vision.PoseLandmarker.create_from_options(options)

def detect_skeleton(frame_bgr, ts_ms):
    _init_pose_detector()
    rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    return _mp_pose_detector.detect_for_video(mp_image, ts_ms)

def draw_landmarks_on_image(bgr_image, detection_result):
    pose_landmarks_list = detection_result.pose_landmarks
    annotated_image = np.copy(bgr_image)
    for idx in range(len(pose_landmarks_list)):
        pose_landmarks = pose_landmarks_list[idx]
        pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        pose_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z) for lm in pose_landmarks
        ])
        mp.solutions.drawing_utils.draw_landmarks(
            annotated_image,
            pose_landmarks_proto,
            mp.solutions.pose.POSE_CONNECTIONS,
            mp.solutions.drawing_styles.get_default_pose_landmarks_style()
        )
    return annotated_image

def _maybe_downscale(frame_bgr, max_side=640):
    h, w = frame_bgr.shape[:2]
    scale = min(1.0, max_side / max(h, w))
    if scale < 1.0:
        return cv2.resize(frame_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return frame_bgr

# ---------- Main loop ----------
def get_webcam():
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    try:
        cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    except Exception:
        pass

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640, 480))
    index = 0

    worker = GeminiWorker(max_queue_size=4, cooldown_ms=2000)
    prev_landmarks = None
    last_good_landmarks = None
    last_context_text = None
    ema = LandmarkEMA(alpha=0.4)

    # ---- Nouvelle partie : instanciation des analyseurs -----------
    exercise_recognizer = ExerciseRecognizer()
    fatigue_analyzer = FatigueAnalyzer()
    # ---------------------------------------------------------------

    try:
        while True:
            ret, frame = cam.read()
            if not ret:
                break
            index += 1

            frame_proc = _maybe_downscale(frame, max_side=640)
            ts_ms = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000.0)
            detection_result = detect_skeleton(frame_proc, ts_ms)

            if detection_result.pose_landmarks:
                cur_landmarks = detection_result.pose_landmarks[0]
            else:
                cur_landmarks = last_good_landmarks

            if cur_landmarks:
                cur_landmarks = ema.apply(cur_landmarks)
                last_good_landmarks = cur_landmarks

            confident = landmarks_confident(cur_landmarks) if cur_landmarks else False
            if confident:
                last_good_landmarks = cur_landmarks

            annotated_image = draw_landmarks_on_image(frame_proc, detection_result if detection_result.pose_landmarks else detection_result)

            # ------- INFOS EXERCICE + FATIGUE (Overlay) -------
            overlay = annotated_image.copy()
            font = cv2.FONT_HERSHEY_SIMPLEX

            exercise_str, ex_confidence, ex_phase = None, 0.0, ""
            fatigue_score, fatigue_ok = 0.0, True

            if cur_landmarks:
                # Analyse posture
                exercise_str, ex_confidence, ex_phase = exercise_recognizer.recognize(cur_landmarks)
                # Analyse fatigue
                fatigue_scores = fatigue_analyzer.update(cur_landmarks)
                fatigue_score = fatigue_scores['overall']
                fatigue_ok = not fatigue_analyzer.is_fatigued()

            # Texte overlay (toujours)
            if exercise_str:
                info = f"Exercice : {exercise_str} | Phase: {ex_phase} | Confiance: {ex_confidence:.2f}"
                cv2.putText(overlay, info, (15, 36), font, 0.7, (0, 200, 40), 2, cv2.LINE_AA)
            if fatigue_score > 0.0:
                txt = f"Fatigue: {fatigue_score:.2f} {'OK' if fatigue_ok else '⚠️ FATIGUE'}"
                col = (150, 220, 255) if fatigue_ok else (0, 0, 255)
                cv2.putText(overlay, txt, (15, 66), font, 0.7, col, 2, cv2.LINE_AA)

            # ---------- Détection contextuelle pour le LLM ----------
            if index % 30 == 0 and cur_landmarks:
                # Stabilité pour résumé
                stable = True
                if prev_landmarks is not None:
                    deltas = [
                        (abs(cur_landmarks[i].x - prev_landmarks[i].x) +
                         abs(cur_landmarks[i].y - prev_landmarks[i].y))
                        for i in range(min(len(cur_landmarks), len(prev_landmarks)))
                    ]
                    avg_delta = sum(deltas) / max(1, len(deltas))
                    stable = avg_delta < 0.003
                prev_landmarks = cur_landmarks

                llm_frame = crop_to_landmarks(overlay, cur_landmarks, pad=0.10) if confident else overlay
                context_text = last_context_text
                if stable and confident:
                    context_text = analyze_and_summarize(cur_landmarks, exercise_type=exercise_str)
                    last_context_text = context_text
                worker.enqueue(llm_frame, context_text)

            out.write(overlay)
            cv2.imshow('Camera', overlay)
            if cv2.waitKey(1) == ord('q'):
                break
    finally:
        worker.stop()
        cam.release()
        out.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    get_webcam()