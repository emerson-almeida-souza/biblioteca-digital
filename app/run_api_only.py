from fastapi import FastAPI
from . import models, routes
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gerenciamento de Biblioteca Digital",
    description="API REST para gerenciar usuários, livros e empréstimos.",
    version="1.0.0"
)

app.include_router(routes.router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API da Biblioteca Digital"}