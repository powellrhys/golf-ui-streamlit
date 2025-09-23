# Use a lightweight Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_CONFIG_DIR=/app/.streamlit \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Set working directory
WORKDIR /app

# Install system dependencies (git needed for custom packages)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --upgrade pip poetry

# Copy project files
COPY pyproject.toml poetry.lock* /app/
COPY frontend/entrypoint.sh /app/entrypoint.sh
COPY . /app

# Enable execution of the entrypoint script
RUN chmod +x /app/entrypoint.sh

# Install only frontend extras and core dependencies
RUN poetry install --only main --extras "frontend"

# Expose Streamlit port
ENV PORT=8501
EXPOSE 8501

# Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
