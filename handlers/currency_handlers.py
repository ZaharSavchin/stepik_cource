from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery
from database.database import users_items, save_users_items
from lexicon.lexicon import answer_dict

from config_data.config import Config, load_config
from aiogram import Bot


router = Router()

config: Config = load_config()
BOT_TOKEN = config.tg_bot.token
bot = Bot(token=BOT_TOKEN, parse_mode='HTML')


async def cur_choice(cur: str, callback: CallbackQuery):
    users_items[callback.from_user.id][0] = cur
    await callback.answer()
    await bot.send_message(chat_id=callback.from_user.id, text=answer_dict[cur])
    await save_users_items()
    await callback.message.delete()


@router.callback_query(Text(text=answer_dict.keys()))
async def process_currency_press(callback: CallbackQuery):
    await cur_choice(callback.data, callback)
