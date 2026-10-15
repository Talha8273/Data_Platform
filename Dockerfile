FROM python:3.9-slim
WORKDIR /app

FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .

RUN apt-get update && apt-get install -y gcc libmariadb-dev pkg-config

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "wanderlog-cache.py"]
