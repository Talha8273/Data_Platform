# Containerized Data Platform Lab 

Bu proje, yerel ortamda (Ubuntu) Docker Compose ile inşa edilmiş, 3 katmanlı (frontend, backend, data) izole ağ mimarisine sahip bir veri platformu laboratuvarıdır.

## Temel Bileşenler ve Mimari
* **Ağ ve Güvenlik:** Dış trafiği yöneten Nginx Reverse Proxy ve 3 katmanlı izole sanal ağ (bridge network) yapılandırması.
* **Asenkron Veri Akışı:** Uygulama bağımlılıklarını (tight-coupling) ortadan kaldıran Apache Kafka (Redpanda) mesaj kuyruğu.
* **Orkestrasyon ve ETL:** Ham veriyi işleyip temizleyerek Data Mart'a aktaran Apache Airflow (Python DAGs) görevleri.
* **Veritabanı:** Yapılandırılmış veriler için PostgreSQL (Docker Volume ile veri kalıcılığı sağlanmıştır).
* **Gözlemlenebilirlik (SRE):** Sistem sağlığını ve gerçek zamanlı veri akışını izlemek için yapılandırılmış Grafana dashboardları ve ELK loglama altyapısı.

## Kurulum ve Çalıştırma (Getting Started)

Proje tamamen konteyner mimarisine (Docker Compose) dayandığı için ayağa kaldırmak oldukça basittir.

1. **Repoyu Klonlayın:**
   ```bash
   git clone [https://github.com/Talha8273/Data_Platform.git](https://github.com/Talha8273/Data_Platform.git)
   cd Data_Platform
