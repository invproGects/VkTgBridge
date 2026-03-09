import re
from aiogram import Bot
import aiohttp
from vk_api.upload import VkApiMethod
from vk_api.longpoll import Event, VkEventType
from config import settings

def prep_md(username: str, text: str) -> str:
    if not text: return f">{username}"

    text = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

    res = f">{username}\n\n>"
    res += text.replace("\n", "\n>")

    return res

def get_text(event: Event, vk: VkApiMethod):
    user = vk.users.get(user_ids = event.user_id)[0]
    username = fr"{user["first_name"]} {user["last_name"]} \({user["id"]}\)"

    md_text = prep_md(username, event.text)
    if event.type == VkEventType.MESSAGE_EDIT:
        md_text = ">EDIT\n" + md_text

    return md_text


async def send_photo(md_text: str, attach: dict, bot: Bot):
    photo_url = max(attach["photo"]["sizes"], key=lambda s: s["width"])["url"]
                        
    tg_msg = await bot.send_photo(settings.TG_CHAT, photo_url, caption=md_text)


async def send_video(md_text: str, attach: dict, bot: Bot):
    #! TODO - Make normal video logic
    video = attach["video"]
    photo_keys = [k for k in video.keys() if k.startswith("photo_")]
    preview_url = video[max(photo_keys, key=lambda k: int(k.split("_")[1]))]

    md_text = f"Video Preview — {video["duration"]//60}:{video["duration"]%60}\n\n" + md_text

    tg_msg = await bot.send_photo(settings.TG_CHAT, preview_url, caption=md_text)


async def send_doc(md_text: str, attach: dict, bot: Bot):
    doc = attach["doc"]
    doc_url = doc["url"]
    filename = doc.get("title", "file")

    async with aiohttp.ClientSession() as s:
        async with s.get(doc_url, allow_redirects=False) as resp:
            location = resp.headers["location"]
    
    md_text = f"[Download File]({location})\n>{filename}\n" + md_text

    tg_msg = await bot.send_message(settings.TG_CHAT, md_text)


async def send_sticker(md_text: str, attach: dict, bot: Bot):
    sticker_url = max(attach["sticker"]["images_with_background"], key=lambda s: s["width"])["url"]

    md_text = "Sticker\n\n" + md_text

    tg_msg = await bot.send_photo(settings.TG_CHAT, sticker_url, caption=md_text)

send_func_table = {
    "photo": send_photo,
    "video": send_video,
    "doc": send_doc,
    "sticker": send_sticker
}