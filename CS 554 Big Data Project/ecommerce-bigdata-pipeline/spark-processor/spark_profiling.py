#!/usr/bin/env python3
"""
Data Profiling Script for E-Commerce Dataset
This addresses the professor's requirement for comprehensive data profiling
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, countDistinct, sum as spark_sum, avg, stddev, 
    min as spark_min, max as spark_max, when, isnan, isnull,
    length, regexp_extract, percentile_approx, lit
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
    StructField("user_session", StringType(), True)
])

def create_spark_session():
    """Create Spark session for batch processing"""
    return SparkSession.builder \
        .appName("ECommerce-Data-Profiling") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

def print_section_header(title):
    """Print formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def profile_dataset(df):
    """
    Comprehensive data profiling following best practices
    """
    
    # =========================================================================
    # 1. BASIC STATISTICS
    # =========================================================================
    print_section_header("1. DATASET OVERVIEW")
    
    total_rows = df.count()
    total_cols = len(df.columns)
    
    print(f"Total Rows: {total_rows:,}")
    print(f"Total Columns: {total_cols}")
    print(f"Column Names: {', '.join(df.columns)}")
    
    # =========================================================================
    # 2. SCHEMA INFORMATION
    # =========================================================================
    print_section_header("2. SCHEMA INFORMATION")
    df.printSchema()
    
    # =========================================================================
    # 3. DATA SUMMARY STATISTICS
    # =========================================================================
    print_section_header("3. SUMMARY STATISTICS (describe)")
    df.describe().show()
    
    print_section_header("3.1 EXTENDED SUMMARY (summary)")
    df.select("price").summary("count", "mean", "stddev", "min", "25%", "50%", "75%", "max").show()
    
    # =========================================================================
    # 4. NULL VALUE ANALYSIS
    # =========================================================================
    print_section_header("4. DATA QUALITY: NULL VALUES")
    
    null_counts = df.select([
        count(when(col(c).isNull() | isnan(c), c)).alias(c)
        for c in df.columns
    ])
    
    print("Null Count per Column:")
    null_counts.show()
    
    # Calculate null percentages
    print("\nNull Percentage per Column:")
    null_percentages = df.select([
        (count(when(col(c).isNull() | isnan(c), c)) * 100.0 / total_rows).alias(c)
        for c in df.columns
    ])
    null_percentages.show()
    
    # =========================================================================
    # 5. MISSING DATA ANALYSIS
    # =========================================================================
    print_section_header("5. MISSING DATA ANALYSIS")
    
    # Empty strings and null values
    empty_or_null = df.select([
        count(when((col(c).isNull()) | (col(c) == ""), c)).alias(c)
        for c in df.columns if df.schema[c].dataType == StringType()
    ])
    
    print("Empty or Null String Columns:")
    empty_or_null.show()
    
    # =========================================================================
    # 6. DATA DISTRIBUTION - CATEGORICAL COLUMNS
    # =========================================================================
    print_section_header("6. CATEGORICAL DATA DISTRIBUTION")
    
    # Event Type Distribution
    print("Event Type Distribution:")
    df.groupBy("event_type").count() \
        .orderBy(col("count").desc()) \
        .withColumn("percentage", (col("count") * 100.0 / total_rows)) \
        .show()
    
    # Brand Distribution
    print("Brand Distribution:")
    df.groupBy("brand").count() \
        .orderBy(col("count").desc()) \
        .withColumn("percentage", (col("count") * 100.0 / total_rows)) \
        .show()
    
    # Category Distribution (top-level)
    print("Top-Level Category Distribution:")
    df.filter(col("category_code").isNotNull() & (col("category_code") != "")) \
        .select(
            regexp_extract(col("category_code"), "^([^.]+)", 1).alias("top_category")
        ) \
        .groupBy("top_category").count() \
        .orderBy(col("count").desc()) \
        .limit(10) \
        .show()
    
    # =========================================================================
    # 7. NUMERICAL DATA ANALYSIS
    # =========================================================================
    print_section_header("7. NUMERICAL DATA ANALYSIS - PRICE")
    
    price_stats = df.select(
        count("price").alias("count"),
        avg("price").alias("mean"),
        stddev("price").alias("stddev"),
        spark_min("price").alias("min"),
        percentile_approx("price", 0.25).alias("q1"),
        percentile_approx("price", 0.5).alias("median"),
        percentile_approx("price", 0.75).alias("q3"),
        spark_max("price").alias("max")
    )
    
    print("Price Statistics:")
    price_stats.show()
    
    # Price ranges
    print("\nPrice Range Distribution:")
    df.groupBy(
        when(col("price") < 50, "0-50")
        .when((col("price") >= 50) & (col("price") < 100), "50-100")
        .when((col("price") >= 100) & (col("price") < 200), "100-200")
        .when((col("price") >= 200) & (col("price") < 500), "200-500")
        .when((col("price") >= 500) & (col("price") < 1000), "500-1000")
        .otherwise("1000+")
        .alias("price_range")
    ).count().orderBy("price_range").show()
    
    # =========================================================================
    # 8. CARDINALITY ANALYSIS
    # =========================================================================
    print_section_header("8. CARDINALITY ANALYSIS")
    
    cardinality = df.select([
        countDistinct(c).alias(c) for c in df.columns
    ])
    
    print("Unique Values per Column:")
    cardinality.show()
    
    # =========================================================================
    # 9. DATA COMPLETENESS
    # =========================================================================
    print_section_header("9. DATA COMPLETENESS")
    
    # Calculate completeness percentage
    completeness = df.select([
        ((count(c) * 100.0) / total_rows).alias(c)
        for c in df.columns
    ])
    
    print("Completeness Percentage (non-null %):")
    completeness.show()
    
    # =========================================================================
    # 10. BUSINESS METRICS
    # =========================================================================
    print_section_header("10. BUSINESS INSIGHTS")
    
    print("Events by Type and Brand:")
    df.groupBy("event_type", "brand").count() \
        .orderBy(col("count").desc()) \
        .show(20)
    
    print("\nConversion Funnel Analysis:")
    conversion = df.groupBy("event_type").agg(
        count("*").alias("count"),
        countDistinct("user_id").alias("unique_users"),
        spark_sum("price").alias("total_value")
    ).orderBy("event_type")
    conversion.show()
    
    # Calculate conversion rates
    view_count = df.filter(col("event_type") == "view").count()
    cart_count = df.filter(col("event_type") == "cart").count()
    purchase_count = df.filter(col("event_type") == "purchase").count()
    
    if view_count > 0:
        print(f"\nConversion Rates:")
        print(f"View to Cart Rate: {(cart_count / view_count * 100):.2f}%")
        print(f"View to Purchase Rate: {(purchase_count / view_count * 100):.2f}%")
        if cart_count > 0:
            print(f"Cart to Purchase Rate: {(purchase_count / cart_count * 100):.2f}%")
    
    # =========================================================================
    # 11. DATA QUALITY SCORE
    # =========================================================================
    print_section_header("11. DATA QUALITY SCORE")
    
    # Calculate overall data quality metrics
    total_cells = total_rows * total_cols
    null_cells = null_counts.first().asDict()
    total_nulls = sum(null_cells.values())
    
    completeness_score = ((total_cells - total_nulls) / total_cells) * 100
    
    print(f"Total Cells: {total_cells:,}")
    print(f"Null Cells: {total_nulls:,}")
    print(f"Data Completeness Score: {completeness_score:.2f}%")
    
    # Uniqueness score for key columns
    total_records = total_rows
    unique_sessions = df.select(countDistinct("user_session")).first()[0]
    unique_users = df.select(countDistinct("user_id")).first()[0]
    
    print(f"\nUser Session Uniqueness: {(unique_sessions / total_records * 100):.2f}%")
    print(f"User ID Uniqueness: {(unique_users / total_records * 100):.2f}%")
    
    # =========================================================================
    # 12. SAMPLE DATA
    # =========================================================================
    print_section_header("12. SAMPLE RECORDS")
    
    print("Random Sample (5 records):")
    df.sample(False, 0.01).limit(5).show(truncate=False)
    
    print("\nFirst 5 records:")
    df.limit(5).show(truncate=False)
    
    print_section_header("DATA PROFILING COMPLETE")

def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print("Usage: spark-submit spark_profiling.py <dataset_path>")
        print("Example: spark-submit spark_profiling.py /app/data/sample_dataset.csv")
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    
    print("\n" + "="*80)
    print("  E-COMMERCE DATASET PROFILING")
    print("  Comprehensive Data Quality and Statistical Analysis")
    print("="*80)
    print(f"\nDataset: {dataset_path}\n")
    
    # Create Spark session
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    # Read dataset
    print("Loading dataset...")
    df = spark.read \
        .option("header", "true") \
        .schema(event_schema) \
        .csv(dataset_path)
    
    # Cache for performance
    df.cache()
    
    print("✓ Dataset loaded successfully\n")
    
    # Perform profiling
    profile_dataset(df)
    
    # Cleanup
    df.unpersist()
    spark.stop()
    
    print("\n✓ Profiling complete!")

if __name__ == "__main__":
    main()
