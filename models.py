from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# 1. Это та самая переменная Base, которую не мог найти ваш main.py
Base = declarative_base()

class Country(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    coordinates = Column(String)  # Оставил как TEXT/VARCHAR, как было в вашем SQL

    # Связь с самолетами (опционально, удобно для ORM)
    aircrafts = relationship("Aircraft", back_populates="country")

class Aircraft(Base):
    __tablename__ = 'aircrafts'  # Обратите внимание: в вашем SQL было aircrafts (мн. число)

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_id = Column(Integer, ForeignKey('countries.id'))
    registration = Column(String(255))
    callsign = Column(String(255))
    x = Column(Float)
    y = Column(Float)
    altitude = Column(Float)
    velocity = Column(Float)
    heading = Column(Float)
    vertical_rate = Column(Float)
    on_ground = Column(Boolean)
    time_position = Column(DateTime)

    # Обратная связь
    country = relationship("Country", back_populates="aircrafts")

