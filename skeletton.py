# Standard library imports
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

# Module imports
from gemini_call import call_gemini
from gemini_prompt import GEMINI_PROMPT

def detect_skeleton(frame):
    # Create an PoseLandmarker object.
    base_options = python.BaseOptions(model_asset_path='pose_landmarker_heavy.task')
    options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=True)
    detector = vision.PoseLandmarker.create_from_options(options)

    # Convert OpenCV BGR frame to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Create MediaPipe Image from numpy array
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Detect pose landmarks from the input image.
    detection_result = detector.detect(mp_image)

    return detection_result
    
    
    
def get_webcam():
    # Open the default camera
    cam = cv2.VideoCapture(0)

    # Get the default frame width and height
    frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))
    index = 0
    while True:
        ret, frame = cam.read()
        index += 1
        # Write the frame to the output file
        out.write(frame)
        detection_result = detect_skeleton(frame)
        annotated_image = draw_landmarks_on_image(frame, detection_result)
        
        if index % 30 == 0:
            feedback = call_gemini(annotated_image, GEMINI_PROMPT)
            print(feedback)


        cv2.imshow('Camera', annotated_image)
        
        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    out.release()
    cv2.destroyAllWindows()
    

def draw_landmarks_on_image(rgb_image, detection_result):
  pose_landmarks_list = detection_result.pose_landmarks
  annotated_image = np.copy(rgb_image)

  # Loop through the detected poses to visualize.
  for idx in range(len(pose_landmarks_list)):
    pose_landmarks = pose_landmarks_list[idx]

    # Draw the pose landmarks.
    pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    pose_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      pose_landmarks_proto,
      solutions.pose.POSE_CONNECTIONS,
      solutions.drawing_styles.get_default_pose_landmarks_style())
  return annotated_image


if __name__ == "__main__":
    get_webcam()
    # STEP 5: Process the detection result. In this case, visualize it.
    #annotated_image = draw_landmarks_on_image(image.numpy_view(), detection_result)
    #cv2_imshow(cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))