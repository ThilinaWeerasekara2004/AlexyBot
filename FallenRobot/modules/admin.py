from pyrogram import Client, filters
from pyrogram.types import Message
from config import SUDO_USERS

# Only allow sudo users or chat admins
def is_admin():
    async def func(flt, client: Client, msg: Message):
        if msg.from_user.id in SUDO_USERS:
            return True
        member = await client.get_chat_member(msg.chat.id, msg.from_user.id)
        return member.status in ("administrator", "creator")
    return filters.create(func)

@Client.on_message(filters.command("ban") & filters.group & is_admin())
async def ban_user(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to ban.")
    user_id = message.reply_to_message.from_user.id
    await client.ban_chat_member(message.chat.id, user_id)
    await message.reply_text(f"Banned user {user_id}.")

@Client.on_message(filters.command("kick") & filters.group & is_admin())
async def kick_user(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to kick.")
    user_id = message.reply_to_message.from_user.id
    await client.ban_chat_member(message.chat.id, user_id)
    await client.unban_chat_member(message.chat.id, user_id)
    await message.reply_text(f"Kicked user {user_id}.")

@Client.on_message(filters.command("mute") & filters.group & is_admin())
async def mute_user(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to mute.")
    user_id = message.reply_to_message.from_user.id
    await client.restrict_chat_member(
        message.chat.id,
        user_id,
        permissions={}
    )
    await message.reply_text(f"Muted user {user_id}.")

@Client.on_message(filters.command("unmute") & filters.group & is_admin())
async def unmute_user(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to the user you want to unmute.")
    user_id = message.reply_to_message.from_user.id
    await client.restrict_chat_member(
        message.chat.id,
        user_id,
        permissions={
            "can_send_messages": True,
            "can_send_media_messages": True,
            "can_send_other_messages": True,
            "can_add_web_page_previews": True,
        }
    )
    await message.reply_text(f"Unmuted user {user_id}.")
