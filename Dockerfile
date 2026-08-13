FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV CMDSTAN=/opt/cmdstan
RUN mkdir -p /opt && \
    curl -L https://github.com/stan-dev/cmdstan/releases/download/v2.33.1/cmdstan-2.33.1.tar.gz -o /tmp/cmdstan.tar.gz && \
    tar -xzf /tmp/cmdstan.tar.gz -C /opt && \
    mv /opt/cmdstan-2.33.1 /opt/cmdstan && \
    rm /tmp/cmdstan.tar.gz

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
