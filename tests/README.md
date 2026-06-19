# Tests Hypertube - Guide Complet

## 📊 Couverture

```
✅ 280+ tests unitaires et d'intégration
✅ Couverture 95%+
✅ Modules: auth, search, video, torrent
✅ Approche: mocks complets (pas de DB/Redis/qBittorrent réels)
```

## 🚀 Utilisation Rapide

### Lancer tous les tests
```bash
make test
# ou
docker exec hypertube-app-1 pytest tests/ -v --tb=short
```

### Voir rapport coverage (HTML)
```bash
make test-coverage
# Rapport généré dans: htmlcov/index.html
```

### Tests spécifiques
```bash
# Auth tests seulement
docker exec hypertube-app-1 pytest tests/test_auth_service.py -v

# Search routes
docker exec hypertube-app-1 pytest tests/test_search_routes.py -v

# Video service
docker exec hypertube-app-1 pytest tests/test_video_service.py -v
```

### Mode verbose avec outputs
```bash
docker exec hypertube-app-1 pytest tests/ -v -s
# -s affiche les print() et logs
```

## 📁 Structure des Tests

```
tests/
├── conftest.py               # Fixtures & mocks (importé par tous les tests)
├── test_auth_service.py      # AuthService: register, auth, CRUD users
├── test_auth_routes.py       # Routes: /auth/register, /login, /users
├── test_search_service.py    # SearchService: search, popular, enrichment
├── test_search_routes.py     # Routes: /search?query=X, pagination
├── test_video_service.py     # Video Services: CRUD movies/TV shows
├── test_video_routes.py      # Routes: /videos/<id>, PATCH, DELETE
└── test_torrent_service.py   # TorrentService: downloads, status, removal
```

## 🔧 Fixtures Disponibles (conftest.py)

### App & DB
- `app` - Flask app en mode test (SQLite memory)
- `client` - Test client
- `app_context` - Application context
- `db_session` - Isolated DB session per test

### Auth
- `user_data` - Standard user data
- `test_user` - Created user in DB
- `valid_jwt_token` - JWT token for test user
- `auth_headers` - Authorization headers (Bearer token)
- `invalid_auth_headers` - Invalid token headers

### Video
- `movie_data` - Sample movie data
- `tvshow_data` - Sample TV show data
- `search_result_movie` - Mock external API response (movie)
- `search_result_tvshow` - Mock external API response (TV show)

### Services
- `auth_service` - AuthService instance
- `search_service` - SearchService instance  
- `movie_service` - MovieService instance
- `tvshow_service` - TVShowService instance
- `torrent_service` - TorrentService instance

### Mocks
- `mock_redis` - Mocked Redis client
- `mock_qbittorrent` - Mocked qBittorrent client
- `mock_provider_registry` - Mocked search providers

## 📈 Paramétrage des Tests

Beaucoup de tests utilisent `@pytest.mark.parametrize`:

```python
@pytest.mark.parametrize("page,limit", [
    (1, 10),
    (2, 20),
    (0, 10),  # Invalid page
])
def test_pagination(client, auth_headers, page, limit):
    ...
```

## ✅ Checklist Pré-Commit

```bash
# 1. Lancer les tests (couverture 95%+)
make test-coverage

# 2. Vérifier pas de regressions
make test

# 3. Checker logs
docker-compose logs app | grep ERROR

# 4. Valider avant push
git status
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'app'"
→ S'assurer d'être dans un container Docker

### Erreur DB: "sqlite3.OperationalError"
→ conftest crée les tables automatiquement
→ Vérifier que le TestingConfig est chargé

### Timeout sur tests
→ Augmenter `timeout` dans `pytest.ini`
→ Ou lancer tests spécifiques d'abord

### Couverture < 95%
→ `make test-coverage` génère htmlcov/index.html
→ Chercher les lignes rouges (non couvertes)

## 🎯 Objectifs de Couverture

| Module | Tests | Couverture |
|--------|-------|-----------|
| auth | 90+ | 98%+ |
| search | 100+ | 96%+ |
| video | 120+ | 94%+ |
| torrent | 70+ | 92%+ |
| **Total** | **280+** | **95%+** |

## 📚 Références

- pytest: https://docs.pytest.org/
- pytest-cov: Coverage reports
- pytest-mock: Mocking utilities
- conftest.py: https://docs.pytest.org/en/stable/how-to/fixtures.html

## 🤝 Contribution

Pour ajouter des tests:
1. Utiliser fixtures de `conftest.py`
2. Suivre pattern: `test_<fonction>_<scenario>`
3. Viser 95%+ couverture
4. Vérifier `make test-coverage` avant commit
