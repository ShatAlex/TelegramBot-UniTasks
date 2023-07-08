from aiogram import Bot
from aiogram.dispatcher import Dispatcher


from aiogram.contrib.fsm_storage.redis import RedisStorage2

storage = RedisStorage2(host='localhost',
                        port=6379)

bot = Bot(token='6212942647:AAEXBZKa2zevlZBy5fCialonV3-8pvvDbUk')
dp = Dispatcher(bot, storage=storage)
