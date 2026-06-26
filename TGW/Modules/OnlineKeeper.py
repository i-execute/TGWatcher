import asyncio
import logging
import random
from datetime import datetime, timedelta

from telethon.errors import AuthKeyUnregisteredError, UserDeactivatedBanError
from telethon.tl.functions.account import UpdateStatusRequest

from installer import BaseModule

logger = logging.getLogger(__name__)


class OnlineKeeperModule(BaseModule):
    name = "OnlineKeeper"
    version = (1, 0, 0)

    def __init__(self):
        super().__init__()
        self._tasks = {}

    async def on_start(self, bot, watcher_manager):
        pass

    async def on_session_start(self, session_id, client):
        if session_id in self._tasks:
            return

        task = asyncio.create_task(self._schedule_runner(session_id, client))
        self._tasks[session_id] = task
        logger.info(f"OnlineKeeper started for session {session_id}")

    async def on_session_stop(self, session_id):
        task = self._tasks.pop(session_id, None)
        if task:
            task.cancel()
        logger.info(f"OnlineKeeper stopped for session {session_id}")

    async def on_stop(self):
        for session_id, task in list(self._tasks.items()):
            task.cancel()
        self._tasks.clear()

    def _generate_daily_schedule(self):
        sessions_count = random.randint(1, 10)
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        total_seconds = int((end_of_day - start_of_day).total_seconds())

        sessions = []
        for _ in range(sessions_count):
            start = start_of_day + timedelta(seconds=random.randint(0, total_seconds))
            duration = random.randint(1, 30)
            sessions.append({"start": start, "duration": duration})

        return sorted(sessions, key=lambda x: x["start"])

    async def _set_online(self, client, duration_minutes):
        try:
            if not await client.is_user_authorized():
                return
            await client(UpdateStatusRequest(offline=False))
            await asyncio.sleep(duration_minutes * 60)
            await client(UpdateStatusRequest(offline=True))
        except (AuthKeyUnregisteredError, UserDeactivatedBanError):
            pass
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"OnlineKeeper set_online error: {e}")

    async def _schedule_runner(self, session_id, client):
        while True:
            schedule = self._generate_daily_schedule()
            now = datetime.now()

            for plan in schedule:
                wait = (plan["start"] - now).total_seconds()
                if wait > 0:
                    await asyncio.sleep(wait)
                await self._set_online(client, plan["duration"])
                now = datetime.now()

            next_day = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            await asyncio.sleep((next_day - now).total_seconds())
