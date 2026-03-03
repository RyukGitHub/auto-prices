"""Purge command handler: bulk-deletes recent messages in Groups and Channels."""
import logging
import asyncio
from typing import List
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)
router = Router(name="purge")


@router.channel_post(Command("purge"))
@router.message(Command("purge"))
async def cmd_purge(message: Message):
    try:
        await _do_purge(message)
    finally:
        try:
            await message.delete()
        except Exception:
            pass


async def _do_purge(message: Message):
    """
    Deletes a batch of recent messages.
    Usage 1: /purge 10 -> Deletes the last 10 messages.
    Usage 2: Reply to a message with /purge -> Deletes from replied message to current one.
    """
    chat_id = message.chat.id
    current_id = message.message_id
    sender_id = message.from_user.id if message.from_user else chat_id

    # Must be in a group, supergroup, or channel
    if message.chat.type == "private":
        await message.reply(
            "The `/purge` command is only available in Groups and Channels.",
            parse_mode="Markdown"
        )
        return

    message_ids_to_delete: List[int] = []

    # 1. Check if the command was sent as a Reply
    if message.reply_to_message:
        start_id = message.reply_to_message.message_id
        # Build the ID range between start and current message
        message_ids_to_delete = list(range(start_id, current_id + 1))
        logger.info(
            "%s initiated a range /purge in %s (IDs %s to %s).",
            sender_id, message.chat.type, start_id, current_id,
        )

    # 2. Check if a number parameter was provided (e.g., /purge 10)
    else:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].isdigit():
            # Nothing was provided — show usage hint, then auto-delete after 5s
            warning = await message.reply(
                "⚠️ Invalid usage.\nReply to a message with `/purge` or type `/purge 10`.",
                parse_mode="Markdown"
            )
            await asyncio.sleep(5)
            try:
                await message.delete()
                await warning.delete()
            except TelegramBadRequest:
                pass
            return

        count = int(parts[1])
        if count <= 0:
            return

        logger.info("%s initiated /purge %s in %s.", sender_id, count, message.chat.type)

        # Telegram IDs auto-increment even for ghost messages, so we loop backward in chunks
        deleted_count = 0
        search_id = current_id

        while deleted_count < count and search_id > 0:
            chunk_needed = min(100, count - deleted_count)
            chunk_ids = list(range(max(1, search_id - chunk_needed + 1), search_id + 1))

            try:
                # delete_messages silently skips IDs that no longer exist
                await message.bot.delete_messages(chat_id=chat_id, message_ids=chunk_ids)
                deleted_count += len(chunk_ids)
            except TelegramBadRequest as e:
                logger.debug("Chunk deletion skipped near ID %s: %s", search_id, e)

            search_id -= chunk_needed

        logger.info("Purge complete for %s.", chat_id)
        return

    # Range Purge Execution (from Reply)
    chunk_size = 100
    for i in range(0, len(message_ids_to_delete), chunk_size):
        chunk = message_ids_to_delete[i:i + chunk_size]
        try:
            await message.bot.delete_messages(chat_id=chat_id, message_ids=chunk)
        except TelegramBadRequest as e:
            logger.warning("Partial failure during bulk purge in %s. Error: %s", chat_id, e)

    logger.info("Purge complete for %s.", chat_id)
