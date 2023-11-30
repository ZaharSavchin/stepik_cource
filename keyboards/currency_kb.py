from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon import LEXICON_CURRENCY


def create_currency_keyboard(*buttons: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(*[InlineKeyboardButton(
        text=LEXICON_CURRENCY[button] if button in LEXICON_CURRENCY else button,
        callback_data=button) for button in buttons], width=2)
    return kb_builder.as_markup()
