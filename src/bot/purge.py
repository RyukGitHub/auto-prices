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
    """Entry point for /purge command."""
    try:
        await _do_purge(message)
    finally:
        try:
            await message.delete()
        except Exception:  # pylint: disable=broad-except
            pass


async def _do_purge(message: Message):
    """
    Deletes a batch of recent messages.
    Usage 1: /purge 10 -> Deletes the last 10 messages.
    Usage 2: Reply to a message with /purge -> Deletes from replied message to current one.
    """
    if message.chat.type == "private":
        await message.reply("The `/purge` command is only available in Groups and Channels.", parse_mode="Markdown")
        return

    if message.reply_to_message:
        await _purge_by_reply(message)
    else:
        await _purge_by_count(message)


async def _purge_by_reply(message: Message):
    """Deletes messages between the replied message and the current one."""
    start_id = message.reply_to_message.message_id
    current_id = message.message_id
    chat_id = message.chat.id
    message_ids = list(range(start_id, current_id + 1))

    chunk_size = 100
    for i in range(0, len(message_ids), chunk_size):
        chunk = message_ids[i:i + chunk_size]
        try:
            await message.bot.delete_messages(chat_id=chat_id, message_ids=chunk)
        except TelegramBadRequest as err:
            logger.warning("Partial failure during bulk purge in %s. Error: %s", chat_id, err)


async def _purge_by_count(message: Message):
    """Deletes a specific number of recent messages."""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        warning = await message.reply(
            "⚠️ Invalid usage.\nReply to a message with `/purge` or type `/purge 10`.",
            parse_mode="Markdown"
        )
        await asyncio.sleep(5)
        try:
            await warning.delete()
        except TelegramBadRequest:
            pass
        return

    count = int(parts[1])
    if count <= 0:
        return

    deleted_count = 0
    search_id = message.message_id
    chat_id = message.chat.id

    while deleted_count < count and search_id > 0:
        chunk_needed = min(100, count - deleted_count)
        chunk_ids = list(range(max(1, search_id - chunk_needed + 1), search_id + 1))

        try:
            await message.bot.delete_messages(chat_id=chat_id, message_ids=chunk_ids)
            deleted_count += len(chunk_ids)
        except TelegramBadRequest:
            pass
        search_id -= chunk_needed
