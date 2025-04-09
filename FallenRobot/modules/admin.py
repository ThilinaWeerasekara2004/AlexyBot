from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from config import SUDO_USERS
import openai
import logging

# Set up your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"  # Or fetch from env var

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if user is admin or sudo
def is_admin():
    async def func(flt, client: Client, msg: Message):
        try:
            if msg.from_user.id in SUDO_USERS:
                return True
            member = await client.get_chat_member(msg.chat.id, msg.from_user.id)
            return member.status in ("administrator", "creator")
        except Exception as e:
            logger.warning(f"Error checking admin: {e}")
            return False
    return filters.create(func)

# AI message generator
async def ai_reply(action: str, username: str) -> str:
    prompt = (
        f"You're a witty and polite AI moderator assistant. "
        f"Create a short and humorous message after performing this action: {action}, "
        f"on user: {username}."
    )
    try:
        res = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50,
            temperature=0.7,
        )
        return res.choices[0].text.strip()
    except Exception as e:
        logger.error(f"AI reply failed: {e}")
        return f"User {username} has been {action}."

@Client.on_message(filters.command("ban") & filters.group & is_admin())
async def ban_user(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to ban.")
    user = message.reply_to_message.from_user
    await client.ban_chat_member(message.chat.id, user.id)
    reply = await ai_reply("banned", user.first_name)
    await message.reply_text(reply)

@Client.on_message(filters.command("kick") & filters.group & is_admin())
async def kick_user(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to kick.")
    user = message.reply_to_message.from_user
    await client.ban_chat_member(message.chat.id, user.id)
    await client.unban_chat_member(message.chat.id, user.id)
    reply = await ai_reply("kicked", user.first_name)
    await message.reply_text(reply)

@Client.on_message(filters.command("mute") & filters.group & is_admin())
async def mute_user(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to mute.")
    user = message.reply_to_message.from_user
    await client.restrict_chat_member(
        message.chat.id,
        user.id,
        permissions=ChatPermissions()  # No permissions = fully muted
    )
    reply = await ai_reply("muted", user.first_name)
    await message.reply_text(reply)

@Client.on_message(filters.command("unmute") & filters.group & is_admin())
async def unmute_user(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to unmute.")
    user = message.reply_to_message.from_user
    await client.restrict_chat_member(
        message.chat.id,
        user.id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
    )
    reply = await ai_reply("unmuted", user.first_name)
    await message.reply_text(reply)

