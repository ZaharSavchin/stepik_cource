from database.database import users_items, save_users_items
from services.search_function import get_price, main_search, bot, get_item, get_item_details
import asyncio
from config_data.config import admin_id


async def monitoring():
    loop_counter = 0
    while True:
        for user_id, list_of_items in users_items.copy().items():
            if len(list_of_items[1]) > 0:
                for item_id, price in list_of_items[1].items():
                    try:
                        response = await get_item(currency=list_of_items[0], item_id=item_id)
                        item_details = await get_item_details(response)
                        actual_price = float(item_details.get('salePriceU', None) / 100) if item_details.get('salePriceU', None) is not None else None
                        name = item_details.get('name', None)
                        if actual_price < price:
                            try:
                                sale = price - actual_price
                                await bot.send_message(chat_id=user_id, text=f"цена товара '{name}' (Артикул: {item_id})"
                                                                             f" снизилась на {round(sale, 2)} "
                                                                             f"{list_of_items[0]}")
                                await main_search(list_of_items[0], item_id, user_id, item_details=item_details)
                            except Exception as error:
                                print(error)
                    except Exception as e:
                        print(e)
            await asyncio.sleep(2)
        loop_counter += 1
        if loop_counter % 5 == 0 or loop_counter == 1:
            await bot.send_message(chat_id=admin_id, text=f"{loop_counter}")
        await asyncio.sleep(15)
