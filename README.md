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

```bash
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
├── .env
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── alembic/
│   └── versions/
├── tests/
│   └── test_api.py
└── README.md
