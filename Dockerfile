# ===============================
# 🔹 [1/7] Base Image & Env Setup
# ===============================
FROM python:3.12-slim-bullseye AS base

RUN echo "🚀 [1/7] Starting Docker image build..."

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_HOME="/opt/poetry"

ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# ===============================
# 🔹 [2/7] Install System Dependencies & Poetry
# ===============================
FROM base AS deps

RUN echo "📦 [2/7] Installing system dependencies and Poetry..."

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
 && curl -sSL https://install.python-poetry.org | python3 - \
 && apt-get remove -y curl \
 && apt-get autoremove -y \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip and confirm Poetry install
RUN pip install --upgrade pip && poetry --version

# ===============================
# 🔹 [3/7] Copy Poetry Config
# ===============================
COPY pyproject.toml poetry.lock* /app/

RUN echo "📄 [3/7] Copied Poetry configuration files..."

# ===============================
# 🔹 [4/7] Install Python Dependencies
# ===============================
FROM deps AS builder

COPY pyproject.toml poetry.lock* /app/

RUN echo "📦 [4/7] Installing Python dependencies (main group only)..."

RUN poetry install --no-root --only main

# ===============================
# 🔹 [5/7] Final Image Build
# ===============================
FROM base AS final

RUN echo "🏗️ [5/7] Assembling final application image..."

COPY --from=deps $POETRY_HOME $POETRY_HOME
ENV PATH="$POETRY_HOME/bin:$PATH"

COPY --from=builder /app /app

# ===============================
# 🔹 [6/7] Copy Application Code
# ===============================
COPY . /app

RUN echo "📁 [6/7] Application code copied to image."

# ===============================
# 🔹 [7/7] Startup Config
# ===============================
EXPOSE 8002

RUN echo "✅ [7/7] Build complete. Ready to launch the app."

CMD ["poetry", "run", "python", "main.py"]
