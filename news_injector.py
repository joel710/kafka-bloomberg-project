import json
import time
from kafka import KafkaProducer

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

EVENTS = {
    "1": {"headline": "FED RAISES RATES by 50bps", "impact": "BEARISH_GOLD", "source": "Bloomberg"},
    "2": {"headline": "ECB Announces Quantitative Easing", "impact": "BEARISH_EUR", "source": "Reuters"},
    "3": {"headline": "Global Uncertainty Increases due to Geopolitics", "impact": "BULLISH_GOLD", "source": "AP"},
    "4": {"headline": "US Inflation Data Lower than Expected", "impact": "BULLISH_EUR", "source": "CNBC"}
}

print("📰 Newsroom Control Center")
print("--------------------------------------------------")
for k, v in EVENTS.items():
    print(f"[{k}] {v['headline']} ({v['impact']})")
print("--------------------------------------------------")
print("Appuyez sur le numéro pour déclencher une BREAKING NEWS.")
print("CTRL+C pour quitter.")

try:
    while True:
        choice = input("\nSimuler une News > ")
        if choice in EVENTS:
            news = EVENTS[choice]
            message = {
                "type": "news",
                "headline": news["headline"],
                "impact": news["impact"],
                "source": news["source"],
                "timestamp": int(time.time())
            }
            producer.send("market-news", value=message)
            print(f"🚨 ENVOI RÉUSSI : {news['headline']}")
        else:
            print("Choix invalide.")
except KeyboardInterrupt:
    print("\nFin de la Newsroom.")
