#!/usr/bin/env python3
"""
Spark Batch Analytics for E-Commerce Dataset
Performs SQL queries and stores results in HBase
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as spark_sum, avg, desc
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType
)

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
    StructField("user_session", StringType(), True)
])

def create_spark_session():
    """Create Spark session"""
    return SparkSession.builder \
        .appName("ECommerce-Batch-Analytics") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: spark-submit spark_batch_analytics.py <dataset_path>")
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    
    print("\n" + "="*60)
    print("E-Commerce Batch Analytics")
    print("="*60 + "\n")
    
    # Create Spark session
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    # Read dataset
    print(f"Loading dataset from: {dataset_path}")
    df = spark.read \
        .option("header", "true") \
        .schema(event_schema) \
        .csv(dataset_path)
    
    # Register as temp view for SQL queries
    df.createOrReplaceTempView("ecommerce_events")
    
    print(f"✓ Loaded {df.count():,} records\n")
    
    # =====================================================================
    # ANALYSIS 1: Views per Brand
    # =====================================================================
    print("\n" + "="*60)
    print("ANALYSIS 1: Views per Brand")
    print("="*60)
    
    views_per_brand = spark.sql("""
        SELECT 
            brand,
            COUNT(*) as view_count,
            AVG(price) as avg_price,
            SUM(price) as total_value
        FROM ecommerce_events
        WHERE event_type = 'view'
        GROUP BY brand
        ORDER BY view_count DESC
    """)
    
    views_per_brand.show()
    
    # =====================================================================
    # ANALYSIS 2: Cart Events per Brand
    # =====================================================================
    print("\n" + "="*60)
    print("ANALYSIS 2: Cart Events per Brand")
    print("="*60)
    
    cart_per_brand = spark.sql("""
        SELECT 
            brand,
            COUNT(*) as cart_count,
            AVG(price) as avg_price,
            SUM(price) as potential_revenue
        FROM ecommerce_events
        WHERE event_type = 'cart'
        GROUP BY brand
        ORDER BY cart_count DESC
    """)
    
    cart_per_brand.show()
    
    # =====================================================================
    # ANALYSIS 3: Purchases per Brand
    # =====================================================================
    print("\n" + "="*60)
    print("ANALYSIS 3: Purchases per Brand")
    print("="*60)
    
    purchase_per_brand = spark.sql("""
        SELECT 
            brand,
            COUNT(*) as purchase_count,
            AVG(price) as avg_order_value,
            SUM(price) as total_revenue
        FROM ecommerce_events
        WHERE event_type = 'purchase'
        GROUP BY brand
        ORDER BY purchase_count DESC
    """)
    
    purchase_per_brand.show()
    
    # =====================================================================
    # ANALYSIS 4: Comprehensive Brand Report
    # =====================================================================
    print("\n" + "="*60)
    print("ANALYSIS 4: Comprehensive Brand Performance")
    print("="*60)
    
    brand_report = spark.sql("""
        SELECT 
            brand,
            COUNT(CASE WHEN event_type = 'view' THEN 1 END) as views,
            COUNT(CASE WHEN event_type = 'cart' THEN 1 END) as carts,
            COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) as purchases,
            SUM(CASE WHEN event_type = 'purchase' THEN price ELSE 0 END) as revenue,
            ROUND(
                COUNT(CASE WHEN event_type = 'cart' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN event_type = 'view' THEN 1 END), 0), 
                2
            ) as view_to_cart_rate,
            ROUND(
                COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN event_type = 'view' THEN 1 END), 0), 
                2
            ) as view_to_purchase_rate
        FROM ecommerce_events
        GROUP BY brand
        ORDER BY revenue DESC
    """)
    
    brand_report.show(truncate=False)
    
    # =====================================================================
    # ANALYSIS 5: Category Performance
    # =====================================================================
    print("\n" + "="*60)
    print("ANALYSIS 5: Top-Level Category Performance")
    print("="*60)
    
    category_report = spark.sql("""
        SELECT 
            SPLIT(category_code, '\\.')[0] as top_category,
            COUNT(*) as event_count,
            COUNT(CASE WHEN event_type = 'view' THEN 1 END) as views,
            COUNT(CASE WHEN event_type = 'cart' THEN 1 END) as carts,
            COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) as purchases
        FROM ecommerce_events
        WHERE category_code IS NOT NULL AND category_code != ''
        GROUP BY SPLIT(category_code, '\\.')[0]
        ORDER BY event_count DESC
        LIMIT 10
    """)
    
    category_report.show(truncate=False)
    
    # =====================================================================
    # Save results (In production, write to HBase here)
    # =====================================================================
    print("\n" + "="*60)
    print("Saving Analytics Results")
    print("="*60)
    
    # Save as Parquet for further analysis
    output_path = "/tmp/analytics_results"
    
    views_per_brand.write.mode("overwrite").parquet(f"{output_path}/views_per_brand")
    cart_per_brand.write.mode("overwrite").parquet(f"{output_path}/cart_per_brand")
    purchase_per_brand.write.mode("overwrite").parquet(f"{output_path}/purchase_per_brand")
    brand_report.write.mode("overwrite").parquet(f"{output_path}/brand_report")
    
    print(f"✓ Results saved to {output_path}")
    
    # Note: In production, implement HBase write logic here
    print("\nNote: In production, these results would be written to HBase")
    print("      for real-time dashboard access")
    
    spark.stop()
    print("\n✓ Batch analytics complete!")

if __name__ == "__main__":
    main()
