import json
import time
from kafka import KafkaConsumer

# Configuration
folder = "./"
service_uri = "kafka-4238954-kafka-2c1f.h.aivencloud.com:17498"

# On s'abonne aux topics de données réelles et d'analyses LLM
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

# État global
market_state = {
    "XAU/USD": 0.0,
    "EUR/USD": 0.0,
    "LATEST_NEWS": "Recherche de news mondiales...",
    "LLM_ANALYSIS": {
        "impact_gold": "WAITING",
        "impact_eur": "WAITING",
        "reason": "En attente d'IA...",
        "forecast": "N/A"
    }
}

def clear_screen():
    print("\033[H\033[J", end="")

def display_dashboard():
    clear_screen()
    print("==========================================================")
    print("       🌍 GLOBAL MARKET INTELLIGENCE (KAFKA + LLM) 🌍       ")
    print("==========================================================")
    
    print(f"\n📈 MARCHÉS EN DIRECT :")
    print(f"   💰 OR (XAU)   : {market_state['XAU/USD']} USD")
    print(f"   💶 EURO (EUR) : {market_state['EUR/USD']} USD")
    
    print("\n📰 DERNIÈRE NEWS ANALYSÉE :")
    print(f"   📝 Titre : {market_state['LATEST_NEWS'][:70]}...")
    
    analysis = market_state["LLM_ANALYSIS"]
    
    # Couleurs pour l'impact
    def get_color(impact):
        if impact == "BULLISH": return "\033[92m" # Vert
        if impact == "BEARISH": return "\033[91m" # Rouge
        return "\033[0m" # Normal

    print(f"\n🧠 ANALYSE INTELLIGENTE :")
    print(f"   🔸 Impact OR   : {get_color(analysis['impact_gold'])}{analysis['impact_gold']}\033[0m")
    print(f"   🔹 Impact EURO : {get_color(analysis['impact_eur'])}{analysis['impact_eur']}\033[0m")
    print(f"   💡 Raison      : {analysis['reason']}")
    print(f"   🔮 Prévision   : {analysis['forecast']}")
    
    print("\n==========================================================")
    print("Système : OK | Flux : Connecté | IA : Active")

if __name__ == "__main__":
    print("Démarrage du Global Sentinel...")
    for message in consumer:
        data = message.value
        
        if message.topic == "market-data":
            asset = data.get("asset")
            price = data.get("price")
            if asset in market_state:
                market_state[asset] = price
                
        elif message.topic == "analyzed-news":
            market_state["LATEST_NEWS"] = data['headline']
            market_state["LLM_ANALYSIS"] = {
                "impact_gold": data['impact_gold'],
                "impact_eur": data['impact_eur'],
                "reason": data['reason'],
                "forecast": data['forecast']
            }

        display_dashboard()
except KeyboardInterrupt:
    print("\nArrêt du Sentinel.")
