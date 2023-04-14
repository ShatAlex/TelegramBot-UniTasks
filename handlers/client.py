from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot_create import bot, dp
from mysql_db import *


async def day_tasks(message):
    res = await sql_read_tasks(message.from_user.id, mode='day')
    if len(res) == 0:
        await message.answer(f'{message.from_user.first_name}, у тебя нет заданий на сегодня!')
        return
    await message.answer(f'Твои задания на сегодня ({len(res)}): ')
    for x in res:
        await bot.send_message(message.from_user.id,
                               f'📚 _Предмет:_ *{x[2]}*\n📖 _Задание:_ *{x[4]}*\n🕔 _Дедлайн:_ *{x[5]}*\n'
                               f'❗ _Статус:_ *в работе*\n', parse_mode="Markdown")


async def week_tasks(message):
    res = await sql_read_tasks(message.from_user.id, mode='week')
    if len(res) == 0:
        await message.answer(f'{message.from_user.first_name}, у тебя нет заданий на неделю!')
        return
    await message.answer(f'Твои задания на *неделю* ({len(res)}): ', parse_mode="Markdown")
    for x in res:
        await bot.send_message(message.from_user.id,
                               f'📚 _Предмет:_ *{x[2]}*\n📖 _Задание:_ *{x[4]}*\n🕔 _Дедлайн:_ *{x[5]}*\n'
                               f'❗ _Статус:_ *в работе*\n', parse_mode="Markdown")


async def review_tasks(message):
    res = await sql_read_tasks(message.from_user.id, mode='all')
    if len(res) == 0:
        await message.answer(f'{message.from_user.first_name}, у тебя нет активных заданий!')
        return
    await message.answer(f'🤗 Привет, {message.from_user.first_name}! Твои задания ({len(res)}): ')
    for x in res:
        if x[7] == 0:  # статус
            await bot.send_message(message.from_user.id,
                                   f'📚 _Предмет:_ *{x[2]}*\n📖 _Задание:_ *{x[4]}*\n🕔 _Дедлайн:_ *{x[5]}*\n'
                                   f'❗ _Статус:_ *в работе*\n', parse_mode="Markdown")
        else:
            await bot.send_message(message.from_user.id,
                                   f'📚 _Предмет:_ *{x[2]}*\n📖 _Задание:_ *{x[4]}*\n🕔 _Дедлайн:_ *{x[5]}*\n'
                                   f'✅ _Статус:_ *выполнено*\n', parse_mode="Markdown")


async def remove_task(message):
    read = await sql_read_tasks(message.from_user.id)
    if len(read) == 0:
        await message.answer('У вас нет активных заданий 😉')
    else:
        lst = [InlineKeyboardButton(text=x[3], callback_data=f'del :{x[0]}:{x[1]}') for x in read]
        inline_kb = InlineKeyboardMarkup(row_width=4)
        inline_kb.add(*lst)
        await message.answer('🗑 Выбери задание, которое нужно удалить', reply_markup=inline_kb)


@dp.callback_query_handler(text_startswith='del')
async def task_remove_callback(callback_query):
    id = callback_query.data.split(":")[1]
    user_id = callback_query.data.split(":")[2]
    read = await sql_read_one_task(id, user_id)
    title = read[3][:30]
    await sql_remove_task(id, user_id)
    await callback_query.answer(f'Удалена запись: {title}')

    read = await sql_read_tasks(user_id)
    if len(read) == 0:
        await callback_query.message.delete()
        await callback_query.message.answer('У вас нет активных заданий 😉')
    else:
        lst = [InlineKeyboardButton(text=x[3], callback_data=f'del :{x[0]}:{x[1]}') for x in read]
        inline_kb = InlineKeyboardMarkup(row_width=4)
        inline_kb.add(*lst)
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=inline_kb)


async def remove_subjects(message):
    read = await sql_read_subjects(message.from_user.id)
    if len(read) == 0:
        await message.answer('У вас нет активных предметов 😉')
    else:
        lst = [InlineKeyboardButton(text=x[2], callback_data=f'sub_del :{x[0]}:{x[1]}') for x in read]
        inline_kb = InlineKeyboardMarkup(row_width=4)
        inline_kb.add(*lst)
        await message.answer('🗑 Выбери предмет, который нужно удалить', reply_markup=inline_kb)


@dp.callback_query_handler(text_startswith='sub_del')
async def subject_remove_callback(callback_query):
    id = callback_query.data.split(":")[1]
    user_id = callback_query.data.split(":")[2]
    await sql_remove_subject(id, user_id)
    await callback_query.answer(f'Предмет удалён!')

    read = await sql_read_subjects(user_id)
    if len(read) == 0:
        await callback_query.message.delete()
        await callback_query.message.answer('У вас нет активных предметов 😉')
    else:
        lst = [InlineKeyboardButton(text=x[2], callback_data=f'sub_del :{x[0]}:{x[1]}') for x in read]
        inline_kb = InlineKeyboardMarkup(row_width=4)
        inline_kb.add(*lst)
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                            message_id=callback_query.message.message_id,
                                            reply_markup=inline_kb)


async def complete_task(message):
    read = await sql_read_tasks(message.from_user.id)
    lst = [InlineKeyboardButton(text=f'❗{x[3]}' if x[7] == 0 else f'✅{x[3]}',
                                callback_data=f'comp :{x[0]}:{x[1]}') for x in read]
    inline_kb = InlineKeyboardMarkup(row_width=4)
    inline_kb.add(*lst)
    await message.answer('Какие задания выполнил:', reply_markup=inline_kb)


@dp.callback_query_handler(text_startswith='comp')
async def task_complete_callback(callback_query):
    id = callback_query.data.split(":")[1]
    user_id = callback_query.data.split(":")[2]

    await sql_complete_task(id, user_id)

    read = await sql_read_tasks(user_id)
    lst = [InlineKeyboardButton(text=f'❗{x[3]}' if x[7] == 0 else f'✅{x[3]}',
                                callback_data=f'comp :{x[0]}:{x[1]}') for x in read]
    inline_kb = InlineKeyboardMarkup(row_width=4)
    inline_kb.add(*lst)
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        reply_markup=inline_kb)
    read = await sql_read_one_task(id, user_id)
    title = read[3][:30]
    await callback_query.answer(f'{title}: статус изменен!"')


def register_handlers_client(dp):
    dp.register_message_handler(review_tasks, commands=['review'])
    dp.register_message_handler(remove_task, commands=['remove_task'])
    dp.register_message_handler(remove_subjects, commands=['remove_sub'])
    dp.register_message_handler(complete_task, commands=['complete'])
    dp.register_message_handler(day_tasks, commands=['day'])
    dp.register_message_handler(week_tasks, commands=['week'])
