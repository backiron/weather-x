FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY examples ./examples
COPY web ./web
RUN pip install --no-cache-dir .

EXPOSE 8080
CMD ["weatherx", "serve", "--config", "examples/network.example.json", "--observations", "examples/observations.example.json", "--as-of", "2025-07-15T18:00:00Z", "--host", "0.0.0.0", "--port", "8080"]
