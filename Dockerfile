# ===============================
# 🔹 [1/7] Base Image & Env Setup
# ===============================
FROM python:3.12-slim-bullseye AS base

RUN echo "🚀 [1/7] Starting Docker image build..."

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ===============================
# 🔹 [2/7] Install System Dependencies & uv via pip
# ===============================
FROM base AS deps

RUN echo "📦 [2/7] Installing system dependencies and uv via pip..."

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    python3-dev \
    libc-dev \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip uv

# ===============================
# 🔹 [3/7] Copy uv Config
# ===============================
COPY pyproject.toml uv.lock* /app/

RUN echo "📄 [3/7] Copied uv configuration files..."

# ===============================
# 🔹 [4/7] Install Python Dependencies
# ===============================
FROM deps AS builder

COPY pyproject.toml uv.lock* /app/

RUN echo "📦 [4/7] Installing Python dependencies (main group only)..."

RUN uv sync --locked --no-install-project --no-dev

# ===============================
# 🔹 [5/7] Final Image Build
# ===============================
FROM base AS final

RUN echo "🏗️ [5/7] Assembling final application image..."

RUN pip install uv

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

CMD ["uv", "run", "python", "main.py"]
