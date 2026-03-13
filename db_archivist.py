import json
from kafka import KafkaConsumer
from pymongo import MongoClient

# Configuration Kafka
folder = "./"
service_uri = "kafka-4238954-kafka-2c1f.h.aivencloud.com:17498"

# Configuration MongoDB
MONGO_URI = "mongodb+srv://jelise710_db_user:msi2025@dji.pzrvgeg.mongodb.net/?appName=dji"
client = MongoClient(MONGO_URI)
db = client['dji']
collection_market = db['market_history']
collection_news = db['news_history']

# Consommateur Kafka
topics = ["market-data", "analyzed-news"]
consumer = KafkaConsumer(
    *topics,
    bootstrap_servers=service_uri,
    security_protocol="SSL",
    ssl_cafile=folder + "ca.pem",
    ssl_certfile=folder + "service.cert",
    ssl_keyfile=folder + "service.key",
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='latest'
)

print("💾 Archiviste MongoDB démarré... Prêt à enregistrer l'historique.")

try:
    for message in consumer:
        data = message.value
        
        if message.topic == "market-data":
            # On ajoute un tag pour MongoDB
            data["category"] = "market_tick"
            collection_market.insert_one(data)
            print(f"✅ [DB] Prix sauvegardé : {data['asset']} = {data['price']}")
            
        elif message.topic == "analyzed-news":
            # On sauvegarde la news avec l'analyse LLM
            data["category"] = "intelligence"
            collection_news.insert_one(data)
            print(f"✅ [DB] News & IA sauvegardées : {data['headline'][:30]}...")

except KeyboardInterrupt:
    print("\nArrêt de l'archiviste.")
finally:
    client.close()
