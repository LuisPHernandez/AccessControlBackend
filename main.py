from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from authorization import verify_token
from proximity import is_near_ble_beacon

app = FastAPI()

class GateOpenRequest(BaseModel):
    token: str
    gate_id: str  # extracted from scanned QR

@app.get("/")
def root():
    return {"message": "API funcionando"}

async def open_gate(request: GateOpenRequest):
    try:
        decoded = verify_token(request.token)

        user_id = decoded["user_id"]

        if not is_near_ble_beacon(user_id):
            raise HTTPException(status_code=403, detail="User not near gate")

        # TODO Send signal to microcontroller
        print(f"Opening gate {request.gate_id} for user {user_id}")

        return {"status": "success", "user_id": user_id, "gate_id": request.gate_id}

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")