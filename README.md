# 🌍 Forex Sentinel: Intelligence de Marché Temps Réel (Kafka & IA)

Forex Sentinel est un terminal de trading et d'analyse financière de nouvelle génération. Il fusionne la puissance du streaming de données asynchrone avec l'intelligence artificielle pour offrir des recommandations d'investissement ultra-rapides sur l'Or et l'Euro.

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![Kafka](https://img.shields.io/badge/streaming-Kafka-orange)
![AI](https://img.shields.io/badge/IA-Gemini--2.0--Flash-purple)

## 🚀 Vision du Projet
L'objectif est de démontrer comment une architecture événementielle (Event-Driven) peut transformer des flux bruts en décisions exploitables. Le système surveille le prix de l'once d'or (**XAU/USD**) et le taux **EUR/USD**, tout en analysant l'impact des news via Gemini 2.0.

---

## 🛠️ Installation et Configuration

### Setup Rapide
```bash
git clone https://github.com/joel710/kafka-bloomberg-project.git
cd kafka-bloomberg-project
pip install -r requirements.txt
echo "GOOGLE_API_KEY=votre_cle_ici" > .env
python main.py
```

---

## 🔍 Debugging & Streaming Direct (CLI)

Pour démontrer la force du streaming brut sans passer par l'interface web, vous pouvez utiliser **kcat** (anciennement kafkacat). Cela permet de voir les ticks de prix circuler en temps réel dans votre terminal.

### 🐧 Sur Linux (Debian/Ubuntu)
```bash
sudo apt install kcat
```

### 🪟 Sur Windows
Utilisez [Chocolatey](https://chocolatey.org/) : `choco install kcat` ou téléchargez le binaire sur le repo officiel.

### 📡 Commande de Streaming en Direct
Exécutez cette commande à la racine du projet pour écouter le flux des prix :
```bash
kcat -b kafka-4238954-kafka-2c1f.h.aivencloud.com:17498 \
  -X security.protocol=ssl \
  -X ssl.ca.location=ca.pem \
  -X ssl.certificate.location=service.cert \
  -X ssl.key.location=service.key \
  -t market-data -C
```
*(Note: Changez `-t market-data` par `-t analyzed-news` pour voir les analyses de l'IA au format JSON brut).*

---

## 🏗️ Architecture Technique
*   **Ingestion** : Yahoo Finance (Prix) & Flux RSS (News).
*   **Streaming** : Apache Kafka sur **Aiven**.
*   **Intelligence** : **Gemini 2.0 Flash** pour l'analyse macro-économique.
*   **Interface** : Design "Liquid Glass" avec WebSockets via **FastAPI**.

## 🛡️ Résilience
Le projet inclut un **Mode Direct** automatique. Si Kafka est injoignable, le système bascule sur un flux interne pour garantir la fluidité de la démonstration.

---
*Projet réalisé pour illustrer la synergie entre le Big Data (Kafka), l'IA et le Web moderne.*
