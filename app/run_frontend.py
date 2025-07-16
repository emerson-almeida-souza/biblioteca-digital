from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import services, schemas, models
from .database import get_db, engine
import logging
from urllib.parse import urlencode

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("frontend")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, success: str = None, error: str = None):
    logger.info("Acessando página inicial")
    return templates.TemplateResponse("index.html", {"request": request, "success": success, "error": error})

@app.get("/users", response_class=HTMLResponse)
async def users(request: Request, db: Session = Depends(get_db), success: str = None, error: str = None):
    logger.info("Listando usuários")
    users_list = services.get_users(db)
    return templates.TemplateResponse("users.html", {"request": request, "users": users_list, "success": success, "error": error})

@app.get("/books", response_class=HTMLResponse)
async def books(request: Request, db: Session = Depends(get_db), success: str = None, error: str = None):
    logger.info("Listando livros")
    books_list = services.get_books(db)
    return templates.TemplateResponse("books.html", {"request": request, "books": books_list, "success": success, "error": error})

@app.get("/users/new", response_class=HTMLResponse)
async def new_user_form(request: Request):
    return templates.TemplateResponse("user_form.html", {"request": request, "user": None, "error": None})

@app.post("/users/new", response_class=HTMLResponse)
async def create_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Criando usuário: {name}, {email}")
        user_data = schemas.UserCreate(name=name, email=email)
        services.create_user(db, user_data)
        success_message = urlencode({"success": "Usuário criado com sucesso!"})
        return RedirectResponse(f"/users?{success_message}", status_code=303)
    except HTTPException as e:
        logger.error(f"Erro ao criar usuário: {e.detail}")
        return templates.TemplateResponse("user_form.html", {"request": request, "user": None, "error": e.detail})

@app.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_form(request: Request, user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Editando usuário id={user_id}")
    user = services.get_user(db, user_id)
    return templates.TemplateResponse("user_form.html", {"request": request, "user": user, "error": None})

@app.post("/users/{user_id}/edit", response_class=HTMLResponse)
async def update_user(
    request: Request,
    user_id: int,
    name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Atualizando usuário id={user_id}")
        user_data = schemas.UserCreate(name=name, email=email)
        services.update_user(db, user_id, user_data)
        success_message = urlencode({"success": "Usuário atualizado com sucesso!"})
        return RedirectResponse(f"/users?{success_message}", status_code=303)
    except HTTPException as e:
        logger.error(f"Erro ao atualizar usuário: {e.detail}")
        user = {"id": user_id, "name": name, "email": email} # Re-populate form with submitted data
        return templates.TemplateResponse("user_form.html", {"request": request, "user": user, "error": e.detail})

@app.post("/users/{user_id}/delete", response_class=HTMLResponse)
async def delete_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Removendo usuário id={user_id}")
        services.delete_user(db, user_id)
        success_message = urlencode({"success": "Usuário removido com sucesso!"})
        return RedirectResponse(f"/users?{success_message}", status_code=303)
    except HTTPException as e:
        logger.error(f"Erro ao remover usuário: {e.detail}")
        error_message = urlencode({"error": e.detail})
        return RedirectResponse(f"/users?{error_message}", status_code=303)


@app.get("/loans", response_class=HTMLResponse)
async def loans(request: Request, db: Session = Depends(get_db), success: str = None, error: str = None):
    logger.info("Listando empréstimos")
    loans_list = services.get_loans(db)
    return templates.TemplateResponse("loans.html", {"request": request, "loans": loans_list, "success": success, "error": error})

@app.get("/loans/new", response_class=HTMLResponse)
async def new_loan_form(request: Request, db: Session = Depends(get_db)):
    logger.info("Exibindo formulário de novo empréstimo")
    users = services.get_users(db)
    books = services.get_books(db)
    return templates.TemplateResponse("loan_form.html", {
        "request": request, "loan": None, "users": users, "books": books, "error": None
    })

@app.post("/loans/new", response_class=HTMLResponse)
async def create_loan(
    request: Request,
    user_id: int = Form(...),
    book_id: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Criando empréstimo: user_id={user_id}, book_id={book_id}")
        loan_data = schemas.LoanCreate(user_id=user_id, book_id=book_id)
        services.create_loan(db, loan_data)
        success_message = urlencode({"success": "Empréstimo realizado com sucesso!"})
        return RedirectResponse(f"/loans?{success_message}", status_code=303)
    except HTTPException as e:
        logger.error(f"Erro ao criar empréstimo: {e.detail}")
        users = services.get_users(db)
        books = services.get_books(db)
        return templates.TemplateResponse("loan_form.html", {
            "request": request, "loan": None, "users": users, "books": books, "error": e.detail
        })

@app.get("/loans/{loan_id}/edit", response_class=HTMLResponse)
async def edit_loan_form(request: Request, loan_id: int, db: Session = Depends(get_db)):
    logger.info(f"Editando empréstimo id={loan_id}")
    loan = services.get_loan(db, loan_id)
    users = services.get_users(db)
    books = services.get_books(db)
    error = None if loan else "Empréstimo não encontrado."
    if not loan:
        logger.error(f"Empréstimo id={loan_id} não encontrado")
    return templates.TemplateResponse("loan_form.html", {
        "request": request, "loan": loan, "users": users, "books": books, "error": error
    })

@app.post("/loans/{loan_id}/edit", response_class=HTMLResponse)
async def update_loan(
    request: Request,
    loan_id: int,
    user_id: int = Form(...),
    book_id: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Atualizando empréstimo id={loan_id}")
        loan_data = schemas.LoanCreate(user_id=user_id, book_id=book_id)
        services.update_loan(db, loan_id, loan_data)
        success_message = urlencode({"success": "Empréstimo atualizado com sucesso!"})
        return RedirectResponse(f"/loans?{success_message}", status_code=303)
    except HTTPException as e:
        logger.error(f"Erro ao atualizar empréstimo: {e.detail}")
        loan = services.get_loan(db, loan_id)
        users = services.get_users(db)
        books = services.get_books(db)
        return templates.TemplateResponse("loan_form.html", {
            "request": request, "loan": loan, "users": users, "books": books, "error": e.detail
        })

@app.post("/loans/{loan_id}/delete", response_class=HTMLResponse)
async def delete_loan(request: Request, loan_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Removendo empréstimo id={loan_id}")
        services.delete_loan(db, loan_id)
        success_message = urlencode({"success": "Empréstimo removido com sucesso!"})
        return RedirectResponse(f"/loans?{success_message}", status_code=303)
    except HTTPException as e:
        logger.error(f"Erro ao remover empréstimo: {e.detail}")
        error_message = urlencode({"error": e.detail})
        return RedirectResponse(f"/loans?{error_message}", status_code=303)

@app.post("/loans/{loan_id}/return", response_class=HTMLResponse)
async def return_loan(request: Request, loan_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Devolvendo empréstimo id={loan_id}")
        services.return_loan(db, loan_id)
        success_message = urlencode({"success": "Devolução registrada com sucesso!"})
        return RedirectResponse(f"/loans?{success_message}", status_code=303)
    except HTTPException as e:
        logger.error(f"Erro ao devolver empréstimo: {e.detail}")
        error_message = urlencode({"error": e.detail})
        return RedirectResponse(f"/loans?{error_message}", status_code=303)

@app.get("/books/new", response_class=HTMLResponse)
async def new_book_form(request: Request):
    return templates.TemplateResponse("book_form.html", {"request": request, "book": None, "error": None})

@app.post("/books/new", response_class=HTMLResponse)
async def create_book(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    quantity: int = Form(1),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Criando livro: {title}")
        book_data = schemas.BookCreate(title=title, author=author, quantity=quantity)
        services.create_book(db, book_data)
        success_message = urlencode({"success": "Livro criado com sucesso!"})
        return RedirectResponse(f"/books?{success_message}", status_code=303)
    except HTTPException as e:
        logger.error(f"Erro ao criar livro: {e.detail}")
        return templates.TemplateResponse("book_form.html", {"request": request, "book": None, "error": e.detail})

@app.get("/books/{book_id}/edit", response_class=HTMLResponse)
async def edit_book_form(request: Request, book_id: int, db: Session = Depends(get_db)):
    logger.info(f"Editando livro id={book_id}")
    book = services.get_book(db, book_id)
    return templates.TemplateResponse("book_form.html", {"request": request, "book": book, "error": None})

@app.post("/books/{book_id}/edit", response_class=HTMLResponse)
async def update_book(
    request: Request,
    book_id: int,
    title: str = Form(...),
    author: str = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Atualizando livro id={book_id}")
        book_data = schemas.BookCreate(title=title, author=author, quantity=quantity)
        services.update_book(db, book_id, book_data)
        success_message = urlencode({"success": "Livro atualizado com sucesso!"})
        return RedirectResponse(f"/books?{success_message}", status_code=303)
    except HTTPException as e:
        logger.error(f"Erro ao atualizar livro: {e.detail}")
        book = {"id": book_id, "title": title, "author": author, "quantity": quantity}
        return templates.TemplateResponse("book_form.html", {"request": request, "book": book, "error": e.detail})

@app.post("/books/{book_id}/delete", response_class=HTMLResponse)
async def delete_book(request: Request, book_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Removendo livro id={book_id}")
        services.delete_book(db, book_id)
        success_message = urlencode({"success": "Livro removido com sucesso!"})
        return RedirectResponse(f"/books?{success_message}", status_code=303)
    except HTTPException as e:
        logger.error(f"Erro ao remover livro: {e.detail}")
        error_message = urlencode({"error": e.detail})
        return RedirectResponse(f"/books?{error_message}", status_code=303)

@app.post("/loans/{loan_id}/undo-return", response_class=HTMLResponse)
async def undo_loan_return(request: Request, loan_id: int, db: Session = Depends(get_db)):
    logger.info(f"Desfazendo devolução do empréstimo id={loan_id}")
    try:
        services.undo_loan_return(db, loan_id)
        success_message = urlencode({"success": "Devolução desfeita com sucesso!"})
        return RedirectResponse(f"/loans?{success_message}", status_code=303)
    except HTTPException as e:
        logger.error(f"Erro ao desfazer devolução: {e.detail}")
        error_message = urlencode({"error": e.detail})
        return RedirectResponse(f"/loans?{error_message}", status_code=303)