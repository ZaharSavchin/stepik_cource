from handlers.admin_handlers import MaxItemsCallbackFactory
from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from database.database import users_max_items, save_users_max_items, users_items, save_users_items, users_db

router = Router()


@router.callback_query(MaxItemsCallbackFactory.filter())
async def plus_press(callback: CallbackQuery,
                     callback_data: MaxItemsCallbackFactory):
    user_id = callback_data.user_id
    change = callback_data.change
    if change == '+':
        users_max_items[user_id] += 1
    if change == '-':
        if users_max_items[user_id] > 1:
            users_max_items[user_id] -= 1
        if user_id in users_items and len(users_items[user_id][1]) > users_max_items[user_id]:
            my_dict = users_items[user_id][1]
            last_key = None
            for key in my_dict:
                last_key = key
            if last_key:
                my_dict.pop(last_key)

    i = user_id
    name = users_db[i][0]
    username = users_db[i][1]
    refs = users_max_items[i]
    if i in users_items:
        cur = users_items[i][0]
        items = users_items[i][1:]
        answer = f"{name}(@{username}, {i}, {refs}): {cur}, {items}✅\n"
    else:
        answer = f"{name}(@{username}, {i}, {refs})🤷\n"

    button_plus = InlineKeyboardButton(text='+', callback_data=MaxItemsCallbackFactory(user_id=i, change='+').pack())
    button_minus = InlineKeyboardButton(text='-', callback_data=MaxItemsCallbackFactory(user_id=i, change='-').pack())
    markup = InlineKeyboardMarkup(inline_keyboard=[[button_minus, button_plus]])

    await callback.message.edit_text(text=answer, reply_markup=markup)

    await callback.answer()
    await save_users_items()
    await save_users_max_items()
