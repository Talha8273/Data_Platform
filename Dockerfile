FROM python:3.9-slim
WORKDIR /app

# Önce gereksinimleri kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# KRİTİK NOKTA: Klasördeki HER ŞEYİ Docker'ın içine kopyala
COPY . .

# Python'a "yazıları biriktirme, anında loglara bas" (-u) emrini veriyoruz
CMD ["python", "-u", "wanderlog-cache.py"]