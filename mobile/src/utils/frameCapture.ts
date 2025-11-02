/**
 * Utilities for capturing and processing camera frames
 */

import { CameraView } from 'expo-camera';

/**
 * Capture a frame from the camera and convert to base64
 * @param cameraRef Reference to the camera component
 * @param quality JPEG quality (0-1)
 * @returns Base64 encoded image string
 */
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
      skipProcessing: true, // Faster processing
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

/**
 * Throttle function calls to a maximum rate
 * Useful for limiting frame capture frequency
 */
export class FrameThrottler {
  private lastCallTime: number = 0;
  private intervalMs: number;

  constructor(fps: number) {
    this.intervalMs = 1000 / fps;
  }

  /**
   * Check if enough time has passed to allow another call
   */
  canCall(): boolean {
    const now = Date.now();
    if (now - this.lastCallTime >= this.intervalMs) {
      this.lastCallTime = now;
      return true;
    }
    return false;
  }

  /**
   * Execute a function if the throttle allows it
   */
  async throttle<T>(fn: () => Promise<T>): Promise<T | null> {
    if (this.canCall()) {
      return await fn();
    }
    return null;
  }

  /**
   * Update the target FPS
   */
  setFPS(fps: number) {
    this.intervalMs = 1000 / fps;
  }
}
