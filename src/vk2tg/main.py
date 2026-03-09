import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config import settings
from vk2tg.utils import get_text, send_func_table

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



async def poll_loop():
    logging.info("VK Long Poll started...")

    for event in longpoll.listen():
        if event.peer_id != settings.VK_CHAT_ID or (event.from_me and not settings.DEBUG):
            continue

        try:
            if event.type in [VkEventType.MESSAGE_NEW, VkEventType.MESSAGE_EDIT]:

                md_text = get_text(event, vk)

                if not event.attachments:
                    tg_msg = await bot.send_message(settings.TG_CHAT, md_text)
                    return

                # If attachments
                message_data = vk.messages.getById(message_ids=[event.message_id])["items"][0]

                for attach in message_data.get("attachments", []):
                    func = send_func_table.get(attach["type"])
                    if func: await func(md_text, attach, bot)
                   

        except Exception as e:
            logging.exception("VK to TG error")


if __name__ == "__main__":
    asyncio.run(poll_loop())