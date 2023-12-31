from aiogram import Router, F
import re

from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from database.database import (users_db, save_users_db, users_items, save_users_items,
                               users_max_items, save_users_max_items)
from lexicon.lexicon import LEXICON, LEXICON_CURRENCY
from services.search_function import main_search
from keyboards.currency_kb import create_currency_keyboard
from config_data.config import admin_id

from config_data.config import Config, load_config
from aiogram import Bot


router = Router()

config: Config = load_config()
BOT_TOKEN = config.tg_bot.token
bot = Bot(token=BOT_TOKEN, parse_mode='HTML')


def replays_tags(text: str):
    if "<" in text or ">" in text:
        text = text.replace(">", "&gt;").replace("<", "&lt;")
        return text


def extract_unique_code(text):
    return text.split()[1] if len(text.split()) > 1 else None


async def new_user(message):
    name = message.from_user.full_name
    username = message.from_user.username
    message = replays_tags(f'{name}, @{username} присоединился')
    await bot.send_message(chat_id=admin_id,
                           text=message)


@router.message(CommandStart())
async def process_start_command(message: Message):
    ref_id = extract_unique_code(message.text)
    name = message.from_user.full_name
    username = message.from_user.username
    id_ = message.from_user.id

    if ref_id is not None and int(ref_id) in users_db and id_ not in users_db:
        users_max_items[int(ref_id)] += 1
        await save_users_max_items()
        mess = replays_tags(f"Пользователь @{username} "
                               f"присоединился по вашему приглашению!\n"
                               f"Теперь у Вас максимальное количество отслеживаемых товаров: "
                               f"{users_max_items[int(ref_id)]}")
        await bot.send_message(chat_id=int(ref_id), text=mess)

    if message.from_user.id not in users_max_items:
        users_max_items[message.from_user.id] = 1
        await save_users_max_items()

    if message.from_user.id not in users_db:
        await new_user(message)

    users_db[message.from_user.id] = [name, username]
    users_items[id_] = ['rub', {}]

    await message.answer(LEXICON["/start"])
    await message.answer('Выберите необходимую валюту для цен товара', reply_markup=create_currency_keyboard(*LEXICON_CURRENCY.keys()))
    await save_users_db()
    await save_users_items()


@router.message(Command(commands='help'))
async def process_help_command(message: Message):

    name = message.from_user.full_name
    username = message.from_user.username
    id_ = message.from_user.id

    users_db[id_] = [name, username]
    await save_users_db()

    await message.answer(LEXICON["/help"])


@router.message(Command(commands='list'))
async def get_list_of_items(message: Message):
    id_ = message.from_user.id
    if len(users_items[id_][1]) == 0:
        await message.answer(text="У вас нет отслеживаемых товаров!\n"
                                  "Отправьте боту артикул товара, цену которого хотите отслеживать.")
    else:
        items = users_items.copy()[id_][1:]
        cur = users_items.copy()[id_][0]
        keys = []
        for dictionary in items:
            keys.extend(int(key) for key in dictionary.keys())
        for i in keys.copy():
            await main_search(cur, i, id_)
    max_itms = users_max_items[id_]
    used_itms = len(users_items[id_][1])
    await message.answer(f'Всего слотов: {max_itms}\n'
                         f'Слотов занято: {used_itms}\n'
                         f'Слотов свободно: {max_itms - used_itms}')


@router.message(F.text == 'my id')
async def my_id(message: Message):
    id_ = message.from_user.id
    name = message.from_user.full_name
    username = message.from_user.username

    await message.answer(f'{id_}')

    mess = replays_tags(f'{name}, @{username}, {id_}')
    await bot.send_message(chat_id=admin_id, text=mess)


@router.message(lambda message: isinstance(message.text, str) and re.match(r'^\s*\d+\s*$', message.text))
async def add_item_process(message: Message):
    id_ = message.from_user.id
    name = message.from_user.full_name
    username = message.from_user.username
    users_db[id_] = [name, username]
    await save_users_db()

    if len(users_items[id_][1]) < users_max_items[id_]\
            or int(message.text) in users_items[id_][1]:
        await main_search(users_items[id_][0], int(message.text), id_)

    else:
        bot_info = await bot.get_me()
        bot_username = bot_info.username
        await message.answer(f"{LEXICON['max_items']}\n\n Чтобы увеличить количество отслеживаемых товаров"
                             f" пригласите друга!\nПросто отправьте ему это сообщение с вашей реферальной ссылкой:")
        await message.answer(f"Привет!\n"
                             f"Я хочу поделиться с тобой полезным ботом, который помогает выгодно "
                             f"покупать на Wildberries (он присылает уведомления, "
                             f"когда снижается цена на выбранный тобою товар!)\n\n"
                             f"Чтобы присоединиться просто перейди по ссылке и отправь боту "
                             f"артикул интересующего тебя товара:\n"
                             f"https://t.me/{bot_username}?start={id_}")
        await message.answer(f"https://t.me/{bot_username}?start={id_}")
