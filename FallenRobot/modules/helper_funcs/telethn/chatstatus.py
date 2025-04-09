from telethon.tl.types import ChannelParticipantsAdmins

from FallenRobot import DRAGONS
from FallenRobot.modules.helper_funcs.telethn import IMMUNE_USERS, telethn


async def user_is_ban_protected(user_id: int, message):
    # If private message or user is immune, protect from bans
    if message.is_private or user_id in IMMUNE_USERS:
        return True

    try:
        async for user in telethn.iter_participants(
            message.chat_id, filter=ChannelParticipantsAdmins
        ):
            if user_id == user.id:
                return True
    except Exception as e:
        print(f"Error checking ban protection: {e}")
    
    return False


async def user_is_admin(user_id: int, message):
    # Check if user is admin or a dragon in the chat
    if message.is_private:
        return True

    try:
        async for user in telethn.iter_participants(
            message.chat_id, filter=ChannelParticipantsAdmins
        ):
            if user_id == user.id or user_id in DRAGONS:
                return True
    except Exception as e:
        print(f"Error checking if user is admin: {e}")

    return False


async def is_user_admin(user_id: int, chat_id):
    # Check if user is admin in a specific chat
    try:
        async for user in telethn.iter_participants(
            chat_id, filter=ChannelParticipantsAdmins
        ):
            if user_id == user.id or user_id in DRAGONS:
                return True
    except Exception as e:
        print(f"Error checking if user is admin in chat: {e}")
    
    return False


async def fallen_is_admin(chat_id: int):
    # Check if Fallen bot is admin in the chat
    try:
        fallen = await telethn.get_me()
        async for user in telethn.iter_participants(
            chat_id, filter=ChannelParticipantsAdmins
        ):
            if fallen.id == user.id:
                return True
    except Exception as e:
        print(f"Error checking if Fallen bot is admin: {e}")

    return False


async def is_user_in_chat(chat_id: int, user_id: int):
    # Check if user is a member of the chat
    try:
        async for user in telethn.iter_participants(chat_id):
            if user_id == user.id:
                return True
    except Exception as e:
        print(f"Error checking if user is in chat: {e}")

    return False


async def can_change_info(message):
    # Check if the admin can change info in the chat
    if message.chat.admin_rights:
        return message.chat.admin_rights.change_info
    return False


async def can_ban_users(message):
    # Check if the admin can ban users in the chat
    if message.chat.admin_rights:
        return message.chat.admin_rights.ban_users
    return False


async def can_pin_messages(message):
    # Check if the admin can pin messages in the chat
    if message.chat.admin_rights:
        return message.chat.admin_rights.pin_messages
    return False


async def can_invite_users(message):
    # Check if the admin can invite users in the chat
    if message.chat.admin_rights:
        return message.chat.admin_rights.invite_users
    return False


async def can_add_admins(message):
    # Check if the admin can add new admins in the chat
    if message.chat.admin_rights:
        return message.chat.admin_rights.add_admins
    return False


async def can_delete_messages(message):
    # Check if the admin can delete messages in the chat
    if message.is_private:
        return True
    elif message.chat.admin_rights:
        return message.chat.admin_rights.delete_messages
    return False
