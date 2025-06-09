import qrcode
from authorization import create_token
import os

"""
Function that creates a qr code, with a token, for a given user.
"""
def generate_qr_token(user_id: str):
    token = create_token(user_id)   # JWT with necessary info
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")

    # Create qr_codes folder, does not fail if it already exists
    folder = "qr_codes"
    os.makedirs(folder, exist_ok=True)

    # Save the generated qr's image in the qr_codes folder
    file_path = os.path.join(folder, f"{user_id}.png")
    img.save(file_path)

    return file_path, token
