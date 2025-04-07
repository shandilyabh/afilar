"""
Script to test liveness detection on video
"""

import cv2 # type: ignore
import numpy as np
import os
import time
import warnings

from src.anti_spoof_predict import AntiSpoofPredict
from src.utility import parse_model_name, CropImage
import json
import datetime
from slack_notification import send_to_slack

slack_webhook = os.getenv("SLACK_WEBHOOK_URL")

warnings.filterwarnings('ignore')

def liveness_detection(device_id:int = 0) -> bool:
    """
    Detects face spoofing in real-time using a webcam for exactly 3 seconds.

    Args:
        device_id (int): GPU device ID (default: 0).

    Returns:
        bool: Final result - True (real) or False (fake)")
    """
    permission = False # the return value

    model_test = AntiSpoofPredict(device_id)
    image_cropper = CropImage()
    
    cap = cv2.VideoCapture(0)
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

            for model_name in os.listdir("resources/anti_spoof_models"):
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
                prediction += model_test.predict(img, os.path.join("resources/anti_spoof_models", model_name))
                test_speed += time.time() - start

            #prediction result
            label = np.argmax(prediction)
            value = prediction[0][label] / 2

            # text and color based on prediction, Real: Green, Spoof: Red
            if label == 1:
                result_text = f"Real: {value:.2f}"
                color = (0, 255, 0)
                permission = True
            else:
                result_text = f"Fake: {value:.2f}"
                color = (0, 0, 255)
                print("spoof attempt detected\n" + result_text)
                permission = False

                # to be replaced by logic to log into the database + returning False, for not allowing further access.
                with open("spoof_attempts.json", "r") as db:
                    logs = json.load(db)
                logs.append({"attempt": "spoof", "percentage": value, "timestamp": str(time.time())})
                with open("spoof_attempts.json", "w") as db:
                    json.dump(logs, db, indent=4)

                send_to_slack(
                    slack_webhook, 
                    datetime.datetime.now(), 
                    "spoof", 
                    "some://url.where.image/is_stored.jpg"
                )

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

        if time.time() - start_time > 3:
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

    return permission

if __name__ == "__main__":
    if liveness_detection():
        print("Onto Facial ID recognition")
    else:
        print("Spoof attempt detected.")
