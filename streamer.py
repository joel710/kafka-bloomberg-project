import time
import requests
from kafka import KafkaProducer
import json

# Configuration des fichiers (assure-toi qu'ils sont dans le même dossier)
folder = "./"
service_uri = "kafka-4238954-kafka-2c1f.h.aivencloud.com:17498"

producer = KafkaProducer(
    bootstrap_servers=service_uri,
    security_protocol="SSL",
    ssl_cafile=folder + "ca.pem",
    ssl_certfile=folder + "service.cert",
    ssl_keyfile=folder + "service.key",
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("🚀 Streamer démarré... Envoi du prix BTC toutes les 2 secondes.")

try:
    while True:
        # Récupération du prix réel
        res = requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot")
        data = res.json()["data"]
        
        # Envoi vers Kafka
        producer.send("test-topic", value=data)
        print(f"Envoi : {data['amount']} USD")
        
        time.sleep(2)
except KeyboardInterrupt:
    print("Arrêt du streamer.")
