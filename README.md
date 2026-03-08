# VK - Telegram Bridge Bot

### A simple bot that forwards messages from a VK chat to a Telegram chat. Supports text, photos, and documents, including message edits.

Requirements:
- Python 3.12+
- VK API token with messages permission
- Telegram Bot token


Env Variables:
- `VK_TOKEN`     - Vk Account Token
- `VK_CHAT_ID`   - VK Chat ID
- `TG_BOT_TOKEN` - Telegram bot Token
- `TG_CHAT`      - Telegram Chat ID

How to get VK Token:
1. go to [VkHost](https://vkhost.github.io)
2. Select VK Admin tool
3. Copy token from address bar

How to use:
```sh
docker compose up
```