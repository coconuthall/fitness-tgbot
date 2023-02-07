import asyncio
from databases import Database
from databases.interfaces import Record
import sqlalchemy
from .schemas import metadata, users, weight_logs
from models.models import User, WeightLog
from datetime import datetime, date


database = Database(
    "postgresql+asyncpg://postgres:coconuthall@localhost:5432/fitnessbot"
)
dialect = sqlalchemy.dialects.postgresql.dialect()

def record_to_user(record: Record):
    user = User.parse_obj(record)
    return user
    
def record_to_weightlog(record: Record):
    log = WeightLog.parse_obj(record)
    return log

async def db_init():
    """Заносит в БД необходимые таблицы, если они не существуют"""
    await database.connect()

    for table in metadata.tables.values():
        schema = sqlalchemy.schema.CreateTable(table, if_not_exists=True)
        query = str(schema.compile(dialect=dialect))
        await database.execute(query=query)


async def db_close():
    await database.disconnect()


async def save_user(user: User):
    values = user.dict()
    if await user_exists(user.id):
        query = users.update().where(users.c.id == user.id)
        await database.execute(query=query, values=values)
    else:
        query = users.insert()
        await database.execute(query=query, values=values)


async def user_exists(id: int) -> bool:
    query = users.select().where(users.c.id == id)
    val = await database.fetch_one(query=query)
    if val:
        return True
    return False


async def get_all_users() -> list[User]:
    query = users.select()
    result = await database.fetch_all(query=query)
    user_list = []
    for item in result:
        user_list.append(record_to_user(item))
    return user_list


async def make_weight_entry(entry: WeightLog):
    values = entry.dict()
    query = weight_logs.insert()
    await database.execute(query=query, values=values)


async def get_latest_entry(user_id: int) -> WeightLog:
    query = (
        weight_logs.select()
        .where(weight_logs.c.user_id == user_id)
        .order_by(sqlalchemy.desc(weight_logs.c.date))
    )
    result = await database.fetch_one(query=query)
    return record_to_weightlog(result)

async def remove_user(user_id: int) -> None:
    query = users.delete().where(users.c.id == user_id)
    log_query = weight_logs.delete().where(weight_logs.c.user_id == user_id)
    await database.execute(query)
    await database.execute(log_query)

async def get_progress(user_id: int, start_period: date, end_period: date):
    query = "select * from weight_logs wl where date >= :startdate and date <= :enddate and user_id = :id;"
    result = await database.fetch_all(
        query=query, 
        values={
            'startdate': start_period, 
            'enddate': end_period, 
            'id' : user_id})

    log_list = []
    for item in result:
        log_list.append(record_to_weightlog(item))
    return log_list


