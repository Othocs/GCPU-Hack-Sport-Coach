from dotenv import load_dotenv
from google import genai
import cv2
import tempfile
import os

#Must have GEMINI_API_KEY in .env file
load_dotenv()

def call_gemini(image_data, prompt):
    client = genai.Client()
    
    # If image_data is a numpy array (OpenCV frame), save it as a temporary file
    if hasattr(image_data, 'shape'):  # Check if it's a numpy array
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            # Save the frame as JPEG
            cv2.imwrite(tmp_file.name, image_data)
            image_path = tmp_file.name
    else:
        # If it's already a file path, use it directly
        image_path = image_data
    
    try:
        my_file = client.files.upload(file=image_path)
        response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=[my_file, prompt])
        return response.text
    finally:
        # Clean up temporary file if we created one
        if hasattr(image_data, 'shape') and os.path.exists(image_path):
            os.unlink(image_path)

if __name__ == "__main__":
    image_path = "thegoat.png"
    prompt = "Describe the image in detail."
    print(call_gemini(image_path, prompt))
