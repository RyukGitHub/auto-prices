"""Telegram deletion handler: automatically deletes any message starting with /."""
import logging
from aiogram import Router, types

logger = logging.getLogger(__name__)
router = Router(name="deleter")


@router.channel_post()
@router.message()
async def cmd_unknown(message: types.Message):
    """
    Catch-all handler for any message that hasn't been handled by previous routers.
    If it starts with '/', we delete it.
    """
    if message.text and message.text.startswith("/"):
        logger.info("Deleting unknown command from Chat ID %s: %s", message.chat.id, message.text)
        try:
            await message.delete()
        except BaseException as e:
            logger.error("Failed to delete unknown command: %s", e)
