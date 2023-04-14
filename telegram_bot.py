from aiogram.utils import executor

from bot_create import dp
from mysql_db import sql_start

from handlers import client, admin, other

client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
other.register_handlers_other(dp)


async def bot_startup(_):
    sql_start()
    print('Бот готов к работе!')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=bot_startup)
