# VK - Telegram Bridge Bot

### A simple bot that relays messages between a VK chat and a Telegram chat. Supports text messages, photos, and documents.

Requirements:
- Python 3.12+
- VK API token with messages permission
- Telegram Bot token


Enviroment Variables:
- `VK_TOKEN`     - Vk Account Token
- `VK_CHAT_ID`   - VK Chat ID
- `TG_BOT_TOKEN` - Telegram bot Token
- `TG_CHAT`      - Telegram Chat ID
- `DEBUG`        - Debug Flag

How to get VK Token:
1. Go to [VkHost](https://vkhost.github.io)
2. Select VK Admin tool
3. Copy token from the address bar

How to use:
```sh
docker compose up
```

Supports:
- From VK to Telegram
    - Text messages
    - Images 
    - Documents
    - Stickers
- From Telegram to VK
    - Text messages
    - Images