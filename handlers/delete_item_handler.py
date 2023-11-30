from datetime import datetime

from services.search_function import DeleteCallbackFactory
from aiogram import Router
from aiogram.types import CallbackQuery
from database.database import users_items, save_users_items
from services.search_function import bot


router = Router()


@router.callback_query(DeleteCallbackFactory.filter())
async def delete_press(callback: CallbackQuery,
                       callback_data: DeleteCallbackFactory):
    user_id = callback.from_user.id
    item_id = callback_data.item_id
    dict_of_items = users_items[user_id][1]
    if item_id in dict_of_items:
        del dict_of_items[item_id]
    try:
        await callback.message.edit_caption(caption=f'товар удален из списка отслеживания (артикул: {item_id})')
    except Exception:
        try:
            await callback.answer(
                'что-то пошло не так, посмотри список отслеживаемых товаров и убедись что ненужный товар удалился.')
            await callback.message.delete()
            # await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        except Exception:
            await callback.answer('что-то пошло не так, просто перезагрузи бота выбрав соответствующий пункт в меню')
    await callback.answer()
    await save_users_items()



