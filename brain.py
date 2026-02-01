import os
import time
import requests

# ===============================
# TELEGRAM CLOUD BRAIN — FINAL
# ===============================

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_ID = os.environ.get("ALLOWED_CHAT_ID")
LAPTOP_BRAIN_URL = os.environ.get("LAPTOP_BRAIN_URL")  # http://IP:8765

API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

last_update_id = None


def send_message(text):
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": ALLOWED_CHAT_ID,
        "text": text
    }
    requests.post(url, json=payload)


def check_laptop_status():
    try:
        r = requests.get(f"{LAPTOP_BRAIN_URL}/health", timeout=3)
        state = r.json().get("state", "unknown")
        return f"💻 Laptop Brain Online\nState: {state}"
    except:
        return "💤 Laptop Brain Offline"


def send_task_to_laptop(command):
    try:
        requests.post(
            f"{LAPTOP_BRAIN_URL}/task",
            json={"command": command},
            timeout=5
        )
        return "⚡ Task sent to Laptop Brain"
    except:
        return "❌ Laptop Brain not reachable"


def handle_command(text):
    text = text.lower()

    if text == "status":
        return check_laptop_status()

    if any(word in text for word in ["build", "create", "make"]):
        return send_task_to_laptop(text)

    return "🧠 Brain online. Command received."


def poll_updates():
    global last_update_id

    url = f"{API_URL}/getUpdates"
    params = {"timeout": 30, "offset": last_update_id}

    r = requests.get(url, params=params).json()

    for update in r.get("result", []):
        last_update_id = update["update_id"] + 1

        message = update.get("message")
        if not message:
            continue

        chat_id = str(message["chat"]["id"])
        text = message.get("text", "")

        if chat_id != ALLOWED_CHAT_ID:
            continue

        response = handle_command(text)
        send_message(response)


if __name__ == "__main__":
    send_message("🧠 Cloud Brain online (Telegram connected)")
    while True:
        poll_updates()
        time.sleep(1)
