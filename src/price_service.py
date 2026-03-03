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
def _fetch_validated_price(currency_pair: str, name: str) -> str:
    data = get_quote(currency_pair)
    price_str = data.get("preTaxAmount")
    if not price_str:
        raise ValueError(f"preTaxAmount not found in {name} response: {data}")
    return price_str

def process_prices_and_notify() -> dict:
    """
    Core sequence: 
    1) Fetches both gold and silver from MMTC-PAMP.
    2) Calculates drops compared to previous memory state.
    3) Automatically broadcasts the message.
    4) Returns the raw message info for API consumption.
    """
    # 1. Fetch Gold & Silver (XAU/XAG)
    gold_price_str = _fetch_validated_price("XAU/INR", "Gold")
    gold_price_float = float(gold_price_str)
    
    silver_price_str = _fetch_validated_price("XAG/INR", "Silver")
        
    # 2. Check Database State and Format Gold Price
    previous_gold_price = db.get_previous_gold_price()
    formatted_gold_price = f"{gold_price_str}".replace(".", "\\.")
    silver_price_md = f"{silver_price_str}".replace(".", "\\.")
    
    # If we have a previous price, and the current price is strictly less than it, bold it
    if previous_gold_price is not None and gold_price_float < previous_gold_price:
        formatted_gold_price = f"*{formatted_gold_price}*"
        
    # 3. Save new state
    db.set_gold_price(gold_price_float)

    # 4. Send to Telegram
    # The default broadcast uses TELEGRAM_CHAT_ID from .env 
    send_telegram_message(formatted_gold_price, silver_price_md)

    return {
        "status": "success",
        "message": "Prices fetched and Telegram channel notified successfully."
    }
