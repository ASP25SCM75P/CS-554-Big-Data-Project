#!/usr/bin/env python3
"""
E-Commerce Event Stream Producer
Reads events from CSV and produces to Kafka topic
"""

import csv
import json
import time
import os
import sys
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Configuration from environment
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'ecommerce-events')
EVENT_RATE = int(os.getenv('EVENT_RATE', 100))  # Events per second
DATASET_PATH = '/app/data/sample_dataset.csv'

class EventProducer:
    def __init__(self):
        """Initialize Kafka producer with retry logic"""
        print(f"Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}...")
        max_retries = 30
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None,
                    acks='all',
                    retries=3,
                    max_in_flight_requests_per_connection=1
                )
                print("✓ Connected to Kafka successfully!")
                break
            except Exception as e:
                retry_count += 1
                print(f"Attempt {retry_count}/{max_retries}: Waiting for Kafka... ({e})")
                time.sleep(2)
        
        if retry_count >= max_retries:
            print("✗ Failed to connect to Kafka after maximum retries")
            sys.exit(1)
    
    def read_dataset(self):
        """Read events from CSV dataset"""
        events = []
        try:
            with open(DATASET_PATH, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    event = {
                        'event_time': row['event_time'],
                        'event_type': row['event_type'],
                        'product_id': row['product_id'],
                        'category_id': row['category_id'],
                        'category_code': row.get('category_code', ''),
                        'brand': row['brand'],
                        'price': float(row['price']),
                        'user_id': row['user_id'],
                        'user_session': row['user_session']
                    }
                    events.append(event)
            print(f"✓ Loaded {len(events)} events from dataset")
            return events
        except Exception as e:
            print(f"✗ Error reading dataset: {e}")
            sys.exit(1)
    
    def produce_events(self):
        """Stream events to Kafka"""
        events = self.read_dataset()
        event_count = 0
        cycle_count = 0
        
        print(f"\n{'='*60}")
        print(f"Starting event stream to topic: {KAFKA_TOPIC}")
        print(f"Target rate: {EVENT_RATE} events/second")
        print(f"{'='*60}\n")
        
        while True:
            cycle_count += 1
            print(f"\n--- Cycle {cycle_count} ---")
            
            for event in events:
                try:
                    # Add current timestamp for tracking
                    event['produced_at'] = datetime.utcnow().isoformat()
                    
                    # Use event_type as key for partitioning
                    key = event['event_type']
                    
                    # Send to Kafka
                    future = self.producer.send(
                        KAFKA_TOPIC,
                        key=key,
                        value=event
                    )
                    
                    # Wait for acknowledgment (optional, for reliability)
                    # future.get(timeout=10)
                    
                    event_count += 1
                    
                    # Log progress
                    if event_count % 100 == 0:
                        print(f"Produced {event_count} events... "
                              f"Last: {event['brand']} - {event['event_type']}")
                    
                    # Rate limiting
                    time.sleep(1.0 / EVENT_RATE)
                    
                except KafkaError as e:
                    print(f"✗ Kafka error: {e}")
                except Exception as e:
                    print(f"✗ Error producing event: {e}")
            
            print(f"Completed cycle {cycle_count} with {len(events)} events")
            print(f"Total events produced: {event_count}")
    
    def close(self):
        """Close producer connection"""
        if hasattr(self, 'producer'):
            self.producer.flush()
            self.producer.close()
            print("\n✓ Producer closed gracefully")

def main():
    producer = EventProducer()
    try:
        producer.produce_events()
    except KeyboardInterrupt:
        print("\n\nShutting down producer...")
    finally:
        producer.close()

if __name__ == '__main__':
    main()
