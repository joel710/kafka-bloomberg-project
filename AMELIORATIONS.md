# Suggestions d'Amélioration - Forex Sentinel

Ce document répertorie les axes d'amélioration identifiés pour le projet **Forex Sentinel**. L'objectif est de transformer ce prototype fonctionnel en une application de production robuste, scalable et maintenable.

---

## 🏗️ 1. Architecture & Qualité du Code

### Modularisation
Actuellement, tout le projet (API, Workers, Logique Métier) est concentré dans `main.py`.
- **Action** : Séparer le code en modules :
    - `api/` : Routes FastAPI et gestion des WebSockets.
    - `workers/` : Scripts pour le Market Data et l'Analyse IA.
    - `services/` : Logique Kafka, MongoDB et client Gemini.
    - `models/` : Schémas Pydantic pour la validation des données.

### Gestion de la Configuration
Certaines valeurs comme `MONGO_URI` ou les hôtes Kafka sont partiellement codées en dur ou ont des valeurs par défaut sensibles.
- **Action** : Utiliser exclusivement `pydantic-settings` pour charger la configuration depuis le `.env` avec une validation stricte.

### Migration vers l'Asynchrone (`asyncio`)
Le projet mélange `threading` et `asyncio`.
- **Action** : Utiliser des librairies asynchrones pour tout :
    - `aiokafka` au lieu de `kafka-python`.
    - `motor` au lieu de `pymongo`.
    - Intégrer les workers directement dans la boucle d'événements de FastAPI via `asyncio.create_task`.

---

## ⚡ 2. Robustesse & Infrastructure (DevOps)

### Résilience de Kafka
La gestion actuelle de la connexion Kafka est manuelle et bloque si le broker est indisponible.
- **Action** : Implémenter une stratégie de "Backoff exponentiel" pour les reconnexions et utiliser un pool de connexions géré.

### Optimisation Docker
Le `Dockerfile` peut être optimisé pour réduire sa taille et améliorer la sécurité.
- **Action** : 
    - Utiliser des builds multi-étapes (*multi-stage builds*).
    - Passer à une image de base plus légère comme `python:3.11-slim`.
    - Ne pas lancer l'application en tant qu'utilisateur `root`.

### Observabilité
- **Action** : Ajouter des logs structurés (via `structlog` ou `loguru`) au lieu de simples `print`. Intégrer un endpoint `/health` pour que Render puisse monitorer l'état du service.

---

## 🧠 3. Intelligence Artificielle & Données

### Raffinement des Prompts
Le prompt actuel est simple. 
- **Action** : Ajouter du contexte macro-économique au prompt (ex: derniers taux de la FED, calendrier économique) pour que Gemini produise des analyses plus fines.

### Persistance & Historique
Les données sont envoyées mais peu exploitées sur le long terme.
- **Action** : Stocker systématiquement les analyses en base de données pour permettre l'affichage d'un historique ou d'un "Sentiment Score" sur les 24 dernières heures.

---

## 🎨 4. Frontend & Expérience Utilisateur

### Visualisation de Données
Le dashboard actuel n'affiche que les prix instantanés.
- **Action** : Intégrer une librairie de graphiques (ex: `Chart.js` ou `Lightweight Charts`) pour visualiser l'évolution des prix en temps réel.

### Système de Notifications
- **Action** : Ajouter des notifications de navigateur (Web Notifications API) lorsqu'une recommandation de type "ACHETER" ou "VENDRE" est générée par l'IA.

### Mode Sombre / Design
L'UI est déjà élégante ("Glassmorphism"), mais pourrait être améliorée avec :
- Un indicateur de latence pour le WebSocket.
- Un bouton pour tester manuellement la connexion aux services (Kafka, IA).

---

## 🛡️ 5. Sécurité

### Gestion des Certificats
Les fichiers `.pem`, `.cert` et `.key` sont à la racine.
- **Action** : Utiliser des secrets d'environnement (Render Secrets) pour injecter ces certificats au runtime plutôt que de les laisser traîner sur le système de fichiers, ou les stocker dans un dossier `certs/` ignoré par Git.

### Validation des Données
- **Action** : Utiliser des modèles Pydantic pour valider chaque message sortant vers le WebSocket afin d'éviter d'envoyer des données malformées au client.
