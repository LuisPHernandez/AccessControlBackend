from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qr import generate_qr_token
from authorization import verify_token
from proximity import is_near_ble_beacon

app = FastAPI()

class TokenPayload(BaseModel):
    token: str

@app.get("/")
def root():
    return {"message": "API funcionando"}

@app.get("/generate_qr/{user_id}")
def get_qr(user_id: str):
    qr_path, token = generate_qr_token(user_id)
    return {
        "qr_image_path": qr_path,
        "token": token
    }

@app.post("/verify_token")
async def verify_qr_token(payload: TokenPayload):
    token = payload.token
    
    try:
        decoded = verify_token(token)

        if not is_near_ble_beacon(decoded["user_id"]):
            raise HTTPException(status_code=403, detail="User not near gate")

        return {"status": "valid", "user_id": decoded["user_id"]}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")