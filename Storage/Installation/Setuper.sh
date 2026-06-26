#!/bin/bash

set -e

INSTALL_DIR="$HOME/TGWatcher"
VENV_DIR="$INSTALL_DIR/venv"
SERVICE_NAME="tgwatcher"
PYTHON_BIN="$(command -v python3)"
REPO_URL="https://github.com/i-execute/TGWatcher.git"
ENV_FILE="$INSTALL_DIR/.env"

if [ -z "$PYTHON_BIN" ]; then
    echo "ERROR: python3 not found"
    exit 1
fi

echo ""
echo "Welcome back $USER"
sleep 0.5
echo "Time to login in new one account"
sleep 0.5
echo "Installing TGWatcher..."
sleep 0.5
echo ""

env_is_valid() {
    [ -f "$ENV_FILE" ] || return 1

    local v_api_id v_api_hash v_bot_token v_owner_id
    v_api_id="$(grep -E '^API_ID=' "$ENV_FILE" | cut -d'=' -f2-)"
    v_api_hash="$(grep -E '^API_HASH=' "$ENV_FILE" | cut -d'=' -f2-)"
    v_bot_token="$(grep -E '^BOT_TOKEN=' "$ENV_FILE" | cut -d'=' -f2-)"
    v_owner_id="$(grep -E '^OWNER_ID=' "$ENV_FILE" | cut -d'=' -f2-)"

    [ -n "$v_api_id" ] && [ -n "$v_api_hash" ] && [ -n "$v_bot_token" ] && [ -n "$v_owner_id" ]
}

write_env_file() {
    cat > "$ENV_FILE" <<EOF
API_ID=$API_ID
API_HASH=$API_HASH
BOT_TOKEN=$BOT_TOKEN
OWNER_ID=$OWNER_ID
EOF
    chmod 600 "$ENV_FILE"
}

prompt_credentials() {
    read -rp "BOT_TOKEN : " BOT_TOKEN < /dev/tty
    if [ -z "$BOT_TOKEN" ]; then
        echo "Enter token next time"
        exit 1
    fi

    read -rp "OWNER_ID  : " OWNER_ID < /dev/tty
    if ! [[ "$OWNER_ID" =~ ^[0-9]+$ ]]; then
        echo "Enter correct ID next time"
        exit 1
    fi

    read -rp "API_ID    : " API_ID < /dev/tty
    if ! [[ "$API_ID" =~ ^[0-9]+$ ]]; then
        echo "Enter correct API ID next time"
        exit 1
    fi

    read -rp "API_HASH  : " API_HASH < /dev/tty
    if [ -z "$API_HASH" ]; then
        echo "Enter API hash next time"
        exit 1
    fi

    echo ""
}

ALREADY_INSTALLED=0
if [ -d "$INSTALL_DIR/.git" ]; then
    ALREADY_INSTALLED=1
fi

if [ "$ALREADY_INSTALLED" -eq 1 ]; then
    echo "TGWatcher already installed, checking .env..."

    if env_is_valid; then
        echo ""
        echo "Current config:"
        echo " API_ID    : $(grep -E '^API_ID=' "$ENV_FILE" | cut -d'=' -f2-)"
        echo " API_HASH  : $(grep -E '^API_HASH=' "$ENV_FILE" | cut -d'=' -f2-)"
        echo " BOT_TOKEN : $(grep -E '^BOT_TOKEN=' "$ENV_FILE" | cut -d'=' -f2-)"
        echo " OWNER_ID  : $(grep -E '^OWNER_ID=' "$ENV_FILE" | cut -d'=' -f2-)"
        echo ""

        read -rp "Change config? [y/N]: " CHANGE_ENV < /dev/tty
        if [[ "$CHANGE_ENV" =~ ^[Yy]$ ]]; then
            prompt_credentials
            write_env_file
        fi
    else
        echo ".env missing or incomplete, please fill it in again"
        echo ""
        prompt_credentials
        write_env_file
    fi

    echo "Pulling latest changes..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    prompt_credentials

    echo "Cloning repository..."
    git clone "$REPO_URL" "$INSTALL_DIR"

    write_env_file

    echo "Building venv and dependencies..."
    $PYTHON_BIN -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip
    "$VENV_DIR/bin/pip" install --quiet telethon aiohttp gitpython
    echo "Successfully installed python packages in venv"

    echo "Building daemon configuration..."

    UNIT_DIR="$HOME/.config/tagwatcher/bot"
    mkdir -p "$UNIT_DIR"

    cat > "$UNIT_DIR/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=TGWatcher
After=network.target

[Service]
WorkingDirectory=$INSTALL_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$VENV_DIR/bin/python3 $INSTALL_DIR/TGW/core.py
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

    mkdir -p "$HOME/.config/systemd/user"
    ln -sf "$UNIT_DIR/${SERVICE_NAME}.service" "$HOME/.config/systemd/user/${SERVICE_NAME}.service"

    systemctl --user daemon-reload
    systemctl --user enable "$SERVICE_NAME"
fi

systemctl --user restart "$SERVICE_NAME"

echo ""
echo "[*] TGWatcher successfully started"
echo "    I_execute.t.me"
echo ""

echo "----------------------------------"
echo " installed in   : $INSTALL_DIR"
echo " venv directory : $VENV_DIR"
echo " config         : $ENV_FILE"
echo ""
echo "Swift commands:"
echo " status  : systemctl --user status $SERVICE_NAME"
echo " logs    : journalctl --user -u $SERVICE_NAME -f"
echo " stop    : systemctl --user stop $SERVICE_NAME"
echo " restart : systemctl --user restart $SERVICE_NAME"