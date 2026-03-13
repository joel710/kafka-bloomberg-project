import time
import json
import yfinance as yf
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

print("🚀 Real-Time Market Producer démarré (Yahoo Finance)...")

ASSETS = {
    "GC=F": "XAU/USD",    # Gold Futures
    "EURUSD=X": "EUR/USD" # Euro/US Dollar
}

def fetch_real_prices():
    data = {}
    for ticker, name in ASSETS.items():
        try:
            t = yf.Ticker(ticker)
            # On prend le dernier prix de clôture ou le prix actuel
            price = t.fast_info['last_price']
            data[name] = round(price, 4)
        except Exception as e:
            print(f"Erreur pour {name}: {e}")
    return data

try:
    while True:
        prices = fetch_real_prices()
        if prices:
            for asset, price in prices.items():
                msg = {
                    "type": "market",
                    "asset": asset,
                    "price": price,
                    "timestamp": int(time.time())
                }
                producer.send("market-data", value=msg)
                print(f"📡 REAL TICK: {asset} = {price}")
        
        # Yahoo Finance n'aime pas être spammé trop vite, 10s c'est bien pour du "temps réel" gratuit
        time.sleep(10)

except KeyboardInterrupt:
    print("Arrêt du Market Producer.")
