from fastapi import FastAPI
from qr import generate_qr_token

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "API funcionando"}

@app.get("/generate_qr/{user_id}")
def get_qr(user_id: str):
    qr_path, token = generate_qr_token(user_id)
    return {
        "qr_image_path": qr_path,
        "token": token
    }