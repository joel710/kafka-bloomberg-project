import time
import json
import feedparser
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

# Flux RSS de Reuters (on peut en ajouter d'autres)
RSS_FEEDS = [
    "https://www.reutersagency.com/feed/?best-types=business-finance&post_type=best",
    "https://search.cnbc.com/rs/search/view.xml?partnerId=2000&keywords=finance"
]

seen_titles = set()

print("📰 Real-Time News Fetcher démarré...")

try:
    while True:
        for url in RSS_FEEDS:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    if entry.title not in seen_titles:
                        msg = {
                            "type": "raw_news",
                            "headline": entry.title,
                            "summary": entry.summary[:200] if hasattr(entry, 'summary') else "",
                            "source": url.split('.')[1], # reuters ou cnbc
                            "timestamp": int(time.time())
                        }
                        producer.send("raw-news", value=msg)
                        seen_titles.add(entry.title)
                        print(f"🚨 NEWS: {entry.title[:50]}...")
            except Exception as e:
                print(f"Erreur RSS: {e}")
        
        # On limite la taille du set pour pas saturer la RAM
        if len(seen_titles) > 1000:
            seen_titles.clear()
            
        time.sleep(30)

except KeyboardInterrupt:
    print("Arrêt du News Fetcher.")
