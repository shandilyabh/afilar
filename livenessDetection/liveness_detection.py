"""
Script to test liveness detection on video (Timed for 3 seconds)
"""

import cv2 # type: ignore
import numpy as np
import os
import time
import warnings

from src.anti_spoof_predict import AntiSpoofPredict
from src.utility import parse_model_name, CropImage

warnings.filterwarnings('ignore')

def liveness_detection(model_dir, device_id=0):
    """
    Detects face spoofing in real-time using a webcam for exactly 3 seconds.

    Args:
        model_dir (str): Path to the model directory.
        device_id (int): GPU device ID (default: 0).

    Returns:
        str: Final result ("Real (score)" or "Fake (score)")
    """

    model_test = AntiSpoofPredict(device_id)
    image_cropper = CropImage()
    
    cap = cv2.VideoCapture(1)
    start_time = time.time()
    final_result = "Unknown"

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        # Conversion of frame to correct format
        image = frame.copy()
        image_bbox = model_test.get_bbox(image)

        if image_bbox is not None:
            prediction = np.zeros((1, 3))
            test_speed = 0

            for model_name in os.listdir(model_dir):
                h_input, w_input, model_type, scale = parse_model_name(model_name)
                param = {
                    "org_img": image,
                    "bbox": image_bbox,
                    "scale": scale,
                    "out_w": w_input,
                    "out_h": h_input,
                    "crop": True if scale else False
                }

                img = image_cropper.crop(**param)
                start = time.time()
                prediction += model_test.predict(img, os.path.join(model_dir, model_name))
                test_speed += time.time() - start

            #prediction result
            label = np.argmax(prediction)
            value = prediction[0][label] / 2

            # text and color based on prediction, Real: Green, Spoof: Red
            if label == 1:
                result_text = f"Real ({value:.2f})"
                color = (0, 255, 0)
            else:
                result_text = f"Fake ({value:.2f})"
                color = (0, 0, 255)

            final_result = result_text

            cv2.rectangle(
                image, 
                (image_bbox[0], image_bbox[1]), 
                (image_bbox[0] + image_bbox[2], image_bbox[1] + image_bbox[3]), 
                color, 2
            )

            cv2.putText(
                image, result_text,
                (image_bbox[0], image_bbox[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
            )

        cv2.imshow("Liveness Detection", image)

        if time.time() - start_time > 5:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

    return final_result

if __name__ == "__main__":
    model_directory = "./resources/anti_spoof_models"
    result = liveness_detection(model_directory)
    print("Final Result:", result)