import os
import random
import uuid
import time
from datetime import datetime, timedelta
from confluent_kafka import Producer
import simplejson as json

# Constants for London and Birmingham coordinates
LONDON_COORDINATES = {"latitude": 51.5074, "longitude": -0.1278}
BIRMINGHAM_COORDINATES = {"latitude": 52.4862, "longitude": -1.8904}

# Calculate the movement increment for latitude and longitude
LATITUDE_INCREMENT = (BIRMINGHAM_COORDINATES['latitude'] - LONDON_COORDINATES['latitude']) / 100
LONGITUDE_INCREMENT = (BIRMINGHAM_COORDINATES['longitude'] - LONDON_COORDINATES['longitude']) / 100

# Environment variables for Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:29092')
VEHICLE_TOPIC = os.getenv('VEHICLE_TOPIC', 'vehicle_data')
GPS_TOPIC = os.getenv('GPS_TOPIC', 'gps_data')
TRAFFIC_TOPIC = os.getenv('TRAFFIC_TOPIC', 'traffic_data')
WEATHER_TOPIC = os.getenv('WEATHER_TOPIC', 'weather_data')
EMERGENCY_TOPIC = os.getenv('EMERGENCY_TOPIC', 'emergency_data')

# Seed random number generator for reproducibility
random.seed(42)
start_time = datetime.now()
start_location = LONDON_COORDINATES.copy()

def get_next_time():
    global start_time
    start_time += timedelta(seconds=random.randint(30, 60))  # Update frequency
    return start_time

def generate_gps_data(device_id, timestamp, vehicle_type='private'):
    return {
        'id': str(uuid.uuid4()),
        'deviceId': device_id,
        'timestamp': timestamp,
        'speed': random.uniform(0, 40),
        'direction': 'North-East',
        'vehicleType': vehicle_type
    }

def generate_traffic_camera_data(device_id, timestamp, location, camera_id):
    return {
        'id': str(uuid.uuid4()),
        'deviceId': device_id,
        'cameraId': camera_id,
        'location': location,
        'timestamp': timestamp,
        'snapshot': 'Base64EncodedString'
    }

def generate_weather_data(device_id, timestamp, location):
    return {
        'id': str(uuid.uuid4()),
        'deviceId': device_id,
        'location': location,
        'timestamp': timestamp,
        'temperature': random.uniform(-5, 26),
        'weatherCondition': random.choice(['Sunny', 'Cloudy', 'Rain', 'Snow']),
        'precipitation': random.uniform(0, 25),
        'windSpeed': random.uniform(0, 100),
        'humidity': random.randint(0, 100),
        'airQualityIndex': random.uniform(0, 500)
    }

def generate_emergency_incident_data(device_id, timestamp, location):
    return {
        'id': str(uuid.uuid4()),
        'deviceId': device_id,
        'incidentId': str(uuid.uuid4()),
        'type': random.choice(['Accident', 'Fire', 'Medical', 'None']),
        'timestamp': timestamp,
        'location': location,
        'status': random.choice(['Active', 'Resolved']),
        'description': 'Description of the incident'
    }

def simulate_vehicle_movement():
    global start_location

    # Move toward Birmingham
    start_location['latitude'] += LATITUDE_INCREMENT
    start_location['longitude'] += LONGITUDE_INCREMENT

    # Add randomness to simulate actual road travel
    start_location['latitude'] += random.uniform(-0.0005, 0.0005)
    start_location['longitude'] += random.uniform(-0.0005, 0.0005)

    return start_location

def generate_vehicle_data(device_id):
    location = simulate_vehicle_movement()

    return {
        'id': str(uuid.uuid4()),
        'deviceId': device_id,
        'timestamp': get_next_time().isoformat(),
        'location': (location['latitude'], location['longitude']),
        'speed': random.uniform(10, 40),
        'direction': 'North-East',
        'make': 'BMW',
        'model': 'CS500',
        'year': 2024,
        'fuelType': 'Hybrid'
    }

def json_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def produce_data_to_kafka(producer, topic, data):
    try:
        producer.produce(
            topic,
            key=str(data['id']),
            value=json.dumps(data, default=json_serializer).encode('utf-8'),
            on_delivery=delivery_report,
        )
        producer.flush()
    except Exception as e:
        print(f'Error producing data to Kafka: {e}')

def simulate_journey(producer, device_id):
    while True:
        try:
            vehicle_data = generate_vehicle_data(device_id)
            gps_data = generate_gps_data(device_id, vehicle_data['timestamp'])
            traffic_camera_data = generate_traffic_camera_data(device_id, vehicle_data['timestamp'], vehicle_data['location'], 'Nikon-Cam123')
            weather_data = generate_weather_data(device_id, vehicle_data['timestamp'], vehicle_data['location'])
            emergency_incident_data = generate_emergency_incident_data(device_id, vehicle_data['timestamp'], vehicle_data['location'])

            if (vehicle_data['location'][0] >= BIRMINGHAM_COORDINATES['latitude'] and 
                vehicle_data['location'][1] <= BIRMINGHAM_COORDINATES['longitude']):
                print('Vehicle has reached Birmingham. Simulation ending...')
                break

            produce_data_to_kafka(producer, VEHICLE_TOPIC, vehicle_data)
            produce_data_to_kafka(producer, GPS_TOPIC, gps_data)
            produce_data_to_kafka(producer, TRAFFIC_TOPIC, traffic_camera_data)
            produce_data_to_kafka(producer, WEATHER_TOPIC, weather_data)
            produce_data_to_kafka(producer, EMERGENCY_TOPIC, emergency_incident_data)

            time.sleep(5)
        except Exception as e:
            print(f'Error during simulation: {e}')
            break

if __name__ == "__main__":
    producer_config = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'error_cb': lambda err: print(f'Kafka error: {err}')
    }
    producer = Producer(producer_config)

    try:
        simulate_journey(producer, 'Vehicle-GIRI')
    except KeyboardInterrupt:
        print('Simulation ended by the user')
    except Exception as e:
        print(f'Unexpected error occurred: {e}')
