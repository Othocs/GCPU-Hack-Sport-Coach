from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import cv2
import base64
import asyncio
import uvicorn
from skeletton import detect_skeleton, draw_landmarks_on_image

app = FastAPI()

# static HTML
app.mount("/static", StaticFiles(directory="static"), name="static")

class VideoStreamer:
    def __init__(self):
        self.clients = set()
        self.cap = None
        self.running = False

    async def start_capture(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.running = True
        
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            ts_ms = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000.0)
            detection_result = detect_skeleton(frame, ts_ms)
            
            if detection_result.pose_landmarks:
                annotated_frame = draw_landmarks_on_image(frame, detection_result)
            else:
                annotated_frame = frame

            _, buffer = cv2.imencode('.jpg', annotated_frame)
            jpg_as_text = base64.b64encode(buffer).decode('utf-8')

            for client in self.clients:
                try:
                    await client.send_text(jpg_as_text)
                except:
                    self.clients.remove(client)

            await asyncio.sleep(0.03)

    async def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()

video_streamer = VideoStreamer()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(video_streamer.start_capture())

@app.on_event("shutdown")
async def shutdown_event():
    await video_streamer.stop()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    video_streamer.clients.add(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except:
        video_streamer.clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)