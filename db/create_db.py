import datetime

import pytz
from sqlalchemy import create_engine, Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///payments.db", echo=True)
Base = declarative_base()


class Payment(Base):
    """Создание базы данных"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)  # id в базе данных
    tg_user_id = Column(BigInteger, nullable=False)  # Telegram ID пользователя
    username = Column(String)  # username пользователя (если есть)
    payment_method = Column(String)  # комментарий к платежу
    status = Column(String, default="pending")  # "pending" - ожидает, "confirmed" - принят, "rejected" - отклонен
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(pytz.timezone("Etc/GMT-5")))  # время создания
    confirmed_at = Column(DateTime, nullable=True)  # время принятия запроса
    duration = Column(BigInteger, nullable=True)  # продолжительность


Base.metadata.create_all(engine)
