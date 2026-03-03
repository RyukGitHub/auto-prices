import os
import aiohttp
import logging

logger = logging.getLogger(__name__)

async def trigger_safegold_workflow():
    """Triggers the GitHub Action workflow using a Personal Access Token."""
    pat = os.getenv("GITHUB_PAT")
    repo = "RyukGitHub/auto-prices"
    workflow_id = "safegold.yml"

    if not pat:
        logger.error("GITHUB_PAT not set in environment.")
        return {"status": "error", "message": "GITHUB_PAT not set"}

    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/dispatches"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = {
        "ref": "master", # or the branch name
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 204:
                logger.info("Successfully triggered GitHub Action workflow.")
                return {"status": "success", "message": "Safegold workflow triggered on GitHub."}
            else:
                resp_text = await response.text()
                logger.error("Failed to trigger GitHub Action: %s - %s", response.status, resp_text)
                return {"status": "error", "message": f"GitHub API error: {response.status}"}
