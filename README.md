<h1 align="center">🚀 FASTAPI-GENAI-BOILERPLATE</h1>

<p align="center">
  <i>Accelerate Innovation with Seamless AI-Driven APIs</i>
</p>

<p align="center">
  <img src="https://img.shields.io/github/last-commit/kevaldekivadiya2415/fastapi-genai-boilerplate?style=flat-square" />
  <img src="https://img.shields.io/github/languages/top/kevaldekivadiya2415/fastapi-genai-boilerplate?style=flat-square" />
  <img src="https://img.shields.io/github/languages/count/kevaldekivadiya2415/fastapi-genai-boilerplate?style=flat-square" />
  <img src=https://img.shields.io/badge/Python-3.9%20|%203.10%20|%203.11%20|%203.12%20|%203.13-blue?style=flat-square&logo=python />
</p>

---

<p align="center">
  <i>Powered by industry-grade technologies</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Markdown-000000?logo=markdown&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/TOML-9c4221?logo=toml&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/Pre--commit-orange?logo=pre-commit&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/Ruff-ccff00?logo=ruff&logoColor=black&style=flat-square" />
  <img src="https://img.shields.io/badge/GNU%20Bash-89e051?logo=gnubash&logoColor=white&style=flat-square" />
  <br/>
  <img src="https://img.shields.io/badge/Gunicorn-499848?logo=gunicorn&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/Docker-2496ed?logo=docker&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/uv-55BB8E?logo=python&logoColor=white&style=flat-square" />
</p>

---

## 📂 Table of Contents

- [Overview](#-overview)
- [Why Use This Boilerplate?](#-why-use-this-boilerplate)
- [Tech Stack](#-tech-stack)
- [Folder Structure](#-folder-structure)
- [Getting Started](#-getting-started)
- [Makefile Commands](#-makefile-commands)
- [Pre-commit Hooks](#-pre-commit-hooks)
- [Logging Middleware](#-logging-middleware)
- [Configuration](#-configuration)
- [Testing & Linting](#-testing--linting)
- [Deployment](#-deployment)
- [Monitoring with Prometheus & Grafana](#-monitoring-with-prometheus--grafana)
- [Docker Compose Setup](#-docker-compose-setup)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📘 Overview

**`fastapi-genai-boilerplate`** is a scalable and production-ready starter template for building FastAPI applications with modern DevOps practices. It supports:

- Environment-aware configuration
- Observability (logging, tracing)
- Security (rate limiting)
- Maintainability (typed config, modular API)
- CI-ready with code quality hooks and Docker support

---

## 🔍 Why Use This Boilerplate?

This template empowers you to build robust, scalable, and maintainable APIs with:

- 🌐 **Environment-aware Config**
  Seamlessly toggle between development and production settings for streamlined deployments.

- 🔎 **Request Tracing & Logging**
  Full observability using `loguru`, with structured logs, X-Request-ID headers, and performance metrics.

- 🛡️ **Rate Limiting Middleware**
  Protect endpoints from abuse using `slowapi`, based on identity/IP-based throttling.

- 🐳 **Dockerized Deployment**
  Container-first architecture with clean Dockerfile and production startup scripts using Gunicorn + Uvicorn.

- 🚀 **Production Server Setup**
  Efficient worker scaling with CPU-aware concurrency, custom Makefile for simplified operations.

- 🧩 **Modular API Architecture**
  Clean separation of concerns with well-defined folder structure, ready for features like chat, auth, etc.

---

## 🧪 Tech Stack

| Category         | Tools |
|------------------|-------|
| Core Framework   | [FastAPI](https://fastapi.tiangolo.com/) |
| ASGI Servers     | [Uvicorn](https://www.uvicorn.org/), [Gunicorn](https://gunicorn.org/) |
| Dependency Mgmt  | [UV](https://docs.astral.sh/uv/) |
| Configuration    | [Pydantic](https://pydantic.dev/) |
| Logging          | [Loguru](https://loguru.readthedocs.io/) |
| Rate Limiting    | [SlowAPI](https://slowapi.readthedocs.io/) |
| Linting/Checks   | [Ruff](https://beta.ruff.rs/), [Black](https://black.readthedocs.io/), [MyPy](https://mypy-lang.org/), [isort](https://pycqa.github.io/isort/) |
| CI & Hooks       | [pre-commit](https://pre-commit.com/) |
| Containerization | [Docker](https://www.docker.com/) |

---

## 🗂️ Folder Structure

```
fastapi_genai_boilerplate/
├── app/
│   ├── api/                     # API routes and handlers
│   ├── core/
│   │   ├── config.py            # App settings and environment config
│   │   └── middlewares/         # Logging, rate limit middleware
│   └── main.py                  # App bootstrap logic
├── tests/                       # Test cases
├── .env                         # Local environment variables
├── Dockerfile                   # Docker setup
├── Makefile                     # Developer shortcuts
├── pyproject.toml               # UV dependencies & configs
├── pre-commit-config.yaml       # Git hook configs
└── README.md                    # Project documentation
```

---

## ⚙️ Getting Started

### 1. Clone & Install Dependencies

```bash
# Clone the repository
git clone https://github.com/kevaldekivadiya2415/fastapi-genai-boilerplate
cd fastapi_genai_boilerplate

# Install uv via pip
pip3 install uv

# Optional: create and activate virtual environment (recommended)
uv venv
source .venv/bin/activate

# Sync dependencies from pyproject.toml and uv.lock
uv sync

# Start an interactive Python shell with uv
uv run main.py
```

### 2. Add a `.env` File

```env
LOG_LEVEL=DEBUG
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8002
WORKER_COUNT=4
```

---

## 🛠️ Makefile Commands

| Command                   | Description                            |
|---------------------------|----------------------------------------|
| `make run-dev`            | Start dev server with auto-reload      |
| `make run-prod`           | Start Gunicorn server with Uvicorn     |
| `make lint`               | Run `ruff` linter                      |
| `make typecheck`          | Run static type checks with MyPy       |
| `make format`             | Format using Black & isort             |
| `make docker-build`       | Build Docker image                     |
| `make docker-run`         | Run Docker container                   |
| `make pre-commit-install` | Install all Git pre-commit hooks       |

---

## ✅ Pre-commit Hooks

Enforce standards before every commit. Tools include:

- ✅ `ruff` for linting
- ✅ `black` for formatting
- ✅ `isort` for import order
- ✅ `mypy` for type checks

Install hooks:

```bash
make pre-commit-install
```

---

## 📊 Logging Middleware

Each request gets a unique ID:

- Injected via `X-Request-ID` header
- Auto-generated if missing
- Passed into log messages using `loguru`
- Added in response header for traceability

Ideal for debugging and log correlation across microservices.

---

## 🔧 Configuration

All environment values are type-safe using `pydantic.BaseSettings`.
Defaults can be overridden via `.env` file.

```python
class AppConfig(BaseSettings):
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "production"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
```

---

## 🧪 Testing & Linting

Run checks with:

```bash
make lint
make typecheck
make format
```

Use `pytest` (not included yet) for writing unit/integration tests inside `tests/`.

---

## 🚀 Deployment

### Docker Deployment:

```bash
make docker-build
make docker-run
```

Production uses:

- `Gunicorn` with `UvicornWorker`
- `.env` to control concurrency

---

## 📊 Monitoring with Prometheus & Grafana

This boilerplate includes built-in observability via the `prometheus-fastapi-instrumentator` library.

### 🔧 Metrics Endpoint

All FastAPI metrics (latency, requests, status codes, etc.) are exposed at:

```http://HOST:PORT/metrics```

---

## 🐳 Docker Compose Setup

A `docker-compose.yml` file is included to run the full observability stack:

* ✅ FastAPI App
* 📊 Prometheus (for metrics collection)
* 📈 Grafana (for dashboards)

### ▶️ Usage

Run everything with:

```bash
docker-compose up --build
```

### 📍 Port Mapping Overview

| Service    | URL                                            | Host Port | Container Port |
| ---------- | ---------------------------------------------- | --------- | -------------- |
| FastAPI    | [http://localhost:8002](http://localhost:8002) | `8002`    | `8002`         |
| Prometheus | [http://localhost:9090](http://localhost:9090) | `9090`    | `9090`         |
| Grafana    | [http://localhost:3000](http://localhost:3000) | `3000`    | `3000`         |

### 🔐 Grafana Credentials
By default, Grafana uses the following login credentials (configured via environment variables):

```
Username: admin
Password: supersecurepassword
```

You can modify these in the ```docker-compose.yml``` under the grafana service:
```
grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=supersecurepassword
```

### 🗂️ Prometheus Configuration

Make sure the following file exists:

```
docker/
└── prometheus/
    └── prometheus.yml
```

Example:

```yaml
# docker/prometheus/prometheus.yml

global:
  scrape_interval: 5s

scrape_configs:
  - job_name: 'fastapi'
    metrics_path: /metrics
    static_configs:
      - targets: ['fastapi:8002']
```

> 🔁 Prometheus scrapes `/metrics` from FastAPI every 5 seconds.

### ⛔ To Stop Everything

```bash
docker-compose down
```

---

## 🤝 Contributing

You're welcome to contribute! Please:

1. Fork this repo
2. Create a new branch
3. Ensure pre-commit and linters pass
4. Open a PR with a clear description

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](./LICENSE) file for details.
