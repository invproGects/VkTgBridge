from io import BytesIO
import aiohttp

from aiogram.types import Message

from vk_api import VkUpload
from vk_api.upload import VkApiMethod

from config import settings

async def send_photo(message: Message, upload: VkUpload, vk: VkApiMethod):
    photo = message.photo[-1]

    file = await message.bot.get_file(photo.file_id)
    file_url = f"https://api.telegram.org/file/bot{settings.TG_BOT_TOKEN}/{file.file_path}"

    async with aiohttp.ClientSession() as s:
        async with s.get(file_url) as resp:
            data = await resp.read()

    photo_file = BytesIO(data)
    photo_vk = upload.photo_messages(photo_file)[0]

    attachment = f"photo{photo_vk['owner_id']}_{photo_vk['id']}"

    vk.messages.send(
        peer_id=settings.VK_CHAT_ID,
        attachment=attachment,
        random_id=0,
        message=message.caption
    )



# doesnt work
async def send_document(message: Message, upload: VkUpload, vk: VkApiMethod):
    doc = message.document

    file = await message.bot.get_file(doc.file_id)
    file_url = f"https://api.telegram.org/file/bot{settings.TG_BOT_TOKEN}/{file.file_path}"

    async with aiohttp.ClientSession() as s:
        async with s.get(file_url) as resp:
            data = await resp.read()

    doc_file = BytesIO(data)

    doc_vk = upload.document_message(doc_file, doc.file_name, settings.VK_CHAT_ID)
    attachment = f"doc{doc_vk['doc']['owner_id']}_{doc_vk['doc']['id']}"

    vk.messages.send(                # Any file sends as .JPG, idk why
        peer_id=settings.VK_CHAT_ID,
        attachment=attachment,
        message=message.caption,
        random_id=0
    )