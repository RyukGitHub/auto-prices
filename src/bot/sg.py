"""Telegram /sg command: authorized SG price fetch, restricted to TELEGRAM_CHAT_ID."""
import os
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.services.sg_service import process_sg_and_notify

logger = logging.getLogger(__name__)
router = Router(name="sg")


@router.channel_post(Command("sg"))
@router.message(Command("sg"))
async def cmd_sg(message: Message):
    """
    Triggers the SG price fetch sequence.
    Restricted to messages sent from TELEGRAM_CHAT_ID.
    Usage: /sg
    """
    authorized_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not authorized_chat_id:
        logger.error("TELEGRAM_CHAT_ID not configured in .env")
        return

    try:
        if str(message.chat.id) != str(authorized_chat_id):
            logger.warning("Unauthorized /sg in Chat ID: %s", message.chat.id)
            return

        status_text = "⏳ Fetching SG prices..."
        status_message = None
        if message.chat.type != "channel":
            try:
                status_message = await message.reply(status_text)
            except Exception: # pylint: disable=broad-except
                pass

        try:
            await process_sg_and_notify()

            if status_message:
                await status_message.delete()

        except Exception as err:
            logger.error("Error during SG manual trigger: %s", err)
            error_text = f"❌ Failed to fetch SG price: `{err}`"

            if status_message:
                await status_message.edit_text(error_text, parse_mode="Markdown")
            elif message.chat.type != "channel":
                await message.reply(error_text, parse_mode="Markdown")
    finally:
        try:
            await message.delete()
        except Exception: # pylint: disable=broad-except
            pass
