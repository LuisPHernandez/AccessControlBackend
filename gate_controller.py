import httpx

async def send_open_message(ip: str):
    try:
        url = f"http://{ip}/open"
        response = await httpx.post(url)
        response.raise_for_status()
        print("ESP32 respondió:", response.json())
    except Exception as e:
        print("Error al comunicar con ESP32:", e)