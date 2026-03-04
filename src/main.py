"""FastAPI entry point: exposes /health and /trigger, and runs the Aiogram polling loop."""
import asyncio
import logging
import os
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from src.bot.purge import router as purge_router
from src.bot.registry import router as registry_router
from src.bot.start import router as start_router
from src.bot.getall_cmd import router as getall_router
from src.bot.trigger import router as command_trigger_router
from src.bot.safegold import router as safegold_router
from src.bot.deleter import router as deleter_router
from src.services.price_service import process_prices_and_notify
from src.services.safegold_service import process_safegold_and_notify

# Configure standardized logging for the entire application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
if not bot_token:
    raise ValueError("TELEGRAM_BOT_TOKEN must be set in .env")

# Initialize Aiogram Bot and Dispatcher
bot = Bot(token=bot_token)
dp = Dispatcher()

# Include routers (deleter MUST be before registry to catch unknown slashes)
dp.include_router(purge_router)
dp.include_router(start_router)
dp.include_router(command_trigger_router)
dp.include_router(safegold_router)
dp.include_router(getall_router)
dp.include_router(deleter_router)
dp.include_router(registry_router)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage the Aiogram polling lifecycle alongside the FastAPI server."""
    bot_task = asyncio.create_task(dp.start_polling(bot))

    # Notify the Telegram channel that the service has started
    startup_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if startup_chat_id:
        try:
            await bot.send_message(
                chat_id=startup_chat_id,
                text="🚀 *Deployment Successful*",
                parse_mode="Markdown"
            )
            logger.info("Sent startup notification to Telegram.")
        except Exception as err:  # pylint: disable=broad-except
            logger.error("Failed to send startup notification: %s", err)

    yield

    # Graceful shutdown
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Fetcher", lifespan=lifespan)


@app.get("/health")
def health_check():
    """Health endpoint to verify the web service is running."""
    return {"status": "ok", "message": "Service is healthy"}


@app.get("/trigger")
async def trigger_quote():
    """Fetch the latest prices and notify Telegram."""
    try:
        return await process_prices_and_notify()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/safegold")
async def trigger_safegold():
    """Execute SafeGold price fetch and notify Telegram."""
    try:
        return await process_safegold_and_notify()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
