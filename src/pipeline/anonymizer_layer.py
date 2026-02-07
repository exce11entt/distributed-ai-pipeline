from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, from_json, current_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, FloatType
from src.core.spark_session import get_spark_session
from src.core.config import settings
from src.core.security import security

# Schema for incoming Kafka records
SCHEMA = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("email_enc", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("currency", StringType(), True),
    StructField("timestamp", FloatType(), True),
    StructField("meta", StringType(), True)
])

# UDF for Anonymization
@udf(returnType=StringType())
def anonymize_user(user_id: str) -> str:
    """Anonymizes User ID using the secure security engine."""
    return security.anonymize_pii(user_id)

class AnonymizerLayer:
    """
    Spark Structured Streaming layer for real-time anonymization.
    Scrub PII and generate audit markers before vectorization.
    """
    def __init__(self):
        self.spark = get_spark_session()

    def process_stream(self):
        """Streams from Kafka, applies security logic, and logs audit trail."""
        print(f"[Anonymizer] Subscribing to secure Kafka topic: {settings.KAFKA_TOPIC}")

        # 1. Read from Kafka
        raw_df = (
            self.spark.readStream
            .format("kafka")
            .options(**settings.get_kafka_config())
            .option("subscribe", settings.KAFKA_TOPIC)
            .option("startingOffsets", "latest")
            .load()
        )

        # 2. Parse JSON and extract fields
        json_df = raw_df.selectExpr("CAST(value AS STRING)").select(
            from_json(col("value"), SCHEMA).alias("data")
        ).select("data.*")

        # 3. Apply Anonymization & Security Marking
        secure_df = (
            json_df
            .withColumn("anonymized_id", anonymize_user(col("user_id")))
            .withColumn("processed_at", current_timestamp())
            .withColumn("audit_tag", lit("secure_spark_v1"))
            # Drop raw User ID and Encrypted Email (keep only for downstream if needed)
            .drop("user_id") 
        )

        # 4. Write to Audit Console (Mocking the Audit database for now)
        query = (
            secure_df.writeStream
            .outputMode("append")
            .format("console") # In prod: .format("delta") or .format("jdbc")
            .option("truncate", "false")
            .start()
        )

        print("[Anonymizer] Stream processing active...")
        query.awaitTermination()

if __name__ == "__main__":
    layer = AnonymizerLayer()
    layer.process_stream()
