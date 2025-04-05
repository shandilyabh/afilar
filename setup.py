"""
to be run only once when the library has to be setup.
"""

import os
import requests

FACENET_URL = "https://github.com/timesler/facenet-pytorch/releases/download/v2.2.9/20180402-114759-vggface2.pt"

def main():
    os.makedirs("resources", exist_ok=True)

    # download and install requirements
    os.system("pip install -r requirements.txt -q")

    # download and store pre-trained facenet from pytorch in the resources folder
    filename = "facenet.pt"
    save_path  = os.path.join("resources", filename)
    response = requests.get(url=FACENET_URL, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print("facenet downloaded successfully.")
    else:
        print(f"Failed to download facenet. Status code: {response.status_code}")

if __name__ == "__main__":
    main()