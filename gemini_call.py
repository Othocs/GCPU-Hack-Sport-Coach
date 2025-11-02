from dotenv import load_dotenv
import google.generativeai as genai
import cv2
import tempfile
import os
import time
from google.api_core import client_options as client_options_lib

load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
_MODEL = "gemini-1.5-pro"

def _encode_jpeg(image_bgr, max_side=512, quality=80):
    h, w = image_bgr.shape[:2]
    scale = min(1.0, max_side / max(h, w))
    if scale < 1.0:
        image_bgr = cv2.resize(image_bgr, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".jpg", image_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    return buf if ok else None

def _call_with_path(image_path: str, prompt: str, context: str = None):

    model = genai.GenerativeModel(_MODEL)
    
    contents = []
    if context:
        contents.append({"text": context})
    
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    message = [
        *[{"text": c["text"]} for c in contents],
        {"text": prompt},
        {"mime_type": "image/jpeg", "data": image_data}
    ]
    
    try:
        
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API Gemini: {e}")
        return None

def call_gemini(image_data=None, prompt: str = "", context: str = None, retries: int = 2, backoff: float = 0.8, jpeg_buf=None):

    def once():
        try:
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
        except Exception as e:
            print(f"Erreur lors de l'appel à Gemini: {e}")
            return None

    last_err = None
    for i in range(retries + 1):
        try:
            return once()
        except Exception as e:
            last_err = e
            if i < retries:
                time.sleep((i + 1) * backoff)
    raise last_err