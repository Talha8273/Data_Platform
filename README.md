# Containerized Data Platform Lab 

A production-ready, 3-tier data platform built with Docker Compose, featuring an isolated network architecture and SRE best practices.

## Architecture & Core Components
* **Networking & Security:** Nginx Reverse Proxy managing external traffic across a 3-tier isolated bridge network.
* **Asynchronous Messaging:** Apache Kafka message broker ensuring decoupled service communication.
* **Orchestration & ETL:** Apache Airflow managing data pipelines to extract, clean, and load data into the Data Mart.
* **Database:** PostgreSQL for structured data storage with Docker Volume persistence.
* **Observability:** ELK Stack and Grafana dashboards for real-time traffic monitoring and system health metrics.

## Getting Started

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/Talha8273/Data_Platform.git](https://github.com/Talha8273/Data_Platform.git)
   cd Data_Platform
