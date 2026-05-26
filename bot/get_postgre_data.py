import httpx
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")


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
        
async def delete_user_data(user_id: str, server_id: str):
    if(server_id == "all"):
        pass
    else:
        pass