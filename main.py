import asyncio
import json
import aiohttp

from aiogram import Bot
from aiogram.types import BufferedInputFile

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config import settings

import logging

bot = Bot(token=settings.TG_BOT_TOKEN,)

vk_session = vk_api.VkApi(token=settings.VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def prep_md(username: str, text: str) -> str:
    if not text: return f">{username}"

    ret = f">{username}\n\n>"
    ret += text.replace("\n", "\n>")

    return ret

def log_message_rel(tg_msg, event):
    with open("message_ids.json") as f:
        data = json.loads(f.read())

    


async def poll_loop():
    logging.info("VK Long Poll started...")

    for event in longpoll.listen():
        # if event.peer_id != settings.VK_CHAT_ID or event.from_me:
        #     continue


        try:
            if event.type in [VkEventType.MESSAGE_NEW, VkEventType.MESSAGE_EDIT]:

                user = vk.users.get(user_ids = event.user_id)[0]
                username = f"{user["first_name"]} {user["last_name"]}"

                md_text = prep_md(username, event.text)
                if event.type == VkEventType.MESSAGE_EDIT:
                    md_text = "EDIT\n" + md_text

                if not event.attachments:
                    tg_msg = await bot.send_message(settings.TG_CHAT, md_text, parse_mode="MarkdownV2")

                else:
                    message_data = vk.messages.getById(message_ids=[event.message_id])["items"][0]

                    for attach in message_data.get("attachments", []):
                        if attach["type"] == "photo":
                            photo_url = max(attach["photo"]["sizes"], key=lambda s: s["width"])["url"]

                            tg_msg = await bot.send_photo(settings.TG_CHAT, photo_url, caption=md_text, parse_mode="MarkdownV2")
                        elif attach["type"] == "doc":
                            doc = attach["doc"]
                            doc_url = doc["url"]
                            filename = doc.get("title", "file")

                            async with aiohttp.ClientSession() as s:
                                async with s.get(doc_url) as resp:
                                    data = await resp.read()

                            file = BufferedInputFile(data, filename=filename)

                            tg_msg = await bot.send_document(settings.TG_CHAT,file,caption=md_text,parse_mode="MarkdownV2")

        except Exception as e:
            logging.error(e)

asyncio.run(poll_loop())