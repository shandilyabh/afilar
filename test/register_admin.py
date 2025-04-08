"""
Script for admin registration and FAISS index creation.
"""

from register_user import generate_facial_id
import faiss # type: ignore[import]
import numpy as np
import json

faiss_index = "users_faiss.index"

base_index = faiss.IndexFlatL2(512)
index = faiss.IndexIDMap2(base_index)

embedding, id_ = generate_facial_id()
index.add_with_ids(embedding, np.array([id_], dtype=np.int64))

faiss.write_index(index, faiss_index)

# to be replaced with db insertion logic:
# as well as storing of faiss Index on FireStore Storage
with open("usernames.json", "r") as file:
    users = json.load(file)

users["usernames"].append("admin")

with open("usernames.json", "w") as file:
    json.dump(users, file, indent=4)

with open("user_data.json", "r") as file:
    data = json.load(file)

data.append({
    "username": "admin",
    "first_name": "admin",
    "last_name": "user",
    "password_hash": "admin123",
    "faiss_id": id_
})

with open("user_data.json", "w") as file:
    json.dump(data, file, indent=4)

print(f"Admin user created successfully.\nFAISS index made: [{faiss_index}]")