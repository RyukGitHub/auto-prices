"""Command handler for retrieving the cached chat registry."""
import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.bot.registry import load_registry

logger = logging.getLogger(__name__)
router = Router(name="getall_cmd")


@router.channel_post(Command("getall"))
@router.message(Command("getall"))
async def cmd_getall(message: Message):
    """
    Retrieves the list of all autonomously cached Channel and Group IDs.
    """
    # Only allow fetching from private chats or public groups/channels if permitted
    registry = load_registry()

    try:
        if not registry:
            await message.reply(
                "The chat registry is currently empty. "
                "The bot hasn't observed any messages in other channels yet."
            )
            return

        response = "🕷️ *Chat Registry:*\n\n"
        for chat_id, data in registry.items():
            title = data.get("title", "Unknown Chat")
            ctype = data.get("type", "unknown")
            response += f"• *{title}* (`{ctype}`)\n  ID: `{chat_id}`\n\n"

        try:
            await message.reply(response, parse_mode="Markdown")
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Failed to send /getall response: %s", e)
    finally:
        try:
            await message.delete()
        except BaseException:
            pass
