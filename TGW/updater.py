import os
import sys
import asyncio
import subprocess
import git
import aiohttp
from git import Repo


REPO_URL = "https://github.com/i-execute/TGWatcher"
REPO_API = "https://api.github.com/repos/i-execute/TGWatcher/commits/main"


async def get_current_commit():
    try:
        repo = Repo(os.path.dirname(os.path.dirname(__file__)))
        return repo.head.commit.hexsha
    except:
        return "unknown"


async def get_latest_commit():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                REPO_API,
                headers={"Accept": "application/vnd.github+json"},
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("sha"), data.get("html_url")
                if response.status == 403:
                    retry_after = response.headers.get("X-RateLimit-Reset")
                    return None, None
                return None, None
    except:
        return None, None


async def check_for_updates():
    current = await get_current_commit()
    latest, url = await get_latest_commit()

    if not latest:
        return False, current, current, None

    has_update = current != "unknown" and latest != current
    return has_update, latest, current, url


async def pull_updates():
    try:
        repo = Repo(os.path.dirname(os.path.dirname(__file__)))
        origin = repo.remote("origin")
        origin.pull()
        return True, "Updated successfully"
    except Exception as e:
        return False, str(e)


async def restart_bot():
    try:
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        return False, str(e)
    return True, "Restarting..."


def get_commit_link(commit_hash):
    if not commit_hash or commit_hash == "unknown":
        return "#"
    return f"{REPO_URL}/commit/{commit_hash}"
