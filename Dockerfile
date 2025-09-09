# --- STAGE 1: The Builder Stage ---
# Installs and then strips the virtual environment to be as small as possible.
FROM python:3.11.9-slim AS builder

WORKDIR /app

# Combine system dependency installation and cleanup in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create and set up the virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy requirements file
COPY requirements_docker.txt .

# --- The Definitive PyTorch Installation Fix ---
# 1. Install torch by itself from the CPU index, ignoring its dependencies.
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu torch --no-deps

# 2. Install the rest of the requirements. Pip will see torch is already installed.
RUN pip install --no-cache-dir -r requirements_docker.txt

# --- Safe Cleanup ---
# We are removing tests and caches, but NOT stripping the binaries.
RUN find /app/venv -type d -name "tests" -exec rm -rf {} + && \
    find /app/venv -type d -name "__pycache__" -exec rm -rf {} + && \
    find /app/venv -type f -name "*.pyc" -delete && \
    rm -rf /root/.cache/pip


# --- STAGE 2: The Final Runtime Stage ---
# Starts fresh and copies only the essential, cleaned components.
FROM python:3.11.9-slim

WORKDIR /app

# Copy the entire, cleaned virtual environment from the builder stage.
COPY --from=builder /app/venv /app/venv

# Copy your application code and your AI models.
COPY ./src/main.py ./src/main.py
COPY ./models ./models

# Set the PATH to use the Python executable from our virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Expose the port the container will listen on
EXPOSE 8080

# The command to run when the container starts
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]

