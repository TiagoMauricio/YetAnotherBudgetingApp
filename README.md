# YABA - Yet Another Budgeting App

A self hostable API for personal expense tracking built with [FastAPI](https://github.com/fastapi/fastapi)

## Context

There are many great opensource options for personal finance tracking. However, I felt like they were either too feature full or lacking particular features I was looking for.
YABA strives to achieve a middle ground where it can track your personal finances and share the progress with your significant other so that multiple people can register expenses on the same account.

:warning:**WARNING**: This API is still in early stages of development.

## Technology

I chose FastAPI because python was my first language and since I'm not a backend engineer, I prefered to ignore the barrier of a new language to make it easier to progress.
I've built a couple tools using Django and worked in a professional setting with Flask, so I wanted to learn a new framework and FastAPI seemed promissing.

## Contributing

If you wish to contribute, please reach out:
- Fork the project and create a PR.
- Create an issue on this repo.
- I have a Discord for my projects, I can add you to it.

This is my first opensource project that I am looking for contributions for and I am still learning how to manage this :blush:

## Setup

1. Copy `.env.example` to `.env` and fill in secrets.
2. Install dependencies:

```sh
make venv
make install
```

3. Run the app locally:

```sh
uvicorn app.main:app --reload
```

## Docker (WIP)

Build and run with Docker:

```sh
docker build -t budget-app .
docker run -p 8000:8000 --env-file .env budget-app
```

## Running Tests

To run the test suite:

```sh
make test
```

This will execute all tests in the `tests/` directory using your current environment and database. For a clean test run, ensure your virtual environment is activated and dependencies are installed.

## License

This project is licensed under the terms of the MIT license.
