from pyspark.sql import SparkSession
from src.core.config import settings

def get_spark_session() -> SparkSession:
    """
    Initializes and returns a secure Spark session for distributed processing.
    Configured with optimized memory settings for AI vectorization.
    """
    return (
        SparkSession.builder
        .appName(settings.SPARK_APP_NAME)
        .master(settings.SPARK_MASTER)
        .config("spark.executor.memory", settings.SPARK_EXECUTOR_MEMORY)
        .config("spark.driver.memory", settings.SPARK_DRIVER_MEMORY)
        .config("spark.sql.shuffle.partitions", "200") # Optimized for scale
        .config("spark.driver.maxResultSize", "2g")
        .getOrCreate()
    )

if __name__ == "__main__":
    # Test initialization
    spark = get_spark_session()
    print(f"[Spark] Session initialized: {spark.version}")
    spark.stop()
