from gemini_call import call_gemini
from gemini_prompt import GEMINI_PROMPT
import cv2
from skeletton import detect_skeleton, draw_landmarks_on_image

if __name__ == "__main__":
    image_path = 'image.png'
    image_data = cv2.imread(image_path)
    detection_result = detect_skeleton(image_data)
    annotated_image = draw_landmarks_on_image(image_data, detection_result)
    feedback = call_gemini(annotated_image, GEMINI_PROMPT)
    print(feedback)
    cv2.imshow('Annotated Image', annotated_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()