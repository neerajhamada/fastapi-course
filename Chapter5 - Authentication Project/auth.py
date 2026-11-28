from fastapi import Header, HTTPException
import os
from dotenv import load_dotenv

load_dotenv()
# Add this secret in your .env file
AUTH_API_KEY = os.getenv("AUTH_API_KEY")

def verify_api_key(x_api_key: str = Header()):
    """Verify the API Key from the request Header"""
    if x_api_key != AUTH_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key