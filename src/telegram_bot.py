import requests
import os

def send_telegram_message(gold_price: str, silver_price: str):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

    message = f"GOLD \\- {gold_price}\nSILVER \\- {silver_price}"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "MarkdownV2"
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()
