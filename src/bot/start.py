"""Handles the /start command: confirms the bot is alive and cleans up the command message."""
import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)
router = Router(name="start")


@router.channel_post(CommandStart())
@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handles the /start command, alerts if lacking admin rights, and auto-deletes the trigger."""
    sender_id = message.from_user.id if message.from_user else message.chat.id
    logger.info("User/Channel %s initiated /start in %s.", sender_id, message.chat.type)

    # 1) Try to respond verifying the bot is alive
    try:
        if message.chat.type == "channel":
            # Channels shouldn't use direct "reply" structure unless tied to a discussion board
            await message.bot.send_message(chat_id=message.chat.id, text="🤖 I am online and ready!")
        else:
            await message.reply("🤖 I am online and ready!")
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Failed to respond to /start command: %s", e)

    finally:
        # 2) Try to blindly delete the trigger message to sanitize public feeds
        try:
            await message.delete()
            if message.chat.type in ["group", "supergroup", "channel"]:
                logger.info(f"Deleted original /start command in {message.chat.type}.")
        except TelegramBadRequest as e:
            if message.chat.type in ["group", "supergroup", "channel"]:
                logger.warning("Lacking Delete Privileges. Error: %s", e)
                try:
                    warning_text = (
                        "⚠️ Warning: I failed to auto-delete the `/start` command "
                        "because I do not have the **'Delete messages'** Admin permission!"
                    )
                    await message.bot.send_message(
                        chat_id=message.chat.id, text=warning_text, parse_mode="Markdown"
                    )
                except Exception:
                    pass
        except Exception:
            pass
