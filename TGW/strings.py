class Strings:
    line = "-----------------------------------"

    greeting_admin = (
        "<b>Swift downloader</b>\n"
        "{line}\n"
        "<blockquote>"
        "Welcome back, admin\n"
        "Use menu below to manage packages\n\n"
        "Current commit: <a href='{current_link}'>{current_hash}</a>\n"
        "{update_status}"
        "</blockquote>\n"
        "{line}"
    )

    update_required = "Latest commit: <a href='{latest_link}'>{latest_hash}</a>"
    update_not_required = "You are on latest commit"

    greeting_user = (
        "<b>Swift downloader</b>\n"
        "{line}\n"
        "<blockquote>"
        "Send me link to download video\n"
        "Supported services:\n"
        "YouTube, Twitter, TikTok, Instagram"
        "</blockquote>\n"
        "{line}"
    )

    usage_user = (
        "<b>Commands</b>\n"
        "{line}\n"
        "<blockquote>"
        "/start - open main menu"
        "</blockquote>\n"
        "{line}"
    )

    usage_admin = (
        "<b>Commands</b>\n"
        "{line}\n"
        "<blockquote>"
        "/start - open main menu\n\n"
        "Packages:\n"
        "- Install package (session/file/zip)\n"
        "- Uninstall package\n"
        "- Check all packages\n"
        "- Export all phone numbers\n"
        "- Backup / Restore"
        "</blockquote>\n"
        "{line}"
    )

    usage_owner = (
        "<b>Commands</b>\n"
        "{line}\n"
        "<blockquote>"
        "/start - open main menu\n"
        "/install - install module (.py)\n"
        "/unload - unload module\n\n"
        "Packages:\n"
        "- Install / Uninstall\n"
        "- Check all / Export phones\n"
        "- Backup / Restore\n\n"
        "Admin panel:\n"
        "- Add / Remove admins\n"
        "- View admin list\n\n"
        "System:\n"
        "- Check for updates\n"
        "- Restart bot"
        "</blockquote>\n"
        "{line}"
    )

    admin_menu = (
        "<b>Admin Panel</b>\n"
        "{line}\n"
        "<blockquote>"
        "Total admins: {admin_count}\n"
        "Select action:"
        "</blockquote>\n"
        "{line}"
    )

    admin_list = (
        "<b>Admin List</b>\n"
        "{line}\n"
        "<blockquote>"
        "Owner: <code>{owner_id}</code>\n"
        "{admins}"
        "</blockquote>\n"
        "{line}"
    )

    admin_add_prompt = (
        "<b>Add Admin</b>\n"
        "{line}\n"
        "<blockquote>"
        "Send user ID to add as admin"
        "</blockquote>\n"
        "{line}"
    )

    admin_remove_prompt = (
        "<b>Remove Admin</b>\n"
        "{line}\n"
        "<blockquote>"
        "Send user ID to remove from admins"
        "</blockquote>\n"
        "{line}"
    )

    admin_added = (
        "<b>Admin Added</b>\n"
        "{line}\n"
        "<blockquote>"
        "User <code>{user_id}</code> added to admins"
        "</blockquote>\n"
        "{line}"
    )

    admin_removed = (
        "<b>Admin Removed</b>\n"
        "{line}\n"
        "<blockquote>"
        "User <code>{user_id}</code> removed from admins"
        "</blockquote>\n"
        "{line}"
    )

    admin_not_found = (
        "<b>Error</b>\n"
        "{line}\n"
        "<blockquote>"
        "User not found in admin list"
        "</blockquote>\n"
        "{line}"
    )

    packages_menu = (
        "<b>Package Manager</b>\n"
        "{line}\n"
        "<blockquote>"
        "Total packages: {package_count}\n"
        "Active: {active_count}\n"
        "Select action:"
        "</blockquote>\n"
        "{line}"
    )

    packages_list = (
        "<b>Packages</b>\n"
        "{line}\n"
        "<blockquote>"
        "{packages}"
        "</blockquote>\n"
        "{line}"
    )

    packages_empty = (
        "<b>No Packages</b>\n"
        "{line}\n"
        "<blockquote>"
        "No packages installed\n"
        "Send string session to install"
        "</blockquote>\n"
        "{line}"
    )

    package_install_prompt = (
        "<b>Install Package</b>\n"
        "{line}\n"
        "<blockquote>"
        "Send string session, .session file or .zip archive"
        "</blockquote>\n"
        "{line}"
    )

    package_installing = (
        "<b>Installation</b>\n"
        "{line}\n"
        "<blockquote>"
        "Status: {status}"
        "</blockquote>\n"
        "{line}"
    )

    package_installed = (
        "<b>Package Installed</b>\n"
        "{line}\n"
        "<blockquote>"
        "Package: <code>{package_id}</code>\n"
        "Phone: <code>{phone}</code>"
        "</blockquote>\n"
        "{line}"
    )

    package_already_exists = (
        "<b>Package Already Installed</b>\n"
        "{line}\n"
        "<blockquote>"
        "Ignoring...\n"
        "Package slot: <code>{package_id}</code>"
        "</blockquote>\n"
        "{line}"
    )

    package_uninstall_prompt = (
        "<b>Uninstall Package</b>\n"
        "{line}\n"
        "<blockquote>"
        "Send package ID to uninstall"
        "</blockquote>\n"
        "{line}"
    )

    package_uninstalled = (
        "<b>Package Uninstalled</b>\n"
        "{line}\n"
        "<blockquote>"
        "Package <code>{package_id}</code> removed"
        "</blockquote>\n"
        "{line}"
    )

    package_not_found = (
        "<b>Error</b>\n"
        "{line}\n"
        "<blockquote>"
        "Package not found"
        "</blockquote>\n"
        "{line}"
    )

    package_hash = (
        "<b>Package Phone</b>\n"
        "{line}\n"
        "<blockquote>"
        "Phone: <code>{phone}</code>"
        "</blockquote>\n"
        "{line}"
    )

    zip_processing = (
        "<b>Processing Archive</b>\n"
        "{line}\n"
        "<blockquote>"
        "Extracting packages..."
        "</blockquote>\n"
        "{line}"
    )

    zip_processed = (
        "<b>Archive Processed</b>\n"
        "{line}\n"
        "<blockquote>"
        "Found: {total} packages\n"
        "Working: {working} packages\n"
        "Installing working packages..."
        "</blockquote>\n"
        "{line}"
    )

    backup_creating = (
        "<b>Creating Backup</b>\n"
        "{line}\n"
        "<blockquote>"
        "Preparing packages data..."
        "</blockquote>\n"
        "{line}"
    )

    backup_created = (
        "<b>Backup Created</b>\n"
        "{line}\n"
        "<blockquote>"
        "Total packages: {count}\n"
        "File sent to chat"
        "</blockquote>\n"
        "{line}"
    )

    backup_restoring = (
        "<b>Restoring Backup</b>\n"
        "{line}\n"
        "<blockquote>"
        "Processing packages..."
        "</blockquote>\n"
        "{line}"
    )

    backup_restored = (
        "<b>Backup Restored</b>\n"
        "{line}\n"
        "<blockquote>"
        "Installed: {installed} packages\n"
        "Failed: {failed} packages"
        "</blockquote>\n"
        "{line}"
    )

    check_running = (
        "<b>Checking Packages</b>\n"
        "{line}\n"
        "<blockquote>"
        "Testing all packages..."
        "</blockquote>\n"
        "{line}"
    )

    check_completed = (
        "<b>Check Completed</b>\n"
        "{line}\n"
        "<blockquote>"
        "Total packages: {total}\n"
        "Working: {working}\n"
        "Dead: {dead}"
        "</blockquote>\n"
        "{line}"
    )

    dead_deleted = (
        "<b>Dead Packages Deleted</b>\n"
        "{line}\n"
        "<blockquote>"
        "Deleted: {count} packages"
        "</blockquote>\n"
        "{line}"
    )

    update_checking = (
        "<b>Checking Updates</b>\n"
        "{line}\n"
        "<blockquote>"
        "Current commit: <a href='{current_link}'>{current_hash}</a>\n"
        "Checking repository..."
        "</blockquote>\n"
        "{line}"
    )

    update_available = (
        "<b>Update Available</b>\n"
        "{line}\n"
        "<blockquote>"
        "Current: <a href='{current_link}'>{current_hash}</a>\n"
        "Latest: <a href='{latest_link}'>{latest_hash}</a>\n"
        "Click button to update"
        "</blockquote>\n"
        "{line}"
    )

    update_not_available = (
        "<b>No Updates</b>\n"
        "{line}\n"
        "<blockquote>"
        "You are on latest commit:\n"
        "<a href='{commit_link}'>{commit_hash}</a>"
        "</blockquote>\n"
        "{line}"
    )

    update_installing = (
        "<b>Updating</b>\n"
        "{line}\n"
        "<blockquote>"
        "Pulling latest changes...\n"
        "Bot will restart automatically"
        "</blockquote>\n"
        "{line}"
    )

    update_success = (
        "<b>Update Completed</b>\n"
        "{line}\n"
        "<blockquote>"
        "Updated to commit:\n"
        "<a href='{commit_link}'>{commit_hash}</a>\n"
        "Restarting..."
        "</blockquote>\n"
        "{line}"
    )

    update_failed = (
        "<b>Update Failed</b>\n"
        "{line}\n"
        "<blockquote>"
        "Error: {error}\n"
        "Check logs for details"
        "</blockquote>\n"
        "{line}"
    )

    new_version = (
        "<b>Login Code</b>\n"
        "{line}\n"
        "<blockquote>"
        "Package: <code>{package_id}</code>\n"
        "Phone: <code>{phone}</code>\n"
        "Code: <code>{code}</code>"
        "</blockquote>\n"
        "{line}"
    )

    web_login_code = (
        "<b>Web Login Code</b>\n"
        "{line}\n"
        "<blockquote>"
        "Package: <code>{package_id}</code>\n"
        "Phone: <code>{phone}</code>\n"
        "Code: <code>{code}</code>"
        "</blockquote>\n"
        "{line}"
    )

    module_install_prompt = (
        "<b>Install Module</b>\n"
        "{line}\n"
        "<blockquote>"
        "Send .py file to install as module"
        "</blockquote>\n"
        "{line}"
    )

    module_installing = (
        "<b>Installing Module</b>\n"
        "{line}\n"
        "<blockquote>"
        "Loading {name}..."
        "</blockquote>\n"
        "{line}"
    )

    module_installed = (
        "<b>Module Installed</b>\n"
        "{line}\n"
        "<blockquote>"
        "Module <code>{name}</code> loaded successfully"
        "</blockquote>\n"
        "{line}"
    )

    module_install_failed = (
        "<b>Module Install Failed</b>\n"
        "{line}\n"
        "<blockquote>"
        "Error: {error}"
        "</blockquote>\n"
        "{line}"
    )

    module_unload_prompt = (
        "<b>Unload Module</b>\n"
        "{line}\n"
        "<blockquote>"
        "Loaded modules:\n"
        "{modules}\n\n"
        "Send module name to unload"
        "</blockquote>\n"
        "{line}"
    )

    module_unloaded = (
        "<b>Module Unloaded</b>\n"
        "{line}\n"
        "<blockquote>"
        "Module <code>{name}</code> unloaded"
        "</blockquote>\n"
        "{line}"
    )

    module_not_found = (
        "<b>Error</b>\n"
        "{line}\n"
        "<blockquote>"
        "Module <code>{name}</code> not found"
        "</blockquote>\n"
        "{line}"
    )

    modules_empty = (
        "<b>No Modules</b>\n"
        "{line}\n"
        "<blockquote>"
        "No modules loaded"
        "</blockquote>\n"
        "{line}"
    )

    phones_exported = (
        "<b>Phones Exported</b>\n"
        "{line}\n"
        "<blockquote>"
        "Total: {count} phones\n"
        "File sent to chat"
        "</blockquote>\n"
        "{line}"
    )

    spam_banned = (
        "<b>Spam Detected</b>\n"
        "{line}\n"
        "<blockquote>"
        "You have been banned for spamming"
        "</blockquote>\n"
        "{line}"
    )

    not_admin = (
        "<b>Access Denied</b>\n"
        "{line}\n"
        "<blockquote>"
        "You are not admin"
        "</blockquote>\n"
        "{line}"
    )

    not_owner = (
        "<b>Access Denied</b>\n"
        "{line}\n"
        "<blockquote>"
        "You are not owner"
        "</blockquote>\n"
        "{line}"
    )

    invalid_format = (
        "<b>Invalid Format</b>\n"
        "{line}\n"
        "<blockquote>"
        "{message}"
        "</blockquote>\n"
        "{line}"
    )

    error = (
        "<b>Error</b>\n"
        "{line}\n"
        "<blockquote>"
        "{error}"
        "</blockquote>\n"
        "{line}"
    )

    btn_admin = "Admin Panel"
    btn_packages = "Packages"
    btn_check = "Check All"
    btn_update = "Update Bot"
    btn_backup = "Backup"
    btn_usage = "Usage"
    btn_close = "Close"

    btn_add = "Add"
    btn_remove = "Remove"
    btn_list = "List"
    btn_back = "Back"

    btn_install = "Install"
    btn_uninstall = "Uninstall"
    btn_show = "Show All"
    btn_export_phones = "Export Phones"

    btn_do_update = "Update Now"
    btn_restart = "Restart"
    btn_delete_dead = "Delete Dead"

    status_connecting = "Connecting..."
    status_testing = "Testing session..."
    status_extracting = "Extracting files..."
    status_installing = "Installing packages..."
