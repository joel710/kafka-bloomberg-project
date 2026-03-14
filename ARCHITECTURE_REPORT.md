# 🏗️ Rapport d'Architecture Système : Forex Sentinel Intelligence

Ce document présente la conception technique et l'intégration des composants du projet **Forex Sentinel**. En tant qu'Architecte Système, l'objectif est de démontrer la fluidité, la sécurité et la résilience de la chaîne de données.

---

## 1. Schéma d'Architecture Global

Le système repose sur une architecture **Event-Driven (Pilotée par les événements)** où chaque composant est découplé.

```mermaid
graph TD
    subgraph "1. Ingestion (Producers)"
        A[Yahoo Finance API] -- "Prix Spot (1s)" --> K1
        B[RSS Feeds (CNBC/Yahoo)] -- "Titres bruts" --> K2
    end

    subgraph "2. Streaming & Cloud (Aiven Kafka)"
        K1((Topic: market-data))
        K2((Topic: raw-news))
        K3((Topic: analyzed-news))
    end

    subgraph "3. Intelligence (Stream Processing)"
        K2 -- "Consommation" --> C[Processeur IA Gemini 2.0]
        C -- "Analyse & Rec" --> K3
    end

    subgraph "4. Frontend & Livraison (FastAPI)"
        K1 -- "Streaming" --> D[Bridge WebSocket]
        K3 -- "Streaming" --> D
        D -- "Temps Réel" --> E[Interface Liquid Glass]
    end

    subgraph "5. Persistance"
        K1 -- "Archivage" --> F[(MongoDB Atlas)]
        K3 -- "Archivage" --> F
    end
```

---

## 2. La Stack Technique (The Stack)

### Pourquoi Aiven Kafka ?
Le choix d'**Aiven** comme fournisseur Cloud pour Kafka a été dicté par :
*   **Haute Disponibilité** : Cluster managé avec réplication automatique des données.
*   **Sécurité SSL Native** : Tous les échanges entre nos scripts Python et le Cloud sont chiffrés via des certificats (CA, Certificat Client, Clé Privée).
*   **Scalabilité** : Capacité à gérer des milliers de messages par seconde sans latence.

### Ingestion Hybride
*   **Données Quantitatives** : Utilisation de `yfinance` pour le flux financier.
*   **Données Qualitatives** : Agrégateur multi-sources RSS pour ne rater aucune nouvelle mondiale.

---

## 3. La Résilience : Le "Mode Direct" (Smart Fallback)

Une architecture robuste doit prévoir l'imprévisible. Forex Sentinel intègre un mécanisme de **bascule automatique (Failover)**.

**Le scénario de crise :** Si le cluster Kafka devient injoignable (panne réseau ou maintenance) :
1.  Le système détecte l'échec de connexion via un bloc `try/except` sur le Producer.
2.  Il bascule instantanément en **Mode Direct**.
3.  Les données sont poussées **directement des threads d'ingestion vers le bridge WebSocket**, contournant Kafka.
4.  **Résultat** : Pour l'utilisateur final, le dashboard reste "vivant" et fonctionnel sans interruption.

---

## 4. Intelligence Artificielle & Traitement
Le traitement n'est pas passif. Nous utilisons le modèle **Gemini 2.0 Flash** pour transformer une news brute en donnée structurée.
*   **Input** : Titre de presse (ex: "La FED maintient ses taux").
*   **Logic** : Analyse de causalité macro-économique.
*   **Output** : JSON contenant l'impact (Bullish/Bearish) et une recommandation explicite (ACHETER/VENDRE).

---

## 5. Interface Utilisateur (UI/UX)

### Design "Liquid Glass"
L'interface utilise le **Glassmorphism**, un style moderne inspiré des systèmes d'exploitation futuristes :
*   **Translucidité** : Utilisation massive de `backdrop-filter: blur()`.
*   **Clarté** : Typographie Inter (OpenAI style) pour une lisibilité maximale.

### Communication Temps Réel
Au lieu du traditionnel polling (rafraîchissement toutes les X secondes), nous utilisons les **WebSockets**. 
*   **Flux poussé (Push)** : C'est le serveur qui envoie la donnée dès qu'elle arrive.
*   **Latence** : Moins de 100ms entre la capture du prix et l'affichage sur l'écran.

---
**Architecte Système** : Joel710
**Technologies** : Kafka, FastAPI, Gemini AI, MongoDB, WebSockets.
