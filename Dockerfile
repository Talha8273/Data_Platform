FROM python:3.9-slim
WORKDIR /app

# Önce gereksinimleri kopyala ve kur
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .

# Eksik derleyici ve MariaDB kütüphanelerini sisteme ekliyoruz
RUN apt-get update && apt-get install -y gcc libmariadb-dev pkg-config

RUN pip install --no-cache-dir -r requirements.txt
# ... (Kalan COPY komutların vb. aynen kalacak)
RUN pip install --no-cache-dir -r requirements.txt

# KRİTİK NOKTA: Klasördeki HER ŞEYİ Docker'ın içine kopyala
COPY . .

# Python'a "yazıları biriktirme, anında loglara bas" (-u) emrini veriyoruz
CMD ["python", "-u", "wanderlog-cache.py"]
