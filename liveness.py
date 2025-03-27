"""
test code to check if liveness detection works
"""
import cv2 #type: ignore

cap = cv2.VideoCapture(1)  # Open webcam

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to access the webcam.")
        break

    cv2.imshow("Webcam Feed - Press 'C' to Capture, 'Q' to Quit", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        cv2.imwrite("my_face.jpg", frame)
        print("Image saved as my_face.jpg")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()