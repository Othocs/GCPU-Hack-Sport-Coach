from dotenv import load_dotenv
from google import genai

#Must have GEMINI_API_KEY in .env file
load_dotenv()

def call_gemini(image_path, prompt):
    client = genai.Client()
    my_file = client.files.upload(file=image_path)
    response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=[my_file, prompt])
    return response.text

if __name__ == "__main__":
    image_path = "thegoat.png"
    prompt = "Describe the image in detail."
    print(call_gemini(image_path, prompt))
