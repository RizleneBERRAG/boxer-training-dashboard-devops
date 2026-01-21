# Boxer Training Dashboard (DevOps)

Projet DevOps (solo) : mise en place d’une architecture conteneurisée avec Docker et orchestrée via Docker Compose, autour d’une application simple de suivi d’entraînements de boxe.

- **Étudiante** : BERRAG Rizlene  
- **Dépôt** : https://github.com/RizleneBERRAG/boxer-training-dashboard-devops  
- **Base de données** : MySQL  
- **Orchestration** : Docker Compose

---

## 1. Objectif
L’application permet de gérer des séances d’entraînement de boxe (ex : date, durée, intensité).  
L’objectif principal du projet est de démontrer une **approche DevOps propre** : architecture claire, conteneurisation, orchestration, documentation et suivi Git.

---

## 2. Architecture cible
Le projet sera composé de 4 services :

- **proxy (Nginx)** : reverse proxy et routage
- **frontend** : page web statique
- **backend (API)** : service applicatif (API)
- **db (MySQL)** : stockage des données

Flux attendu :
- `/` → frontend
- `/api` → backend
- backend → MySQL

Un schéma d’architecture sera maintenu dans `architecture.puml`.

---

## 3. Lancement (à venir)
Les commandes ci-dessous seront valides lorsque la stack Docker Compose sera en place :

```bash
docker compose up --build
