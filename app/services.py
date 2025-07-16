import logging
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import date, timedelta
from fastapi import HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user(db: Session, user_id: int):
    logger.info(f"Buscando usuário com id={user_id}")
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"Listando usuários: skip={skip}, limit={limit}")
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    logger.info(f"Criando usuário: name={user.name}, email={user.email}")
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado.")
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"Usuário criado com id={db_user.id}")
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        logger.error(f"Usuário id={user_id} não encontrado para atualização")
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    existing_user_email = db.query(models.User).filter(models.User.email == user.email, models.User.id != user_id).first()
    if existing_user_email:
        raise HTTPException(status_code=400, detail="Email já está em uso por outro usuário.")

    db_user.name = user.name
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    logger.info(f"Usuário id={user_id} atualizado")
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        logger.error(f"Usuário id={user_id} não encontrado para remoção")
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    active_loans = db.query(models.Loan).filter(models.Loan.user_id == user_id, models.Loan.return_date == None).count()
    if active_loans > 0:
        raise HTTPException(status_code=400, detail="Usuário possui empréstimos ativos e não pode ser removido.")

    db.delete(db_user)
    db.commit()
    logger.info(f"Usuário id={user_id} removido")
    return {"detail": "Usuário removido"}

def get_book(db: Session, book_id: int):
    logger.info(f"Buscando livro com id={book_id}")
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"Listando livros: skip={skip}, limit={limit}")
    return db.query(models.Book).offset(skip).limit(limit).all()

def create_book(db: Session, book: schemas.BookCreate):
    logger.info(f"Criando livro: title={book.title}, author={book.author}, quantity={book.quantity}")
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    logger.info(f"Livro criado com id={db_book.id}")
    return db_book

def update_book(db: Session, book_id: int, book: schemas.BookCreate):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        logger.error(f"Livro id={book_id} não encontrado para atualização")
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    db_book.title = book.title
    db_book.author = book.author
    db_book.quantity = book.quantity
    db.commit()
    db.refresh(db_book)
    logger.info(f"Livro id={book_id} atualizado")
    return db_book

def delete_book(db: Session, book_id: int):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not db_book:
        logger.error(f"Livro id={book_id} não encontrado para remoção")
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    active_loans = db.query(models.Loan).filter(models.Loan.book_id == book_id, models.Loan.return_date == None).count()
    if active_loans > 0:
        raise HTTPException(status_code=400, detail="Este livro possui empréstimos ativos e não pode ser removido.")

    db.delete(db_book)
    db.commit()
    logger.info(f"Livro id={book_id} removido")
    return {"detail": "Livro removido"}

def check_book_availability(db: Session, book_id: int):
    logger.info(f"Verificando disponibilidade do livro id={book_id}")
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        logger.warning(f"Livro id={book_id} não encontrado")
        return False
    
    active_loans = db.query(models.Loan).filter(models.Loan.book_id == book_id, models.Loan.return_date == None).count()
    available = book.quantity > active_loans
    logger.info(f"Livro id={book_id} disponível: {available} (quantidade={book.quantity}, empréstimos ativos={active_loans})")
    return available

def create_loan(db: Session, loan: schemas.LoanCreate):
    logger.info(f"Tentando criar empréstimo: user_id={loan.user_id}, book_id={loan.book_id}")
    user = get_user(db, loan.user_id)
    if not user:
        logger.error(f"Usuário id={loan.user_id} não encontrado")
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if not check_book_availability(db, loan.book_id):
        logger.error(f"Livro id={loan.book_id} não disponível para empréstimo")
        raise HTTPException(status_code=400, detail="Livro não disponível para empréstimo.")

    active_user_loans = db.query(models.Loan).filter(models.Loan.user_id == loan.user_id, models.Loan.return_date == None).count()
    if active_user_loans >= 3:
        logger.error(f"Usuário id={loan.user_id} atingiu o limite de 3 empréstimos ativos")
        raise HTTPException(status_code=400, detail="Usuário atingiu o limite de 3 empréstimos ativos.")

    db_loan = models.Loan(user_id=loan.user_id, book_id=loan.book_id)
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    logger.info(f"Empréstimo criado com id={db_loan.id} para user_id={loan.user_id}, book_id={loan.book_id}")
    return db_loan

def get_loans(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"Listando empréstimos: skip={skip}, limit={limit}")
    return db.query(models.Loan).order_by(models.Loan.loan_date.desc()).offset(skip).limit(limit).all()

def get_loan(db: Session, loan_id: int):
    logger.info(f"Buscando empréstimo com id={loan_id}")
    return db.query(models.Loan).filter(models.Loan.id == loan_id).first()

def update_loan(db: Session, loan_id: int, loan: schemas.LoanCreate):
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not db_loan:
        logger.error(f"Empréstimo id={loan_id} não encontrado para atualização")
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    if db_loan.return_date:
        raise HTTPException(status_code=400, detail="Não é possível editar um empréstimo que já foi devolvido.")
    db_loan.user_id = loan.user_id
    db_loan.book_id = loan.book_id
    db.commit()
    db.refresh(db_loan)
    logger.info(f"Empréstimo id={loan_id} atualizado")
    return db_loan

def delete_loan(db: Session, loan_id: int):
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not db_loan:
        logger.error(f"Empréstimo id={loan_id} não encontrado para remoção")
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado")
    if not db_loan.return_date:
        raise HTTPException(status_code=400, detail="Não é possível remover um empréstimo em andamento. Realize a devolução primeiro.")
    db.delete(db_loan)
    db.commit()
    logger.info(f"Empréstimo id={loan_id} removido")
    return {"detail": "Empréstimo removido"}

def return_loan(db: Session, loan_id: int):
    logger.info(f"Tentando registrar devolução do empréstimo id={loan_id}")
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id, models.Loan.return_date == None).first()
    if not db_loan:
        logger.error(f"Empréstimo id={loan_id} não encontrado ou já devolvido")
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado ou já devolvido.")

    db_loan.return_date = date.today()
    logger.info(f"Empréstimo id={loan_id} devolvido em {db_loan.return_date}")

    if db_loan.return_date > db_loan.due_date:
        overdue_days = (db_loan.return_date - db_loan.due_date).days
        db_loan.fine = overdue_days * 2.00 # R$ 2,00 por dia de atraso
        logger.info(f"Empréstimo id={loan_id} está atrasado {overdue_days} dias. Multa aplicada: R${db_loan.fine:.2f}")

    db.commit()
    db.refresh(db_loan)
    return db_loan

def undo_loan_return(db: Session, loan_id: int):
    logger.info(f"Tentando desfazer devolução do empréstimo id={loan_id}")
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not db_loan:
        logger.error(f"Empréstimo id={loan_id} não encontrado")
        raise HTTPException(status_code=404, detail="Empréstimo não encontrado.")
    
    if db_loan.return_date is None:
        logger.error(f"Empréstimo id={loan_id} não está devolvido.")
        raise HTTPException(status_code=400, detail="Este empréstimo não está marcado como devolvido.")

    if not check_book_availability(db, db_loan.book_id):
        logger.error(f"Livro id={db_loan.book_id} não disponível para um novo empréstimo")
        raise HTTPException(status_code=400, detail="A devolução não pode ser desfeita pois o livro não está mais disponível (todos as cópias foram emprestadas).")

    db_loan.return_date = None
    db_loan.fine = 0.0
    db.commit()
    db.refresh(db_loan)
    logger.info(f"Devolução do empréstimo id={loan_id} desfeita com sucesso")
    return db_loan

def get_user_loans(db: Session, user_id: int):
    logger.info(f"Listando empréstimos do usuário id={user_id}")
    return db.query(models.Loan).filter(models.Loan.user_id == user_id).all()