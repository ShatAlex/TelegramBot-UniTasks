from datetime import datetime, timedelta
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from apscheduler.jobstores.redis import RedisJobStore

from bot_create import dp

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from mysql_db import *

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from shedulers import day_sheduler, week_sheduler, custom_sheduler


class FSMAdmin_task(StatesGroup):
    subject = State()
    title = State()
    description = State()
    deadline = State()
    important_degree = State()


job_stores = {
    "default": RedisJobStore(
        jobs_key="dispatched_trips_jobs",
        run_times_key="dispatched_trips_running",
        host='localhost',
        db=2,
        port=6379
    )
}


async def task_machine_start(message):
    read = await sql_read_subjects(message.from_user.id)
    lst = [InlineKeyboardButton(text=x[2], callback_data=f'sub :{x[0]}:{x[1]}:{x[2]}') for x in read]
    inline_kb = InlineKeyboardMarkup(row_width=4)
    inline_kb.add(*lst)
    await message.answer('📍[1/5] Выбери предмет (Нет нужного? - /add_subject. Для отмены - /cancel)',
                         reply_markup=inline_kb)


@dp.callback_query_handler(text_startswith='sub')
async def task_load_subject(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.data.split(":")[2]
    await FSMAdmin_task.subject.set()
    await state.update_data(user_id=user_id, subject=callback_query.data.split(":")[1])
    await FSMAdmin_task.next()
    await callback_query.message.edit_text(f"📍[1/5] Предмет: {callback_query.data.split(':')[3]}")
    await callback_query.bot.send_message(user_id, '📍[2/5] Введи заголовок')
    await callback_query.answer()


async def task_load_title(message, state: FSMContext):
    await state.update_data(title=message.text)
    await FSMAdmin_task.next()
    await message.reply('📍[3/5] Введи описание')


async def task_load_description(message, state: FSMContext):
    await state.update_data(description=message.text)
    await FSMAdmin_task.next()
    await message.reply('📍[4/5] Введи дедлайн. (Формат: YYYY-mm-dd HH:MI:S)')


async def task_load_deadline(message, state: FSMContext):
    pattern = re.compile('^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$')
    if not pattern.match(message.text):
        await message.reply('Неверный формат! Введите дату в формате: YYYY-mm-dd HH:MI:S')
    else:
        await state.update_data(deadline=message.text)
        await FSMAdmin_task.next()
        await message.reply('📍[5/5] Насколько важен предмет от 0 до 10')


async def task_load_degree(message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 10):
        await message.reply('Неверный формат! Введите целое число от 0 до 10')
    else:
        await state.update_data(important_degree=int(message.text))
        await sql_add_task(state)
        await message.answer('Новое задание добавлено!')
        data = await state.get_data()
        date = data['deadline']
        await state.finish()

        apscheduler = AsyncIOScheduler(timezone='Europe/Moscow', jobstores=job_stores)

        run_day = datetime.strptime(date, '%Y-%m-%d %H:%M:%S') - timedelta(hours=24)
        now = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        if run_day < now:
            run_day = datetime.now()

        apscheduler.add_job(day_sheduler, 'date', run_date=run_day,
                            kwargs={'message': message, 'user_id': data['user_id'], 'title': data['title'],
                                    'description': data['description']})
        apscheduler.add_job(week_sheduler, 'cron', day_of_week='mon',
                            kwargs={'message': message, 'user_id': data['user_id']})

        apscheduler.start()


class FSMAdmin_subject(StatesGroup):
    title = State()


async def subject_machine_start(message):
    await FSMAdmin_subject.title.set()
    await message.reply('📍[1/1] Введи предмет. Для отмены - /cancel')


async def subject_load_title(message, state: FSMContext):
    await state.update_data(user_id=int(message.from_user.id), title=message.text)
    await sql_add_subject(state)
    await message.answer('Новый предмет добавлен!')
    await state.finish()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message, state: FSMContext):
    current_state = await state.get_state()
    if not current_state:
        return
    await state.finish()
    await message.reply('Adding process is canceled!')


class FSMAdmin_scheduler(StatesGroup):
    task = State()
    date = State()


async def scheduler_machine_start(message):
    read = await sql_read_tasks(message.from_user.id)
    lst = [InlineKeyboardButton(text=x[3], callback_data=f'add_sch :{x[0]}:{x[1]}') for x in read]
    inline_kb = InlineKeyboardMarkup(row_width=4)
    inline_kb.add(*lst)
    await message.answer('📆 [1/2] Выбери задание', reply_markup=inline_kb)


@dp.callback_query_handler(text_startswith='add_sch')
async def scheduler_load_task(callback_query: types.CallbackQuery, state: FSMContext):
    id = callback_query.data.split(":")[1]
    user_id = callback_query.data.split(":")[2]
    await FSMAdmin_scheduler.task.set()
    await state.update_data(user_id=user_id, task=id)
    await FSMAdmin_scheduler.next()

    task = await sql_read_one_task(id, user_id)
    title = task[3]
    await callback_query.message.edit_text(f"📆 [1/2] Задание: {title}")
    await callback_query.bot.send_message(user_id, '📆 [2/2] Когда напомнить? (Формат: YYYY-mm-dd HH:MI:S)')
    await callback_query.answer()


async def scheduler_load_date(message, state: FSMContext):
    pattern = re.compile('^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$')
    if not pattern.match(message.text):
        await message.reply('Неверный формат! Введите дату в формате: YYYY-mm-dd HH:MI:S')
    if datetime.strptime(message.text, '%Y-%m-%d %H:%M:%S') < datetime.strptime(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'):
        await message.reply('Это время уже в прошлом! Введите корректно:')
    else:
        await state.update_data(date=message.text)
    data = await state.get_data()
    date = data['date']
    await message.answer('📆 Уведомление добавлено!')
    await state.finish()

    apscheduler = AsyncIOScheduler(timezone='Europe/Moscow', jobstores=job_stores)

    run_day = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

    apscheduler.add_job(custom_sheduler, 'date', run_date=run_day,
                        kwargs={'message': message, 'user_id': data['user_id'], 'task_id': data['task']})
    apscheduler.start()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message, state: FSMContext):
    current_state = await state.get_state()
    if not current_state:
        return
    await state.finish()
    await message.reply('Adding process is canceled!')


def register_handlers_admin(dp):
    dp.register_message_handler(task_machine_start, commands=['add_task'], state=None)
    dp.register_message_handler(subject_machine_start, commands=['add_subject'], state=None)
    dp.register_message_handler(scheduler_machine_start, commands=['add_notification'], state=None)
    dp.register_message_handler(task_load_title, state=FSMAdmin_task.title)
    dp.register_message_handler(task_load_description, state=FSMAdmin_task.description)
    dp.register_message_handler(task_load_deadline, state=FSMAdmin_task.deadline)
    dp.register_message_handler(task_load_degree, state=FSMAdmin_task.important_degree)
    dp.register_message_handler(task_load_subject, state=FSMAdmin_task.subject)
    dp.register_message_handler(subject_load_title, state=FSMAdmin_subject.title)
    dp.register_message_handler(scheduler_load_task, state=FSMAdmin_scheduler.task)
    dp.register_message_handler(scheduler_load_date, state=FSMAdmin_scheduler.date)
