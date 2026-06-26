import random
from telethon.tl.functions.messages import SendMediaRequest
from telethon.tl.types import InputMediaWebPage, InputReplyToMessage
from telethon.utils import get_inner_text

REPO_BASE = "https://raw.githubusercontent.com/i-execute/TGWatcher/main/Storage"
GREETING_VIDEO = f"{REPO_BASE}/Video/GreetingsNew.mp4"
PHOTOS = [f"{REPO_BASE}/Photo/Photo{i}.jpeg" for i in range(1, 6)]


def get_random_photo():
    return random.choice(PHOTOS)


async def send_with_preview(bot, chat_id, text, url, invert=True, reply_to=None, buttons=None):
    peer = await bot.get_input_entity(chat_id)

    reply_to_msg = InputReplyToMessage(reply_to_msg_id=reply_to) if reply_to else None

    parsed_text, entities = await bot._parse_message_text(text, "html")

    reply_markup = bot.build_reply_markup(buttons) if buttons else None

    request = SendMediaRequest(
        peer=peer,
        media=InputMediaWebPage(
            url=url,
            optional=True,
            force_large_media=True,
        ),
        message=parsed_text,
        entities=entities,
        invert_media=invert,
        reply_to=reply_to_msg,
        reply_markup=reply_markup,
    )

    result = await bot(request)
    return bot._get_response_message(request, result, peer)