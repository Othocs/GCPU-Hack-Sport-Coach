from dotenv import load_dotenv
from google import genai
import cv2
import tempfile
import os
import time

load_dotenv()

_api_key = os.getenv("GEMINI_API_KEY")
_client = genai.Client(api_key=_api_key) if _api_key else None
_MODEL = "gemini-2.5-flash-lite"

def _encode_jpeg(image_bgr, max_side=512, quality=80):
    h, w = image_bgr.shape[:2]
    scale = min(1.0, max_side / max(h, w))
    if scale < 1.0:
        image_bgr = cv2.resize(image_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".jpg", image_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    return buf if ok else None

def _call_with_path(image_path: str, prompt: str, context: str = None):
    contents = []
    if context:
        contents.append(context)
    my_file = _client.files.upload(file=image_path)
    contents.extend([my_file, prompt])
    resp = _client.models.generate_content(model=_MODEL, contents=contents)
    return getattr(resp, "text", None)

def call_gemini(image_data=None, prompt: str = "", context: str = None, retries: int = 2, backoff: float = 0.8, jpeg_buf=None):
    """Call Gemini API with image and prompt"""
    if _client is None:
        raise ValueError("Gemini API client not initialized. Please set GEMINI_API_KEY environment variable.")

    def once():
        if jpeg_buf is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(jpeg_buf if isinstance(jpeg_buf, (bytes, bytearray)) else jpeg_buf.tobytes())
                image_path = tmp_file.name
            try:
                return _call_with_path(image_path, prompt, context)
            finally:
                if os.path.exists(image_path):
                    os.unlink(image_path)

        if hasattr(image_data, 'shape'):
            buf = _encode_jpeg(image_data, max_side=512, quality=80)
            if buf is None:
                return None
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_file.write(buf.tobytes())
                image_path = tmp_file.name
            try:
                return _call_with_path(image_path, prompt, context)
            finally:
                if os.path.exists(image_path):
                    os.unlink(image_path)
        else:
            return _call_with_path(image_data, prompt, context)

    last_err = None
    for i in range(retries + 1):
        try:
            return once()
        except Exception as e:
            last_err = e
            if i < retries:
                time.sleep((i + 1) * backoff)
    raise last_err
