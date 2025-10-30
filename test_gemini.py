import argparse
import cv2
import os
from dotenv import load_dotenv
from gemini_call import call_gemini
from gemini_prompt import GEMINI_PROMPT
from posture_analyzer import analyze_and_summarize, quick_detect_exercise
from skeletton import detect_skeleton, draw_landmarks_on_image, _maybe_downscale

load_dotenv()

def run_image_pipeline(image_path: str, exercise: str = None):
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Failed to read: {image_path}")
        return

    frame = _maybe_downscale(frame, max_side=640)
    ts_ms = 0
    detection_result = detect_skeleton(frame, ts_ms)

    if not detection_result.pose_landmarks or len(detection_result.pose_landmarks) == 0:
        print("No pose detected.")
        annotated = frame.copy()
    else:
        landmarks = detection_result.pose_landmarks[0]
        exercise_type = exercise or quick_detect_exercise(landmarks)
        context_text = analyze_and_summarize(landmarks, exercise_type=exercise_type)
        annotated = draw_landmarks_on_image(frame, detection_result)
        print("Local analysis context:")
        print(context_text)
        print("\nGemini:")
        print(call_gemini(annotated, GEMINI_PROMPT, context=context_text))

    cv2.imshow("Annotated", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def run_image_llm(image_path: str):
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Failed to read: {image_path}")
        return
    print(call_gemini(frame, GEMINI_PROMPT))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, help="Image path to send directly to Gemini")
    parser.add_argument("--pipeline", type=str, help="Image path to run full pose->summary->Gemini pipeline")
    parser.add_argument("--exercise", type=str, default=None, help="Optional exercise hint (squat/pushup/deadlift/plank/lunge)")
    args = parser.parse_args()

    if args.pipeline:
        run_image_pipeline(args.pipeline, exercise=args.exercise)
    elif args.image:
        run_image_llm(args.image)
    else:
        print("Usage:")
        print("  python test_gemini.py --image image.png")
        print("  python test_gemini.py --pipeline image.png --exercise squat")