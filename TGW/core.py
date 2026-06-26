import os
import sys
import json
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from protection import Protection
from commands import Commands
from installer import installer
from strings import Strings

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))

DATA_FILE = os.path.join(os.path.dirname(__file__), "TGWatcher.json")

s = Strings()


class DataManager:
    def __init__(self, api_id, api_hash, owner_id):
        self.api_id = api_id
        self.api_hash = api_hash
        self.owner_id = owner_id
        self.data = self.load_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {"admins": [], "sessions": {}, "banned": []}

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

    def get_admins(self):
        return self.data.get("admins", [])

    def add_admin(self, user_id):
        if user_id not in self.data["admins"]:
            self.data["admins"].append(user_id)
            self.save_data()
            return True
        return False

    def remove_admin(self, user_id):
        if user_id in self.data["admins"]:
            self.data["admins"].remove(user_id)
            self.save_data()
            return True
        return False

    def get_sessions(self):
        return self.data.get("sessions", {})

    def add_session(self, session_string, phone, user_id=None):
        session_id = str(len(self.data["sessions"]) + 1)
        while session_id in self.data["sessions"]:
            session_id = str(int(session_id) + 1)

        self.data["sessions"][session_id] = {
            "session": session_string,
            "phone": phone,
            "user_id": user_id
        }
        self.save_data()
        return session_id

    def remove_session(self, session_id):
        if session_id in self.data["sessions"]:
            del self.data["sessions"][session_id]
            self.save_data()
            return True
        return False

    def find_session_by_user_id(self, user_id):
        for session_id, session_data in self.data["sessions"].items():
            if session_data.get("user_id") == user_id:
                return session_id
        return None

    def get_banned(self):
        return self.data.get("banned", [])

    def add_banned(self, user_id):
        if user_id not in self.data["banned"]:
            self.data["banned"].append(user_id)
            self.save_data()
            return True
        return False

    def remove_banned(self, user_id):
        if user_id in self.data["banned"]:
            self.data["banned"].remove(user_id)
            self.save_data()
            return True
        return False


class WatcherManager:
    def __init__(self, bot, api_id, api_hash, data_manager):
        self.bot = bot
        self.api_id = api_id
        self.api_hash = api_hash
        self.data = data_manager
        self.watchers = {}

    async def start_session(self, session_id, session_string):
        try:
            client = TelegramClient(
                StringSession(session_string),
                self.api_id,
                self.api_hash,
                device_model="Package Manager",
                system_version="Linux",
                app_version="1.0"
            )

            await client.connect()

            if not await client.is_user_authorized():
                await client.disconnect()
                return False, "Session not authorized"

            me = await client.get_me()
            phone = me.phone

            self.watchers[session_id] = client

            await installer.notify_session_start(session_id, client)

            asyncio.create_task(client.run_until_disconnected())

            return True, phone

        except Exception as e:
            logger.error(f"Failed to start session {session_id}: {e}")
            return False, str(e)

    async def stop_session(self, session_id):
        await installer.notify_session_stop(session_id)

        if session_id in self.watchers:
            try:
                await self.watchers[session_id].disconnect()
            except Exception:
                pass
            del self.watchers[session_id]

    def get_active_sessions(self):
        return list(self.watchers.keys())

    async def notify_admins(self, message):
        notify_ids = [self.data.owner_id] + self.data.get_admins()

        for user_id in notify_ids:
            try:
                await self.bot.send_message(user_id, message, parse_mode='html')
            except Exception:
                pass

    async def restore_all_sessions(self):
        sessions = self.data.get_sessions()

        for session_id, session_data in sessions.items():
            success, result = await self.start_session(session_id, session_data['session'])

            if success:
                logger.info(f"Restored session {session_id} (+{result})")
            else:
                logger.error(f"Failed to restore session {session_id}: {result}")

    async def stop_all_sessions(self):
        for session_id in list(self.watchers.keys()):
            await self.stop_session(session_id)


async def set_bot_profile(token):
    import aiohttp

    bot_name = "TGWatcher"
    bot_desc = "Telegram session monitoring bot"
    bot_about = "Monitor your Telegram sessions"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.telegram.org/bot{token}/setMyName",
                params={"name": bot_name},
            ) as r:
                res_name = await r.json()

            async with session.get(
                f"https://api.telegram.org/bot{token}/setMyDescription",
                params={"description": bot_desc},
            ) as r:
                res_desc = await r.json()

            async with session.get(
                f"https://api.telegram.org/bot{token}/setMyShortDescription",
                params={"short_description": bot_about},
            ) as r:
                res_about = await r.json()

            if res_name.get("ok") and res_desc.get("ok") and res_about.get("ok"):
                logger.info("Bot profile updated successfully")
            else:
                logger.warning("Failed to update bot profile")
    except Exception as e:
        logger.error(f"Error updating bot profile: {e}")


async def main():
    if not all([API_ID, API_HASH, BOT_TOKEN, OWNER_ID]):
        logger.error("Missing required environment variables")
        logger.error("Required: API_ID, API_HASH, BOT_TOKEN, OWNER_ID")
        sys.exit(1)

    bot = TelegramClient("TGWatcher", API_ID, API_HASH)

    await bot.start(bot_token=BOT_TOKEN)

    me = await bot.get_me()
    logger.info(f"Bot started: {me.first_name} (@{me.username})")

    await set_bot_profile(BOT_TOKEN)

    data_manager = DataManager(API_ID, API_HASH, OWNER_ID)
    watcher_manager = WatcherManager(bot, API_ID, API_HASH, data_manager)

    installer.set_context(bot, watcher_manager)
    logger.info("Loading modules...")
    await installer.load_all()
    logger.info(f"Loaded modules: {installer.get_loaded()}")

    protection = Protection(
        bot,
        OWNER_ID,
        data_manager.get_admins,
        data_manager.get_banned,
        data_manager.add_banned
    )

    @bot.on(events.ChatAction)
    async def handle_chat_action(event):
        await protection.handle_chat_action(event)

    @bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_group or e.is_channel))
    async def handle_group_message(event):
        await protection.handle_group_message(event)

    commands = Commands(bot, protection, data_manager, watcher_manager, installer=installer)
    commands.register_handlers()

    logger.info("Restoring sessions...")
    await watcher_manager.restore_all_sessions()
    logger.info("All sessions restored")

    logger.info("Bot is ready")

    try:
        await bot.run_until_disconnected()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await watcher_manager.stop_all_sessions()
        await bot.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
