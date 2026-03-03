import aiohttp
import os
from typing import Dict, Any

async def send_telegram_message(gold_buy: str, silver_buy: str, gold_sell: str, silver_sell: str) -> Dict[str, Any]:
    """
    Broadcasts the newly formatted price data matrix to the configured Telegram Chat.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env")

    message = f"*BUY PRICES*\nGOLD \\- {gold_buy}\nSILVER \\- {silver_buy}\n\n*SELL PRICES*\nGOLD \\- {gold_sell}\nSILVER \\- {silver_sell}"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "MarkdownV2"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()
