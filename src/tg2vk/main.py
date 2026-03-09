import asyncio
from aiogram import Dispatcher, F, Bot
from aiogram.types import Message

import vk_api

from config import settings

import logging

from tg2vk.utils import send_document, send_photo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


bot = Bot(token=settings.TG_BOT_TOKEN,)
dp = Dispatcher()

vk_session = vk_api.VkApi(token=settings.VK_TOKEN)
vk = vk_session.get_api()

@dp.message(F.chat.id == settings.TG_CHAT)
async def tg_to_vk(message: Message):
    if message.text:
        vk.messages.send(
            peer_id=settings.VK_CHAT_ID,
            message=message.text,
            random_id=0
        )

    if message.photo:
        upload = vk_api.VkUpload(vk)
        await send_photo(message, upload, vk)

    if message.document: # It doesnt work      #! TODO Fix later
        upload = vk_api.VkUpload(vk_session)
        await send_document(message, upload, vk)

        

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())