from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """
    Secure configuration management for the Big Data AI Pipeline.
    Loads secrets from .env or Vault.
    """
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Pipeline Execution Mode
    PIPELINE_MODE: str = "SIMULATED" # "DOCKER" or "SIMULATED"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_SECURITY_PROTOCOL: str = "SASL_SSL"
    KAFKA_SASL_MECHANISM: str = "PLAIN"
    KAFKA_SASL_USERNAME: Optional[str] = None
    KAFKA_SASL_PASSWORD: Optional[str] = None
    KAFKA_TOPIC: str = "secure-data-stream"

    # Spark
    SPARK_MASTER: str = "local[*]"
    SPARK_APP_NAME: str = "SecureBigDataAI"
    SPARK_EXECUTOR_MEMORY: str = "4g"
    SPARK_DRIVER_MEMORY: str = "2g"

    # Chroma DB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION: str = "distributed-intelligence"

    # AI & Security
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    PII_SALT: str = "default_secure_salt"
    OPENAI_API_KEY: Optional[str] = None
    MASTER_ENCRYPTION_KEY: Optional[str] = None

    def get_kafka_config(self) -> dict:
        """Returns configuration dictionary for Confluent Kafka."""
        return {
            'bootstrap.servers': self.KAFKA_BOOTSTRAP_SERVERS,
            'security.protocol': self.KAFKA_SECURITY_PROTOCOL,
            'sasl.mechanism': self.KAFKA_SASL_MECHANISM,
            'sasl.username': self.KAFKA_SASL_USERNAME,
            'sasl.password': self.KAFKA_SASL_PASSWORD,
        }

# Singleton instance
settings = Settings()
