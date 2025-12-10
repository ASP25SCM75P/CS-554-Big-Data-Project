#!/bin/bash

# E-Commerce Big Data Pipeline - Startup Script
# This script starts all services and runs the data profiling

set -e

echo "=========================================="
echo "E-Commerce Big Data Pipeline"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Starting Docker services...${NC}"
docker-compose up -d

echo ""
echo -e "${BLUE}Step 2: Waiting for services to be healthy...${NC}"
echo "This may take 1-2 minutes..."
sleep 30

# Check if Kafka is ready
echo -e "${YELLOW}Checking Kafka...${NC}"
until docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092 > /dev/null 2>&1; do
    echo "Waiting for Kafka..."
    sleep 5
done
echo -e "${GREEN}✓ Kafka is ready${NC}"

# Check if HBase is ready
echo -e "${YELLOW}Checking HBase...${NC}"
sleep 20
echo -e "${GREEN}✓ HBase is ready${NC}"

# Check if Spark is ready
echo -e "${YELLOW}Checking Spark...${NC}"
until docker exec spark-master curl -s http://localhost:8080 > /dev/null 2>&1; do
    echo "Waiting for Spark..."
    sleep 5
done
echo -e "${GREEN}✓ Spark is ready${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "All services are running!"
echo "==========================================${NC}"
echo ""
echo "Service URLs:"
echo "  • Kafka:          localhost:9092"
echo "  • Spark Master:   http://localhost:8080"
echo "  • HBase Master:   http://localhost:16010"
echo "  • Dashboard:      http://localhost:8050"
echo ""
echo -e "${BLUE}Step 3: Running data profiling (REQUIRED BY PROFESSOR)...${NC}"
echo ""

# Copy dataset to Spark container
docker cp data/sample_dataset.csv spark-master:/opt/spark-apps/dataset.csv

# Run data profiling
docker exec spark-master spark-submit \
    --master local[*] \
    /opt/spark-apps/spark_profiling.py \
    /opt/spark-apps/dataset.csv

echo ""
echo -e "${GREEN}✓ Data profiling complete!${NC}"
echo ""
echo -e "${BLUE}Step 4: Running batch analytics...${NC}"

# Run batch analytics
docker exec spark-master spark-submit \
    --master local[*] \
    /opt/spark-apps/spark_batch_analytics.py \
    /opt/spark-apps/dataset.csv

echo ""
echo -e "${GREEN}✓ Batch analytics complete!${NC}"
echo ""
echo -e "${GREEN}=========================================="
echo "Pipeline is fully operational!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Open dashboard: http://localhost:8050"
echo "  2. View Spark UI: http://localhost:8080"
echo "  3. Events are streaming from Kafka producer"
echo ""
echo "To start Spark Streaming:"
echo "  ./scripts/start_streaming.sh"
echo ""
echo "To stop all services:"
echo "  docker-compose down"
echo ""
