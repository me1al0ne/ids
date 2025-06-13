import os

# Discord configuration
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_COMMAND_PREFIX = '+'

# TikTok configuration
TIKTOK_API_HOST = "https://api.tiktok.com"
TIKTOK_SHARE_ENDPOINT = "/aweme/v1/aweme/share/"

# Account configuration
ACCOUNTS = {
    "account1": {
        "session_id": os.getenv('TIKTOK_SESSION_ID_1'),
        "device_id": os.getenv('TIKTOK_DEVICE_ID_1'),
        "user_id": os.getenv('TIKTOK_USER_ID_1')
    },
    "account2": {
        "session_id": os.getenv('TIKTOK_SESSION_ID_2'),
        "device_id": os.getenv('TIKTOK_DEVICE_ID_2'),
        "user_id": os.getenv('TIKTOK_USER_ID_2')
    },
    # Add more accounts as needed
}

# Proxy configuration (essential to avoid bans)
PROXIES = [
    os.getenv('PROXY_1'),
    os.getenv('PROXY_2'),
    # Add more proxies as needed
]
