"""
tkinter UI test file for username selection
"""

import tkinter as tk
import redis

# Redis connection details
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
USERNAME_SET_KEY = 'available_usernames'

def is_username_taken(username: str, redis_client: redis.Redis) -> bool:
    """
    Checks if a given username is taken using Redis.
    """
    try:
        return redis_client.sismember(USERNAME_SET_KEY, username)
    except redis.exceptions.ConnectionError as e:
        status_label.config(text=f"Error connecting to Redis: {e}", fg="red")
        return False

def check_availability(event):
    username = username_entry.get()
    if username:
        taken = is_username_taken(username, redis_client)
        if taken:
            status_label.config(text="choose another", fg="red")
        else:
            status_label.config(text="available", fg="green")
    else:
        status_label.config(text="", fg="black")

def submit_username():
    username = username_entry.get()
    if username and not is_username_taken(username, redis_client):
        status_label.config(text=f"Username '{username}' submitted!", fg="blue")
    elif not username:
        status_label.config(text="Username cannot be empty.", fg="red")
    else:
        status_label.config(text="Please choose an available username.", fg="red")

# Initialize Tkinter
root = tk.Tk()
root.title("Real-time Username Check")

# Redis client
try:
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    redis_client.ping()
except redis.exceptions.ConnectionError as e:
    error_label = tk.Label(root, text=f"Could not connect to Redis: {e}", fg="red")
    error_label.pack(pady=10)
    redis_client = None

if redis_client:
    # Username Label
    username_label = tk.Label(root, text="Choose username:")
    username_label.pack(pady=5)

    # Username Entry
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)
    username_entry.bind("<KeyRelease>", check_availability)

    # Status Label (for 'available' or 'choose another')
    status_label = tk.Label(root, text="", fg="black")
    status_label.pack(pady=5)

    # Submit Button
    submit_button = tk.Button(root, text="Submit Username", command=submit_username)
    submit_button.pack(pady=10)

root.mainloop()