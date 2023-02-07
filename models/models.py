from pydantic import BaseModel, ValidationError, validator
from databases.interfaces import Record
from typing import Optional
from datetime import time, date, datetime


class User(BaseModel):
    id: Optional[int]
    full_name: Optional[str]
    notification_time: Optional[time]
    weight: Optional[float]
    desired_weight: Optional[float]

    @validator("weight")
    def weight_correct(cls, val):
        if val is None:
            return val
        if val < 30:
            raise ValueError("Вес не может быть меньше 30кг")
        return val

    @validator("desired_weight")
    def desired_weight_correct(cls, val, values, **kwargs):
        if val is None:
            return val
        if "weight" in values and val >= values["weight"]:
            raise ValueError("Желаемый вес не может быть больше текущего")
        return val

    class Config:
        validate_assignment = True



class WeightLog(BaseModel):
    user_id: Optional[int]
    weight: Optional[float]
    date: Optional[date]

    @validator("date")
    def date_validator(cls, value):
        if not value:
            return datetime.now().date()
        return value

    class Config:
        validate_assignment = True


user = User()
