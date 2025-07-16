from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import schemas, services
from .database import get_db

router = APIRouter()

#Rotas para controle de usuários
@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return services.create_user(db=db, user=user)

@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = services.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = services.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user

@router.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    return services.update_user(db=db, user_id=user_id, user=user)

@router.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return services.delete_user(db=db, user_id=user_id)

@router.get("/users/{user_id}/loans", response_model=List[schemas.Loan])
def read_user_loans(user_id: int, db: Session = Depends(get_db)):
    return services.get_user_loans(db=db, user_id=user_id)

#Rotas para livros
@router.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return services.create_book(db=db, book=book)

@router.get("/books/", response_model=List[schemas.Book])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = services.get_books(db, skip=skip, limit=limit)
    return books

@router.get("/books/{book_id}", response_model=schemas.Book)
def read_book(book_id: int, db: Session = Depends(get_db)):
    db_book = services.get_book(db=db, book_id=book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return db_book

@router.put("/books/{book_id}", response_model=schemas.Book)
def update_book(book_id: int, book: schemas.BookCreate, db: Session = Depends(get_db)):
    return services.update_book(db=db, book_id=book_id, book=book)

@router.delete("/books/{book_id}", response_model=dict)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    return services.delete_book(db=db, book_id=book_id)

@router.get("/books/{book_id}/availability", response_model=dict)
def check_book_availability(book_id: int, db: Session = Depends(get_db)):
    available = services.check_book_availability(db=db, book_id=book_id)
    return {"book_id": book_id, "available": available}

# Rotas para emprestimos
@router.post("/loans/", response_model=schemas.Loan)
def create_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    return services.create_loan(db=db, loan=loan)

@router.get("/loans/", response_model=List[schemas.Loan])
def read_loans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return services.get_loans(db=db, skip=skip, limit=limit)

@router.get("/loans/{loan_id}", response_model=schemas.Loan)
def read_loan(loan_id: int, db: Session = Depends(get_db)):
    db_loan = services.get_loan(db=db, loan_id=loan_id)
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    return db_loan

@router.put("/loans/{loan_id}", response_model=schemas.Loan)
def update_loan(loan_id: int, loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    return services.update_loan(db=db, loan_id=loan_id, loan=loan)

@router.delete("/loans/{loan_id}", response_model=dict)
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    return services.delete_loan(db=db, loan_id=loan_id)

@router.post("/loans/{loan_id}/return", response_model=schemas.Loan)
def return_loan(loan_id: int, db: Session = Depends(get_db)):
    return services.return_loan(db=db, loan_id=loan_id)