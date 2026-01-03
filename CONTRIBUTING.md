# Contributing

## Project Structure

Relevant top level directories are the following:

```
├── app/
├── migrations/
├── src/
└── tests/
```

* `app`: Contains the actual API implementation
* `migrations`: Alembic migrations for database changes
* `bin`: Directory containing random scripts that might be useful during development
* `test`: This one is self explanatory :D Pytests go in here

Inside the `app` directory the project is organised in a similar way as MVC would be, but in this case the concepts are a bit different:

```
app/
├── config.py
├── crud/
├── database.py
├── main.py
├── models.py
├── routes/
├── schemas/
└── utils/
```

Directories:

* `crud`: Inside this directory reside the files and functions that do operations on the data layer.
* `routes`: The API "shape" is defined through routers and routes. This allows isolation of API resources where each resource is configured by its own router.
* `schemas`: Pydantic schemas allow for data validation on API requests and responses.
* `utils`: Groups of functions that are useful for the whole project, examples are: messages, exceptions, time calculation operations, etc etc.

Files:

* `config.py`: File that reads environment variables and init
* `database.py`: Inits database and creates connections to the request sessions.
* `main.py`: API startup file
* `models.py`: Database Table Schemas are defined in this file. At this moment there's no strong reason to break this file into a directory.

## Data Model

erDiagram
    USER ||--o{ REFRESH_TOKEN : "has"
    USER ||--o{ ACCOUNT_MEMBERSHIP : "belongs to"
    ACCOUNT ||--o{ ACCOUNT_MEMBERSHIP : "has members"
    ACCOUNT ||--o{ TRANSACTION : "contains"
    ACCOUNT ||--o{ CATEGORY : "defines"
    CURRENCY ||--o{ ACCOUNT : "used by"
    CATEGORY ||--o{ TRANSACTION : "classifies"
    USER ||--o{ TRANSACTION : "manages"

    USER {
        int id PK
        string email
        string password_hash
        string name
        datetime created_at
        datetime updated_at
        bool is_active
        datetime last_login
    }

    ACCOUNT {
        int id PK
        string name
        string currency_code FK
        string description
    }

    TRANSACTION {
        int id PK
        int account_id FK
        int category_id FK
        int user_id FK
        string type "income/expense"
        float amount
        date date
    }

    CATEGORY {
        int id PK
        int account_id FK
        string name
        string type "income/expense"
        bool is_default
    }

    CURRENCY {
        string code PK
        string name
        string symbol
    }
