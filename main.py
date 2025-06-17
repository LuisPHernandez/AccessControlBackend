from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from authorization import create_token, verify_token
from proximity import is_near_ble_beacon
from passlib.context import CryptContext

app = FastAPI()

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

        user_id = decoded["email"]
        exp_time = decoded["exp"]    

        if not is_near_ble_beacon(user_id):
            raise HTTPException(status_code=403, detail="User not near gate")

        # TODO Send signal to microcontroller
        print(f"Opening gate {request.gate_id} for user {user_id}")

        return {"user_id": user_id, "gate_id": request.gate_id}

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")