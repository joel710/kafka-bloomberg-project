import json
import ssl
from aiokafka import AIOKafkaProducer
from loguru import logger
from V2.config import settings

class KafkaService:
    def __init__(self):
        self.producer = None
        self.context = ssl.create_default_context(cafile=settings.KAFKA_CA)
        self.context.load_cert_chain(settings.KAFKA_CERT, settings.KAFKA_KEY)
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED

    async def start(self):
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=f"{settings.KAFKA_HOST}:{settings.KAFKA_PORT}",
                security_protocol="SSL",
                ssl_context=self.context,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.producer.start()
            logger.info("✅ Kafka Producer démarré")
        except Exception as e:
            logger.error(f"❌ Échec démarrage Kafka : {e}")
            self.producer = None

    async def send(self, topic: str, value: dict):
        if self.producer:
            try:
                await self.producer.send_and_wait(topic, value)
            except Exception as e:
                logger.warning(f"⚠️ Erreur envoi Kafka: {e}")

    async def stop(self):
        if self.producer:
            await self.producer.stop()

kafka_service = KafkaService()
