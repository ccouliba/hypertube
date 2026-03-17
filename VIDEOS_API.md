# Videos API - Documentation

## Architecture

L'API Videos est une **API unifiée** qui gère à la fois les films (movies) et les séries TV (tv_shows) à travers un seul point d'entrée `/api/videos`.

### Avantages de cette approche:

1. ✅ **Cohérence**: Un seul endpoint pour tous les contenus vidéo
2. ✅ **Simplicité**: Pas besoin de maintenir deux APIs séparées
3. ✅ **DRY**: Évite la duplication de code
4. ✅ **Flexibilité**: Paramètre `content_type` pour filtrer

## Structure des Routes

Base URL: `/api/videos`

### 1. GET /api/videos/:id
Récupère une vidéo par son ID

**Query Parameters:**
- `content_type` (required): `"movie"` ou `"tv_show"`

**Exemple:**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:5000/api/videos/1?content_type=movie"
```

### 2. GET /api/videos/
Récupère toutes les vidéos

**Query Parameters:**
- `content_type` (optional): `"movie"`, `"tv_show"`, ou `"all"` (default: `"all"`)

**Exemples:**
```bash
# Toutes les vidéos (movies + tv_shows)
curl -H "Authorization: Bearer <token>" \
  "http://localhost:5000/api/videos/"

# Seulement les films
curl -H "Authorization: Bearer <token>" \
  "http://localhost:5000/api/videos/?content_type=movie"

# Seulement les séries TV
curl -H "Authorization: Bearer <token>" \
  "http://localhost:5000/api/videos/?content_type=tv_show"
```

**Response (all):**
```json
{
  "videos": [...],
  "total": 25,
  "movies_count": 15,
  "tvshows_count": 10
}
```

**Response (filtered):**
```json
{
  "videos": [...],
  "total": 15,
  "content_type": "movie"
}
```

### 3. PATCH /api/videos/:id
Met à jour une vidéo

**Query Parameters:**
- `content_type` (required): `"movie"` ou `"tv_show"`

**Body:**
```json
{
  "viewed": true,
  "last_watched": "2026-01-08T13:00:00Z"
}
```

**Exemple:**
```bash
curl -X PATCH \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"viewed": true}' \
  "http://localhost:5000/api/videos/1?content_type=movie"
```

### 4. DELETE /api/videos/:id
Supprime une vidéo

**Query Parameters:**
- `content_type` (required): `"movie"` ou `"tv_show"`

**Exemple:**
```bash
curl -X DELETE \
  -H "Authorization: Bearer <token>" \
  "http://localhost:5000/api/videos/1?content_type=movie"
```

### 5. GET /api/videos/downloaded
Récupère toutes les vidéos téléchargées

**Query Parameters:**
- `content_type` (optional): `"movie"`, `"tv_show"`, ou `"all"` (default: `"all"`)

**Exemple:**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:5000/api/videos/downloaded?content_type=all"
```

## Services Backend

### Architecture en couches:

```
videos/
├── models.py          # Abstract Video (base pour Movie et TVShow)
├── dao.py             # Abstract VideoDAO (CRUD operations)
├── service.py         # Abstract VideoService (business logic)
├── api.py             # Unified API (routes communes)
│
├── movies/            # Sous-domaine Movies
│   ├── models.py      # Movie (hérite de Video)
│   ├── dao.py         # MovieDAO (hérite de VideoDAO)
│   └── service.py     # MovieService (hérite de VideoService)
│
└── tvshows/           # Sous-domaine TV Shows
    ├── models.py      # TVShow (hérite de Video)
    ├── dao.py         # TVShowDAO (hérite de VideoDAO)
    └── service.py     # TVShowService (hérite de VideoService)
```

### Services disponibles:

```python
from src.videos.movies.service import movie_service
from src.videos.tvshows.service import tvshow_service

# Méthodes communes (héritées de VideoService)
movie_service.get_all()                    # Liste tous les films
movie_service.get_by_id(id)                # Film par ID
movie_service.update(id, data)             # Met à jour un film
movie_service.delete(id)                   # Supprime un film
movie_service.get_downloaded()             # Films téléchargés

# Méthodes spécifiques (ajoutées dans les services enfants)
movie_service.get_movie_by_id(id)          # Retourne dict
movie_service.get_all_movies()             # Retourne list[dict]
movie_service.update_movie(id, data)       # Retourne dict
movie_service.delete_movie(id)             # Retourne bool

# Même chose pour tvshow_service
tvshow_service.get_tvshow_by_id(id)
tvshow_service.get_all_tvshows()
tvshow_service.update_tvshow(id, data)
tvshow_service.delete_tvshow(id)
```

## Migration depuis l'ancienne API

### Avant (movies endpoint):
```javascript
// Frontend
const response = await fetch('/api/movies/1');
```

### Maintenant (videos endpoint):
```javascript
// Frontend
const response = await fetch('/api/videos/1?content_type=movie');
```

### Exemple de mise à jour du frontend:

```typescript
// api/videoService.ts
export const getVideo = async (id: number, contentType: 'movie' | 'tv_show') => {
  const response = await fetch(`/api/videos/${id}?content_type=${contentType}`);
  return response.json();
};

export const getAllVideos = async (contentType: 'movie' | 'tv_show' | 'all' = 'all') => {
  const response = await fetch(`/api/videos/?content_type=${contentType}`);
  return response.json();
};

export const updateVideo = async (
  id: number, 
  contentType: 'movie' | 'tv_show',
  data: any
) => {
  const response = await fetch(
    `/api/videos/${id}?content_type=${contentType}`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }
  );
  return response.json();
};
```

## Pourquoi cette architecture?

### ✅ Avantages:

1. **Point d'entrée unique**: `/api/videos` pour tous les contenus
2. **Code mutualisé**: Toute la logique commune dans VideoService
3. **Extensibilité**: Facile d'ajouter un nouveau type (documentaries, shorts, etc.)
4. **Type safety**: Polymorphisme SQLAlchemy avec `content_type` discriminator
5. **Frontend simplifié**: Une seule API à consommer

### 🎯 Cas d'usage:

- **Recherche unifiée**: Chercher dans tous les contenus
- **Téléchargements**: Voir tous les téléchargements (films + séries)
- **Statistiques**: Compter facilement les contenus par type
- **Recommandations**: Suggérer des films OU des séries

### 📊 Comparaison:

| Aspect | API Séparées | API Unifiée |
|--------|-------------|-------------|
| Endpoints | `/api/movies`, `/api/tvshows` | `/api/videos` |
| Code dupliqué | Beaucoup | Minimal |
| Maintenance | 2x effort | 1x effort |
| Frontend calls | 2 services | 1 service |
| Filtrage | Par URL | Par paramètre |
| Extensibilité | Ajouter nouveau blueprint | Ajouter enum |
