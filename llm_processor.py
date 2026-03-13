import json
import time
import os
from kafka import KafkaConsumer, KafkaProducer
import google.generativeai as genai

# Configuration Kafka
folder = "./"
service_uri = "kafka-4238954-kafka-2c1f.h.aivencloud.com:17498"

consumer = KafkaConsumer(
    "raw-news",
    bootstrap_servers=service_uri,
    security_protocol="SSL",
    ssl_cafile=folder + "ca.pem",
    ssl_certfile=folder + "service.cert",
    ssl_keyfile=folder + "service.key",
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='latest'
)

producer = KafkaProducer(
    bootstrap_servers=service_uri,
    security_protocol="SSL",
    ssl_cafile=folder + "ca.pem",
    ssl_certfile=folder + "service.cert",
    ssl_keyfile=folder + "service.key",
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Configuration LLM
api_key = os.getenv("GOOGLE_API_KEY")
llm_active = False
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    llm_active = True
    print("🧠 LLM Gemini activé.")
else:
    print("⚠️ Pas de clé API. Utilisation du Sentiment Engine local.")

def analyze_news(headline, summary):
    """Demande au LLM ou au moteur local d'analyser l'impact"""
    if llm_active:
        prompt = f"""
        Analyse ce titre financier: "{headline}"
        Résumé: "{summary}"
        
        Réponds uniquement en format JSON strict:
        {{
            "impact_gold": "BULLISH" | "BEARISH" | "NEUTRAL",
            "impact_eur": "BULLISH" | "BEARISH" | "NEUTRAL",
            "reason": "Une phrase d'explication très courte",
            "forecast": "Une prévision prudente (ex: Hausse légère probable)"
        }}
        """
        try:
            response = model.generate_content(prompt)
            # Nettoyage rudimentaire du JSON (enlever les ```json etc)
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"Erreur LLM: {e}")
            
    # Moteur de secours par mots-clés
    impact = {"impact_gold": "NEUTRAL", "impact_eur": "NEUTRAL", "reason": "Analyse technique locale", "forecast": "Stabilité"}
    h = headline.lower()
    if any(w in h for w in ["inflation", "war", "crisis", "fed"]):
        impact["impact_gold"] = "BULLISH"
        impact["reason"] = "Incertitude économique détectée."
        impact["forecast"] = "Hausse de l'or comme valeur refuge."
    elif any(w in h for w in ["ecb", "eurozone", "europe"]):
        impact["impact_eur"] = "BEARISH"
        impact["reason"] = "Pression sur la zone Euro."
    return impact

print("🧠 Intelligence Processor démarré... En attente de news.")

try:
    for message in consumer:
        news_data = message.value
        headline = news_data["headline"]
        
        print(f"🔍 Analyse de: {headline[:40]}...")
        analysis = analyze_news(headline, news_data.get("summary", ""))
        
        # On enrichit le message original avec l'analyse
        enriched_msg = {**news_data, **analysis}
        
        producer.send("analyzed-news", value=enriched_msg)
        print(f"✅ Analyse envoyée: {analysis['impact_gold']}/{analysis['impact_eur']}")

except KeyboardInterrupt:
    print("Arrêt du processeur.")
