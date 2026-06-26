import re
import os
import tempfile
import zipfile
import shutil
import struct
import base64
import ipaddress
import sqlite3
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import AuthKeyUnregisteredError, UserDeactivatedBanError

STRING_SESSION_PATTERN = re.compile(r'1[A-Za-z0-9_-]{200,}={0,2}')

LOGIN_CODE_PATTERN = re.compile(r'\b(\d{5,6})\b')

WEB_LOGIN_PATTERN = re.compile(r'\n([A-Za-z0-9]{8,})\s*\n')

URL_PATTERN = re.compile(r'https?://[^\s]+')

DC_IP_MAP = {
    1: "149.154.175.53",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130"
}


def find_string_session(text):
    if not text:
        return None
    match = STRING_SESSION_PATTERN.search(text)
    return match.group(0) if match else None


def find_url(text):
    if not text:
        return None
    match = URL_PATTERN.search(text)
    return match.group(0) if match else None


def parse_login_code(text):
    match = LOGIN_CODE_PATTERN.search(text)
    return match.group(1) if match else None


def parse_web_login(text):
    match = WEB_LOGIN_PATTERN.search(text)
    return match.group(1) if match else None


def parse_string_session(session_str):
    try:
        if not session_str or not session_str.startswith('1'):
            return None

        string = session_str[1:]
        string_padded = string + '=' * (-len(string) % 4)

        try:
            data = base64.urlsafe_b64decode(string_padded)
        except Exception:
            return None

        if len(data) == 263:
            dc_id, ip_bytes, port, auth_key = struct.unpack('>B4sH256s', data)
            ip = str(ipaddress.IPv4Address(ip_bytes))
        elif len(data) == 275:
            dc_id, ip_bytes, port, auth_key = struct.unpack('>B16sH256s', data)
            ip = str(ipaddress.IPv6Address(ip_bytes))
        else:
            return None

        return {'dc_id': dc_id, 'ip': ip, 'port': port, 'auth_key': auth_key}
    except Exception:
        return None


def build_string_session(dc_id, auth_key):
    try:
        if dc_id not in DC_IP_MAP:
            return None

        if isinstance(auth_key, str):
            auth_key = auth_key.encode('latin-1')
        elif not isinstance(auth_key, bytes):
            auth_key = bytes(auth_key)

        if len(auth_key) != 256:
            return None

        ip = ipaddress.IPv4Address(DC_IP_MAP[dc_id])
        port = 443

        data = struct.pack('>B4sH256s', dc_id, ip.packed, port, auth_key)
        encoded = base64.urlsafe_b64encode(data).decode('ascii')

        return '1' + encoded
    except Exception:
        return None


def read_session_file(file_path):
    try:
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
        if not cursor.fetchone():
            conn.close()
            return None

        cursor.execute("SELECT dc_id, auth_key FROM sessions LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            dc_id = row[0]
            auth_key = row[1]

            if isinstance(auth_key, str):
                auth_key = auth_key.encode('latin-1')

            if not auth_key or len(auth_key) != 256:
                return None

            return {'dc_id': dc_id, 'auth_key': auth_key}

        return None
    except Exception:
        return None


async def convert_session_to_string(file_path):
    data = read_session_file(file_path)
    if not data:
        return None
    return build_string_session(data['dc_id'], data['auth_key'])


async def process_zip_file(file_path):
    sessions = []
    temp_dir = tempfile.mkdtemp()

    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith('.session'):
                    session_path = os.path.join(root, file)
                    string_session = await convert_session_to_string(session_path)
                    if string_session:
                        sessions.append(string_session)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return sessions


async def test_session(api_id, api_hash, session_string):
    try:
        client = TelegramClient(
            StringSession(session_string),
            api_id,
            api_hash,
            device_model="Package Manager",
            system_version="Linux",
            app_version="1.0"
        )

        await client.connect()

        if not await client.is_user_authorized():
            await client.disconnect()
            return False, "Session not authorized"

        me = await client.get_me()
        await client.disconnect()

        return True, me.phone

    except (AuthKeyUnregisteredError, UserDeactivatedBanError):
        return False, "Session revoked or banned"
    except Exception as e:
        return False, str(e)


async def get_all_phones(api_id, api_hash, sessions):
    phones = []

    for session_id, session_data in sessions.items():
        success, phone = await test_session(api_id, api_hash, session_data['session'])
        if success:
            phones.append(phone)

    return phones


async def create_phones_file(phones):
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    temp_file.write('\n'.join(phones))
    temp_file.close()
    return temp_file.name
