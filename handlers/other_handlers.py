from config_data.config import Config, load_config
from aiogram import Bot, Router
from aiogram.types import Message

from database.database import users_max_items, save_users_max_items

router = Router()

config: Config = load_config()
BOT_TOKEN = config.tg_bot.token
bot = Bot(token=BOT_TOKEN, parse_mode='HTML')


@router.message()
async def other(message: Message):
    if message.from_user.id not in users_max_items:
        users_max_items[message.from_user.id] = 1
        await save_users_max_items()
    caption = 'Это не похоже на артикул товара!\n' \
              'Зайдите, пожалуйста, на сайт или приложение wildberries, ' \
              'скопируйте артикул товара (как на фото) и отправьте его боту.'
    photo_url = 'https://github.com/ZaharSavchin/wb/blob/main/photos/image_2023-05-15_11-02-18.png?raw=true'

    await message.answer(text=caption)
    await message.answer_photo(photo=photo_url)

