"""
test script to register a user
using afilar
"""

import re
import os
import time
import random
import bcrypt # type: ignore[import]
from typing import Optional
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.completion import WordCompleter
import json

def generate_numeric_ulid() -> int:
    """
    generates a unique numeric id for the user
    a 128 bit integer made of 48 bits timestamp
    and 80 bits of random numbers
    """
    timestamp = int(time.time() * 1000) & ((1 << 48) - 1)
    random_bits = random.getrandbits(80)
    ulid = (timestamp << 80) | random_bits
    return ulid

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
    
def register_face():
    """
    register the face of the user
    """
    # initiating face ID registration (halo)
    pass
    # return embeddings

def register_user(first_name: str, last_name: str, username: str, password_hash: str, faiss_ulid: str) -> None:
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
            "embeddings": "face_id",
            "faiss_id": faiss_ulid
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
        return username
    except KeyboardInterrupt:
        print("\nInput interrupted. terminal exited the program.")
        return None

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
                    face_id = register_face()
                    if face_id:
                        faiss_ulid = str(generate_numeric_ulid())
                        register_user(first_name, last_name, username, password_hash, faiss_ulid)
                        print("User Registered Successfully.")
                    else:
                        print("User Registration Failed. Face ID could not be registered.")
                else:
                    print("User Registration Failed. Password could not be hashed.")
            else:
                print("User Registration Failed. An unique username is required.")
        else:
            print("User Registration Failed. First name and last name are required.")
    except KeyboardInterrupt:
        print("\nInput interrupted. terminal exited the program.")
