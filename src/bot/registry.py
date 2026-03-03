"""Silently tracks all observed Telegram chats in a local JSON registry file."""
import json
import logging
from aiogram import Router
from aiogram.types import Message

logger = logging.getLogger(__name__)
router = Router(name="registry")

DB_FILE = "registered_chats.json"


def load_registry():
    """Load the registry JSON from disk, returning an empty dict on failure."""
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error loading %s: %s", DB_FILE, e)
        return {}


def save_registry(data):
    """Persist the registry dict to disk as JSON."""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error saving %s: %s", DB_FILE, e)


@router.channel_post()
@router.message()
async def spider_logger(message: Message):
    """
    Wildcard listener! Silently caches the ID and Title of ANY chat it observes.
    This bypasses Telegram's inability to list bot chats natively.
    """
    # Skip private DMs between user and bot to prevent clutter
    if message.chat.type == "private":
        return

    chat_id = str(message.chat.id)
    chat_title = message.chat.title or "Unnamed Chat"
    chat_type = message.chat.type

    registry = load_registry()

    # If the chat is new or its title changed, update the database
    if chat_id not in registry or registry[chat_id].get("title") != chat_title:
        registry[chat_id] = {
            "title": chat_title,
            "type": chat_type
        }
        save_registry(registry)
        logger.info("[SPIDER] Cached chat: '%s' (%s)", chat_title, chat_id)
