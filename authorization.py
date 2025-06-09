import jwt
from datetime import datetime, timedelta

ALGORITHM = "RS256"

# Load RSA keys once at startup
with open("keys/private.pem", "rb") as f:
    PRIVATE_KEY = f.read()

with open("keys/public.pem", "rb") as f:
    PUBLIC_KEY = f.read()

"""
Function that creates a JWT for a specific user_id.
Takes the time (in seconds) after which the token should expire.
"""
def create_token(user_id: str, expires_in=60):
    payload = {
        "user_id": user_id,                                    # User for whom the token is destined
        "iat": datetime.now(),                                 # 'Issued at time'
        "exp": datetime.now() + timedelta(seconds=expires_in)  # 'Expiration time'
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    return jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])