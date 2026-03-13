# 🏗️ Architecture Kafka : Forex Sentinel Intelligence

Ce document détaille comment Apache Kafka est utilisé pour orchestrer les flux de données temps réel dans ce projet.

## 1. Pourquoi Kafka ?
Dans un système financier, la latence et la fiabilité sont critiques. Kafka a été choisi pour :
*   **Découplage total** : Les producteurs (Yahoo Finance, RSS) ne connaissent pas les consommateurs (IA, MongoDB, Dashboard).
*   **Gestion des pics de charge** : Si l'IA est lente à répondre, Kafka stocke les news en attente sans bloquer le reste du système.
*   **Multi-consommation** : Un seul message de prix peut être lu simultanément par le Dashboard ET par l'archiviste MongoDB.

## 2. Structure des Topics

Le projet utilise deux topics principaux sur le cluster Aiven :

### 📡 `market-data`
*   **Rôle** : Transmet les variations de prix spot.
*   **Format** : JSON `{"asset": "XAU/USD", "price": 2350.12, "timestamp": ...}`
*   **Fréquence** : Haute (1 message/seconde).

### 🧠 `analyzed-news`
*   **Rôle** : Transmet les news après traitement par l'IA.
*   **Format** : JSON enrichi `{"headline": "...", "recommendation": "ACHETER OR", "reason": "...", ...}`
*   **Fréquence** : Modérée (selon l'actualité mondiale).

## 3. Flux de Données (Data Pipeline)

Le cycle de vie d'une donnée dans ce projet suit ce chemin :

1.  **Ingestion** : Le `market_worker` et le `ai_news_worker` récupèrent les données externes.
2.  **Production** : Les workers envoient ces données brutes vers Kafka via le `KafkaProducer`.
3.  **Traitement (Stream Processing)** : Le thread IA consomme les news brutes, interroge Gemini, et republie le résultat "intelligent" dans le topic `analyzed-news`.
4.  **Consommation** :
    *   **Bridge WebSocket** : Consomme les topics pour mettre à jour l'interface Web.
    *   **Archiviste DB** : Consomme les topics pour sauvegarder l'historique dans MongoDB.

## 4. Configuration de Sécurité
La connexion au cluster Aiven est sécurisée par le protocole **SSL/TLS** :
*   `ca.pem` : Certificat de l'autorité de certification.
*   `service.cert` : Certificat client pour l'authentification.
*   `service.key` : Clé privée pour le chiffrement.

## 5. Résilience et Fallback
Le code inclut un **Mode Direct** : si le cluster Kafka est inaccessible (réseau, maintenance), le système bascule automatiquement sur une communication interne via WebSockets pour garantir que le Dashboard reste fonctionnel pendant la démo.
