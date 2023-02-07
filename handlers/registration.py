from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, types
from pydantic import ValidationError
from database import db
from models.models import User, WeightLog
from datetime import datetime
from .scheduled import schedule_user
from aiogram import Bot

bot: Bot

class RegistrationStates(StatesGroup):
    waiting_for_currrent_weight = State()
    waiting_for_desired_weight = State()
    waiting_for_measurement_time = State()

async def action_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено")

async def registration_start(message: types.Message, state: FSMContext):
    """Начать регистрацию и запросить текущий вес"""
    await state.update_data({"user_obj": User()})
    if await db.user_exists(message.from_id):
        await message.reply("Вы уже записаны. Вы можете начать заново с помощью комманды /quit")
        await state.finish()
        return

    await message.reply("Введите свой текущий вес в килограммах")
    await state.set_state(RegistrationStates.waiting_for_currrent_weight)


async def get_current_weight(message: types.Message, state: FSMContext):
    """Записать текущий вес и спросить желаемый вес"""
    user_data = await state.get_data()
    user = user_data["user_obj"]
    try:
        user.weight = float(message.text)
    except ValidationError as e:
        await message.reply("Вес не может быть меньше 30кг")
        return
    except ValueError as e:
        await message.reply("Введите число.")
        return

    await state.update_data({"user_obj": user})
    await message.reply("Теперь введите желаемый вес")
    await state.set_state(RegistrationStates.waiting_for_desired_weight)


async def get_desired_weight(message: types.Message, state: FSMContext):
    """Записать желаемый вес и запросить время уведомления"""
    user_data = await state.get_data()
    user = user_data["user_obj"]
    try:
        user.desired_weight = float(message.text)
    except ValidationError as e:
        await message.reply("Желаемый вес не может быть больше текущего")
        return
    except ValueError as e:
        await message.reply("Введите число.")
        return

    await state.update_data({"user_obj": user})
    await message.reply(
        "Теперь укажите время, когда вам присылать напоминание взвеситься"
    )
    await state.set_state(RegistrationStates.waiting_for_measurement_time)


async def registration_finish(message: types.Message, state: FSMContext):
    """Записать время уведомления, и если всё правильно, записать всё в БД"""
    user_data = await state.get_data()
    user = user_data["user_obj"]
    try:
        user.notification_time = message.text
    except ValueError:
        await message.reply("Введите время в 24 часовом формате. Например 8:00")
        return
    user.full_name = message.from_user.full_name
    user.id = message.from_user.id

    await db.save_user(user)
    await message.reply(
        f"Отлично! Ваш текущий вес:{user.weight} ваш желаемый вес: {user.desired_weight} Будем напоминать вам взвешиваться каждый день в {user.notification_time}"
    )
    await state.finish()
    await db.make_weight_entry(
        WeightLog(user_id=user.id, weight=user.weight, date=datetime.now().date())
    )
    
    
    
    
    


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(action_cancel, commands="cancel", state="*")
    dp.register_message_handler(registration_start, commands="begin", state="*")
    dp.register_message_handler(
        get_current_weight, state=RegistrationStates.waiting_for_currrent_weight
    )
    dp.register_message_handler(
        get_desired_weight, state=RegistrationStates.waiting_for_desired_weight
    )
    dp.register_message_handler(
        registration_finish, state=RegistrationStates.waiting_for_measurement_time
    )
