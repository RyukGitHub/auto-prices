import logging
from src.api_client import get_quote
from src.telegram_bot import send_telegram_message
from src.database import db

logger = logging.getLogger(__name__)

def process_prices_and_notify() -> dict:
    """
    Core sequence: 
    1) Fetches both gold and silver from MMTC-PAMP.
    2) Calculates drops compared to previous memory state.
    3) Automatically broadcasts the message.
    4) Returns the raw message info for API consumption.
    """
async def _fetch_validated_price(currency_pair: str, name: str, quote_type: str = "BUY") -> str:
    data = await get_quote(currency_pair, quote_type)
    price_str = data.get("preTaxAmount")
    if not price_str:
        raise ValueError(f"preTaxAmount not found in {name} ({quote_type}) response: {data}")
    return price_str

async def process_prices_and_notify() -> dict:
    """
    Core sequence: 
    1) Fetches both gold and silver (Buy & Sell) from MMTC-PAMP.
    2) Calculates drops compared to previous memory state on the Gold Buy price.
    3) Automatically broadcasts the message.
    4) Returns the raw message info for API consumption.
    """
    try:
        # 1. Fetch Gold & Silver BUY Prices
        gold_buy_str = await _fetch_validated_price("XAU/INR", "Gold", "BUY")
        gold_buy_float = float(gold_buy_str)
        silver_buy_str = await _fetch_validated_price("XAG/INR", "Silver", "BUY")
        
        # 2. Fetch Gold & Silver SELL Prices
        gold_sell_str = await _fetch_validated_price("XAU/INR", "Gold", "SELL")
        silver_sell_str = await _fetch_validated_price("XAG/INR", "Silver", "SELL")
            
        # 3. Check Database State and Format Gold Buy Price
        previous_gold_buy = db.get_previous_gold_price()
        
        formatted_gold_buy = f"{gold_buy_str}".replace(".", "\\.")
        silver_buy_md = f"{silver_buy_str}".replace(".", "\\.")
        
        formatted_gold_sell = f"{gold_sell_str}".replace(".", "\\.")
        silver_sell_md = f"{silver_sell_str}".replace(".", "\\.")
        
        # If we have a previous BUY price, and the current BUY price is strictly less than it, bold it
        if previous_gold_buy is not None and gold_buy_float < previous_gold_buy:
            formatted_gold_buy = f"*{formatted_gold_buy}*"
            
        # 4. Save new state
        db.set_gold_price(gold_buy_float)

        # 5. Send to Telegram
        await send_telegram_message(formatted_gold_buy, silver_buy_md, formatted_gold_sell, silver_sell_md)

        return {
            "status": "success",
            "message": "Prices fetched and Telegram channel notified successfully."
        }
    except Exception as e:
        logger.error(f"Price processing pipeline failed: {e}", exc_info=True)
        raise RuntimeError(f"Failed to process prices: {e}") from e
