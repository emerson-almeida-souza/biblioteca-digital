# Sistema de Gerenciamento de Biblioteca Digital

API REST em Python para gerenciar uma biblioteca digital, permitindo o cadastro de livros, autores e o controle do fluxo de empréstimos.

## Decisões Arquiteturais

*   **Framework:** **FastAPI** foi escolhido por sua alta performance, sintaxe moderna baseada em type hints do Python, e pela geração automática de documentação interativa (Swagger/OpenAPI), o que acelera o desenvolvimento e os testes.
*   **Banco de Dados:** **SQLite** foi utilizado para simplificar a configuração e a portabilidade do projeto, não exigindo um servidor de banco de dados separado. A interação com o banco é feita através do **SQLAlchemy ORM**, que abstrai as queries SQL e facilita a manutenção.
*   **Estrutura do Projeto:** O código foi organizado seguindo o princípio da **Separação de Responsabilidades**:
    *   `main.py`: Ponto de entrada da aplicação.
    *   `database.py`: Configuração da conexão com o banco de dados.
    *   `models.py`: Definição das tabelas do banco de dados (Entidades).
    *   `schemas.py`: Validação dos dados de entrada e saída da API (Pydantic).
    *   `services.py`: Camada de serviço que contém toda a lógica de negócio.
    *   `routes.py`: Definição dos endpoints da API.
*   **Validação:** A validação de dados é feita de forma robusta pelo **Pydantic**, garantindo que os dados que chegam à aplicação estejam no formato correto.

## Funcionalidades Implementadas

### Gestão de Usuários
*   `POST /users/`: Cadastrar novo usuário.
*   `GET /users/`: Listar todos os usuários.
*   `GET /users/{user_id}`: Buscar usuário por ID.
*   `PUT /users/{user_id}`: Atualizar dados de um usuário.
*   `DELETE /users/{user_id}`: Remover usuário.
*   `GET /users/{user_id}/loans`: Listar todos os empréstimos (histórico) de um usuário.

### Catálogo de Livros
*   `POST /books/`: Cadastrar novo livro.
*   `GET /books/`: Listar todos os livros.
*   `GET /books/{book_id}`: Buscar livro por ID.
*   `PUT /books/{book_id}`: Atualizar dados de um livro.
*   `DELETE /books/{book_id}`: Remover livro.
*   `GET /books/{book_id}/availability`: Verificar se um livro está disponível para empréstimo.

### Sistema de Empréstimos
*   `POST /loans/`: Realizar um novo empréstimo.
*   `GET /loans/`: Listar todos os empréstimos.
*   `GET /loans/{loan_id}`: Buscar empréstimo por ID.
*   `PUT /loans/{loan_id}`: Atualizar dados de um empréstimo.
*   `DELETE /loans/{loan_id}`: Remover empréstimo.
*   `POST /loans/{loan_id}/return`: Processar a devolução de um livro com cálculo de multa.

### Regras de Negócio Implementadas
*   **Prazo de Empréstimo:** 14 dias.
*   **Multa por Atraso:** R$ 2,00 por dia de atraso.
*   **Limite de Empréstimos:** Um usuário pode ter no máximo 3 empréstimos ativos simultaneamente.

## Frontend

O projeto inclui um frontend simples feito com FastAPI + Jinja2, que permite realizar todas as operações de CRUD para usuários, livros e empréstimos via páginas HTML.

### Funcionalidades do Frontend

* Listar, criar, editar e remover usuários.
* Listar, criar, editar e remover livros.
* Listar, criar, editar e remover empréstimos.
* Navegação fácil entre as entidades.
* Formulários para cadastro e edição.

## Como Instalar e Executar a API

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/emerson-almeida-souza/biblioteca-digital.git
    cd biblioteca-digital
    ```

2.  **Crie um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a API (modo padrão):**
    ```bash
    uvicorn app.main:app --reload
    ```

5.  **Execute somente a API (sem frontend):**
    ```bash
    uvicorn app.run_api_only:app --reload
    ```

6.  **Acesse a documentação interativa:**
    Abra seu navegador e acesse [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## Exemplos de Uso da API
Você pode usar a documentação interativa (Swagger) para testar os endpoints.
