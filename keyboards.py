from lang import lang
from telegram import InlineKeyboardButton

class keyboards:

    def translate_kb(user_lang, lang_kb):
        return [
            [
                InlineKeyboardButton(
                    text = lang[el][user_lang],
                    callback_data = el
                ) for el in row
            ] for row in lang_kb
        ]

    def choose_language():
        return [
            [
                InlineKeyboardButton(text=lang["language"]["en"], callback_data="en"),
                InlineKeyboardButton(text=lang["language"]["ru"], callback_data="ru"),
            ]
        ]

    def choose_sign(user_lang):
        return keyboards.translate_kb(user_lang,
            [
                ["sign_aries", "sign_taurus"],
                ["sign_gemini", "sign_cancer"],
                ["sign_leo", "sign_virgo"],
                ["sign_sagittarius", "sign_capricorn"],
                ["sign_aquarius", "sign_pisces"],
                ["sign_aries", "sign_taurus"]
            ]
        )