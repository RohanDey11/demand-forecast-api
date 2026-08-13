FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc g++ curl python3-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --upgrade pip wheel setuptools
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m cmdstanpy.install_cmdstan --dir /opt --overwrite && ln -s /opt/cmdstan-* /opt/cmdstan

FROM python:3.11-slim
COPY --from=builder /opt /opt
ENV PATH="/opt/venv/bin:$PATH"
ENV CMDSTAN=/opt/cmdstan
WORKDIR /app
COPY . .
EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
