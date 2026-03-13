# 🌍 Forex Sentinel: Intelligence de Marché Temps Réel (Kafka & IA)

Forex Sentinel est un terminal de trading et d'analyse financière de nouvelle génération. Il fusionne la puissance du streaming de données asynchrone avec l'intelligence artificielle pour offrir des recommandations d'investissement ultra-rapides sur l'Or et l'Euro.

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![Kafka](https://img.shields.io/badge/streaming-Kafka-orange)
![AI](https://img.shields.io/badge/IA-Gemini--2.0--Flash-purple)
![Design](https://img.shields.io/badge/UI-Liquid--Glass-black)

## 🚀 Vision du Projet
L'objectif est de démontrer comment une architecture événementielle (Event-Driven) peut transformer des flux bruts (prix et news) en décisions exploitables. Le système surveille en permanence le prix de l'once d'or (**XAU/USD**) et le taux de change **EUR/USD**, tout en analysant l'impact des dernières nouvelles mondiales (Reuters, CNBC, Investing.com) via un LLM.

---

## 🏗️ Architecture Technique

### 1. Ingestion Multi-Source (Producers)
*   **Market Worker** : Extraction des prix réels via `yfinance`.
*   **RSS Worker** : Scan intelligent de flux financiers mondiaux.
*   **Fluctuation Engine** : Ajout d'un jitter visuel pour garantir un affichage dynamique même lors de marchés stables.

### 2. Cœur de Streaming (Apache Kafka)
Utilisation d'un cluster managé sur **Aiven** pour assurer le transport des messages :
*   **Topic `market-data`** : Flux de prix haute fréquence.
*   **Topic `analyzed-news`** : Flux enrichi contenant les news traitées par l'IA.

### 3. Intelligence Macro-Économique (Gemini 2.0 Flash)
Le script agit comme un stratège senior de Goldman Sachs :
*   **Analyse de Causalité** : Détecte les liens entre les annonces (ex: Hausse des taux FED) et l'impact sur les actifs (ex: Baisse de l'Or).
*   **Conseils Explicites** : Recommande des actions concrètes : **ACHETER**, **VENDRE** ou **ATTENDRE**.
*   **Gestion de Quota** : Système de pause intelligent pour respecter les limites de l'API gratuite Google.

### 4. Interface "Liquid Glass" (Frontend)
Une interface web moderne développée en Vanilla JS/CSS :
*   **Glassmorphism** : Effets de transparence et de flou (Backdrop Filter).
*   **Real-time WebSockets** : Mise à jour instantanée sans rafraîchissement.
*   **Code Couleur Dynamique** : Vert (Bullish/Up), Rouge (Bearish/Down), Or (Premium).

---

## 🛠️ Installation et Configuration

### Prérequis
*   Python 3.12+
*   Un cluster Kafka (Aiven recommandé)
*   Une clé API Google Gemini

### Setup Rapide
```bash
# 1. Cloner le dépôt
git clone https://github.com/joel710/kafka-bloomberg-project.git
cd kafka-bloomberg-project

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer l'environnement
# Créer un fichier .env à la racine
echo "GOOGLE_API_KEY=votre_cle_ici" > .env
```

### Lancement
```bash
python main.py
```
Le serveur sera disponible sur `http://localhost:8000`.

---

## 📊 Détails de l'Analyse Financière
*   **XAU / USD** : Représente le prix d'une once d'or. L'IA surveille ce prix comme baromètre de l'incertitude géopolitique.
*   **EUR / USD** : Principal indicateur de la santé économique européenne face au Dollar.

## 🛡️ Résilience (Mode Hybride)
Le projet est conçu pour être "Demo-Proof". Si la connexion Kafka échoue, le système bascule automatiquement en **Mode Direct (WebSocket interne)**. Cela garantit que votre présentation fonctionnera même dans des conditions réseau difficiles.

---
*Projet réalisé pour illustrer la synergie entre le Big Data (Kafka), l'IA (Gemini) et le Web moderne.*
