import asyncio

import aiogram
from aiogram import Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from aiogram.filters import Text

from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.database import users_db, save_users_db, users_items, save_users_items


from config_data.config import Config, load_config
from aiogram import Bot


router = Router()

config: Config = load_config()
BOT_TOKEN = config.tg_bot.token
bot = Bot(token=BOT_TOKEN, parse_mode='HTML')


LEXICON_DELETE_KB: dict[str, str] = {'delete': 'удалить',
                                     'cansel': 'отмена'}


def create_delete_users_keyboard(*buttons: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(*[InlineKeyboardButton(
        text=LEXICON_DELETE_KB[button] if button in LEXICON_DELETE_KB else button,
        callback_data=button) for button in buttons], width=2)
    return kb_builder.as_markup()


users_to_delete = {}


async def clear_users(user_id, name, sem: asyncio.Semaphore):
    async with sem:
        if "<" in name or ">" in name:
            name = name.replace(">", "&gt;").replace("<", "&lt;")
        try:
            sent_message = await bot.send_message(chat_id=user_id, text="_", disable_notification=True)
            await bot.delete_message(chat_id=user_id, message_id=sent_message.message_id)
        except aiogram.exceptions.TelegramForbiddenError as e:
            users_to_delete[user_id] = name


@router.message(F.text == 'bot users clear')
async def dell_users(message: Message):

    sem = asyncio.Semaphore(10)

    tasks = [asyncio.create_task(clear_users(user_id, name, sem)) for user_id, name in users_db.copy().items()]
    await asyncio.gather(*tasks)

    message_dict = {}

    for k, v in users_to_delete.items():
        if k in users_db:
            message_dict[v[0]] = ""

        if k in users_items:
            message_dict[v[0]] = users_items[k]

    answer = [f"{k}: {v}\n" for k, v in message_dict.items()]

    stat = ''.join(answer)
    try:
        await message.answer(
            f"{stat}users to delete: {len(users_to_delete)}",
            reply_markup=create_delete_users_keyboard('delete',
                                                      'cansel'))
    except Exception:
        await message.answer(f"users to delete: {len(users_to_delete)}",
                             reply_markup=create_delete_users_keyboard('delete',
                                                                       'cansel'))


@router.callback_query(Text(text='delete'))
async def delete(callback: CallbackQuery):
    id_to_delete = set(users_db.keys()) & set(users_to_delete.keys())

    for key in id_to_delete:
        users_db.pop(key, None)
        users_items.pop(key, None)

    users_to_delete.clear()
    await callback.answer("Недоступные пользователи удалены")
    await save_users_items()
    await save_users_db()


@router.callback_query(Text(text='cansel'))
async def cansel(callback: CallbackQuery):
    users_to_delete.clear()
    await callback.answer("удаление отменено")
