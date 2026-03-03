import os
import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from src.price_service import process_prices_and_notify

logger = logging.getLogger(__name__)
router = Router(name="trigger")

@router.channel_post(Command("trigger"))
@router.message(Command("trigger"))
async def cmd_trigger(message: Message):
    """
    Allows authorized group chats or channels to trigger the price fetch sequence manually via Telegram.
    Restrict this so it only works if the command is sent in the TELEGRAM_CHAT_ID defined in .env.
    """
    authorized_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not authorized_chat_id:
        logger.error("TELEGRAM_CHAT_ID not configured in .env")
        return

    # Verify that the message originated from the authorized chat
    if str(message.chat.id) != str(authorized_chat_id):
        # We silently ignore unauthorized triggers to prevent abuse
        logger.warning(f"Unauthorized /trigger attempted in Chat ID: {message.chat.id}")
        return

    # Acknowledge receipt first to avoid a timeout feeling
    status_message = None
    if message.chat.type != "channel":
        try:
            status_message = await message.reply("⏳ Fetching latest prices from MMTC-PAMP...")
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
        logger.error(f"Error during Telegram manual trigger: {e}")
        error_text = f"❌ Failed to fetch prices: `{e}`"
        
        if status_message:
            await status_message.edit_text(error_text, parse_mode="Markdown")
        elif message.chat.type != "channel":
            await message.reply(error_text, parse_mode="Markdown")
