import os
import asyncio
import tempfile
import logging
from telethon import events, Button

from strings import Strings
from updater import check_for_updates, pull_updates, restart_bot, get_commit_link
from functions import (
    find_string_session, find_url, process_zip_file,
    test_session, get_all_phones, create_phones_file
)
from tl import send_with_preview, get_random_photo, GREETING_VIDEO

logger = logging.getLogger(__name__)

s = Strings()

PREVIEW_URL = "https://github.com/i-execute/TGWatcher"


def btn(text, data, style="primary"):
    # valid: "primary" (blue), "success" (green), "danger" (red)
    valid = {"primary", "success", "danger"}
    return Button.inline(text, data.encode(), style=style if style in valid else "primary")


def btn_url(text, url):
    return Button.url(text, url)


async def send(bot, chat_id, text, buttons=None, reply_to=None):
    photo = get_random_photo()
    return await send_with_preview(
        bot, chat_id, text, photo,
        invert=True,
        reply_to=reply_to,
        buttons=buttons
    )


async def edit_msg(message, text, buttons=None):
    await message.edit(text, buttons=buttons, parse_mode='html', link_preview=False)


class Commands:
    def __init__(self, bot, protection, data_manager, watcher_manager, installer=None):
        self.bot = bot
        self.protection = protection
        self.data = data_manager
        self.watcher = watcher_manager
        self.installer = installer

        self._pending = {}

    def register_handlers(self):
        self.bot.add_event_handler(self._cmd_start, events.NewMessage(pattern='/start', incoming=True, func=lambda e: e.is_private))
        self.bot.add_event_handler(self._cmd_install_module, events.NewMessage(pattern='/install', incoming=True, func=lambda e: e.is_private))
        self.bot.add_event_handler(self._cmd_unload_module, events.NewMessage(pattern='/unload', incoming=True, func=lambda e: e.is_private))
        self.bot.add_event_handler(self._on_callback, events.CallbackQuery())
        self.bot.add_event_handler(self._on_message, events.NewMessage(incoming=True, func=lambda e: e.is_private and not e.text.startswith('/')))

    async def _cmd_start(self, event):
        user_id = event.sender_id

        if self.protection.check_spam(user_id):
            await send(self.bot, user_id, s.spam_banned.format(line=s.line))
            return

        is_owner = user_id == self.data.owner_id
        is_admin = user_id in self.data.get_admins()

        if is_owner or is_admin:
            has_update, latest, current, url = await check_for_updates()
            current_link = get_commit_link(current)

            if has_update:
                latest_link = get_commit_link(latest)
                update_status = s.update_required.format(
                    latest_link=latest_link,
                    latest_hash=latest[:7]
                )
            else:
                update_status = s.update_not_required

            text = s.greeting_admin.format(
                line=s.line,
                current_link=current_link,
                current_hash=current[:7] if current != "unknown" else "unknown",
                update_status=update_status
            )

            buttons = [
                [btn(s.btn_packages, "packages"), btn(s.btn_admin, "admin")],
                [btn(s.btn_check, "check_all"), btn(s.btn_update, "update_check")],
                [btn(s.btn_backup, "backup_menu"), btn(s.btn_usage, "usage")],
                [btn(s.btn_close, "close", "danger")],
            ]
        else:
            text = s.greeting_user.format(line=s.line)
            buttons = [
                [btn(s.btn_usage, "usage")],
                [btn(s.btn_close, "close", "danger")],
            ]

        await send_with_preview(self.bot, user_id, text, GREETING_VIDEO, invert=True, buttons=buttons)

    async def _cmd_install_module(self, event):
        user_id = event.sender_id

        if user_id != self.data.owner_id:
            await send(self.bot, user_id, s.not_owner.format(line=s.line))
            return

        self._pending[user_id] = "install_module"
        await send(self.bot, user_id, s.module_install_prompt.format(line=s.line))

    async def _cmd_unload_module(self, event):
        user_id = event.sender_id

        if user_id != self.data.owner_id:
            await send(self.bot, user_id, s.not_owner.format(line=s.line))
            return

        if not self.installer:
            await send(self.bot, user_id, s.error.format(line=s.line, error="Installer not available"))
            return

        loaded = self.installer.get_loaded()
        if not loaded:
            await send(self.bot, user_id, s.modules_empty.format(line=s.line))
            return

        self._pending[user_id] = "unload_module"
        modules_list = "\n".join(f"- <code>{m}</code>" for m in loaded)
        await send(self.bot, user_id, s.module_unload_prompt.format(line=s.line, modules=modules_list))

    async def _on_callback(self, event):
        user_id = event.sender_id
        data = event.data.decode()

        if self.protection.check_spam(user_id):
            await event.answer(s.spam_banned.format(line=s.line), alert=True)
            return

        is_owner = user_id == self.data.owner_id
        is_admin = user_id in self.data.get_admins()
        is_privileged = is_owner or is_admin

        await event.answer()

        if data == "close":
            await event.delete()
            return

        if data == "back_start":
            await self._cb_back_start(event, user_id, is_owner, is_admin)
            return

        if data == "usage":
            await self._cb_usage(event, user_id, is_owner, is_admin)
            return

        if data == "packages" and is_privileged:
            await self._cb_packages_menu(event)
            return

        if data == "admin" and is_owner:
            await self._cb_admin_menu(event)
            return

        if data == "admin_list" and is_owner:
            await self._cb_admin_list(event)
            return

        if data == "admin_add" and is_owner:
            self._pending[user_id] = "admin_add"
            await edit_msg(await event.get_message(), s.admin_add_prompt.format(line=s.line), buttons=[
                [btn(s.btn_back, "admin", "danger")]
            ])
            return

        if data == "admin_remove" and is_owner:
            self._pending[user_id] = "admin_remove"
            await edit_msg(await event.get_message(), s.admin_remove_prompt.format(line=s.line), buttons=[
                [btn(s.btn_back, "admin", "danger")]
            ])
            return

        if data == "pkg_install" and is_privileged:
            self._pending[user_id] = "pkg_install"
            await edit_msg(await event.get_message(), s.package_install_prompt.format(line=s.line), buttons=[
                [btn(s.btn_back, "packages", "danger")]
            ])
            return

        if data == "pkg_uninstall" and is_privileged:
            self._pending[user_id] = "pkg_uninstall"
            await edit_msg(await event.get_message(), s.package_uninstall_prompt.format(line=s.line), buttons=[
                [btn(s.btn_back, "packages", "danger")]
            ])
            return

        if data == "pkg_list" and is_privileged:
            await self._cb_pkg_list(event)
            return

        if data == "pkg_export" and is_privileged:
            await self._cb_pkg_export(event, user_id)
            return

        if data == "check_all" and is_privileged:
            await self._cb_check_all(event, user_id)
            return

        if data == "delete_dead" and is_privileged:
            await self._cb_delete_dead(event, user_id)
            return

        if data == "backup_menu" and is_privileged:
            await self._cb_backup_menu(event)
            return

        if data == "backup_create" and is_privileged:
            await self._cb_backup_create(event, user_id)
            return

        if data == "backup_restore" and is_privileged:
            self._pending[user_id] = "backup_restore"
            await edit_msg(await event.get_message(), s.backup_restoring.format(line=s.line), buttons=[
                [btn(s.btn_back, "backup_menu", "danger")]
            ])
            return

        if data == "update_check" and is_owner:
            await self._cb_update_check(event)
            return

        if data == "update_now" and is_owner:
            await self._cb_update_now(event)
            return

    async def _on_message(self, event):
        user_id = event.sender_id

        if self.protection.check_spam(user_id):
            return

        is_owner = user_id == self.data.owner_id
        is_admin = user_id in self.data.get_admins()
        is_privileged = is_owner or is_admin

        pending = self._pending.get(user_id)
        if not pending:
            return

        if pending == "install_module" and is_owner:
            await self._handle_module_install(event, user_id)
            return

        if pending == "unload_module" and is_owner:
            await self._handle_module_unload(event, user_id)
            return

        if pending == "admin_add" and is_owner:
            await self._handle_admin_add(event, user_id)
            return

        if pending == "admin_remove" and is_owner:
            await self._handle_admin_remove(event, user_id)
            return

        if pending == "pkg_install" and is_privileged:
            await self._handle_pkg_install(event, user_id)
            return

        if pending == "pkg_uninstall" and is_privileged:
            await self._handle_pkg_uninstall(event, user_id)
            return

        if pending == "backup_restore" and is_privileged:
            await self._handle_backup_restore(event, user_id)
            return

    async def _handle_module_install(self, event, user_id):
        if not event.document:
            await send(self.bot, user_id, s.invalid_format.format(line=s.line, message="Send a .py file"))
            return

        filename = ""
        for attr in event.document.attributes:
            if hasattr(attr, 'file_name'):
                filename = attr.file_name
                break

        if not filename.endswith('.py'):
            await send(self.bot, user_id, s.invalid_format.format(line=s.line, message="File must be .py"))
            return

        del self._pending[user_id]

        module_name = os.path.splitext(filename)[0]
        await send(self.bot, user_id, s.module_installing.format(line=s.line, name=module_name))

        content = await event.download_media(bytes)
        file_path = self.installer.save_module_file(module_name, content)

        success, result = await self.installer.load_from_file(file_path)

        if success:
            await send(self.bot, user_id, s.module_installed.format(line=s.line, name=result))
        else:
            await send(self.bot, user_id, s.module_install_failed.format(line=s.line, error=result))

    async def _handle_module_unload(self, event, user_id):
        name = event.raw_text.strip()
        del self._pending[user_id]

        success, result = await self.installer.unload(name)

        if success:
            await send(self.bot, user_id, s.module_unloaded.format(line=s.line, name=result))
        else:
            await send(self.bot, user_id, s.module_not_found.format(line=s.line, name=name))

    async def _handle_admin_add(self, event, user_id):
        try:
            target_id = int(event.raw_text.strip())
        except ValueError:
            await send(self.bot, user_id, s.invalid_format.format(line=s.line, message="Send a valid user ID"))
            return

        del self._pending[user_id]
        self.data.add_admin(target_id)
        await send(self.bot, user_id, s.admin_added.format(line=s.line, user_id=target_id))

    async def _handle_admin_remove(self, event, user_id):
        try:
            target_id = int(event.raw_text.strip())
        except ValueError:
            await send(self.bot, user_id, s.invalid_format.format(line=s.line, message="Send a valid user ID"))
            return

        del self._pending[user_id]

        if self.data.remove_admin(target_id):
            await send(self.bot, user_id, s.admin_removed.format(line=s.line, user_id=target_id))
        else:
            await send(self.bot, user_id, s.admin_not_found.format(line=s.line))

    async def _handle_pkg_install(self, event, user_id):
        text = event.raw_text.strip() if event.raw_text else ""
        session_string = find_string_session(text)

        if session_string:
            del self._pending[user_id]
            await self._install_session(user_id, session_string)
            return

        if event.document:
            filename = ""
            for attr in event.document.attributes:
                if hasattr(attr, 'file_name'):
                    filename = attr.file_name
                    break

            del self._pending[user_id]

            tmp = tempfile.mktemp(suffix=os.path.splitext(filename)[1])
            await event.download_media(tmp)

            if filename.endswith('.zip'):
                await send(self.bot, user_id, s.zip_processing.format(line=s.line))
                sessions = await process_zip_file(tmp)
                os.unlink(tmp)

                working = []
                for ss in sessions:
                    ok, _ = await test_session(self.data.api_id, self.data.api_hash, ss)
                    if ok:
                        working.append(ss)

                await send(self.bot, user_id, s.zip_processed.format(
                    line=s.line, total=len(sessions), working=len(working)
                ))

                for ss in working:
                    await self._install_session(user_id, ss)

            elif filename.endswith('.session'):
                from functions import convert_session_to_string
                ss = await convert_session_to_string(tmp)
                os.unlink(tmp)
                if ss:
                    await self._install_session(user_id, ss)
                else:
                    await send(self.bot, user_id, s.error.format(line=s.line, error="Failed to read session file"))
            else:
                os.unlink(tmp)
                await send(self.bot, user_id, s.invalid_format.format(line=s.line, message="Unsupported file type"))
            return

        await send(self.bot, user_id, s.invalid_format.format(line=s.line, message="Send string session, .session or .zip file"))

    async def _install_session(self, user_id, session_string):
        await send(self.bot, user_id, s.package_installing.format(line=s.line, status=s.status_connecting))

        existing_id = self.data.find_session_by_user_id(None)
        ok, phone = await test_session(self.data.api_id, self.data.api_hash, session_string)

        if not ok:
            await send(self.bot, user_id, s.error.format(line=s.line, error=phone))
            return

        session_id = self.data.add_session(session_string, phone)
        success, result = await self.watcher.start_session(session_id, session_string)

        if success:
            await send(self.bot, user_id, s.package_installed.format(
                line=s.line, package_id=session_id, phone=phone
            ))
        else:
            self.data.remove_session(session_id)
            await send(self.bot, user_id, s.error.format(line=s.line, error=result))

    async def _handle_pkg_uninstall(self, event, user_id):
        session_id = event.raw_text.strip()
        del self._pending[user_id]

        sessions = self.data.get_sessions()
        if session_id not in sessions:
            await send(self.bot, user_id, s.package_not_found.format(line=s.line))
            return

        await self.watcher.stop_session(session_id)
        self.data.remove_session(session_id)
        await send(self.bot, user_id, s.package_uninstalled.format(line=s.line, package_id=session_id))

    async def _handle_backup_restore(self, event, user_id):
        if not event.document:
            return

        del self._pending[user_id]

        tmp = tempfile.mktemp(suffix='.json')
        await event.download_media(tmp)

        import json
        try:
            with open(tmp, 'r') as f:
                backup_data = json.load(f)
            os.unlink(tmp)
        except Exception:
            os.unlink(tmp)
            await send(self.bot, user_id, s.error.format(line=s.line, error="Invalid backup file"))
            return

        installed = 0
        failed = 0

        for session_id, session_data in backup_data.get("sessions", {}).items():
            ok, phone = await test_session(self.data.api_id, self.data.api_hash, session_data['session'])
            if ok:
                new_id = self.data.add_session(session_data['session'], phone)
                success, _ = await self.watcher.start_session(new_id, session_data['session'])
                if success:
                    installed += 1
                else:
                    self.data.remove_session(new_id)
                    failed += 1
            else:
                failed += 1

        await send(self.bot, user_id, s.backup_restored.format(
            line=s.line, installed=installed, failed=failed
        ))

    async def _cb_usage(self, event, user_id, is_owner, is_admin):
        if is_owner:
            text = s.usage_owner.format(line=s.line)
        elif is_admin:
            text = s.usage_admin.format(line=s.line)
        else:
            text = s.usage_user.format(line=s.line)

        buttons = [[btn(s.btn_back, "back_start", "danger")]]
        await edit_msg(await event.get_message(), text, buttons=buttons)

    async def _cb_back_start(self, event, user_id, is_owner, is_admin):
        if is_owner or is_admin:
            has_update, latest, current, url = await check_for_updates()
            current_link = get_commit_link(current)
            if has_update:
                latest_link = get_commit_link(latest)
                update_status = s.update_required.format(latest_link=latest_link, latest_hash=latest[:7])
            else:
                update_status = s.update_not_required

            text = s.greeting_admin.format(
                line=s.line,
                current_link=current_link,
                current_hash=current[:7] if current != "unknown" else "unknown",
                update_status=update_status
            )
            buttons = [
                [btn(s.btn_packages, "packages"), btn(s.btn_admin, "admin")],
                [btn(s.btn_check, "check_all"), btn(s.btn_update, "update_check")],
                [btn(s.btn_backup, "backup_menu"), btn(s.btn_usage, "usage")],
                [btn(s.btn_close, "close", "danger")],
            ]
        else:
            text = s.greeting_user.format(line=s.line)
            buttons = [
                [btn(s.btn_usage, "usage")],
                [btn(s.btn_close, "close", "danger")],
            ]

        await edit_msg(await event.get_message(), text, buttons=buttons)

    async def _cb_packages_menu(self, event):
        sessions = self.data.get_sessions()
        active = self.watcher.get_active_sessions()

        text = s.packages_menu.format(
            line=s.line,
            package_count=len(sessions),
            active_count=len(active)
        )

        buttons = [
            [btn(s.btn_install, "pkg_install", "success"), btn(s.btn_uninstall, "pkg_uninstall", "danger")],
            [btn(s.btn_show, "pkg_list"), btn(s.btn_export_phones, "pkg_export")],
            [btn(s.btn_check, "check_all"), btn(s.btn_backup, "backup_menu")],
            [btn(s.btn_back, "back_start", "danger")],
        ]

        await edit_msg(await event.get_message(), text, buttons=buttons)

    async def _cb_admin_menu(self, event):
        admins = self.data.get_admins()
        text = s.admin_menu.format(line=s.line, admin_count=len(admins))

        buttons = [
            [btn(s.btn_add, "admin_add", "success"), btn(s.btn_remove, "admin_remove", "danger")],
            [btn(s.btn_list, "admin_list")],
            [btn(s.btn_back, "back_start", "danger")],
        ]

        await edit_msg(await event.get_message(), text, buttons=buttons)

    async def _cb_admin_list(self, event):
        admins = self.data.get_admins()

        if admins:
            admins_text = "\n".join(f"- <code>{a}</code>" for a in admins)
        else:
            admins_text = "No admins"

        text = s.admin_list.format(
            line=s.line,
            owner_id=self.data.owner_id,
            admins=admins_text
        )

        buttons = [[btn(s.btn_back, "admin", "danger")]]
        await edit_msg(await event.get_message(), text, buttons=buttons)

    async def _cb_pkg_list(self, event):
        sessions = self.data.get_sessions()
        active = self.watcher.get_active_sessions()

        if not sessions:
            await edit_msg(await event.get_message(), s.packages_empty.format(line=s.line), buttons=[
                [btn(s.btn_back, "packages", "danger")]
            ])
            return

        lines = []
        for sid, sdata in sessions.items():
            status = "online" if sid in active else "offline"
            lines.append(f"<code>{sid}</code> | {sdata.get('phone', 'unknown')} | {status}")

        text = s.packages_list.format(line=s.line, packages="\n".join(lines))
        await edit_msg(await event.get_message(), text, buttons=[[btn(s.btn_back, "packages", "danger")]])

    async def _cb_pkg_export(self, event, user_id):
        sessions = self.data.get_sessions()
        phones = await get_all_phones(self.data.api_id, self.data.api_hash, sessions)

        if not phones:
            await edit_msg(await event.get_message(), s.error.format(line=s.line, error="No working sessions"), buttons=[
                [btn(s.btn_back, "packages", "danger")]
            ])
            return

        file_path = await create_phones_file(phones)
        await self.bot.send_file(user_id, file_path, caption=s.phones_exported.format(
            line=s.line, count=len(phones)
        ), parse_mode='html')
        os.unlink(file_path)

    async def _cb_check_all(self, event, user_id):
        sessions = self.data.get_sessions()

        await edit_msg(await event.get_message(), s.check_running.format(line=s.line))

        working = []
        dead = []

        for session_id, session_data in sessions.items():
            ok, _ = await test_session(self.data.api_id, self.data.api_hash, session_data['session'])
            if ok:
                working.append(session_id)
            else:
                dead.append(session_id)

        text = s.check_completed.format(
            line=s.line,
            total=len(sessions),
            working=len(working),
            dead=len(dead)
        )

        buttons = []
        if dead:
            buttons.append([btn(s.btn_delete_dead, "delete_dead", "danger")])
        buttons.append([btn(s.btn_back, "packages", "danger")])

        await edit_msg(await event.get_message(), text, buttons=buttons)

    async def _cb_delete_dead(self, event, user_id):
        sessions = self.data.get_sessions()
        deleted = 0

        for session_id, session_data in list(sessions.items()):
            ok, _ = await test_session(self.data.api_id, self.data.api_hash, session_data['session'])
            if not ok:
                await self.watcher.stop_session(session_id)
                self.data.remove_session(session_id)
                deleted += 1

        await edit_msg(await event.get_message(), s.dead_deleted.format(line=s.line, count=deleted), buttons=[
            [btn(s.btn_back, "packages", "danger")]
        ])

    async def _cb_backup_menu(self, event):
        buttons = [
            [btn("Create Backup", "backup_create", "success"), btn("Restore Backup", "backup_restore")],
            [btn(s.btn_back, "packages", "danger")],
        ]
        await edit_msg(await event.get_message(), s.backup_creating.format(line=s.line), buttons=buttons)

    async def _cb_backup_create(self, event, user_id):
        import json
        sessions = self.data.get_sessions()

        tmp = tempfile.mktemp(suffix='.json')
        with open(tmp, 'w') as f:
            json.dump({"sessions": sessions}, f, indent=2)

        await self.bot.send_file(user_id, tmp, caption=s.backup_created.format(
            line=s.line, count=len(sessions)
        ), parse_mode='html')
        os.unlink(tmp)

    async def _cb_update_check(self, event):
        from updater import get_commit_link
        has_update, latest, current, url = await check_for_updates()
        current_link = get_commit_link(current)

        if has_update:
            latest_link = get_commit_link(latest)
            text = s.update_available.format(
                line=s.line,
                current_link=current_link,
                current_hash=current[:7],
                latest_link=latest_link,
                latest_hash=latest[:7]
            )
            buttons = [
                [btn(s.btn_do_update, "update_now", "success")],
                [btn(s.btn_back, "back_start", "danger")],
            ]
        else:
            commit_link = get_commit_link(current)
            text = s.update_not_available.format(
                line=s.line,
                commit_link=commit_link,
                commit_hash=current[:7]
            )
            buttons = [[btn(s.btn_back, "back_start", "danger")]]

        await edit_msg(await event.get_message(), text, buttons=buttons)

    async def _cb_update_now(self, event):
        await edit_msg(await event.get_message(), s.update_installing.format(line=s.line))

        success, result = await pull_updates()
        if success:
            from updater import get_current_commit, get_commit_link
            current = await get_current_commit()
            commit_link = get_commit_link(current)
            await edit_msg(await event.get_message(), s.update_success.format(
                line=s.line,
                commit_link=commit_link,
                commit_hash=current[:7]
            ))
            await asyncio.sleep(2)
            await restart_bot()
        else:
            await edit_msg(await event.get_message(), s.update_failed.format(line=s.line, error=result), buttons=[
                [btn(s.btn_back, "back_start", "danger")]
            ])
