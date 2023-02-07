"""File with sqlalchemy tables defined"""
import sqlalchemy

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("full_name", sqlalchemy.String(length=100)),
    sqlalchemy.Column("notification_time", sqlalchemy.Time),
    sqlalchemy.Column("weight", sqlalchemy.Float),
    sqlalchemy.Column("desired_weight", sqlalchemy.Float),
)

weight_logs = sqlalchemy.Table(
    "weight_logs",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer),
    sqlalchemy.Column("weight", sqlalchemy.Integer),
    sqlalchemy.Column("date", sqlalchemy.Date),
)
