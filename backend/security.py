import hashlib
import os
from dotenv import load_dotenv

load_dotenv()
SALT = os.getenv("HASH_SALT")

def get_hashed_id(discord_id):
    payload = f"{SALT}{discord_id}"
    return hashlib.sha256(payload.encode()).hexdigest()