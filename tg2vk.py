import asyncio
from aiogram import Dispatcher, F, Bot
from aiogram.types import Message

import aiohttp
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config import settings

import logging
from io import BytesIO


bot = Bot(token=settings.TG_BOT_TOKEN,)
dp = Dispatcher()

vk_session = vk_api.VkApi(token=settings.VK_TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


@dp.message(F.chat.id == settings.TG_CHAT)
async def tg_to_vk(message: Message):

    text = message.text or message.caption or ""

    if not text and not message.photo and not message.document:
        return

    if text:
        vk.messages.send(
            peer_id=settings.VK_CHAT_ID,
            message=text,
            random_id=0
        )

    if message.photo:
        photo = message.photo[-1]

        file = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{settings.TG_BOT_TOKEN}/{file.file_path}"

        async with aiohttp.ClientSession() as s:
            async with s.get(file_url) as resp:
                data = await resp.read()

        upload = vk_api.VkUpload(vk_session)

        photo_file = BytesIO(data)
        photo_vk = upload.photo_messages(photo_file)[0]

        attachment = f"photo{photo_vk['owner_id']}_{photo_vk['id']}"

        vk.messages.send(
            peer_id=settings.VK_CHAT_ID,
            attachment=attachment,
            random_id=0,
            message=text
        )

    if message.document: # This dont work
        doc = message.document

        file = await bot.get_file(doc.file_id)
        file_url = f"https://api.telegram.org/file/bot{settings.TG_BOT_TOKEN}/{file.file_path}"

        async with aiohttp.ClientSession() as s:
            async with s.get(file_url) as resp:
                data = await resp.read()

        upload = vk_api.VkUpload(vk_session)

        doc_file = BytesIO(data)
        doc_vk = upload.document_message(doc_file, doc.file_name)

        attachment = f"doc{doc_vk['doc']['owner_id']}_{doc_vk['doc']['id']}"

        vk.messages.send(
            peer_id=settings.VK_CHAT_ID,
            attachment=attachment,
            message=text,
            random_id=0
        ) #! TODO - fix sending documents

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())