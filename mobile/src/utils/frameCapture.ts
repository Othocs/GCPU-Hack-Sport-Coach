
import { CameraView } from 'expo-camera';

export const captureFrame = async (
  cameraRef: React.RefObject<CameraView>,
  quality: number = 0.7
): Promise<string | null> => {
  try {
    if (!cameraRef.current) {
      console.warn('Camera ref not available');
      return null;
    }

    const photo = await cameraRef.current.takePictureAsync({
      quality,
      base64: true,
      skipProcessing: true, 
    });

    if (!photo || !photo.base64) {
      console.warn('Failed to capture photo with base64');
      return null;
    }

    return photo.base64;
  } catch (error) {
    console.error('Error capturing frame:', error);
    return null;
  }
};

export class FrameThrottler {
  private lastCallTime: number = 0;
  private intervalMs: number;

  constructor(fps: number) {
    this.intervalMs = 1000 / fps;
  }

  canCall(): boolean {
    const now = Date.now();
    if (now - this.lastCallTime >= this.intervalMs) {
      this.lastCallTime = now;
      return true;
    }
    return false;
  }

  async throttle<T>(fn: () => Promise<T>): Promise<T | null> {
    if (this.canCall()) {
      return await fn();
    }
    return null;
  }

  setFPS(fps: number) {
    this.intervalMs = 1000 / fps;
  }
}
