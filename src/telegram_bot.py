"""Async Telegram messaging client for broadcasting price updates."""
import os
from typing import Dict, Any

import aiohttp


async def send_telegram_message(
    gold_buy: str,
    silver_buy: str,
    gold_sell: str,
    silver_sell: str,
) -> Dict[str, Any]:
    """Broadcasts the Buy/Sell price matrix to the Telegram Chat."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        error_msg = ("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID "
                     "must be set in .env")
        raise ValueError(error_msg)

    message = (
        f"*BUY PRICES*\nGOLD \\- {gold_buy}\nSILVER \\- {silver_buy}\n\n"
        f"*SELL PRICES*\nGOLD \\- {gold_sell}\nSILVER \\- {silver_sell}"
    )

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


async def send_custom_message(text: str) -> Dict[str, Any]:
    """Sends a custom MarkdownV2 formatted message to the Telegram Chat."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in .env"
        )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()
