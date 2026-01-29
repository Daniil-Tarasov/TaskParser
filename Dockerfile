FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.8.3
WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-dev --no-root

COPY src/ ./src/
COPY run_worker.py .

ENV PATH="/root/.local/bin:${PATH}"

CMD ["python", "run_worker.py"]