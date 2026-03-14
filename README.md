# 🌍 Forex Sentinel: Intelligence de Marché Temps Réel (Kafka & IA)

Forex Sentinel est un terminal d'analyse financière de pointe fusionnant le streaming de données temps réel (Apache Kafka) et l'intelligence artificielle générative (Gemini 2.0). Il transforme des flux bruts de prix et d'actualités en recommandations d'investissement explicites.

![Version](https://img.shields.io/badge/version-1.2.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![Kafka](https://img.shields.io/badge/streaming-Kafka-orange)
![AI](https://img.shields.io/badge/IA-Gemini--2.0--Hybrid-purple)

## 🚀 Fonctionnalités Clés
- **Surveillance Live** : Suivi du cours de l'Or (**XAU/USD**) et de l'Euro (**EUR/USD**) avec une latence < 1s.
- **Intelligence Artificielle Hybride** : Analyse macro-économique via **Gemini 2.0 Flash** avec un moteur de secours (Mock IA) en cas de dépassement de quota.
- **Conseils Explicites** : Recommandations claires (ACHETER/VENTE/ATTENDRE) basées sur l'actualité mondiale.
- **Architecture Résiliente** : Bascule automatique en "Mode Direct" si le cluster Kafka est indisponible.
- **Design Premium** : Interface "Liquid Glass" (Glassmorphism) pour une expérience utilisateur moderne.

---

## 🏗️ Architecture du Système

Le projet utilise une architecture **Event-Driven** totalement découplée :
1. **Ingestion** : Workers dédiés pour Yahoo Finance et flux RSS (CNBC, Yahoo, Investing.com).
2. **Streaming** : Orchestration via un cluster **Aiven Kafka** (SSL sécurisé).
3. **Traitement** : Enrichissement des données par IA (Gemini) en tant que Stream Processor.
4. **Diffusion** : Pont WebSocket asynchrone via **FastAPI**.
5. **Persistance** : Archivage automatique dans **MongoDB Atlas**.

---

## 🛠️ Installation et Lancement

### Configuration
```bash
# 1. Clonage et installation
git clone https://github.com/joel710/kafka-bloomberg-project.git
cd kafka-bloomberg-project
pip install -r requirements.txt

# 2. Variables d'environnement (.env)
echo "GOOGLE_API_KEY=votre_cle_gemini" > .env
```

### Lancement
```bash
python main.py
```
Accédez au terminal via `http://localhost:8000`.

---

## 🔍 Streaming CLI (kcat)
Pour visualiser le flux binaire brut dans votre terminal :
```bash
kcat -b kafka-4238954-kafka-2c1f.h.aivencloud.com:17498 \
  -X security.protocol=ssl \
  -X ssl.ca.location=ca.pem \
  -X ssl.certificate.location=service.cert \
  -X ssl.key.location=service.key \
  -t market-data -C
```

---

## 🛡️ Fiabilité et Quotas
Le système est optimisé pour les comptes Gemini Free Tier :
- **Gestion des pauses** (90s) entre les analyses pour préserver le quota.
- **IA de secours** : Moteur de règles financières local prenant le relais en cas d'erreur 429.
- **Système de Cache** : Les nouveaux clients reçoivent instantanément la dernière analyse connue.

---
*Projet réalisé pour démontrer la synergie entre Big Data, IA et Web moderne.*
