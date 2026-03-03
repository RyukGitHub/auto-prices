"""Orchestrates the price fetch, drop detection, and Telegram notification pipeline."""
import logging

from src.api_client import get_quote
from src.telegram_bot import send_telegram_message
from src.database import db

logger = logging.getLogger(__name__)


async def _fetch_validated_price(currency_pair: str, name: str, quote_type: str = "BUY") -> str:
    """Fetch a single price and validate the expected field exists."""
    data = await get_quote(currency_pair, quote_type)
    price_str = data.get("preTaxAmount")
    if not price_str:
        raise ValueError(f"preTaxAmount not found in {name} ({quote_type}) response: {data}")
    return price_str


async def process_prices_and_notify() -> dict:
    """
    Core sequence:
    1) Fetches Gold and Silver BUY and SELL prices.
    2) Compares Gold BUY price against the stored previous value.
    3) Bolds the Gold BUY price in the Telegram message if it dropped.
    4) Saves the new Gold BUY price to the in-memory state.
    5) Sends the formatted message to Telegram.
    6) Returns a status dict for the FastAPI response.
    """
    try:
        # 1. Fetch all four prices concurrently could be added here with asyncio.gather
        gold_buy_str = await _fetch_validated_price("XAU/INR", "Gold", "BUY")
        gold_buy_float = float(gold_buy_str)
        silver_buy_str = await _fetch_validated_price("XAG/INR", "Silver", "BUY")

        gold_sell_str = await _fetch_validated_price("XAU/INR", "Gold", "SELL")
        silver_sell_str = await _fetch_validated_price("XAG/INR", "Silver", "SELL")

        # 2. Format all values for MarkdownV2 (escape dots)
        previous_gold_buy = db.get_previous_gold_price()
        formatted_gold_buy = gold_buy_str.replace(".", "\\.")
        silver_buy_md = silver_buy_str.replace(".", "\\.")
        formatted_gold_sell = gold_sell_str.replace(".", "\\.")
        silver_sell_md = silver_sell_str.replace(".", "\\.")

        # 3. Bold the Gold BUY price if it dropped since the last run
        if previous_gold_buy is not None and gold_buy_float < previous_gold_buy:
            formatted_gold_buy = f"*{formatted_gold_buy}*"

        # 4. Persist the new state
        db.set_gold_price(gold_buy_float)

        # 5. Send the formatted message to Telegram
        await send_telegram_message(
            formatted_gold_buy, silver_buy_md,
            formatted_gold_sell, silver_sell_md,
        )

        return {
            "status": "success",
            "message": "Prices fetched and Telegram channel notified successfully.",
        }
    except Exception as e:
        logger.error("Price processing pipeline failed: %s", e, exc_info=True)
        raise RuntimeError(f"Failed to process prices: {e}") from e
