from pydantic import BaseModel
from typing import List, Optional
import datetime

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class BookBase(BaseModel):
    title: str
    author: str
    quantity: int

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int

    class Config:
        orm_mode = True

class LoanBase(BaseModel):
    user_id: int
    book_id: int

class LoanCreate(LoanBase):
    pass

class Loan(LoanBase):
    id: int
    loan_date: datetime.date
    due_date: datetime.date
    return_date: Optional[datetime.date]
    fine: float

    class Config:
        orm_mode = True