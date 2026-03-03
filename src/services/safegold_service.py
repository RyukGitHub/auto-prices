import logging
from src.api_client import get_safegold_quote
from src.telegram_bot import send_custom_message
from src.database import db

logger = logging.getLogger(__name__)


async def process_safegold_and_notify(use_cache: bool = True) -> dict:  # pylint: disable=unused-argument
    """
    Fetches SafeGold price via direct API and notifies Telegram.
    This bypasses WAF using TLS spoofing.
    """
    try:
        logger.info("Fetching SafeGold price via direct API...")
        quote = await get_safegold_quote()
        price_str = quote["preTaxAmount"]
        price_float = float(price_str)

        # 2. Format for MarkdownV2
        formatted_price = str(price_str).replace(".", "\\.")
        
        # 3. Check for price drop
        previous_price = db.get_previous_safegold_price()
        if previous_price is not None and price_float < previous_price:
            formatted_price = f"*{formatted_price}*"
            
        # 4. Save state
        db.set_safegold_price(price_float)

        # 5. Notify Telegram
        message = f"SAFEGOLD \\- ₹ {formatted_price} /g"
        await send_custom_message(message)

        return {
            "status": "success",
            "message": f"SafeGold price fetched: {price_str}",
        }

    except Exception as e:
        logger.error("SafeGold fetch failed: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to fetch SafeGold price: {str(e)}"
        }
