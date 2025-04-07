"""
test script to register a user
using afilar
"""

import re
import os
import cv2  # type: ignore[import]
import torch
import json
import time
import faiss # type: ignore[import]
import bcrypt # type: ignore[import]
from typing import Optional
import mediapipe as mp # type: ignore[import]
import numpy as np  # type: ignore[import]
from pathlib import Path
from halo import Halo # type: ignore[import]
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.completion import WordCompleter
from facenet_pytorch import MTCNN, InceptionResnetV1  # type: ignore[import]
from snowflake import Snowflake64  # type: ignore[import]

# for Ensuring frontal face alignment during face registration
EAR_THRESH = 0.2
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# unique int64 numeric ID generator
id_generator = Snowflake64(machine_id=1)
FAISS_INDEX_PATH = Path("path/to/faiss_index.index")

def eye_aspect_ratio(landmarks, eye_indices) -> float:
    """
    calculates the eye aspect ratio
    based on the eye landmarks to determine if the eyes are open
    """
    eye = np.array([landmarks[i] for i in eye_indices])
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)


def generate_facial_id() -> np.ndarray:
    """
    generates facial embeddings of the subject
    returns 512-dimensional numpy array
    """
    try:
        mtcnn = MTCNN(keep_all=False)
        model = InceptionResnetV1(pretrained='vggface2').eval()
        mp_face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)
        
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return False

        face_img, start_time = None, None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = mp_face_mesh.process(rgb)

            boxes, _ = mtcnn.detect(frame)
            if boxes is not None and results.multi_face_landmarks:
                x1, y1, x2, y2 = boxes[0].astype(int)
                landmarks = results.multi_face_landmarks[0].landmark
                h, w = frame.shape[:2]
                coords = [(int(l.x * w), int(l.y * h)) for l in landmarks]

                left_ear = eye_aspect_ratio(coords, LEFT_EYE)
                right_ear = eye_aspect_ratio(coords, RIGHT_EYE)

                if left_ear > EAR_THRESH and right_ear > EAR_THRESH:
                    if start_time is None:
                        start_time = time.time()
                        face_img = frame[y1:y2, x1:x2]

                    elapsed = time.time() - start_time
                    if elapsed < 5:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (128, 128, 128), 2)
                        cv2.putText(frame, f'Hold still for... {3 - int(elapsed)}s',
                                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 2)
                    else:
                        face = cv2.resize(face_img, (160, 160))
                        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                        tensor = torch.tensor(face).permute(2, 0, 1).float().unsqueeze(0) / 255

                        with torch.no_grad():
                            embedding = model(tensor).squeeze().tolist()

                        # make the embedding a numpy array
                        if hasattr(embedding, 'detach'):
                            embedding = embedding.detach().cpu().numpy()
                        
                        embedding = np.asarray(embedding, dtype=np.float32)
                        face_id = embedding.reshape(1, -1)

                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, 'facial ID generated', (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.imshow('Facial ID', frame)
                        cv2.waitKey(2000)
                        break
                else:
                    start_time = None
                    cv2.putText(frame, 'Keep your eyes open and look straight',
                                (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                start_time = None

            cv2.imshow('Facial ID', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return face_id

    except Exception as e:
        print(e)
        return None


def hash_password() -> Optional[str]:
    """
    validates, hashes and stores the password
    """
    try:
        pwd = prompt("Enter your password: ", is_password=True)
        if not is_valid_password(pwd):
            print("Password must be at least 8 characters long, contain an uppercase letter, a number, and a special character.")
            return hash_password()
        else:
            hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
            return hashed.decode('utf-8')
    except KeyboardInterrupt:
        print("\nInput interrupted. terminal exited the program.")
        return None

def is_valid_password(password: str) -> bool:
    """
    checks if the password has at least 8 characters,
    an uppercase letter, a number & a special character
    """
    return (
        len(password) >= 8
        and re.search(r"[A-Z]", password)
        and re.search(r"\d", password)
        and re.search(r"[^\w\s]", password)
    )

def make_user(first_name: str, last_name: str, username: str, password_hash: str, faiss_id: str) -> None:
    """
    supposed to be the function that registers
    a user onto firestore, here written for test
    hence appending to a local json file.
    """
    with open("user_data.json", "r") as file:
        users = json.load(file)

    users.append({
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "hashed_password": password_hash,
            "faiss_id": faiss_id
        })
    
    with open("user_data.json", "w") as file:
        json.dump(users, file, indent=4)

    return None


def take_username() -> Optional[str]:
    """
    a list of usernames must be imported here
    """
    with open("usernames.json", "r") as file:
        users = json.load(file)
    usernames = users[0].get("usernames", [])
    username_completer = WordCompleter(usernames, ignore_case=True)
    try:
        username = prompt('Choose username: ', completer=username_completer).lower()
        if username in usernames:
            print("\nusername taken, choose another.\n[hint]: if it is coming in autocomplete, it's taken.")
            time.sleep(3)
            return take_username()
        else:
            users[0]["usernames"].append(username)
            with open("usernames.json", "w") as file:
                json.dump(users, file, indent=4)
            return username
    except KeyboardInterrupt:
        print("\nInput interrupted. terminal exited the program.")
        return None
    

def update_faiss_index(face_id: np.ndarray) -> int:
    """
    Adds a new face embedding to the FAISS index with a unique 64-bit ID.
    
    Parameters:
        face_id (np.ndarray): The (1, 512) float32 face embedding.

    Returns:
        int: The 64-bit numeric ID assigned to the user.
    """
    assert isinstance(face_id, np.ndarray), "face_id must be a numpy array"
    assert face_id.shape == (1, 512), "Expected embedding shape (1, 512)"
    assert face_id.dtype == np.float32, "Embedding must be float32"

    index = faiss.read_index(str(FAISS_INDEX_PATH))
    user_id = id_generator.generate()
    index.add_with_ids(face_id, np.array([user_id], dtype=np.int64))
    faiss.write_index(index, str(FAISS_INDEX_PATH))
    return user_id


if __name__ == "__main__":
    os.system("clear")
    try:
        first_name = prompt("first name: ")
        last_name = prompt("last name: ")
        if first_name and last_name:
            username = take_username()
            if username:
                password_hash = hash_password()
                if password_hash:
                    try:
                        face_id = generate_facial_id()
                        os.system("clear")
                        faiss_id = update_faiss_index(face_id)
                        make_user(first_name, last_name, username, password_hash, str(faiss_id))
                        
                        # Arficially inducing delay for aesthetic purposes:
                        spinner = Halo(text='Registering User...', spinner='dots')
                        spinner.start()
                        time.sleep(3)
                        spinner.stop()

                        print("User Registered Successfully.")
                    except Exception as e:
                        print(e)
                        print("User Registration Failed. Face ID could not be registered.")
                else:
                    print("User Registration Failed. Password could not be hashed.")
            else:
                print("User Registration Failed. An unique username is required.")
        else:
            print("User Registration Failed. First name and last name are required.")
    except KeyboardInterrupt:
        print("\nInput interrupted. terminal exited the program.")
