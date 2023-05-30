import asyncio
import logging
import time
import openai
import os
from lang import lang
from keyboards import keyboards
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    filters,
    ConversationHandler,
    MessageHandler
)
from dotenv import load_dotenv


## - Логирование -

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

## - Ключи -

openai.api_key = os.getenv("OPENAI_API_KEY")
telegram_api_key = os.getenv("TELEGRAM_API_KEY")

## - Значения -

LANGUAGES = [
    "en", "ru"
]

SIGNS = [
    "sign_aries",
    "sign_taurus",
    "sign_gemini",
    "sign_cancer",
    "sign_leo",
    "sign_virgo",
    "sign_libra",
    "sign_scorpio",
    "sign_sagittarius",
    "sign_capricorn",
    "sign_aquarius",
    "sign_pisces",
]

MARKDOWN = "markdown"

## ---- РАБОТА С OPENAI ----

# lol я не буду использовать зз в обращении
async def make_new_horo(user_lang):
    prompt = lang["prompts"][user_lang].format(count = 3)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )

    return response.choices[0].message.content


## ---- СОСТОЯНИЯ БОТА ----

INIT_LANGUAGE, INIT_ZODIAC_SIGN, IDLE, SETTINGS, \
    SET_LANGUAGE, SET_ZODIAC_SIGN = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало разговора - спрашивает язык"""
    context.user_data["lang"] = "en"
    context.user_data["sign"] = "sign_aries"
    context.user_data["last_result"] = ""
    context.user_data["last_update"] = 0
    reply_keyboard = keyboards.choose_language()

    await update.message.reply_text(
        "*Выбери свой язык*\n"
        "Choose your language",
        parse_mode=MARKDOWN,
        reply_markup=InlineKeyboardMarkup(reply_keyboard)
    )
    return INIT_LANGUAGE

async def init_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет язык - приветствует, спрашивает знак зодиака"""
    context.user_data["lang"] = update.callback_query.data
    user_lang = context.user_data["lang"]

    reply_keyboard = keyboards.choose_sign(user_lang)

    await update.callback_query.edit_message_text(
        lang["welcome1"][user_lang],
        parse_mode=MARKDOWN,
        reply_markup=InlineKeyboardMarkup(reply_keyboard)
    )
    return INIT_ZODIAC_SIGN

async def init_zodiac_sign(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет знак - приветствует, предлагает начать """
    context.user_data["sign"] = update.callback_query.data
    user_lang = context.user_data["lang"]

    reply_keyboard = [[lang["btn_generate"][user_lang]]]

    await update.callback_query.edit_message_reply_markup(None)

    await context.bot.send_message(
        update.callback_query.message.chat_id,
        text = lang["welcome2"][user_lang].format(str =
            lang[context.user_data["sign"]][user_lang]
            ),
        parse_mode=MARKDOWN,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard)
        )
    return IDLE

async def user_generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Пользователь попросил сгенерить"""
    user_lang = context.user_data["lang"]
    if ((context.user_data["last_update"] < time.time() - 86400) or context.user_data["last_result"] == ""):
        context.user_data["last_result"] = await make_new_horo(user_lang)
        context.user_data["last_update"] = time.time()

    await update.message.reply_text(
        lang["your_horoscope"][user_lang] +
        context.user_data["last_result"],
        parse_mode=MARKDOWN
        )

    print("User generates (username: " + update.message.from_user.full_name + ", text: "+ context.user_data["last_result"] +" )")

    return IDLE

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END

## ---- MAIN ----

def main():
    application = Application.builder().token(telegram_api_key).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            INIT_LANGUAGE: [
                CallbackQueryHandler(init_language, lambda str: str in LANGUAGES)
            ],
            INIT_ZODIAC_SIGN: [
                CallbackQueryHandler(init_zodiac_sign, lambda str: str in SIGNS)
            ],
            IDLE: [
                MessageHandler(filters.Text(lang["btn_generate"].values()), user_generate)
            ],
        },
        fallbacks=[
            CommandHandler("restart", start)
        ]
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == '__main__':
    main()