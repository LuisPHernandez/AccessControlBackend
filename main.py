from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from authorization import create_token, verify_token
from gate_controller import send_open_message
from proximity import is_near_ble_beacon
from passlib.context import CryptContext

app = FastAPI()
IP_MICRO = "192.168.0.60"

# Request Models
class GateOpenRequest(BaseModel):
    token: str
    gate_id: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

# Simple in-memory "database"
users_db = {}

# Password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/")
def root():
    return {"message": "API funcionando"}

@app.post("/login")
def login(request: LoginRequest):
    email = request.email
    password = request.password
    if (email not in users_db):
        raise HTTPException(status_code=401, detail="User not found")
    if (not pwd_context.verify(password, users_db[email])):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    token = create_token(email)
    return {"token": token}

@app.post("/signup")
def login(request: SignupRequest):
    if request.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(request.password)
    users_db[request.email] = hashed_password

    return {"message": "Signup successful"}

@app.post("/open_gate")
async def open_gate(request: GateOpenRequest):
    try:
        decoded = verify_token(request.token) 

        user_id = decoded["user_id"]

        await send_open_message(IP_MICRO)

        return {"user_id": user_id, "gate_id": request.gate_id}

    except HTTPException:
        raise  # Re-raise internal HTTP errors coming from verify_token()
    except Exception as e:
        print(f"Unexpected error in /open_gate: {e}")
        raise HTTPException(status_code=500, detail="Error del servidor")