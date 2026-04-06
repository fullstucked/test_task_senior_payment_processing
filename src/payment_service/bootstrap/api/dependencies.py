import os

from fastapi import Header, HTTPException

async def get_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("API_KEY", "dev-key"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_api_key
