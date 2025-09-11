# Personal Budget App Backend

A secure, lightweight FastAPI backend for personal finance budgeting, supporting:

- User registration/login with JWT authentication
- SQLite database (easily swappable for PostgreSQL)
- Field-level encryption of sensitive data (Fernet)
- Users, budgets, categories, transactions, and budget sharing
- Secure-by-default: password hashing, JWT secrets, encrypted fields

## For development

Reference repository: https://github.com/fastapi/full-stack-fastapi-template/tree/master

## Folder Structure

```plain_text
app/
  ├── main.py
  ├── database.py
  ├── models/
  ├── schemas/
  ├── crud/
  ├── routes/
  └── utils/
```

## Setup

1. Copy `.env.example` to `.env` and fill in secrets.
2. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Run the app:

   ```sh
   uvicorn app.main:app --reload
   ```

## API Endpoints

- `/api/auth/register` — Register user
- `/api/auth/login` — Login user (returns JWT)
- `/api/users/me` — Get current user
- `/api/users/` — CRUD users

## Docker

Build and run with Docker:

```sh
docker build -t budget-app .
docker run -p 8000:8000 --env-file .env budget-app
```

## Running Tests

To run the backend test suite:

```sh
PYTHONPATH=. pytest
```

This will execute all tests in the `tests/` directory using your current environment and database. For a clean test run, ensure your virtual environment is activated and dependencies are installed.

## API Documentation

When the backend server is running, interactive API documentation is automatically generated and available via Swagger UI. To access it, open your browser and navigate to:

- `http://localhost:8000/docs` for Swagger UI
- `http://localhost:8000/openapi.json` for the raw OpenAPI specification

These endpoints allow you to explore and test your API interactively.

## License

MIT
