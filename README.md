# Çok Dillilik İçeren Veri Platformu ve Merkezi Gözlemlenebilirlik Mimarisi (Polyglot Data Platform)

Bu depo; kurumsal düzeydeki veri mühendisliği iş akışlarını, otonom ETL süreçlerini ve merkezi log yönetimini simüle etmek amacıyla tasarlanmış, Docker tabanlı kapsamlı bir altyapı ve laboratuvar ortamıdır.

---

## 🏗️ Mimari Genel Bakış

Sistem, farklı veri saklama paradigmalarını ayrıştırırken bir yandan merkezi izleme ve otonom boru hattı orkestrasyonunu koruyacak şekilde WSL2 üzerinde Docker Compose ile çalışmaktadır.

*   **İlişkisel Veritabanı (OLTP):** MariaDB & PostgreSQL (Yapısal işlemsel veriler ve hata simülasyonları)
*   **NoSQL / Belge Veritabanı:** MongoDB (Yapılandırılmamış ve yarı yapılandırılmış veri depolama)
*   **Bellek İçi / Önbellek (In-Memory):** Redis (Geçici veriler, oturum önbellekleme ve uçucu durum yönetimi)
*   **İş Akışı Orkestrasyonu:** Apache Airflow (Redis, MariaDB ve PostgreSQL arasında veri taşıyan otonom, zamanlanmış ETL boru hatları)
*   **Merkezi Gözlemlenebilirlik (ELK Stack):** Elasticsearch, Kibana ve Filebeat (Konteyner log toplama, özel log ayrıştırma ve gerçek zamanlı görselleştirme)

---

## 🛠️ Karşılaşılan Kritik Teknik Zorluklar ve Çözümleri

Bu altyapının kurulumu sırasında, kurumsal düzeyde karşılaşlabilecek birkaç platform kriz başarıyla çözülmüştür:

1.  **WSL2 ve Systemd Log Sürücüsü Kısıtlamaları:** Kısıtlayıcı systemd soket/journald izinleri aşılmış; `journald` girdisinden Docker'ın yerel konteyner log sürücüsüne (`/var/lib/docker/containers/*/*.log`) geçiş yapılarak güvenilir ve izin hatasız bir log toplama süreci sağlanmıştır.
2.  **Filebeat Güvenliği ve Sahiplik (`EPERM`):** Elastik bileşenlerinin sıkı çalışma zamanı güvenlik gereksinimlerini karşılamak amacıyla Filebeat yapılandırma dosyaları için sıkı kök sahipliği (`chown root:root`) ayarlanmış ve ana makine-konteyner bağlama (mount) izinleri koordine edilmiştir.
3.  **Platformlar Arası YAML Doğrulaması:** Kesintisiz servis orkestrasyonu ve otomatik kurtarma mekanizmasını garanti etmek için karmaşık çoklu konteyner `docker-compose.yml` bildirimlerindeki iç içe geçmiş sözdizimi (syntax) hataları giderilmiştir.

---

## 🚀 Başlangıç Rehberi

1. **Repoyu Klonlayın:**
   ```bash
   git clone [https://github.com/Talha8273/Data_Platform.git](https://github.com/Talha8273/Data_Platform.git)
   cd Data_Platform
