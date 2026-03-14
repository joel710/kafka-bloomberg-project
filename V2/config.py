from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Kafka
    KAFKA_HOST: str = "kafka-4238954-kafka-2c1f.h.aivencloud.com"
    KAFKA_PORT: int = 17498
    KAFKA_CA: str = "certs/ca.pem"
    KAFKA_CERT: str = "certs/service.cert"
    KAFKA_KEY: str = "certs/service.key"
    
    # Mongo
    MONGO_URI: str = Field(..., env="MONGO_URI")
    
    # Gemini
    GOOGLE_API_KEY: str = Field(..., env="GOOGLE_API_KEY")
    
    # Assets à surveiller
    ASSETS: dict = {
        "GC=F": "OR",
        "EURUSD=X": "EUR/USD",
        "NVDA": "NVIDIA",
        "MSFT": "MICROSOFT",
        "AAPL": "APPLE",
        "GOOGL": "GOOGLE",
        "TSLA": "TESLA"
    }

    # Flux de News
    RSS_SOURCES: list = [
        "https://www.cnbc.com/id/10000664/device/rss/rss.html", # Finance
        "https://www.investing.com/rss/news_1.rss",            # Marchés
        "https://feeds.feedburner.com/TechCrunch/",           # Tech/IA
        "https://www.theverge.com/rss/index.xml"               # Tech/AI
    ]
    
    DEBUG: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
