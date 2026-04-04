# Task API

A FastAPI backend project for managing tasks with JWT authentication, role-based access control (RBAC), task ownership enforcement, SQLite + SQLAlchemy persistence, Alembic migrations, Docker support, and automated API tests.

This project was built as part of my backend/cloud portfolio to strengthen practical skills in:

- FastAPI
- REST API design
- Authentication & authorization
- Database modeling
- Testing
- Containerization

---

## Features

- User registration and login
- JWT-based authentication
- Password hashing with bcrypt / passlib
- Role-based access control (`admin` and `user`)
- Task creation with ownership enforcement
- Users can only access and modify **their own tasks**
- Admin can view and manage **all tasks**
- Protected endpoints using FastAPI dependencies
- SQLite persistence with SQLAlchemy ORM
- Alembic database migrations
- Docker + Docker Compose support
- Automated API tests with `pytest`

---

## Tech Stack

- **Backend:** FastAPI
- **Language:** Python 3.12
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Authentication:** JWT (`python-jose`)
- **Password Hashing:** Passlib + bcrypt
- **Testing:** Pytest
- **Containerization:** Docker, Docker Compose

---

## Project Structure

```text
task-api/
├── main.py
├── auth.py
├── security.py
├── config.py
├── database.py
├── models.py
├── init_db.py
├── seed_users.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── alembic/
│   └── versions/
├── tests/
│   └── test_api.py
└── README.md
```

---

## API Endpoints

### Auth
- `POST /auth/register` — Register a new user
- `POST /auth/login` — Login and receive JWT token

### User
- `GET /me` — Get current authenticated user info

### Tasks
- `POST /tasks` — Create a new task
- `GET /tasks` — View tasks  
  - Regular users see **only their own tasks**
  - Admin users can see **all tasks**
- `PATCH /tasks/{task_id}` — Update a task  
  - Users can only update **their own** tasks
- `DELETE /tasks/{task_id}` — Delete a task  
  - Admin users can delete any task

---

## Security & Authorization Logic

This project demonstrates practical backend security patterns:

- Passwords are hashed before storage using **Passlib + bcrypt**
- Authentication is handled with **JWT access tokens**
- Protected routes use **FastAPI dependency injection**
- Role-based access control (RBAC) is enforced for `admin` and `user`
- Task ownership is enforced so users cannot modify another user's data

### Access Rules

#### User
- Can create tasks
- Can view only their own tasks
- Can update only their own tasks

#### Admin
- Can view all tasks
- Can manage all tasks
- Can delete any task

---

## Setup Instructions

### 1) Clone the repository

```bash
git clone https://github.com/elizabethkapusa-commits/task-api.git
cd task-api
```

### 2) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Create your `.env` file

Create a `.env` file in the project root and add:

```env
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./tasks.db
```

### 5) Initialize the database

```bash
python init_db.py
```

### 6) Run the API

```bash
uvicorn main:app --reload
```

Then open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Running Tests

This project includes automated API tests using **pytest** and **FastAPI TestClient**.

### Covered test scenarios
- User registration success
- Duplicate email registration rejection
- Login success
- Login failure with wrong password
- Auth-protected route enforcement
- Valid token authentication
- Task creation with ownership assignment
- User sees only their own tasks
- Admin sees all tasks
- User cannot access another user's task
- User can update their own task
- Admin can delete any task

Run tests with:

```bash
pytest -v
```

---

## Docker Support

### Build and run with Docker Compose

```bash
docker-compose up --build
```

This will start the FastAPI app inside a containerized environment.

---

## Why I Built This

I built this project as part of my backend/cloud engineering portfolio to strengthen hands-on skills in:

- secure API development
- authentication and authorization
- backend architecture
- database persistence
- automated testing
- containerized deployment

This project was designed to reflect practical backend engineering concepts commonly used in real-world systems.

---

## Future Improvements

Planned enhancements include:

- Add task due dates and status tracking
- Add refresh tokens and token revocation
- Add stricter user validation and profile management
- Add PostgreSQL support for production deployment
- Add CI/CD pipeline with GitHub Actions
- Add API documentation screenshots and usage examples

---

## Author

**Elizabeth Kapusa**  
MS Computer Engineering — UMass Dartmouth  
Backend / Cloud / Cybersecurity Portfolio Project
