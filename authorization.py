import jwt
import os
from dotenv import load_dotenv
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone

load_dotenv()

ALGORITHM = "RS256"

# Load RSA keys once at startup
with open(os.getenv("PRIVATE_KEY_PATH"), "rb") as f:
    PRIVATE_KEY = f.read()

with open(os.getenv("PUBLIC_KEY_PATH"), "rb") as f:
    PUBLIC_KEY = f.read()

"""
Function that creates a JWT for a specific user_id.
Takes the time (in seconds) after which the token should expire.
"""
def create_token(user_id: str, expires_in=3600):
    now = datetime.now(timezone.utc)

    payload = {
        "user_id": user_id,                         # User for whom the token is destined
        "iat": now,                                 # 'Issued at time'
        "exp": now + timedelta(seconds=expires_in)  # 'Expiration time'
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        return jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")