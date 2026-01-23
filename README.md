# Boxer Training Dashboard – Projet DevOps
## Présentation du projet :

Ce projet consiste en la conception et le déploiement d’une application web de suivi d’entraînements sportifs (boxe, musculation et entraînements hybrides), dans une démarche orientée DevOps.

L’objectif principal est de mettre en œuvre une architecture complète, depuis le développement de l’application jusqu’à son déploiement automatisé et son orchestration via Kubernetes, en appliquant les bonnes pratiques utilisées dans un environnement professionnel.

## Objectifs pédagogiques

### Ce projet a été réalisé afin de :

- Comprendre et appliquer les principes DevOps
- Mettre en place une architecture multi-services
- Conteneuriser une application avec Docker
- Automatiser le build et le déploiement avec un pipeline CI/CD
- Publier des images Docker sur un registre distant
- Déployer une application sur Kubernetes
- Exposer une application via un Ingress

### Description de l’application :

L’application permet de gérer des sessions d’entraînement sportif.
Elle est pensée pour être évolutive et adaptable à plusieurs disciplines, notamment la boxe et la musculation.

### Fonctionnalités principales :

- Interface web accessible via un navigateur
- Backend exposant une API REST
- Stockage des données dans une base de données relationnelle
- Vérification de l’état de l’application via une route de santé (health check)

### Architecture globale :

L’architecture repose sur plusieurs services indépendants communiquant entre eux :

- Un frontend web servant l’interface utilisateur
- Un backend exposant une API REST
- Une base de données MySQL pour le stockage persistant
- Un reverse proxy pour l’exposition des services
- Un pipeline CI/CD pour l’automatisation
- Un cluster Kubernetes pour l’orchestration

Le trafic utilisateur passe par un Ingress qui redirige les requêtes vers le frontend ou le backend selon le chemin demandé.

### Technologies utilisées : 

- Les technologies suivantes ont été utilisées tout au long du projet :
- Docker et Docker Compose pour la conteneurisation
- Git et GitHub pour le versionnement
- GitHub Actions pour l’intégration continue
- Docker Hub pour le stockage des images
- Kubernetes (Minikube) pour l’orchestration
- NGINX Ingress Controller pour l’exposition des service
- MySQL pour la base de données
- Flask (Python) pour le backend
- Nginx pour le frontend
- Conteneurisation avec Docker

### Chaque composant de l’application est isolé dans un conteneur distinct :

- Le frontend est servi par Nginx
- Le backend fonctionne avec un serveur Flask
- La base de données utilise une image MySQL officielle
- Docker Compose est utilisé pour faciliter l’exécution de l’ensemble des services en local et gérer les dépendances entre eux.
- Mise en place du CI/CD
- Un pipeline CI/CD a été configuré à l’aide de GitHub Actions.

### À chaque mise à jour de la branche principale :

- Les images Docker du frontend et du backend sont construites
- Les images sont automatiquement publiées sur Docker Hub
- Cela garantit que les images utilisées en production ou sur Kubernetes sont toujours à jour et cohérentes avec le code source.
- Publication des images Docker

### Les images Docker générées par le pipeline sont stockées sur Docker Hub, ce qui permet :

- Leur réutilisation sur d’autres environnements
- Un déploiement simplifié sur Kubernetes
- Une séparation claire entre build et déploiement

### Déploiement Kubernetes

L’application a été déployée sur un cluster Kubernetes local à l’aide de Minikube.

Les ressources Kubernetes utilisées sont :

- Deployments pour le frontend, le backend et la base de données
- Services pour permettre la communication interne
- Persistent Volume Claim pour assurer la persistance des données MySQL
- ConfigMap et Secret pour la configuration
- Ingress pour exposer l’application

Chaque composant fonctionne dans son propre pod et communique via les services Kubernetes.

### Exposition de l’application

L’application est exposée via un Ingress NGINX.

Un nom de domaine local est utilisé pour simuler un environnement réel.
Les requêtes vers la racine sont redirigées vers le frontend, tandis que les requêtes vers l’API sont redirigées vers le backend.

Cette approche permet d’avoir un point d’entrée unique pour l’application, comme dans un environnement de production.

### Captures d’écran

Des captures d’écran sont fournies afin d’illustrer :

- L’interface de l’application
- Le fonctionnement du pipeline CI/CD
- Les images Docker publiées
- Les pods Kubernetes en fonctionnement
- L’accès à l’application via Ingress

Ces captures sont disponibles dans le dossier dédié du projet.

### Méthodologie de travail

Pour mener à bien ce projet, j’ai adopté une approche progressive :

- Mise en place de l’application en local
- Conteneurisation des services
- Automatisation via CI/CD
- Déploiement sur Kubernetes
- Débogage et validation étape par étape

Un assistant IA a été utilisé comme outil de soutien afin de mieux comprendre certains concepts et accélérer la phase de conception, tout en conservant une implication active sur les choix techniques et leur mise en œuvre.

### Compétences développées

Ce projet m’a permis de développer les compétences suivantes :

- Compréhension globale d’une chaîne DevOps
- Conteneurisation d’une application complète
- Mise en place d’un pipeline CI/CD
- Déploiement et orchestration Kubernetes
- Gestion du stockage persistant
- Exposition sécurisée des services
- Analyse et résolution de problèmes techniques

### Conclusion

Ce projet représente une mise en pratique complète des concepts DevOps, depuis le développement jusqu’au déploiement orchestré.
Il m’a permis d’acquérir une vision concrète et réaliste du cycle de vie d’une application moderne dans un contexte professionnel.