# HyperTube

Plateforme de streaming de films et séries via torrents.

---

## Stack

### Backend
| Technologie | Rôle |
|---|---|
| **Flask 3** | Framework web, Application Factory Pattern |
| **flask-smorest** | Blueprints OpenAPI 3 — génère la spec et Swagger UI automatiquement |
| **Marshmallow** | Validation et sérialisation des données entrantes/sortantes |
| **flask-migrate** (Alembic) | Migrations de schéma BDD versionnées |
| **Flask-SQLAlchemy** | ORM, modèles, sessions |
| **PostgreSQL** | Base de données relationnelle |
| **Celery + Redis** | Tâches asynchrones (téléchargements, maintenance planifiée) |
| **qBittorrent** | Client BitTorrent piloté via son API WebUI |
| **Flask-CORS** | Politique CORS explicite |

### Frontend
| Technologie | Rôle |
|---|---|
| **React 18 + TypeScript** | UI, Vite comme bundler |
| **Redux Toolkit** | État global (auth, session) |
| **Axios** | Client HTTP avec interceptors JWT |
| **styled-components** | Theming et styles isolés par composant |
| **openapi-typescript** | Génère `src/types/api.d.ts` depuis la spec OpenAPI du backend |

---

## Démarrage

```bash
cp .env.example .env
# Renseigner DB_USER, DB_PASSWORD, DB_NAME, JWT_SECRET_KEY, TMDB_API_KEY, etc.

docker compose up --build
```

- Backend + Swagger UI : `http://localhost:5000/api/docs`
- Frontend : `http://localhost:3000`
- qBittorrent WebUI : `http://localhost:8080`

Pour regénérer les types TypeScript depuis la spec (backend doit être démarré) :

```bash
cd front && npm run generate:api
```

---

## API

Spec complète disponible sur `/api/docs` (Swagger UI) ou `/api/openapi.json`.

| Préfixe | Description |
|---|---|
| `GET /api/info` | Métadonnées de l'API (version, liens docs) |
| `/api/auth` | Inscription, connexion, gestion des utilisateurs |
| `/api/video` | Catalogue, détail, marquage comme vu |
| `/api/search` | Recherche unifiée (YTS, EZTV, TMDb) |

Toutes les routes protégées attendent un header `Authorization: Bearer <token>`.

---

## Tâches asynchrones

Celery orchestre deux workflows :

- **Téléchargement** : `start → monitor (polling 30s) → process` — déclenché par POST sur `/api/video/<id>/download`
- **Maintenance** : suppression quotidienne des vidéos non vues depuis N jours (Celery Beat)

---

## Sécurité

- Secrets exclusivement dans `.env` (non versionné)
- JWT stocké **en mémoire** côté front (Redux), jamais en localStorage
- Conteneurs Python en mode non-root
- Mots de passe : lettre + chiffre + caractère spécial obligatoires (validé par Marshmallow)

---

## Structure

```
app/
├── api/          # Routes flask-smorest (blueprints)
├── schemas/      # Schémas Marshmallow (contrats d'API)
├── services/     # Logique métier (auth, video, search, torrent, maintenance)
├── tasks/        # Orchestration Celery (downloads, maintenance)
├── core/         # Config, erreurs, CORS, JWT
└── db/           # Session SQLAlchemy, migrations Alembic

front/src/
├── api/          # Instance Axios + interceptors
├── services/     # Appels API par domaine
├── store/        # Redux slices
├── hooks/        # Custom hooks
├── features/     # Pages par domaine
└── types/        # Interfaces (api.d.ts généré, types manuels)
```
