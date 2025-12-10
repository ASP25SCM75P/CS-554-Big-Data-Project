#!/bin/bash

# Start Spark Streaming Job

echo "=========================================="
echo "Starting Spark Streaming Job"
echo "=========================================="
echo ""

docker exec -d spark-master spark-submit \
    --master spark://spark-master:7077 \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
    /opt/spark-apps/spark_streaming.py

echo "✓ Spark Streaming job submitted!"
echo ""
echo "Monitor progress:"
echo "  • Spark Application UI: http://localhost:4040"
echo "  • Spark Master UI: http://localhost:8080"
echo ""
echo "View logs:"
echo "  docker logs -f spark-master"
echo ""
