from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    loans = relationship("Loan", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    quantity = Column(Integer, default=1)

    loans = relationship("Loan", back_populates="book")

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))
    loan_date = Column(Date, default=datetime.date.today)
    due_date = Column(Date, default=lambda: datetime.date.today() + datetime.timedelta(days=14))
    return_date = Column(Date, nullable=True)
    fine = Column(Float, default=0.0)

    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")