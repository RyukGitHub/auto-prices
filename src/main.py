import uvicorn
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from src.price_service import process_prices_and_notify

from aiogram import Bot, Dispatcher
import os
import asyncio
import logging

# Configure standardized logging for the entire application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load the Routers
from src.modules.purge import router as purge_router
from src.modules.start import router as start_router
from src.modules.registry import router as registry_router
from src.modules.trigger import router as command_trigger_router

# Load environment variables
load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
if not bot_token:
    raise ValueError("TELEGRAM_BOT_TOKEN must be set in .env")

# Initialize Aiogram
bot = Bot(token=bot_token)
dp = Dispatcher()

# Include routers
dp.include_router(purge_router)
dp.include_router(start_router)
dp.include_router(command_trigger_router)
# Include registry LAST because it contains a wildcard message listener that intercepts everything!
dp.include_router(registry_router)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the aiogram bot polling in the background when FastAPI starts
    bot_task = asyncio.create_task(dp.start_polling(bot))
    yield
    # Cleanup when FastAPI shuts down
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
def trigger_quote():
    try:
        # Run the shared price logic
        response = process_prices_and_notify()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
