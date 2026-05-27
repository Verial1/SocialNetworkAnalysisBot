import httpx
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")

# Get's user's servers
async def get_user_servers(user_id: str) -> list:
    url = f"{BACKEND_URL}/users/{user_id}/servers"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return [] # Utente non trovato = zero server
            else:
                print(f"Backend Error {response.status_code}: {response.text}")
                return []
        except Exception as e:
            print(f"Connection Error: {e}")
            return []


async def has_already_given_consent(user_id: str, server_id: str) -> bool:
    url = f"{BACKEND_URL}/consent/check"
    params = {"u_hash": user_id, "s_hash": server_id}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            
            if response.status_code == 200:
                return response.json().get("exists", False)
            return False
        except Exception as e:
            print(f"Connection Error: {e}")
            return False
        
async def get_latest_id(user_id: str, server_id:str):
    url = f"{BACKEND_URL}/latest_id"
    params = {"user_id": user_id, "server_id": server_id}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            
            if response.status_code == 200:
                # Potrebbe restituire un ID o None teoricamente (difficile perché il /consent è il primo messaggio e viene subito salvato nel db)
                return response.json().get("latest_id")
            elif response.status_code == 404:
                return None
            else:
                print(f"get_latest_id failed with code {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"Connection Error: {e}")
            return None
        
async def delete_user_data(user_id: str, server_id: str):
    # può essere sia un server_id che "all"
    url = f"{BACKEND_URL}/consent"
    params = {"user_id": user_id, "server_id": server_id}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(url, timeout=15.0)
            
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                print(f"delete_user_data failed with code {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"Connection Error during delete: {e}")
            return False