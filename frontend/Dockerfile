# Define base python image
FROM python:3.12-slim

# Define container environmental variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_CONFIG_DIR=/app/.streamlit

# Define container working directory
WORKDIR /app

# Install git to enable import of custom package
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy codebase into container
COPY . /app
COPY frontend/entrypoint.sh /app/entrypoint.sh

# Enable script execution within container
RUN chmod +x /app/entrypoint.sh

# Install project requirements
RUN pip install --upgrade pip && pip install -r requirements.txt

# Define application ports
ENV PORT=8501
EXPOSE 8501

# Define container entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
