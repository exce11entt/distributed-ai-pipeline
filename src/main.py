from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, from_json, current_timestamp, lit
from pyspark.sql.types import StringType
from prometheus_client import start_http_server, Counter, Histogram
import time
from src.core.spark_session import get_spark_session
from src.core.config import settings
from src.core.security import security
from src.pipeline.anonymizer_layer import SCHEMA, anonymize_user
from src.pipeline.vector_engine import process_spark_partition

# Prometheus Metrics
RECORDS_PROCESSED = Counter('pipeline_records_processed_total', 'Total number of records processed by the pipeline')
PII_SCRUBBED = Counter('pipeline_pii_scrubbed_total', 'Total number of PII fields anonymized')
BATCH_LATENCY = Histogram('pipeline_batch_latency_seconds', 'Time spent processing a micro-batch')

class BigDataOrchestrator:
    """
    Orchestrates the 100M+ Record AI Pipeline with Observability.
    Kafka -> Spark (Anonymize) -> Vector Engine (Pinecone).
    """
    def __init__(self):
        self.spark = get_spark_session()
        # Start metrics server on port 8000
        start_http_server(8000)
        print("[Orchestrator] Metrics server started on port 8000")

    def run_pipeline(self):
        """Executes the end-to-end secure streaming pipeline with instrumentation."""
        print(f"[Orchestrator] Launching Secure AI Pipeline in {settings.PIPELINE_MODE} mode...")

        # 1. Ingest Data
        if settings.PIPELINE_MODE == "DOCKER":
            raw_df = (
                self.spark.readStream
                .format("kafka")
                .options(**settings.get_kafka_config())
                .option("subscribe", settings.KAFKA_TOPIC)
                .load()
            )
            # Parse JSON from Kafka 'value' column
            json_df = raw_df.selectExpr("CAST(value AS STRING)").select(from_json(col("value"), SCHEMA).alias("data")).select("data.*")
        else:
            # SIMULATED Mode: Read from local JSONL file
            stream_path = "data/"
            os.makedirs(stream_path, exist_ok=True)
            # Create empty file if it doesn't exist to avoid Spark error
            open(os.path.join(stream_path, "stream.jsonl"), "a").close()
            
            raw_df = (
                self.spark.readStream
                .schema(SCHEMA)
                .json(stream_path)
            )
            json_df = raw_df

        # 2. Transform & Anonymize
        secure_df = (
            json_df
            .withColumn("anonymized_id", anonymize_user(col("user_id")))
            .withColumn("audit_tag", lit("secure_pipeline_v1"))
            .drop("user_id")
        )

        def process_and_track(batch_df, batch_id):
            """Processes a micro-batch and updates Prometheus metrics."""
            with BATCH_LATENCY.time():
                record_count = batch_df.count()
                if record_count > 0:
                    RECORDS_PROCESSED.inc(record_count)
                    PII_SCRUBBED.inc(record_count)
                    print(f"[Orchestrator] Batch {batch_id} processed {record_count} records.")
                    batch_df.foreachPartition(process_spark_partition)

        # 3. Distributed Vectorization & Sink
        query = (
            secure_df.writeStream
            .foreachBatch(process_and_track)
            .start()
        )

        print("[Orchestrator] Pipeline active and scaling...")
        query.awaitTermination()

if __name__ == "__main__":
    orchestrator = BigDataOrchestrator()
    orchestrator.run_pipeline()
