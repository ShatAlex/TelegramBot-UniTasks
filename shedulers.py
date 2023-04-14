from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot_create import dp
from mysql_db import sql_read_tasks, sql_read_day_schedul, sql_read_custom_schedul, sql_read_one_task


async def day_sheduler(message, user_id, title, description):
    task = await sql_read_day_schedul(user_id, title, description)
    if task:
        text = f'Уведомление\n📚 _Предмет:_ *{task[2]}*\n📖 _Задание:_ *{task[4]}*\n🕔 _Осталось:_ *{task[8]}*\n'
        button = InlineKeyboardButton(text='Подробнее', callback_data=f'day_sch :{task[0]}:{task[1]}')
        inline_kb = InlineKeyboardMarkup()
        inline_kb.add(button)
        await message.answer(text, reply_markup=inline_kb, parse_mode='Markdown')


@dp.callback_query_handler(text_startswith='day_sch')
async def day_sch_callback(callback_query):
    id = callback_query.data.split(":")[1]
    user_id = callback_query.data.split(":")[2]
    read = await sql_read_one_task(id, user_id)

    title = read[3]
    description = read[4]
    deadline = read[5]
    text = f'📚 Предмет: {title}\n📖 Задание: {description}\n🕔 Дедлайн: {deadline}\n'

    await callback_query.answer(text, show_alert=True)


async def week_sheduler(message, user_id):
    read = await sql_read_tasks(user_id, mode='week')
    if len(read) == 0:
        await message.answer('У вас нет активных заданий на неделю! 😉')
    else:
        for task in read:
            text = f'Уведомление\n📚 _Предмет:_ *{task[2]}*\n📖 _Задание:_ *{task[4]}*\n🕔 _Осталось:_ *{task[8]}*\n'
            button = InlineKeyboardButton(text='Подробнее', callback_data=f'week_sch :{task[0]}:{task[1]}')
            inline_kb = InlineKeyboardMarkup()
            inline_kb.add(button)
            await message.answer(text, reply_markup=inline_kb, parse_mode='Markdown')


@dp.callback_query_handler(text_startswith='week_sch')
async def week_sch_callback(callback_query):
    id = callback_query.data.split(":")[1]
    user_id = callback_query.data.split(":")[2]
    read = await sql_read_one_task(id, user_id)

    title = read[3]
    description = read[4]
    deadline = read[5]
    text = f'📚 Предмет: {title}\n📖 Задание: {description}\n🕔 Дедлайн: {deadline}\n'

    await callback_query.answer(text, show_alert=True)


async def custom_sheduler(message, user_id, task_id):
    read = await sql_read_custom_schedul(user_id, task_id)
    task = read[0]
    if task:
        text = f'Уведомление\n📚 _Предмет:_ *{task[2]}*\n📖 _Задание:_ *{task[4]}*\n'
        button = InlineKeyboardButton(text='Подробнее', callback_data=f'custom_sch :{task[0]}:{task[1]}')
        inline_kb = InlineKeyboardMarkup()
        inline_kb.add(button)
        await message.answer(text, reply_markup=inline_kb, parse_mode='Markdown')


@dp.callback_query_handler(text_startswith='custom_sch')
async def custom_sch_callback(callback_query):
    id = callback_query.data.split(":")[1]
    user_id = callback_query.data.split(":")[2]
    read = await sql_read_one_task(id, user_id)

    title = read[3]
    description = read[4]
    deadline = read[5]
    text = f'📚 Предмет: {title}\n📖 Задание: {description}\n🕔 Дедлайн: {deadline}\n'

    await callback_query.answer(text, show_alert=True)
