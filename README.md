---
title: Sentinel Hub V2
emoji: 🚀
colorFrom: blue
colorTo: black
sdk: docker
pinned: true
---

# 🌍 Sentinel Hub V2: Intelligence de Marché & Tech (Kafka & IA)

Sentinel Hub est un terminal d'analyse temps réel de nouvelle génération fusionnant le streaming de données (Apache Kafka), la finance traditionnelle et l'écosystème **Big Tech/IA**. Il transforme les flux bruts de prix et d'actualités technologiques en recommandations stratégiques via **Gemini 2.0**.

![Version](https://img.shields.io/badge/version-2.0.0-gold)
![Python](https://img.shields.io/badge/python-3.12+-green)
![Async](https://img.shields.io/badge/stack-Asynchrone-blue)
![Kafka](https://img.shields.io/badge/streaming-Kafka-orange)
![AI](https://img.shields.io/badge/IA-Gemini--2.0--Flash-purple)

## 🌟 Nouveautés de la V2 (Dossier `/V2`)
La version 2.0 apporte une refonte totale pour plus de performance et une couverture sectorielle élargie :

- **Multi-Assets Sectoriels** : 
  - **Macro** : Or (XAU/USD), Euro (EUR/USD).
  - **Big Tech & IA** : NVIDIA, Microsoft, Apple, Google, Tesla.
- **Flux de News Élargis** : Intégration de **TechCrunch** et **The Verge** pour une veille spécifique sur l'Intelligence Artificielle.
- **Architecture Modulaire & Async** : 
  - Passage au **Full-Async** avec `AIOKafka` et `FastAPI`.
  - Séparation stricte : `api/`, `workers/`, `services/`, `models/`.
- **UI Dynamique V2** : Interface "Sentinel Terminal" auto-adaptative aux nouveaux actifs.
- **Configuration Robuste** : Utilisation de `Pydantic Settings` pour une gestion sécurisée des environnements.

---

## 🏗️ Architecture du Système (V2)

Le système repose sur une architecture **Event-Driven** haute performance :
1. **Ingestion (Workers)** : 
   - `market_worker.py` : Fetch asynchrone multi-actifs via Yahoo Finance.
   - `news_worker.py` : Monitoring RSS multi-sources (Finance & Tech).
2. **Streaming (Kafka)** : Orchestration asynchrone via un cluster **Aiven Kafka**.
3. **Analyse (IA)** : Processeur Gemini 2.0 analysant l'impact croisé entre macro-économie et tech.
4. **Diffusion (WebSocket)** : Hub central FastAPI pour le broadcast en temps réel.

---

## 🛠️ Installation et Lancement (V2)

### Configuration
```bash
# 1. Accéder au dossier V2
cd kafka-aiven/V2

# 2. Installer les dépendances V2
pip install -r requirements.txt

# 3. Préparer les certificats Kafka dans V2/certs/
# ca.pem, service.cert, service.key
```

### Lancement
```bash
# Lancement de l'API et des Workers intégrés
python main.py
```
Accédez au terminal V2 via `http://localhost:7860`.

---

## 🔍 Visualisation du Flux (kcat)
Pour surveiller les messages transitant dans le cluster Kafka :
```bash
kcat -b <KAFKA_HOST>:<KAFKA_PORT> \
  -X security.protocol=ssl \
  -X ssl.ca.location=certs/ca.pem \
  -X ssl.certificate.location=certs/service.cert \
  -X ssl.key.location=certs/service.key \
  -t market-data -C
```

---

## 🛡️ Sécurité & Fiabilité
- **Validation Strict** : Les schémas de données sont validés par Pydantic.
- **Gestion d'Erreur IA** : Système de "Graceful Degradation" si l'API Gemini est saturée.
- **Isolation** : La V2 est isolée dans son propre dossier pour faciliter la transition depuis la V1.

---
*Projet Sentinel : La synergie ultime entre Big Data, IA et Marchés Mondiaux.*
