# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc libc-dev python3-dev \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set .venv in PATH for all commands
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode & force copy mode (for mounted volumes)
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy


# --- Dependency layer (cacheable without BuildKit) ---
# Copy only files needed to resolve dependencies
COPY pyproject.toml uv.lock /app/

# Install dependencies into the project venv (no dev deps, don't install project yet)
RUN uv sync --locked --no-install-project --no-dev

# --- Application layer ---
# Now copy the rest of the application
COPY . /app

# Ensure venv is up to date (installs the project itself)
RUN uv sync --locked --no-dev

# Install dependencies using BuildKit mounts (efficient caching)
#RUN --mount=type=cache,target=/root/.cache/uv \
#    --mount=type=bind,source=uv.lock,target=uv.lock \
#    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
#    uv sync --locked --no-install-project --no-dev

# Copy the rest of the application
#COPY . /app
#RUN --mount=type=cache,target=/root/.cache/uv \
#    uv sync --locked --no-dev

# Expose app port
EXPOSE 8002

# Default run command
CMD ["uv", "run", "python", "main.py"]
