import logging
from src.services.github_service import trigger_safegold_workflow

logger = logging.getLogger(__name__)


async def process_safegold_and_notify() -> dict:
    """
    Triggers the SafeGold price fetching workflow on GitHub Actions.
    """
    try:
        logger.info("Triggering SafeGold fetch on GitHub Actions...")
        result = await trigger_safegold_workflow()
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "SafeGold workflow triggered successfully on GitHub.",
            }
        else:
            return result

    except Exception as e:
        logger.error("SafeGold trigger failed: %s", e, exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to trigger SafeGold action: {str(e)}"
        }
