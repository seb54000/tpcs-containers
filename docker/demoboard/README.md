# Demoboard – microservices de démonstration

Une mini‑application pensée pour les TP : un tableau de tâches avec une API FastAPI, un worker Python, un frontend Vue 3 et deux briques d'infrastructure (PostgreSQL + Redis). Chaque service a son Dockerfile pour être déployé sur une VM, via Docker Compose ou empaqueté pour Kubernetes.

## Architecture

```
docker/demoboard
├── api-service          # FastAPI + PostgreSQL
├── worker-service       # Worker Python + Redis + PostgreSQL
├── frontend-service     # Vue 3 + Vite + Nginx
├── docker-compose.yml   # Orchestration locale
└── README.md            # Ce document
```

- **frontend-service** : interface Vue 3/Vite, buildée puis servie par Nginx. L'appel `/api` est automatiquement proxifié vers `api-service`.
- **api-service** : FastAPI expose CRUD `/tasks` + endpoint `/tasks/{id}/start-job`. La base est initialisée au démarrage.
- **worker-service** : worker Python en écoute sur Redis, simule un traitement long puis met à jour PostgreSQL.
- **db-service** : PostgreSQL 15 pour stocker les tâches.
- **queue-service** : Redis 7 pour les jobs (liste `jobs`). La mise en file se fait via `publish_job`.

## Démarrage rapide (Docker Compose)

```bash
cd docker/demoboard
docker compose up --build
```

Services exposés :

| Service            | Port hôte | Description                         |
| ------------------ | --------- | ----------------------------------- |
| frontend-service   | 8080      | UI Vue (http://localhost:8080)      |
| api-service        | 8000      | API FastAPI (http://localhost:8000) |
| db (PostgreSQL)    | 5432      | Base de données                     |
| redis              | 6379      | File de jobs                        |

Arrêt : `docker compose down` (ajoutez `-v` pour supprimer aussi les volumes PostgreSQL).

## API utile pendant le TP

- `GET /tasks` : liste les tâches.
- `POST /tasks` : crée une tâche `{ "title": "..." }`.
- `GET /tasks/{id}` : détail.
- `PUT /tasks/{id}` : met à jour `title` et/ou `status`.
- `DELETE /tasks/{id}` : supprime.
- `POST /tasks/{id}/start-job` : passe la tâche en `processing`, envoie un message Redis, le worker termine et met `completed`.
- `GET /healthz` : ping rapide.

## Développement local sans Compose

1. Lancer Postgres + Redis (via `docker compose up db redis` ou vos services locaux).
2. **API**
   ```bash
   cd api-service
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
3. **Worker**
   ```bash
   cd worker-service
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   python worker.py
   ```
4. **Frontend**
   ```bash
   cd frontend-service
   npm install
   npm run dev -- --host
   ```
   Le proxy Vite redirige `/api` vers `http://localhost:8000`.

## Déploiement Kubernetes (pistes)

- Construire/pusher les images `api-service`, `worker-service`, `frontend-service`.
- Créer des manifests (Deployment + Service) pour chaque composant, ajouter un `StatefulSet`/`Deployment` pour PostgreSQL & Redis ou utiliser des offres managées.
- Injecter la configuration (variables `DB_*`, `REDIS_*`, `VITE_API_URL`) via ConfigMap/Secret.

Le dossier `kubernetes/` du dépôt pourra accueillir ces manifests pour aller plus loin en TP.
