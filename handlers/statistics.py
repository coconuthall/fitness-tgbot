from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, types
from database import db
from datetime import datetime, date, timedelta
from aiogram.dispatcher.filters.state import State, StatesGroup

class StatisticsStates(StatesGroup):
    waiting_for_answer = State()



async def get_statistics(message: types.Message, state:FSMContext):
    start_period = date(date.today().year, date.today().month, 1)
    end_period = datetime.now().date()
    await state.update_data({"month": start_period.month})
    statistics = await db.get_progress(user_id=message.from_user.id, start_period=start_period, end_period=end_period)
    message_reply = "Ваш вес за текущий месяц:"
    for entry in statistics:
        message_reply += f"\n{entry.date} - {entry.weight} кг"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    keyboard.add("Предыдущий месяц")
    keyboard.add("Выйти")
    await message.answer(message_reply, reply_markup=keyboard)
    await state.set_state(StatisticsStates.waiting_for_answer)


async def answer_handler(message:types.Message, state: FSMContext):
    if message.text.lower() == "выйти":
        await message.answer("Выходим из просмотра статистики", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        return
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Выйти")
    user_data = await state.get_data()
    current_month = user_data['month']
    #placeholder
    try:
        start_period = date(date.today().year, current_month - 1, 1)
    except:
        await message.answer("Данные недоступны", reply_markup=keyboard)
        return
    end_period = date(date.today().year, current_month, 1) - timedelta(days=1)
    statistics = await db.get_progress(user_id=message.from_user.id, start_period=start_period, end_period=end_period)
    
    message_reply = f"Ваш вес за {current_month - 1}й месяц:"
    for entry in statistics:
        message_reply += f"\n{entry.date} - {entry.weight} кг"
    
    keyboard.add("Предыдущий месяц")
    
    await message.answer(message_reply, reply_markup=keyboard)
    await state.update_data({"month": start_period.month})
    
    



def register_handlers(dp: Dispatcher):
    dp.register_message_handler(get_statistics, commands="statistics")
    dp.register_message_handler(answer_handler, state=StatisticsStates.waiting_for_answer)