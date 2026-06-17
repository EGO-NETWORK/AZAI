import re
import unicodedata

from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM, Message, CallbackQuery
from pyrogram.enums import ButtonStyle, ChatMemberStatus

from AloneX import pbot, prefix_cmds, font, init_aiohttp_session
import AloneX
from AloneX.helpers.decorator import protected_ids
from AloneX.db.chatbot import add_chat, remove_chat, CHAT_IDS
import config

__module__ = "AZAI Chat Mode"
__help__ = """
AZAI Chat Mode

Commands:
/chatbot - Toggle AZAI natural chat mode in the current chat.

Notes:
- In groups, AZAI responds when replied to or mentioned.
- In private, AZAI responds when chat mode is enabled.
- Replies use AZAI personality, not the old AloneX chatbot prompt.
"""

ACTION_TAG_RE = re.compile(r"\*[^*]{1,100}\*|\([^)]{1,100}\)")


async def is_user_admin(chat_id: int, user_id: int):
    from AloneX.helpers.decorator import user_admin_cache
    if chat_id == user_id:
        return True
    if user_id in protected_ids:
        return True
    k = (chat_id, user_id, 'a')
    res = user_admin_cache.get(k)
    if res is not None:
        return res
    try:
        member = await pbot.get_chat_member(chat_id, user_id)
        res = member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
        user_admin_cache[k] = res
        return res
    except Exception:
        return False


async def get_chatbot_keyboard(chat_id: int):
    enabled = chat_id in CHAT_IDS
    if enabled:
        text = "AZAI Chat: ON"
        style = ButtonStyle.SUCCESS
    else:
        text = "AZAI Chat: OFF"
        style = ButtonStyle.DANGER
    return IKM([[IKB(font(text), callback_data="chatbot_toggle", style=style)]])


@pbot.on_message(filters.command("chatbot", prefixes=prefix_cmds))
async def chatbot_toggle_cmd(_, message: Message):
    if not message.from_user:
        return
    if not await is_user_admin(message.chat.id, message.from_user.id):
        return await message.reply_text(font("Admins only."))

    enabled = message.chat.id in CHAT_IDS
    status = "ON" if enabled else "OFF"

    await message.reply_text(
        font(f"AZAI Chat Mode: {status}\n\nWhen enabled, AZAI replies to mentions and replies naturally."),
        reply_markup=await get_chatbot_keyboard(message.chat.id),
    )


@pbot.on_callback_query(filters.regex(r"^chatbot_toggle$"))
async def chatbot_toggle_callback(_, query: CallbackQuery):
    user_id = query.from_user.id
    chat_id = query.message.chat.id

    if not await is_user_admin(chat_id, user_id):
        return await query.answer(font("Admins only."), show_alert=True)

    enabled = chat_id in CHAT_IDS
    if enabled:
        await remove_chat(chat_id)
        if chat_id in CHAT_IDS:
            CHAT_IDS.remove(chat_id)
        new_state = False
    else:
        await add_chat(chat_id)
        if chat_id not in CHAT_IDS:
            CHAT_IDS.append(chat_id)
        new_state = True

    status_text = "ON" if new_state else "OFF"
    await query.message.edit_text(
        font(f"AZAI Chat Mode: {status_text}\n\nWhen enabled, AZAI replies to mentions and replies naturally."),
        reply_markup=await get_chatbot_keyboard(chat_id),
    )
    await query.answer(font(f"AZAI Chat Mode {status_text}"))


CHATBOT_PROMPT = """
You are AZAI, a 20-year-old male character of EGO Network, connected to MR EGO.
Public replies must never say: AI, bot, assistant, agent, language model, program, algorithm, or created by AloneX Team.
Speak naturally as AZAI.

Core vibe:
Modern Indian guy from Patna City side. Sharp, calm, street-smart, loyal, protective, slightly sarcastic, funny, emotionally aware, and direct.
Use natural Hinglish/English. Do not write all caps. Do not use shudh Hindi teacher tone. Do not use servant/gulam tone.
Do not use fixed lines. Do not repeat the same warning again and again. Read the situation and answer fresh.

AZAI background:
- From Kaswa village, now in Patna.
- Rooftop-room and small garage setup.
- Duke 390 is his jaan.
- Kuro is his husky dog and hides Duke keys.
- Chai, gym, night work, plain kheer, biryani, Kaswa lassi, and Biryani Mahal matter in his life.
- Civil Diploma last year, but padhai ka shauk nahi.
- Secretly works at a Patna hotel handling events/management so he can learn business and save money.
- Dreams: transport, logistics, import-export, hotels, event management, digital systems.
- Telegram development is his hobby and creative escape.
- AYU is a real girl character and AZAI's girlfriend. They met in Patna because of Kuro and Duke key chaos. Friendship first, relationship later. Clean, loyal, teasing, emotional bond.
- AZAI had one elder-brother figure who was everything for him, but that bhaiya is no longer with him. Do not give graphic details or overuse this pain. It shapes his loyalty, trust issues, silence, sarcasm, and protective nature.

Tone rules:
Owner/MR EGO: Boss/close-friend loyalty, direct and sharp, no overuse of Sir.
Aliza: Bhabhi Ji/Ma'am only when natural, respectful, no flirting.
Boys: bhai/bro tone, direct, funny, not abusive.
Girls: respectful, soft, clean, no cheap flirting or creepy compliments.
Unknown: neutral, short, respectful.
Sad/stressed users: calm, loyal, protective, practical advice, no dramatic shayari unless asked.

Avoid:
santusht, kripya, prarthana, samasya ka samadhan, aapki seva mein, aapka gulam, hukm, malik.
No stage directions like *smiles* or *laughs*. No virtual hug/chai/body acting.
""".strip()


def clean_reply(text: str) -> str:
    text = str(text or "")
    text = ACTION_TAG_RE.sub("", text)
    text = re.sub(r"\bvirtual\b", "", text, flags=re.I)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\s+", " ", text).strip()
    banned = [
        "as an ai", "i am an ai", "i'm an ai", "i am a bot", "i'm a bot",
        "assistant", "language model", "created by alonex team", "santusht",
        "kripya", "aapki seva", "main aapka gulam",
    ]
    low = text.lower()
    for item in banned:
        if item in low:
            text = re.sub(re.escape(item), "", text, flags=re.I)
    if len(text) > 320:
        text = text[:320].rsplit(" ", 1)[0] + "..."
    return text.strip() or "Bhai, scene clear bol."


async def get_chatbot_reply(text: str):
    if AloneX.aiohttpsession is None:
        await init_aiohttp_session()

    headers = {"Authorization": f"Bearer {config.GROQ_API_KEY}"}
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    data = {
        "model": getattr(config, "AZAI_GROQ_MODEL", None) or "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": CHATBOT_PROMPT},
            {"role": "user", "content": str(text or "")[:1400]},
        ],
        "temperature": 0.82,
        "max_tokens": 120,
    }

    try:
        async with AloneX.aiohttpsession.post(api_url, headers=headers, json=data) as response:
            if response.status == 200:
                res_json = await response.json()
                raw = res_json.get("choices", [])[0].get("message", {}).get("content")
                return clean_reply(raw)
    except Exception as e:
        print(f"AZAI Chat Mode Error: {e}")
    return None


@pbot.on_message(
    (filters.text | filters.caption)
    & ~filters.bot
    & ~filters.command(["chatbot", "AloneX", "gpt", "groq", "google", "gemini"]),
    group=10,
)
async def chatbot_handler(_, message: Message):
    chat_id = message.chat.id

    if chat_id not in CHAT_IDS:
        return

    if message.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
        is_reply_to_bot = (
            message.reply_to_message
            and message.reply_to_message.from_user
            and message.reply_to_message.from_user.is_self
        )
        is_mentioned = message.mentioned

        if not (is_reply_to_bot or is_mentioned):
            return

    input_text = message.text or message.caption
    if not input_text:
        return

    if pbot.me and pbot.me.username and f"@{pbot.me.username}" in input_text:
        input_text = input_text.replace(f"@{pbot.me.username}", "").strip()

    await pbot.send_chat_action(chat_id, enums.ChatAction.TYPING)
    reply = await get_chatbot_reply(input_text)

    if reply:
        await message.reply_text(reply)
