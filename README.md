# Smart City Data Simulation and Processing Pipeline

## Project Overview

This project simulates and processes smart city data in real-time. It generates data for vehicles, GPS, traffic cameras, weather conditions, and emergency incidents. The data is streamed using Apache Kafka, processed with Apache Spark, and orchestrated using Docker Compose. The pipeline is designed to handle and analyze streaming data efficiently.

## Components

1. **Kafka Producer**: Simulates and sends data to Kafka topics.
2. **Spark Streaming Job**: Consumes and processes data from Kafka topics.
3. **Docker Compose**: Manages and orchestrates Kafka, Zookeeper, Spark, and Kafka Manager services.

## Project Setup

### Prerequisites

- **Docker**: Install Docker and Docker Compose. Follow the [official installation guide](https://docs.docker.com/get-docker/) for instructions.
- **Python**: Install Python 3.x and required libraries.
- **Apache Spark**: Ensure Apache Spark is installed and configured.

### Environment Variables

Set the following environment variables for Kafka configuration:

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka server address (default: `localhost:29092`)
- `VEHICLE_TOPIC`: Kafka topic for vehicle data (default: `vehicle_data`)
- `GPS_TOPIC`: Kafka topic for GPS data (default: `gps_data`)
- `TRAFFIC_TOPIC`: Kafka topic for traffic data (default: `traffic_data`)
- `WEATHER_TOPIC`: Kafka topic for weather data (default: `weather_data`)
- `EMERGENCY_TOPIC`: Kafka topic for emergency data (default: `emergency_data`)

### Docker Compose Setup

The `docker-compose.yml` file configures all necessary services for the project.

### Data Flow

Data Generation: The Kafka producer simulates data for vehicles, GPS, traffic cameras, weather conditions, and emergency incidents. The data is sent to Kafka topics.
Data Consumption: The Spark streaming job consumes data from Kafka topics, processes it, and stores it in Parquet files.
Service Management: Docker Compose orchestrates the Kafka, Zookeeper, Spark, and Kafka Manager services, ensuring they run and interact correctly.

![Screenshot 2024-08-09 103907](https://github.com/user-attachments/assets/fa061dce-8bef-46bb-90bd-8e2dcbda7b70)
