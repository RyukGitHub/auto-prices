"""Telegram /trigger command: authorized price fetch, restricted to TELEGRAM_CHAT_ID."""
import os
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.services.price_service import process_prices_and_notify

logger = logging.getLogger(__name__)
router = Router(name="trigger")


@router.channel_post(Command("trigger"))
@router.message(Command("trigger"))
async def cmd_trigger(message: Message):
    """
    Triggers the price fetch sequence.
    Restricted to messages sent from TELEGRAM_CHAT_ID.
    """
    authorized_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not authorized_chat_id:
        logger.error("TELEGRAM_CHAT_ID not configured in .env")
        return

    try:
        # Verify that the message originated from the authorized chat
        if str(message.chat.id) != str(authorized_chat_id):
            # We silently ignore unauthorized triggers to prevent abuse
            logger.warning("Unauthorized /trigger in Chat ID: %s", message.chat.id)
            return

        # Acknowledge receipt first to avoid a timeout feeling
        status_message = None
        if message.chat.type != "channel":
            try:
                status_message = await message.reply("⏳ Fetching latest prices...")
            except BaseException:
                pass

        try:
            # Run the same core code the FastAPI endpoint uses!
            # This will send the actual message out to TELEGRAM_CHAT_ID natively
            await process_prices_and_notify()

            # We can clean up our status message since it worked
            if status_message:
                await status_message.delete()

        except Exception as e:
            logger.error("Error during Telegram manual trigger: %s", e)
            error_text = f"❌ Failed to fetch prices: `{e}`"

            if status_message:
                await status_message.edit_text(error_text, parse_mode="Markdown")
            elif message.chat.type != "channel":
                await message.reply(error_text, parse_mode="Markdown")
    finally:
        try:
            await message.delete()
        except BaseException:
            pass
