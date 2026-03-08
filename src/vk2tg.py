import asyncio
from fcntl import FASYNC
from socket import timeout

import aiohttp

from aiogram import Bot
from aiogram.types import BufferedInputFile
from aiogram.client.default import DefaultBotProperties

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config import settings

import re
import logging


logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

bot = Bot(
    token=settings.TG_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="MarkdownV2")
)


vk_session = vk_api.VkApi(token=settings.VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def prep_md(username: str, text: str) -> str:
    if not text: return f">{username}"

    text = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

    ret = f">{username}\n\n>"
    ret += text.replace("\n", "\n>")

    return ret


async def poll_loop():
    logging.info("VK Long Poll started...")

    for event in longpoll.listen():
        if event.peer_id != settings.VK_CHAT_ID or (event.from_me and not settings.DEBUG):
            continue

        try:
            if event.type in [VkEventType.MESSAGE_NEW, VkEventType.MESSAGE_EDIT]:

                user = vk.users.get(user_ids = event.user_id)[0]
                username = fr"{user["first_name"]} {user["last_name"]} \({user["id"]}\)"

                md_text = prep_md(username, event.text)
                if event.type == VkEventType.MESSAGE_EDIT:
                    md_text = "EDIT\n" + md_text

                if not event.attachments:
                    tg_msg = await bot.send_message(settings.TG_CHAT, md_text)

                else:
                    message_data = vk.messages.getById(message_ids=[event.message_id])["items"][0]

                    for attach in message_data.get("attachments", []):
                        if attach["type"] == "photo":
                            photo_url = max(attach["photo"]["sizes"], key=lambda s: s["width"])["url"]
                        
                            tg_msg = await bot.send_photo(settings.TG_CHAT, photo_url, caption=md_text)
                        
                        elif attach["type"] == "video":
                            #! TODO - Make normal video logic
                            video = attach["video"]
                            photo_keys = [k for k in video.keys() if k.startswith("photo_")]
                            preview_url = video[max(photo_keys, key=lambda k: int(k.split("_")[1]))]

                            md_text = f"Video Preview — {video["duration"]//60}:{video["duration"]%60}\n\n" + md_text

                            tg_msg = await bot.send_photo(settings.TG_CHAT, preview_url, caption=md_text)

                        elif attach["type"] == "doc":
                            doc = attach["doc"]
                            doc_url = doc["url"]
                            filename = doc.get("title", "file")

                            async with aiohttp.ClientSession() as s:
                                async with s.get(doc_url, allow_redirects=False) as resp:
                                    location = resp.headers["location"]
                            
                            md_text = f"[Download File]({location})\n\n" + md_text

                            tg_msg = await bot.send_message(settings.TG_CHAT, md_text)
                        
                        elif attach["type"] == "sticker":
                            sticker_url = max(attach["sticker"]["images_with_background"], key=lambda s: s["width"])["url"]

                            md_text = "Sticker\n\n" + md_text

                            tg_msg = await bot.send_photo(settings.TG_CHAT, sticker_url, caption=md_text)


        except Exception as e:
            logging.exception("VK to TG error")


if __name__ == "__main__":
    asyncio.run(poll_loop())