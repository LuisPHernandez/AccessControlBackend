from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from authorization import create_token, verify_token
from gate_controller import send_open_message
from passlib.context import CryptContext
from db import get_db_connection

# Global variables
IP_MICRO = "192.168.0.60"

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

# Password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/")
def root():
    return {"message": "API funcionando"}

@app.post("/login")
def login(request: LoginRequest):
    # Connect to the database
    conn = get_db_connection()
    cur = conn.cursor()

    # Extract email and password from request
    email = request.email
    password = request.password

    # Check if a user exists with the given email
    cur.execute(
        """SELECT 1 FROM "user" WHERE email = %s""",
        (email,)
        )
    if (not cur.fetchone()):
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="User not found")
    
    # Verify if the given password matches the stored password
    cur.execute(
        """SELECT password FROM "user" WHERE email = %s""",
        (email,)
        )
    result = cur.fetchone()
    db_hashed_password = result[0]
    if (not pwd_context.verify(password, db_hashed_password)):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    # Close connection to database
    conn.commit()
    cur.close()
    conn.close()
    
    # If the login request is valid, generate and return token
    token = create_token(email)
    return {"token": token}

@app.post("/signup")
def signup(request: SignupRequest):
    # Connect to the database
    conn = get_db_connection()
    cur = conn.cursor()

    # Extract email and password from request, hash the password
    email = request.email
    hashed_password = pwd_context.hash(request.password)

    # Verify if the given email is already registered to an account
    cur.execute(
        """SELECT 1 FROM "user" WHERE email = %s""",
        (email,)
        )
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="User already registered")

    # If request is valid, insert email and password to the database
    cur.execute(
        """INSERT INTO "user" (email, password) VALUES (%s, %s)""",
        (email, hashed_password)
        )
    
    # Close connection to database
    conn.commit()
    cur.close()
    conn.close()

    # Return success message
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