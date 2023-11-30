import json
import re

from bs4 import BeautifulSoup

import requests
from aiogram import Bot
from aiogram.enums import ParseMode

from config_data.config import Config, load_config
from database.database import url_images, save_url_images, users_items, save_users_items
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.callback_data import CallbackData

API_URL: str = 'https://api.telegram.org/bot'
config: Config = load_config()
BOT_TOKEN = config.tg_bot.token
bot = Bot(token=BOT_TOKEN, parse_mode='HTML')


async def get_item(currency, item_id):
    url_1 = f'https://card.wb.ru/cards/detail?appType=128&curr={currency}&locale=by&lang=ru&dest=-59208&regions=1,4,22,30,31,33,40,48,66,68,69,70,80,83,114,115&reg=1&spp=0&nm={item_id}'
    url_2 = f'https://card.wb.ru/cards/detail?appType=128&curr={currency}&locale=ru&lang=ru&dest=123585494&regions=1,4,22,30,31,33,38,40,48,64,66,68,69,70,80,83,110,114&reg=1&spp=0&nm={item_id}'
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Origin': 'https://www.wildberries.by',
        'Referer': 'https://www.wildberries.by/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    response = requests.get(url=url_1, headers=headers)
    if len(response.json()['data']['products']) == 0:
        response = requests.get(url=url_2, headers=headers)
    return response.json()


async def get_item_details(response):
    item_details = (response.get('data', {})).get('products', None)[0]
    return item_details


async def prepare_item(currency, item_id, item_details):
    if len(item_details) > 0:
        price = float(item_details.get('salePriceU', None) / 100) if item_details.get('salePriceU', None) is not None else None
        name = item_details.get('name', None)
        return (f"артикул: {item_details.get('id', None)}\n"                                                                                                 
                f"брэнд: {item_details.get('brand', None)}\n"
                f"название: {name}\n"
                f"цена: {price} {currency} (без учёта Вашей персональной скидки)\n"
                f"рейтинг: {item_details.get('rating', '0')}⭐ ({item_details.get('feedbacks', '0')} отзывов)\n"
                f"ссылка: https://www.wildberries.ru/catalog/{item_id}/detail.aspx")


async def get_name(currency, item_id):
    response = await get_item(currency, item_id)
    item_details = (response.get('data', {})).get('products', None)[0]
    if len(item_details) > 0:
        return {item_details.get('name', None)}


async def get_price(currency, item_id):
    response = await get_item(currency, item_id)
    item_details = (response.get('data', {})).get('products', None)[0]
    if len(item_details) > 0:
        return float(item_details.get('salePriceU', None) / 100) if item_details.get('salePriceU', None) is not None else None


async def search_image(item_id: int):

    baskets = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16',
               '17', '18', '19', '20']

    for basket in baskets:
        try:
            if len(str(item_id)) < 6:
                image_url = f'https://basket-{basket}.wb.ru/vol0/part{str(item_id)[0:len(str(item_id)) - 3]}/{item_id}/images/big/1.jpg'
                response = requests.get(image_url)
                if response.status_code == 200:
                    return image_url
            else:
                image_url = f'https://basket-{basket}.wb.ru/vol{str(item_id)[0:len(str(item_id)) - 5]}/part{str(item_id)[0:len(str(item_id)) - 3]}/{item_id}/images/big/1.jpg'
                response = requests.get(image_url)
                if response.status_code == 200:
                    return image_url

        except Exception as err:
            print(err)


class DeleteCallbackFactory(CallbackData, prefix='id_article'):
    user_id: int
    item_id: int


async def main_search(currency: str, item_id: int, user_id: int, item_details=None):
    response = await get_item(currency, item_id)
    try:
        if item_details is None:
            item_details = await get_item_details(response)
        message = await prepare_item(currency, item_id, item_details)
    except Exception:
        await bot.send_message(chat_id=user_id, text="По этому артикулу ничего не найдено!")
        return None
    image_url = None  # Initialize with None

    if item_id not in url_images:
        image_url = await search_image(item_id)
        url_images[item_id] = image_url
        await save_url_images()

    image_url = url_images[item_id]
    price_int = float(item_details.get('salePriceU', None) / 100) if item_details.get('salePriceU', None) is not None else None
    users_items[user_id][1][item_id] = price_int
    await save_users_items()

    name = item_details.get('name', None)
    button = InlineKeyboardButton(text=f"Удалить: '{name}'",
                                  callback_data=DeleteCallbackFactory(user_id=user_id,
                                                                      item_id=item_id).pack())
    markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
    try:
        await bot.send_photo(chat_id=user_id, photo=image_url, caption=message, reply_markup=markup)
    except Exception as err:
        print(err)
        message_with_image = f'{message}\n<a href="{image_url}">&#8203;</a>'
        await bot.send_message(chat_id=user_id, text=message_with_image, parse_mode=ParseMode.HTML, reply_markup=markup)
