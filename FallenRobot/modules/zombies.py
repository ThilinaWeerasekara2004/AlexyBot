from asyncio import sleep

from pyrogram import filters
from pyrogram.types import Message

from FallenRobot import pbot
from FallenRobot.utils.admins import can_restrict


@pbot.on_message(filters.command(["zombies", "ghosts"]) & filters.group)
@can_restrict
async def ban_zombies(_, message: Message):
    deleted_count = 0
    failed = 0
    banned = 0

    args = message.text.split(maxsplit=1)
    cleaning = len(args) > 1 and args[1].lower() == "clean"

    check_msg = await message.reply_text("🔍 Searching for deleted accounts...")

    deleted_users = []
    async for member in pbot.get_chat_members(message.chat.id):
        if member.user.is_deleted:
            deleted_users.append(member.user.id)
            deleted_count += 1
            await sleep(0.05)

    if not deleted_users:
        return await check_msg.edit_text("✅ No deleted accounts found in this chat.")

    if not cleaning:
        return await check_msg.edit_text(
            f"⚠️ Found `{deleted_count}` deleted account(s).\nUse `/zombies clean` to remove them."
        )

    await check_msg.edit_text("🧹 Cleaning deleted accounts...")

    for user_id in deleted_users:
        try:
            await pbot.ban_chat_member(message.chat.id, user_id)
            banned += 1
        except Exception:
            failed += 1
            continue

    await check_msg.edit_text(
        f"✅ Cleaned `{banned}` deleted account(s).\n❌ Failed to remove `{failed}` (maybe admins)."
    )


__help__ = """
*Remove Deleted Accounts:*

 ❍ /zombies - Scans the group for deleted accounts
 ❍ /zombies clean - Removes all deleted accounts from the group
"""

__mod_name__ = "Zᴏᴍʙɪᴇ"
