import asyncio
import logging
import os
import re
import sys
import subprocess
from aiogram import Bot

# Reuse logic from safegold_service but adapted for Action environment
# Since we don't have the same DB on Action, we'll just send the current price.
# If you want price drop detection, we'd need a persistence layer like GitHub Gists or a remote DB.
# For now, let's focus on getting the price to Telegram.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_robot():
    """Run robot framework and return stdout."""
    cmd = [sys.executable, "-m", "robot", "--outputdir", "robot-results", "tests/robot/sg.robot"]
    process = subprocess.run(cmd, capture_output=True, text=True)
    return process.stdout, process.stderr, process.returncode

async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return

    logger.info("Starting SafeGold Robot fetch...")
    repo = "RyukGitHub/auto-prices"
    workflow_id = "safegold.yml"
    stdout, stderr, code = await run_robot()

    if code != 0:  # Assuming 'pat' was meant to be 'code' or 'stdout' based on the original logic
        logger.error("Robot failed: %s", stderr)

    # Parse price
    match = re.search(r"Live Buy Price is:.*?([\d,]+\.\d+\s*/g)", stdout, re.DOTALL)
    if not match:
        match = re.search(r"([\d,]+\.\d+\s*/g)", stdout)

    if match:
        raw_price = match.group(1).strip()
        price_msg = f"₹ {raw_price}"
        escaped_msg = price_msg.replace(".", "\\.").replace("-", "\\-")
        message = f"SAFEGOLD \\(Action\\) \\- {escaped_msg}"
        
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message, parse_mode="MarkdownV2")
        await bot.session.close()
        logger.info("Notified Telegram successfully.")
    else:
        logger.error("Could not parse price from: %s", stdout)

if __name__ == "__main__":
    asyncio.run(main())
