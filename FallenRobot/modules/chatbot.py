import html
import json
import re
import openai
from time import sleep
from googletrans import Translator

import requests
from telegram import (
    CallbackQuery, Chat, InlineKeyboardButton, InlineKeyboardMarkup,
    ParseMode, Update, User
)
from telegram.ext import (
    CallbackContext, CallbackQueryHandler, CommandHandler,
    Filters, MessageHandler
)
from telegram.utils.helpers import mention_html

import FallenRobot.modules.sql.chatbot_sql as sql
from FallenRobot import (
    BOT_ID, BOT_NAME, BOT_USERNAME, dispatcher, OPENAI_API_KEY
)
from FallenRobot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from FallenRobot.modules.log_channel import gloggable

openai.api_key = OPENAI_API_KEY
translator = Translator()

@user_admin
@gloggable
def fallen(update: Update, context: CallbackContext):
    message = update.effective_message
    msg = "• Choose an option to enable or disable chatbot:"
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 ENABLE", callback_data="add_chat({})"),
            InlineKeyboardButton("🔴 DISABLE", callback_data="rm_chat({})"),
        ],
    ])
    message.reply_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

@user_admin_no_reply
@gloggable
def fallenrm(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat
    match = re.match(r"rm_chat\((.+?)\)", query.data)

    if match:
        sql.set_fallen(chat.id)
        update.effective_message.edit_text(
            f"🤖 Chatbot disabled by {mention_html(user.id, html.escape(user.first_name))}.",
            parse_mode=ParseMode.HTML,
        )
        return f"<b>{html.escape(chat.title)}:</b>\nAI_DISABLED\n<b>Admin :</b> {mention_html(user.id, html.escape(user.first_name))}"

    return ""

@user_admin_no_reply
@gloggable
def fallenadd(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat
    match = re.match(r"add_chat\((.+?)\)", query.data)

    if match:
        sql.rem_fallen(chat.id)
        update.effective_message.edit_text(
            f"✅ Chatbot enabled by {mention_html(user.id, html.escape(user.first_name))}.",
            parse_mode=ParseMode.HTML,
        )
        return f"<b>{html.escape(chat.title)}:</b>\nAI_ENABLED\n<b>Admin :</b> {mention_html(user.id, html.escape(user.first_name))}"

    return ""

def fallen_message(context: CallbackContext, message):
    reply_message = message.reply_to_message
    if message.text.lower() == "fallen":
        return True
    elif BOT_USERNAME in message.text:
        return True
    elif reply_message and reply_message.from_user.id == BOT_ID:
        return True
    return False

def detect_language_and_translate(text: str, dest: str = "en"):
    try:
        translated = translator.translate(text, dest=dest)
        return translated.text, translated.src
    except:
        return text, "en"

async def get_ai_response(prompt: str) -> str:
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        return completion.choices[0].message["content"].strip()
    except Exception:
        return ""

def fallback_api(prompt: str) -> str:
    try:
        r = requests.get(
            f"https://kora-api.vercel.app/chatbot/2d94e37d-937f-4d28-9196-bd5552cac68b/{BOT_NAME}/Anonymous/message={prompt}"
        )
        res = json.loads(r.text)
        return res["reply"]
    except:
        return "I couldn't understand that, sorry!"

def chatbot(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot

    if sql.is_fallen(chat_id):
        return

    if not message.text or message.document:
        return
    if not fallen_message(context, message):
        return

    bot.send_chat_action(chat_id, action="typing")
    user_input, lang = detect_language_and_translate(message.text)

    reply_text = fallback_api(user_input)  # Default fallback

    ai_reply = context.run_async(get_ai_response, user_input)
    ai_text = ai_reply.result()

    if ai_text:
        reply_text = ai_text

    # Translate reply back to user language if needed
    if lang != "en":
        reply_text = translator.translate(reply_text, dest=lang).text

    sleep(0.5)
    message.reply_text(reply_text)

# Dispatcher bindings
CHATBOTK_HANDLER = CommandHandler("chatbot", fallen, run_async=True)
ADD_CHAT_HANDLER = CallbackQueryHandler(fallenadd, pattern=r"add_chat", run_async=True)
RM_CHAT_HANDLER = CallbackQueryHandler(fallenrm, pattern=r"rm_chat", run_async=True)
CHATBOT_HANDLER = MessageHandler(
    Filters.text & (~Filters.command),
    chatbot,
    run_async=True,
)

dispatcher.add_handler(ADD_CHAT_HANDLER)
dispatcher.add_handler(CHATBOTK_HANDLER)
dispatcher.add_handler(RM_CHAT_HANDLER)
dispatcher.add_handler(CHATBOT_HANDLER)

__mod_name__ = "AI Chatbot"
__help__ = f"""
🤖 *{BOT_NAME} now supports AI-powered chatting with OpenAI + multilingual replies!*

Commands:
• `/chatbot` – Enable or Disable chatbot in group.

Triggers:
• Reply to the bot or mention its username.
• Say "fallen" directly in chat.

Supports:
• ChatGPT (OpenAI)
• Auto language detection & translation
"""
