import redis
import json

users_db = {}
# users_db = {5754662958: ['name', 'username'], 1042048167: ['Zahar', 'ZaharMaster']}

users_items = {}
# users_items = {5754662958: ['byn', {64161614: 29.07, 60197297: 30.13, 106122360: 33.26,
#                8940466: 5.76, 119448764: 48.73}], 1042048167: ['rub', {77510248: 1648.0,
#                153353594: 389.0, 83862402: 282.0, 14231589: 1168.0}], 6031519620: ['byn', {84296486: 28.57}]}

url_images: [int, str] = {}
# url_images = {64161614: https://basket-04.wb.ru/vol641/part64161/64161614/images/big/1.jpeg}

users_max_items: [int, int] = {}
# users_max_items: [int, int] = {5754662958: 1, 6031519620: 3}

r = redis.Redis(host='127.0.0.1', port=6379, db=6)


# Получение словаря из Redis
user_dict_json = r.get('users_db')
if user_dict_json is not None:
    users_db = json.loads(user_dict_json)
    users_db = {int(k): v for k, v in users_db.items()}
else:
    users_db = {}


users_max_items_json = r.get('users_max_items')
if users_max_items_json is not None:
    users_max_items = json.loads(users_max_items_json)
    users_max_items = {int(k): int(v) for k, v in users_max_items.items()}
else:
    users_max_items = {}

users_items_dict_json = r.get('users_items')
if users_items_dict_json is not None:
    users_items = json.loads(users_items_dict_json)
    users_items = {int(k): v for k, v in users_items.items()}
    for k, v in users_items.items():
        if len(v) > 1:
            v[1] = {int(k): float(v) for k, v in v[1].items()}
else:
    users_items = {}

url_images_dict_json = r.get('url_images')
if url_images_dict_json is not None:
    url_images = json.loads(url_images_dict_json)
    url_images = {int(k): v for k, v in url_images.items()}
else:
    url_images = {}


async def save_url_images():
    r.set('url_images', json.dumps(url_images))


async def save_users_db():
    r.set('users_db', json.dumps(users_db))


async def save_users_items():
    r.set('users_items', json.dumps(users_items))


async def save_users_max_items():
    r.set('users_max_items', json.dumps(users_max_items))
