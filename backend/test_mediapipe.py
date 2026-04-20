import requests
import sys

def test_mediapipe():
    print("Testing MediaPipe integration...")
    
    # You can test with a sample image URL
    # For now, just check if imports work
    try:
        import mediapipe as mp
        import cv2
        print("✅ MediaPipe and OpenCV imported successfully")
        
        # Test pose initialization
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(static_image_mode=True)
        print("✅ MediaPipe Pose initialized successfully")
        
        print("\n🎉 MediaPipe is ready! Now upload a photo to test measurement extraction.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please run: pip install mediapipe opencv-python")
        return False
    
    return True

if __name__ == "__main__":
    test_mediapipe()