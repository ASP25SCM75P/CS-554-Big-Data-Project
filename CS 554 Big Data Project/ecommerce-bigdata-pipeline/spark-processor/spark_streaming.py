#!/usr/bin/env python3
"""
Spark Structured Streaming Job for E-Commerce Events
Includes real-time processing, aggregations, and HBase writes
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, window, count, sum as spark_sum, avg, max as spark_max, 
    min as spark_min, when, isnan, isnull, current_timestamp, to_timestamp,
    concat_ws, lit
)
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, 
    DoubleType, TimestampType
)
import sys

# Event schema
event_schema = StructType([
    StructField("event_time", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("category_id", StringType(), True),
    StructField("category_code", StringType(), True),
    StructField("brand", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("user_id", StringType(), True),
    StructField("user_session", StringType(), True),
    StructField("produced_at", StringType(), True)
])

def create_spark_session():
    """Create Spark session with HBase connector"""
    return SparkSession.builder \
        .appName("ECommerce-Streaming-Pipeline") \
        .config("spark.jars.packages", 
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
                "org.apache.hbase:hbase-client:2.4.17,"
                "org.apache.hbase:hbase-common:2.4.17,"
                "org.apache.hbase:hbase-mapreduce:2.4.17") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

def write_to_hbase(df, table_name, epoch_id):
    """
    Write DataFrame to HBase
    Note: This is a simplified version. In production, use HBase bulk load or proper connector
    """
    try:
        # Convert DataFrame to format suitable for HBase
        # Here we would use HBase connector or REST API
        # For demonstration, we'll log the data
        print(f"\n{'='*60}")
        print(f"Writing batch {epoch_id} to HBase table: {table_name}")
        print(f"{'='*60}")
        df.show(truncate=False)
        
        # In production, implement actual HBase write logic here
        # Example using happybase or HBase REST API
        
    except Exception as e:
        print(f"Error writing to HBase: {e}")

def main():
    print("\n" + "="*60)
    print("Starting E-Commerce Real-Time Analytics Pipeline")
    print("="*60 + "\n")
    
    # Create Spark session
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    # Kafka connection parameters
    kafka_bootstrap_servers = "kafka:29092"
    kafka_topic = "ecommerce-events"
    
    print(f"Connecting to Kafka: {kafka_bootstrap_servers}")
    print(f"Subscribing to topic: {kafka_topic}\n")
    
    # Read from Kafka
    raw_stream = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", kafka_topic) \
        .option("startingOffsets", "latest") \
        .option("failOnDataLoss", "false") \
        .load()
    
    # Parse JSON from Kafka value
    events = raw_stream \
        .select(from_json(col("value").cast("string"), event_schema).alias("data")) \
        .select("data.*")
    
    # Convert event_time to timestamp
    events = events.withColumn(
        "event_timestamp",
        to_timestamp(col("event_time"), "yyyy-MM-dd HH:mm:ss z")
    )
    
    # =====================================================================
    # AGGREGATION 1: Event Type Counts (2-second windows)
    # =====================================================================
    print("Setting up Aggregation 1: Event Type Counts...")
    
    event_counts = events \
        .withWatermark("event_timestamp", "10 seconds") \
        .groupBy(
            window(col("event_timestamp"), "2 seconds"),
            col("event_type")
        ) \
        .agg(
            count("*").alias("event_count"),
            spark_sum("price").alias("total_value"),
            avg("price").alias("avg_price")
        ) \
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("event_type"),
            col("event_count"),
            col("total_value"),
            col("avg_price")
        )
    
    # Write event counts to console and HBase
    query1 = event_counts \
        .writeStream \
        .outputMode("update") \
        .format("console") \
        .option("truncate", False) \
        .foreachBatch(lambda df, epoch_id: write_to_hbase(df, "event_counts", epoch_id)) \
        .start()
    
    # =====================================================================
    # AGGREGATION 2: Brand Performance (2-second windows)
    # =====================================================================
    print("Setting up Aggregation 2: Brand Performance...")
    
    brand_metrics = events \
        .withWatermark("event_timestamp", "10 seconds") \
        .groupBy(
            window(col("event_timestamp"), "2 seconds"),
            col("brand"),
            col("event_type")
        ) \
        .agg(
            count("*").alias("event_count"),
            spark_sum("price").alias("revenue"),
            avg("price").alias("avg_price"),
            count(col("user_id").isNotNull()).alias("unique_interactions")
        ) \
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("brand"),
            col("event_type"),
            col("event_count"),
            col("revenue"),
            col("avg_price"),
            col("unique_interactions")
        )
    
    query2 = brand_metrics \
        .writeStream \
        .outputMode("update") \
        .format("console") \
        .option("truncate", False) \
        .start()
    
    # =====================================================================
    # AGGREGATION 3: Category Performance
    # =====================================================================
    print("Setting up Aggregation 3: Category Performance...")
    
    # Extract top-level category from category_code
    category_events = events \
        .filter(col("category_code").isNotNull() & (col("category_code") != "")) \
        .withColumn(
            "top_category",
            when(col("category_code").contains("."), 
                 col("category_code").substr(lit(1), 
                     when(col("category_code").contains("."),
                          col("category_code").rlike("\\.") - 1).otherwise(100)))
            .otherwise(col("category_code"))
        )
    
    category_metrics = category_events \
        .withWatermark("event_timestamp", "10 seconds") \
        .groupBy(
            window(col("event_timestamp"), "2 seconds"),
            col("top_category")
        ) \
        .agg(
            count("*").alias("view_count"),
            count(when(col("event_type") == "purchase", 1)).alias("purchase_count")
        ) \
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("top_category"),
            col("view_count"),
            col("purchase_count")
        )
    
    query3 = category_metrics \
        .writeStream \
        .outputMode("update") \
        .format("console") \
        .option("truncate", False) \
        .start()
    
    print("\n" + "="*60)
    print("All streaming queries started successfully!")
    print("Waiting for data... (Press Ctrl+C to stop)")
    print("="*60 + "\n")
    
    # Wait for all queries to finish
    query1.awaitTermination()

if __name__ == "__main__":
    main()
