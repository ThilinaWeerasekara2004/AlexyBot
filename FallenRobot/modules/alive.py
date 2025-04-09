from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram import __version__ as telever
from telethon import __version__ as tlhver

from FallenRobot import BOT_NAME, BOT_USERNAME, OWNER_ID, START_IMG, SUPPORT_CHAT, pbot

import openai
import os

# Load your OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY") or "YOUR_OPENAI_API_KEY"

# AI response generator for fun Alive caption
async def ai_alive_text(username):
    prompt = (
        f"You are a witty and energetic Telegram bot named {BOT_NAME}. "
        f"A user named {username} used the /alive command. "
        "Reply with a fun message to show you're alive, include a light personality."
    )

    try:
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=70,
            temperature=0.8,
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        return f"Hey {username}, I'm online and ready to help you conquer Telegram!"

@pbot.on_message(filters.command("alive"))
async def awake(_, message: Message):
    user = message.from_user.mention
    ai_text = await ai_alive_text(user)

    TEXT = f"**{ai_text}**\n\n"
    TEXT += f"» **Developer:** [𝗦𝗮𝘁𝗮𝗻 ✘](tg://user?id={OWNER_ID})\n"
    TEXT += f"» **Library:** `{telever}` | **Telethon:** `{tlhver}` | **Pyrogram:** `{pyrover}`"

    BUTTON = [
        [
            InlineKeyboardButton("🛠 Help", url=f"https://t.me/{BOT_USERNAME}?start=help"),
            InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_CHAT}"),
        ]
    ]

    await message.reply_photo(
        photo=START_IMG,
        caption=TEXT,
        reply_markup=InlineKeyboardMarkup(BUTTON),
    )

__mod_name__ = "Aʟɪᴠᴇ"
