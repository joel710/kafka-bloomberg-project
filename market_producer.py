import time
import requests
import json
import random
from kafka import KafkaProducer

# Configuration Kafka
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

print("📈 Market Watcher démarré... Envoi des prix OR (XAU) et EURO (EUR)")

def get_prices():
    # Pour la démo, on simule une variation réaliste autour d'un pivot
    # car les API gratuites ont souvent des limites de rate (1 requête / minute)
    # ce qui est trop lent pour une démo Kafka "temps réel".
    # On ajoute une petite tendance aléatoire.
    return {
        "XAU": round(2350 + random.uniform(-5, 5), 2),  # Prix de l'or (~2350$)
        "EUR": round(1.08 + random.uniform(-0.005, 0.005), 4) # Prix de l'Euro (~1.08$)
    }

try:
    while True:
        prices = get_prices()
        
        # Envoi de l'Or
        msg_xau = {"type": "market", "asset": "XAU/USD", "price": prices["XAU"], "trend": "neutral"}
        producer.send("market-data", value=msg_xau)
        
        # Envoi de l'Euro
        msg_eur = {"type": "market", "asset": "EUR/USD", "price": prices["EUR"], "trend": "neutral"}
        producer.send("market-data", value=msg_eur)
        
        print(f"📡 Tick: OR={prices['XAU']} USD | EUR={prices['EUR']} USD")
        time.sleep(1) # Haute fréquence pour la démo

except KeyboardInterrupt:
    print("Arrêt du Market Watcher.")
