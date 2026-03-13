"""Service layer for fetching SG prices via API and notifying Telegram."""
import logging
from src.api_client import get_sg_quote
from src.telegram_bot import send_custom_message
from src.database import db

logger = logging.getLogger(__name__)


async def process_sg_and_notify() -> dict:
    """
    Fetches SG prices via direct API and notifies Telegram.
    This bypasses WAF using TLS spoofing.
    """
    try:
        logger.info("Fetching SG prices via direct API...")
        quote = await get_sg_quote()
        buy_rate = quote["buy"]
        sell_rate = quote["sell"]

        # 2. Format for MarkdownV2
        buy_md = str(buy_rate).replace(".", "\\.")
        sell_md = str(sell_rate).replace(".", "\\.")

        # 3. Check for price drop (on Buy rate)
        previous_price = db.get_previous_sg_price()
        if previous_price is not None and float(buy_rate) < previous_price:
            buy_md = f"*{buy_md}*"

        # 4. Save state
        db.set_sg_price(float(buy_rate))

        # 5. Notify Telegram
        message = (
            "SAFEGOLD\n"
            f"BUY: ₹ {buy_md} /g\n"
            f"SELL: ₹ {sell_md} /g"
        )
        await send_custom_message(message)

        return {
            "status": "success",
            "message": "SG prices fetched and notified successfully.",
        }

    except Exception as e:
        logger.error("SG fetch failed: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to fetch SG prices: {str(e)}"
        }
