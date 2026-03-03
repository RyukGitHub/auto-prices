import asyncio
import logging
import re
import sys
from src.telegram_bot import send_custom_message
from src.database import db

logger = logging.getLogger(__name__)


async def process_safegold_and_notify() -> dict:
    """
    Runs the SafeGold Robot test, parses the price from the output,
    compares it with the previous price, and notifies Telegram.
    """
    try:
        # 1. Run the Robot test
        # Use sys.executable -m robot for cross-platform compatibility (Windows/Linux)
        cmd = [sys.executable, "-m", "robot", "--outputdir", "logs", "tests/robot/sg.robot"]
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            logger.error("Robot test failed with return code %s", process.returncode)
            logger.error("Stderr: %s", stderr.decode())
            # Even if it failed, we might have part of stdout.
            # But usually, it means the price wasn't found.

        # Use utf-8 decoding by default, but be resilient to encoding issues
        output = stdout.decode("utf-8", errors="replace")
        logger.info("Robot output: %s", output)

        # 2. Parse the price from stdout
        # Flexible match: Look for digits followed by /g, after "Live Buy Price is:"
        # This ignores the currency symbol which might be mangled to '?' or something else.
        match = re.search(r"Live Buy Price is:.*?([\d,]+\.\d+\s*/g)", output, re.DOTALL)

        if not match:
            # Fallback: just look for the price pattern anywhere
            match = re.search(r"([\d,]+\.\d+\s*/g)", output)

        if not match:
            raise ValueError(f"Could not parse SafeGold price from Robot output: {output}")

        raw_price_val = match.group(1).strip()
        # Ensure we have the rupee symbol for the Telegram message if it was stripped/mangled
        price_msg = f"₹ {raw_price_val}"

        # Extract numeric value for comparison
        price_numeric_match = re.search(r"[\d,]+\.\d+", raw_price_val)
        if not price_numeric_match:
            raise ValueError(f"Could not extract numeric price from {raw_price_val}")

        current_price = float(price_numeric_match.group(0).replace(",", ""))
        previous_price = db.get_previous_safegold_price()

        # 3. Format message for Telegram
        # Escaping for MarkdownV2
        escaped_price_msg = price_msg.replace(".", "\\.").replace("-", "\\-")

        # Bold if price dropped
        if previous_price is not None and current_price < previous_price:
            escaped_price_msg = f"*{escaped_price_msg}*"

        message = f"SAFEGOLD \\- {escaped_price_msg}"

        # 4. Notify Telegram
        await send_custom_message(message)

        # 5. Persist the new price
        db.set_safegold_price(current_price)

        return {
            "status": "success",
            "message": "SafeGold price fetched and notified successfully.",
        }

    except Exception as e:
        logger.error("SafeGold processing failed: %s", e, exc_info=True)
        raise RuntimeError(f"Failed to process SafeGold prices: {e}") from e
