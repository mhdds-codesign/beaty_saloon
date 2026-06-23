from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)           # در دیاگرام UNIQUE نیست
    register_date = Column(String, nullable=True)           # TEXT NULL
    notes = Column(String, nullable=True)                   # TEXT NULL
    address = Column(String, nullable=True)                 # TEXT NULL

    reservations = relationship("Reservation", back_populates="customer")