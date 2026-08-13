FROM python:3.8-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip wheel setuptools
RUN pip install --no-cache-dir Cython==0.29.36 numpy==1.21.6
RUN pip install --no-cache-dir pystan==2.19.1.1
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
