# 🌍 Forex Sentinel: Intelligence de Marché Temps Réel avec Kafka & IA

Forex Sentinel est une plateforme de surveillance financière avancée capable d'agréger des flux de données hétérogènes (prix du marché et actualités mondiales) pour générer des recommandations d'investissement en temps réel grâce à l'Intelligence Artificielle.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![Kafka](https://img.shields.io/badge/streaming-Kafka-orange)
![AI](https://img.shields.io/badge/IA-Gemini--1.5-purple)

## 🚀 Architecture du Système

Le projet repose sur une architecture **événementielle (Event-Driven)** totalement découplée grâce à Apache Kafka :

1.  **Ingestion (Producers)** : Flux de données réels depuis Yahoo Finance (Prix) et des flux RSS mondiaux (News).
2.  **Streaming (Kafka)** : Orchestration et transit des données via un cluster managé sur Aiven.
3.  **Intelligence (Processeur IA)** : Analyse sémantique des news par **Google Gemini** pour déterminer l'impact et produire des recommandations.
4.  **Visualisation (Frontend)** : Dashboard temps réel "Liquid Glass" alimenté par WebSockets via FastAPI.
5.  **Persistance** : Archivage historique de toutes les transactions dans **MongoDB Atlas**.

---

## 🛠️ Composants Techniques

### 📡 Les Producers (Producteurs)
*   **Market Producer** : Utilise l'API `yfinance` pour extraire le prix spot de l'Or (**XAU/USD**) et le taux de change de l'Euro (**EUR/USD**).
    *   *Fréquence* : ~1 seconde.
    *   *Fonctionnalité* : Ajout d'un jitter visuel pour une fluidité totale sur le dashboard.
*   **News Producer** : Scanne plusieurs flux RSS (CNBC, Yahoo Finance, MarketWatch) pour capturer les événements économiques mondiaux dès leur publication.

### 🧠 Le Processeur d'IA (Consumer/Producer)
*   **Logique** : Il consomme les news brutes, interroge le LLM **Gemini 1.5 Flash**, et produit un message enrichi.
*   **Format de sortie** : JSON strict contenant l'impact (Bullish/Bearish), une raison technique et une **recommandation explicite** (ACHETER/VENDRE/ATTENDRE).

### 🌉 Le Pont WebSocket (Bridge)
*   Implémenté avec **FastAPI**, il sert de passerelle entre le monde binaire de Kafka et le protocole WebSocket du navigateur, garantissant une latence proche de zéro.

---

## 💻 Installation et Lancement

### Préréquis
*   Un cluster Kafka (ex: **Aiven**) avec les certificats SSL (`ca.pem`, `service.cert`, `service.key`).
*   Une clé API **Google Gemini** (gratuite sur AI Studio).
*   Une instance **MongoDB** (pour l'archivage).

### Installation
```bash
# Cloner le projet
git clone https://github.com/joel710/kafka-bloomberg-project.git
cd kafka-bloomberg-project

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install fastapi uvicorn kafka-python-ng yfinance feedparser google-generativeai pymongo
```

### Lancement Unifié
Le projet est conçu pour être lancé avec une seule commande gérant tous les workers en parallèle :
```bash
export GOOGLE_API_KEY="VOTRE_CLE_GEMINI"
python3 main.py
```
Accédez ensuite au dashboard sur : `http://localhost:8000`

---

## 📊 APIs Utilisées
*   **Yahoo Finance (`yfinance`)** : Flux de prix boursiers en direct.
*   **Google Gemini AI** : Analyse sémantique et aide à la décision.
*   **Aiven Kafka** : Infrastructure de message-broker hautement disponible.
*   **CNBC / Yahoo / Reuters** : Sources d'actualités via RSS.

## 🎨 Interface Utilisateur
Le Dashboard utilise les dernières tendances du Web Design :
*   **Glassmorphism** : Effets de flou et de transparence (Liquid Glass).
*   **Dark Mode Pro** : Palette de couleurs inspirée des terminaux Bloomberg.
*   **Dynamic Visuals** : Changement de couleur instantané (Vert/Rouge) selon les variations de prix.

---

## 🔒 Sécurité
*   Les certificats SSL ne sont jamais inclus dans le dépôt.
*   La gestion de la clé API se fait via les variables d'environnement.

---
*Projet réalisé pour démontrer la puissance du traitement de données en temps réel avec Kafka.*
