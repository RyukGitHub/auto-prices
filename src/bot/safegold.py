"""Telegram /safegold command: authorized SafeGold price fetch, restricted to TELEGRAM_CHAT_ID."""
import os
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.services.safegold_service import process_safegold_and_notify

logger = logging.getLogger(__name__)
router = Router(name="safegold")


@router.channel_post(Command("safegold"))
@router.message(Command("safegold"))
async def cmd_safegold(message: Message):
    """
    Triggers the SafeGold price fetch sequence.
    Restricted to messages sent from TELEGRAM_CHAT_ID.
    """
    authorized_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not authorized_chat_id:
        logger.error("TELEGRAM_CHAT_ID not configured in .env")
        return

    try:
        if str(message.chat.id) != str(authorized_chat_id):
            logger.warning("Unauthorized /safegold in Chat ID: %s", message.chat.id)
            return

        status_message = None
        if message.chat.type != "channel":
            try:
                status_message = await message.reply("⏳ Fetching SafeGold price...")
            except BaseException:
                pass

        try:
            await process_safegold_and_notify()

            if status_message:
                await status_message.delete()

        except Exception as e:
            logger.error("Error during SafeGold manual trigger: %s", e)
            error_text = f"❌ Failed to fetch SafeGold price: `{e}`"

            if status_message:
                await status_message.edit_text(error_text, parse_mode="Markdown")
            elif message.chat.type != "channel":
                await message.reply(error_text, parse_mode="Markdown")
    finally:
        try:
            await message.delete()
        except BaseException:
            pass
