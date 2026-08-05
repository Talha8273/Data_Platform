# 1. Hangi işletim sistemi ve dili kullanacağız? (Temel imaj)
FROM python:3.9-slim

# 2. Konteyner içinde çalışacağımız klasörü belirliyoruz
WORKDIR /app

# 3. İhtiyacımız olan kütüphaneleri (pip paketlerini) kuruyoruz
RUN pip install requests redis psycopg2-binary

# 4. Kendi yazdığımız kodu konteynerin içine kopyalıyoruz
COPY wanderlog_fetcher.py .

# 5. Konteyner ayağa kalktığında hangi komut çalışsın?
CMD ["python", "wanderlog_fetcher.py"]
