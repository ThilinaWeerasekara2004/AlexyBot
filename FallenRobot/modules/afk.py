import html
import random
import logging
import openai  # Make sure to install via pip: pip install openai

from telegram import MessageEntity, Update, Chat
from telegram.error import BadRequest
from telegram.ext import CallbackContext, Filters, MessageHandler

from FallenRobot import dispatcher
from FallenRobot.modules.disable import (
    DisableAbleCommandHandler,
    DisableAbleMessageHandler,
)
from FallenRobot.modules.sql import afk_sql as sql
from FallenRobot.modules.users import get_user_id

# Set your OpenAI API key here or load from an environment variable for improved security.
openai.api_key = "YOUR_OPENAI_API_KEY"

AFK_GROUP = 7
AFK_REPLY_GROUP = 8

logger = logging.getLogger(__name__)


def generate_ai_afk_reply(user_name: str, reason: str) -> str:
    """
    Generate a witty AI-powered comment for the AFK reply.
    
    Args:
        user_name (str): The first name of the afk user.
        reason (str): The reason provided for being AFK.
    
    Returns:
        str: A generated response string.
    """
    prompt = (
        f"Generate a friendly and witty comment for an AFK user. "
        f"The user is named {user_name} and they're away because: {reason}. "
        "Keep it casual and humorous."
    )
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can choose the model you prefer
            prompt=prompt,
            max_tokens=50,
            temperature=0.7,
        )
        reply = response.choices[0].text.strip()
        return reply
    except Exception as e:
        logger.error(f"Error generating AI reply: {e}")
        return f"{user_name} is AFK.\nReason: {reason}"


def afk(update: Update, context: CallbackContext) -> None:
    """Mark a user as AFK with an optional reason."""
    args = update.effective_message.text.split(None, 1)
    user = update.effective_user

    if not user:  # ignore channels
        return

    # Ignore system or special accounts
    if user.id in [777000, 1087968824]:
        return

    notice = ""
    if len(args) >= 2:
        reason = args[1]
        if len(reason) > 100:
            reason = reason[:100]
            notice = "\nYour AFK reason was shortened to 100 characters."
    else:
        reason = ""

    sql.set_afk(user.id, reason)
    fname = user.first_name
    try:
        update.effective_message.reply_text(f"{fname} is now away!{notice}")
    except BadRequest:
        pass


def no_longer_afk(update: Update, context: CallbackContext) -> None:
    """Remove AFK status once a user becomes active."""
    user = update.effective_user
    message = update.effective_message

    if not user:  # ignore channels
        return

    res = sql.rm_afk(user.id)
    if res:
        # Don't send a message if new chat members join (avoid cluttering welcome messages)
        if message.new_chat_members:
            return
        fname = user.first_name
        try:
            options = [
                "{} is here!",
                "{} is back!",
                "{} is now in the chat!",
                "{} is awake!",
                "{} is back online!",
                "{} is finally here!",
                "Welcome back, {}!",
                "Where's {}? In the chat!",
            ]
            chosen_option = random.choice(options)
            update.effective_message.reply_text(chosen_option.format(fname))
        except Exception as e:
            logger.error(f"Error sending no-longer-afk message: {e}")
            return


def reply_afk(update: Update, context: CallbackContext) -> None:
    """Check messages for AFK mentions and reply with an AI-powered message if applicable."""
    bot = context.bot
    message = update.effective_message
    userc = update.effective_user
    userc_id = userc.id

    if message.entities and message.parse_entities(
        [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
    ):
        entities = message.parse_entities(
            [MessageEntity.TEXT_MENTION, MessageEntity.MENTION]
        )
        chk_users = []
        for ent in entities:
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
                if user_id in chk_users:
                    continue
                chk_users.append(user_id)
                fst_name = ent.user.first_name
                check_afk(update, context, user_id, fst_name, userc_id)

            elif ent.type == MessageEntity.MENTION:
                user_id = get_user_id(message.text[ent.offset : ent.offset + ent.length])
                if not user_id or (user_id in chk_users):
                    continue
                chk_users.append(user_id)

                try:
                    chat: Chat = bot.get_chat(user_id)
                except BadRequest:
                    logger.error(f"Could not fetch user ID {user_id} for AFK module.")
                    continue
                fst_name = chat.first_name
                check_afk(update, context, user_id, fst_name, userc_id)
    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        fst_name = message.reply_to_message.from_user.first_name
        check_afk(update, context, user_id, fst_name, userc_id)


def check_afk(update: Update, context: CallbackContext, user_id: int, fst_name: str, userc_id: int) -> None:
    """
    Check the AFK status for a user and reply accordingly.
    
    If the user has an AFK reason, use the AI function to generate a witty response.
    """
    if sql.is_afk(user_id):
        user_afk = sql.check_afk_status(user_id)
        # Avoid replying for the user who is sending the message
        if int(userc_id) == int(user_id):
            return
        if not user_afk.reason:
            response = f"{fst_name} is AFK."
        else:
            # Generate an AI powered response
            response = generate_ai_afk_reply(fst_name, user_afk.reason)
        try:
            update.effective_message.reply_text(response, parse_mode="html")
        except BadRequest as e:
            logger.error(f"Error sending AFK reply: {e}")


__help__ = """
*Away from group*
 ❍ /afk <reason>*:* mark yourself as AFK (away from keyboard).
 ❍ brb <reason>*:* same as the AFK command – but not a command.
When marked as AFK, any mentions will trigger a witty reply with your AFK status!
"""

AFK_HANDLER = DisableAbleCommandHandler("afk", afk, run_async=True)
AFK_REGEX_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r"^(?i)brb(.*)$"), afk, friendly="afk", run_async=True
)
NO_AFK_HANDLER = MessageHandler(Filters.all & Filters.chat_type.groups, no_longer_afk, run_async=True)
AFK_REPLY_HANDLER = MessageHandler(Filters.all & Filters.chat_type.groups, reply_afk, run_async=True)

dispatcher.add_handler(AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REGEX_HANDLER, AFK_GROUP)
dispatcher.add_handler(NO_AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REPLY_HANDLER, AFK_REPLY_GROUP)

__mod_name__ = "Aꜰᴋ​"
__command_list__ = ["afk"]
__handlers__ = [
    (AFK_HANDLER, AFK_GROUP),
    (AFK_REGEX_HANDLER, AFK_GROUP),
    (NO_AFK_HANDLER, AFK_GROUP),
    (AFK_REPLY_HANDLER, AFK_REPLY_GROUP),
]
