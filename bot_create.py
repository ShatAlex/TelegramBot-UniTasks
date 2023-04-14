from aiogram import Bot
from aiogram.dispatcher import Dispatcher

from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

bot = Bot(token='6212942647:AAEXBZKa2zevlZBy5fCialonV3-8pvvDbUk')
dp = Dispatcher(bot, storage=storage)
