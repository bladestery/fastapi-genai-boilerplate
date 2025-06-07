# fastapi\_boilerplate

**A production-ready FastAPI project template**
with structured configuration, request ID logging middleware, rate limiting, and code quality tooling using Poetry.

---

## Table of Contents

* [Project Overview](#project-overview)
* [Features](#features)
* [Tech Stack](#tech-stack)
* [Project Structure](#project-structure)
* [Getting Started](#getting-started)
* [Makefile Commands](#makefile-commands)
* [Pre-commit Hooks](#pre-commit-hooks)
* [Logging Middleware](#logging-middleware)
* [Configuration](#configuration)
* [Testing and Linting](#testing-and-linting)
* [Deployment](#deployment)
* [Contributing](#contributing)
* [License](#license)

---

## Project Overview

This project provides a FastAPI boilerplate with a strong focus on:

* Centralized and environment-aware application configuration using Pydantic `BaseSettings`.
* Middleware that attaches a unique request ID to each HTTP request, enhancing log traceability.
* Rate limiting using `slowapi` for protecting endpoints.
* Strict type checking and linting setup with MyPy, Ruff, Black, and isort.
* Pre-commit hooks automation for enforcing code quality before commits.
* Simple Makefile commands for easy development, testing, and deployment workflows.

---

## Features

* **AppConfig**: Typed environment-based config with defaults and `.env` support.
* **Logging Middleware**: Injects `X-Request-ID` header, tracked in logs via `loguru`.
* **Rate Limiting**: Integrated via `slowapi` middleware.
* **Code Quality**: Pre-commit configured with ruff, black, isort, mypy.
* **Deployment Ready**: Gunicorn support with Uvicorn workers.
* **Makefile**: Convenient commands to run, lint, format, and deploy the app.

---

## Tech Stack

* Python 3.12+
* [FastAPI](https://fastapi.tiangolo.com/)
* [Poetry](https://python-poetry.org/) for dependency and environment management
* [Uvicorn](https://www.uvicorn.org/) ASGI server for development
* [Gunicorn](https://gunicorn.org/) for production with Uvicorn workers
* [Pydantic](https://pydantic.dev/) for settings and validation
* [Loguru](https://loguru.readthedocs.io/) for structured logging
* [SlowAPI](https://slowapi.readthedocs.io/) for rate limiting
* [Ruff](https://beta.ruff.rs/) linter, [MyPy](https://mypy-lang.org/) type checker, [Black](https://black.readthedocs.io/) formatter, [isort](https://pycqa.github.io/isort/) import sorter
* [pre-commit](https://pre-commit.com/) for Git hooks automation

---

## Project Structure

```plaintext
fastapi_boilerplate/
├── app/
│   ├── api/                     # API routes and endpoint handlers
│   ├── core/                    # Config, middleware, logging utils
│   │   ├── config.py            # AppConfig with environment settings
│   │   ├── middlewares/         # Custom middleware (logging, rate limiting)
│   ├── main.py                  # FastAPI app initialization and startup
├── tests/                       # Unit and integration tests
├── .env                        # Environment variables
├── Dockerfile                  # Docker container setup
├── Makefile                   # Handy commands for dev and deployment
├── pyproject.toml              # Poetry dependencies and project metadata
├── pre-commit-config.yaml      # Git pre-commit hooks config
└── README.md                   # This documentation file
```

---

## Getting Started

### Prerequisites

* Python 3.12+ installed
* Poetry installed (`curl -sSL https://install.python-poetry.org | python3 -`)
* Docker (optional, for containerization)

### Setup

1. Clone the repo:

   ```bash
   git clone https://github.com/kevaldekivadiya2415/fastapi-boilerplate
   cd fastapi_boilerplate
   ```

2. Install dependencies with Poetry:

   ```bash
   poetry install
   ```

3. Activate virtual environment:

   ```bash
   poetry shell
   ```

4. Create a `.env` file at root (example):

   ```env
   LOG_LEVEL=DEBUG
   ENVIRONMENT=development
   HOST=0.0.0.0
   PORT=8002
   WORKER_COUNT=4
   ```

---

## Makefile Commands

Use the Makefile for common tasks:

| Command                   | Description                                                |
| ------------------------- | ---------------------------------------------------------- |
| `make run-dev`            | Run FastAPI with Uvicorn in development mode (auto-reload) |
| `make run-prod`           | Run with Gunicorn using Uvicorn workers (production)       |
| `make lint`               | Run ruff linter on app and tests                           |
| `make typecheck`          | Run MyPy static type checking                              |
| `make format`             | Format code using Black and sort imports with isort        |
| `make pre-commit-install` | Install Git pre-commit hooks                               |
| `make docker-build`       | Build the Docker image                                     |
| `make docker-run`         | Run the Docker container                                   |

---

## Pre-commit Hooks

This project uses **pre-commit** to run code quality checks before committing:

* Ruff for linting
* MyPy for type checks
* Black for formatting
* isort for import sorting

Install hooks:

```bash
make pre-commit-install
```

---

## Logging Middleware

The project includes a custom middleware that:

* Extracts or generates a unique `X-Request-ID` per incoming request.
* Injects this request ID into all log messages via `loguru`.
* Adds the request ID to the HTTP response headers for traceability.

This helps track individual requests across distributed services and logs.

---

## Configuration

Settings are managed via Pydantic’s `BaseSettings`:

* Defined in `app/core/config.py` with typed fields.
* Supports `.env` file with UTF-8 encoding.
* Configurable log level, host, port, environment, worker count, and app version.

---

## Testing and Linting

* Use **Ruff** to lint code: `make lint`
* Use **MyPy** for type checks: `make typecheck`
* Use **Black** and **isort** for formatting: `make format`

Add your tests under the `tests/` directory and run with your favorite test runner (e.g., `pytest`).

---

## Deployment

* Dockerize the app with included `Dockerfile`:

  ```bash
  make docker-build
  make docker-run
  ```

* Adjust worker count according to your CPU cores in `.env` or `AppConfig`.

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a new feature branch
3. Run all linters and type checks before committing
4. Submit a pull request with clear description

---

## License

© 2025 Keval Dekivadiya. All rights reserved.

This repository is private and proprietary.
Unauthorized copying, distribution, or use of the code or any part thereof is strictly prohibited without prior written permission from the author.
