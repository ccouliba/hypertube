# Hypertube – Documentation Technique

## Architecture Générale

### Backend
- **API REST Flask** (auth, vidéos, recherche, torrents)
- **Celery** pour les tâches asynchrones (téléchargements, maintenance)
- **PostgreSQL** (base de données)
- **Redis** (broker Celery)
- **qBittorrent** (client P2P)

### Frontend
- Organisation par features (auth, vidéos, etc.)
- Séparation claire UI / logique métier / hooks / services

---

## Configuration & Secrets
- Toutes les variables sensibles sont dans `.env` (jamais versionné)
- Exemple de variables :
  - DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT
  - YTS_BASE_URL, EZTV_BASE_URL, TMDB_API_KEY, etc.
- Pour changer une URL d’API ou une clé, modifie `.env` ou les fichiers `config.py` de chaque service.

---

## API Principales

### Authentification
- `/api/auth/register` : Inscription
- `/api/auth/login` : Connexion
- `/api/auth/users` : Liste des utilisateurs

### Vidéos
- `/api/videos/` : Liste tous les contenus (movies + tv_shows)
- `/api/videos/<id>` : Détail d’un contenu
- Paramètre `content_type` pour filtrer (movie, tv_show, all)
- PATCH pour mettre à jour, POST pour marquer comme vu

### Recherche
- `/api/search` : Recherche unifiée sur tous les providers (YTS, EZTV, etc.)

### Torrents
- `/api/torrents/download` : Démarrer un téléchargement (asynchrone via Celery)
- `/api/torrents/status/<hash>` : Statut d’un téléchargement
- `/api/torrents/task/<task_id>` : Statut d’une tâche Celery

---

## Tâches Asynchrones & Maintenance
- **Celery** gère les téléchargements et le nettoyage automatique des vieux films.
- Nettoyage automatique : suppression des films non vus depuis 30 jours (configurable).
- Tâches planifiées via Celery Beat.

---

## Gestion des Erreurs
- Toutes les erreurs API utilisent la classe `APIError` et des messages standardisés (`ERROR_MESSAGES`).
- Codes HTTP utilisés : 400, 401, 403, 404, 409, 415, 422, 500.
- Messages d’erreur centralisés pour l’auth, la validation, la recherche, les vidéos.

---

## Projection
- **Sécurité** : Jamais de secrets en dur, toujours dans `.env`.
- **Non-root Docker** : Tous les services Python tournent sous un utilisateur non-root.
- **PYTHONPATH** : Uniformisé à `/app` dans tous les conteneurs Python.
- **Imports** : Toujours absolus, structure de projet claire.
- **Tests** : Prévoir des tests unitaires pour chaque service.

---

## Démarrage rapide

```bash
cp .env.example .env
# Édite .env avec tes vraies valeurs

docker compose up --build
```

---

## Structure des dossiers (exemple backend)

```
app/
├── api/           # Routes Flask
├── core/          # Middlewares, erreurs, CORS
├── db/            # Modèles et init DB
├── services/      # Logique métier (auth, video,torrent, search)
├── tasks/         # Tâches Celery
├── app.py         # Entrée principale Flask
├── requirements.txt
```