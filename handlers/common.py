from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, types
from database import db
from datetime import datetime
from models.models import WeightLog
from aiogram.dispatcher.filters.state import State, StatesGroup


class QuitStates(StatesGroup):
    waiting_for_confirmation = State()


async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Commands:\n/starttracking - start trackin'")

async def user_quit(message: types.Message, state: FSMContext):
    await state.set_state(QuitStates.waiting_for_confirmation)
    await message.reply('Внимание! Это сотрёт весь ваш прогресс. Вы уверены, что хотите начать заново? Напишите "Подтверждаю", чтобы удалить свой прогресс')

async def quit_confirm(message: types.Message, state: FSMContext):
    if message.text.lower() == "подтверждаю":
        await db.remove_user(message.from_user.id)
        await message.reply("Ваш прогресс удалён.")
    else:
        await message.reply("Хорошо, стирать прогресс не будем")

    await state.finish()



async def default_handler(message: types.Message):
    if await db.user_exists(message.from_id):
        entry = await db.get_latest_entry(message.from_id)
        if entry.date == datetime.now().date():
            await message.reply(f"На сегодня вес уже записан: {entry.weight}")
        else:
            try:
                weight = float(message.text)
            except ValueError:
                await message.reply("Если хочешь записать вес, то введи его цифрами!!!")
                return

            await db.make_weight_entry(
                WeightLog(
                    user_id=message.from_id,
                    weight=weight,
                    date=datetime.now().date(),
                )
            )
            await message.reply("Отлично, записал твой вес за сегодня.")
            
    else:
        await message.reply(
            "Воспользуйся командой /help, чтобы узнать, как мной пользоваться"
        )



def register_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=["start", "help"])
    dp.register_message_handler(user_quit, commands="quit")
    dp.register_message_handler(quit_confirm, state=QuitStates.waiting_for_confirmation)
    dp.register_message_handler(default_handler)
