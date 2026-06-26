# TGWatcher

Emergency access to your Telegram accounts when SMS codes are blocked.

## What is TGWatcher?

TGWatcher is a Telegram bot that helps users maintain access to their accounts during SMS disruptions caused by Roskomnadzor blocking. It monitors login codes sent to authorized devices and keeps backup sessions alive.

## Why is this needed?

Since Roskomnadzor blocked Telegram's SMS services in Russia, users cannot receive login codes via SMS. The only way to log in is through codes sent to already-authorized devices. TGWatcher solves this by:

- Storing backup string sessions for emergency access
- Monitoring login codes from the Telegram service
- Keeping sessions alive automatically
- Helping you regain access after reinstalling the app

## Features

- Session management (string / file / zip)
- Login code monitoring from Telegram service (777000)
- Auto-update via Git commits
- Backup and restore functionality
- Session keeper (prevents timeout)
- Admin panel
- Spam protection
- Phone number export
- Dead session cleanup
- Duplicate detection

## Quick Start

One-line installation with curl:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/i-execute/TGWatcher/main/Storage/Installation/QuickStart.sh)
```

One-line installation with wget:

```bash
bash <(wget -qO- https://raw.githubusercontent.com/i-execute/TGWatcher/main/Storage/Installation/QuickStart.sh)
```

Manual installation:

```bash
git clone https://github.com/i-execute/TGWatcher.git
cd TGWatcher/Storage/Installation
chmod +x Setuper.sh
./Setuper.sh
```

## Requirements

- Python 3.8+
- Git
- systemd

## Configuration

During installation you will be asked for:

- `BOT_TOKEN` - your Telegram bot token from @BotFather
- `OWNER_ID` - your Telegram user ID
- `API_ID` - from https://my.telegram.org
- `API_HASH` - from https://my.telegram.org

## Usage

Admin commands:

- `/start` - main menu with update status
- `/menu` - quick access menu
- `/admin` - admin panel (owner only)
- `/packages` - package manager
- `/check` - check all sessions health
- `/backup` - create backup file
- `/update` - check and install updates

Regular users:

- `/start` - greeting and instructions
- Send any link - fake download simulation

## Package Management

1. Send a string session to install
2. Send a `.session` file
3. Send a `.zip` archive with sessions
4. Use the `/packages` menu for management

## Admin Management

1. Use `/admin` command (owner only)
2. Click Add
3. Send the user ID
4. The user is automatically unbanned if previously banned

## How It Works

**Session Keeper**

Each session slot runs on a randomized schedule:

- 1-10 connections per day
- Each connection lasts 1-30 minutes
- Schedule regenerates daily
- Prevents session timeout

**Code Monitoring**

The bot watches for messages from 777000:

- Login codes: `Login code: 12345`
- Web codes: `login code: AbCdEfGh`
- All admins are notified instantly

**Security**

- Auto-deletes sensitive messages
- Spam protection (5/10s and 10/60s limits)
- Auto-bans spammers
- Auto-leaves groups
- Admin management restricted to owner only

## File Structure

```
TGWatcher/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── Storage/
│   ├── installation/
│   │   ├── QuickStart.sh
│   │   └── Setuper.sh
│   ├── README/
│   │   ├── README_RU.md
│   │   └── README_EN.md
│   ├── Photo/
│   └── Video/
└── TGW/
    ├── tl.py
    ├── core.py
    ├── protection.py
    ├── functions.py
    ├── commands.py
    ├── updater.py
    └── strings.py
```

## Service Management

```bash
systemctl --user status tgwatcher
systemctl --user restart tgwatcher
systemctl --user stop tgwatcher
journalctl --user -u tgwatcher -f
```

## Troubleshooting

Bot does not start:

```bash
journalctl --user -u tgwatcher -f
```

Update failed:

```bash
cd ~/.local/tgwatcher
git pull origin main
systemctl --user restart tgwatcher
```

Reset everything:

```bash
systemctl --user stop tgwatcher
rm -rf ~/.local/tgwatcher
```

Then run the installer again.

## Contributing

Pull requests are welcome. For major changes, open an issue first.

## License

GNU GPL v3 - this license requires that all derivative works remain open source.

## Author

[@I_execute](https://t.me/I_execute)

## Disclaimer

This tool is for personal use only. Keep your sessions secure. The author is not responsible for misuse.
