import time
from collections import defaultdict
from telethon import events
from telethon.errors import ChatWriteForbiddenError, RPCError


class Protection:
    def __init__(self, bot, owner_id, get_admins_func, get_banned_func, add_banned_func):
        self.bot = bot
        self.owner_id = owner_id
        self.get_admins = get_admins_func
        self.get_banned = get_banned_func
        self.add_banned = add_banned_func

        self._leaving_now = set()
        self._user_commands = defaultdict(list)

        self.LEAVE_MESSAGE = "I leave the group if creator is asshole"
        self.SPAM_LIMIT_10S = 5
        self.SPAM_LIMIT_60S = 10

    def is_privileged(self, user_id):
        return user_id == self.owner_id or user_id in self.get_admins()

    def is_banned(self, user_id):
        return user_id in self.get_banned()

    def check_spam(self, user_id):
        if self.is_privileged(user_id):
            return False

        if self.is_banned(user_id):
            return True

        now = time.time()
        self._user_commands[user_id].append(now)

        recent = [t for t in self._user_commands[user_id] if now - t < 60]
        self._user_commands[user_id] = recent

        last_10s = [t for t in recent if now - t < 10]

        if len(last_10s) > self.SPAM_LIMIT_10S or len(recent) > self.SPAM_LIMIT_60S:
            self.add_banned(user_id)
            return True

        return False

    async def leave_chat(self, chat_id):
        try:
            await self.bot.send_message(chat_id, self.LEAVE_MESSAGE)
        except (ChatWriteForbiddenError, RPCError):
            pass

        try:
            await self.bot.delete_dialog(chat_id)
        except RPCError:
            pass

    async def handle_chat_action(self, event):
        if not isinstance(event, events.ChatAction.Event):
            return

        if not (event.user_added or event.user_joined):
            return

        me = await self.bot.get_me()

        affected_ids = set()
        if event.user_id:
            affected_ids.add(event.user_id)
        if getattr(event, "user_ids", None):
            affected_ids.update(event.user_ids)

        if me.id not in affected_ids:
            return

        if event.chat_id in self._leaving_now:
            return

        self._leaving_now.add(event.chat_id)
        try:
            await self.leave_chat(event.chat_id)
        finally:
            self._leaving_now.discard(event.chat_id)

    async def handle_group_message(self, event):
        await self.leave_chat(event.chat_id)
