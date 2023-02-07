import logging
import asyncio
from aiogram import Bot
from database import db
from datetime import datetime, time, timedelta
from models.models import User, WeightLog


async def schedule_all(bot: Bot):
    for user in await db.get_all_users():
        await schedule_user(user = user, bot=bot)
    

async def schedule_user(user: User, bot: Bot):
    if user.notification_time:
        asyncio.create_task(send_notification(bot, user))
        asyncio.create_task(add_missed_entry(user))

async def send_notification(bot: Bot, user: User):
    latest_entry = await db.get_latest_entry(user.id)
    while True:
        if not await db.user_exists(user.id) or user.desired_weight >= latest_entry.weight:
            break
        else:
            current_time = datetime.now()
            notification_time = datetime(
                current_time.year, 
                current_time.month,
                current_time.day,
                user.notification_time.hour,
                user.notification_time.minute)

            if current_time > notification_time:
                notification_time = notification_time.replace(day=notification_time.day + 1)

            seconds = (notification_time - current_time).total_seconds()
            logging.log(logging.INFO, f"Notification scheduled for user {user.id} at {notification_time}")
            await asyncio.sleep(seconds)
            if latest_entry.date != datetime.now().date():
                await bot.send_message(user.id, "Время взвеситься. Напишите свой вес.")
        
        


async def add_missed_entry(user: User):
    while True:
        current_time = datetime.now()
        missed_time = datetime.now().replace(hour=23, minute=59, second=59)
        seconds = (missed_time - current_time).total_seconds()
        await asyncio.sleep(seconds)
        latest_entry = await db.get_latest_entry(user.id)
        if latest_entry.date != current_time.date():
            logging.log(logging.INFO, f"Missed entry added for user {user.id}")
            await db.make_weight_entry(
                WeightLog(
                    user_id=user.id, weight=latest_entry.weight, date=datetime.now().date()
                )
            )
