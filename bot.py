import asyncio

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config, admin_id
from keyboards.main_menu import set_main_menu
from handlers import other_handlers, user_handlers, admin_handlers, \
    currency_handlers, delete_item_handler, change_max_items_handler, delete_users_handler


async def main():
    config: Config = load_config()

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher()

    await bot.send_message(chat_id=admin_id, text="бот WB перезапущен")

    await set_main_menu(bot)

    dp.include_router(admin_handlers.router)
    dp.include_router(delete_users_handler.router)
    dp.include_router(user_handlers.router)
    dp.include_router(currency_handlers.router)
    dp.include_router(other_handlers.router)
    dp.include_router(delete_item_handler.router)
    dp.include_router(change_max_items_handler.router)

    await dp.start_polling(bot, polling_timeout=30)


if __name__ == '__main__':
    asyncio.run(main())



