# APIs d’Analyse de Rapports Médicaux (FastAPI)

API REST FastAPI pour :
- gérer l’authentification JWT (register, login, refresh),
- uploader un fichier PDF,
- extraire/analyser le contenu via un LLM local,
- sauvegarder les rapports dans MongoDB,
- exposer la consultation des rapports d’un utilisateur authentifié.

Architecture en couches : `routers` (HTTP), `services` (métier), `repositorys` (accès DB).

---

## 1) Fonctionnalités

- **Authentification JWT**
  - `POST /register`
  - `POST /login`
  - `POST /refresh`
- **Pipeline PDF médical**
  1. validation du fichier (présence + extension `.pdf`),
  2. extraction texte avec `PyPDF2`,
  3. classification du document (médical / non médical) via LLM,
  4. extraction JSON structurée via LLM,
  5. sauvegarde en collection `reports` MongoDB.
- **Accès protégé**
  - Toutes les routes `/reports` nécessitent un token Bearer valide.
- **Isolation des données**
  - Un utilisateur ne peut consulter que ses propres rapports.

---

## 2) Stack technique

- **Framework API** : FastAPI
- **Serveur ASGI** : Uvicorn
- **Base de données** : MongoDB (`pymongo`)
- **Auth/Sécurité** : JWT (`python-jose`) + hash mot de passe (`bcrypt`)
- **Validation** : Pydantic v2 + `email-validator`
- **Traitement PDF** : `PyPDF2`
- **Client HTTP LLM** : `requests`
- **Chargement env** : `python-dotenv`

Le service d’analyse appelle :
- endpoint : `http://localhost:11434/api/generate`
- modèle : `mistral`

---

## 3) Structure réelle du projet

```text
src/
├── core/
│   ├── config.py
│   ├── connection.py
│   └── security.py
├── repositorys/
│   ├── auth_repository.py
│   └── report_repository.py
├── routers/
│   ├── login_router.py
│   ├── refresh_router.py
│   ├── register_router.py
│   └── report_router.py
├── schemas/
│   └── user_schema.py
├── services/
│   ├── inputs_validator_service.py
│   ├── login_service.py
│   ├── register_service.py
│   └── report_service.py
├── main.py
├── requirements.txt
└── Procfile
```

---

## 4) Prérequis

- Python **3.10+**
- MongoDB accessible
- Service LLM local actif sur `localhost:11434` (ex: Ollama)

---

## 5) Installation

Depuis le dossier `src` :

```bash
python -m venv venv
```

### Windows (PowerShell)

```powershell
.\venv\Scripts\Activate.ps1
```

### Installer les dépendances

```bash
pip install -r requirements.txt
```

### Installer et lancer Ollama (Mistral)

1. Installer Ollama
   - Windows : https://ollama.com/download/windows
   - macOS : `brew install ollama`
   - Linux : `curl -fsSL https://ollama.com/install.sh | sh`

2. Démarrer Ollama

```bash
ollama serve
```

3. Télécharger le modèle

```bash
ollama pull mistral
```

4. Lancer le modèle

```bash
ollama run mistral
```

---

## 6) Configuration (.env)

Créer un fichier `.env` à la racine de `src`.

### Variables utilisées par le code

```env
APP_NAME=PFA APIs

# MongoDB
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=pfa_db

# JWT
JWT_SECRET=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (obligatoire dans l'état actuel)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Important

- Dans l’état actuel, `CORS_ORIGINS` doit être défini (sinon erreur au démarrage lors du parsing).
- `MONGO_URI`, `DATABASE_NAME`, `JWT_SECRET` et `JWT_ALGORITHM` doivent être présents.

---

## 7) Démarrage

### Développement

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API : `http://localhost:8000`
- Swagger : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

### Production (Procfile)

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 8) Endpoints

## Authentification

### `POST /register`

Body JSON :

```json
{
  "name": "Jean Dupont",
  "email": "jean@example.com",
  "password": "MotDePasse123!"
}
```

Réponse succès :

```json
{
  "message": "utilisateur ajoute avec succes"
}
```

### `POST /login`

Body JSON :

```json
{
  "email": "jean@example.com",
  "password": "MotDePasse123!"
}
```

Réponse succès :

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {
    "id": "65f...",
    "name": "Jean Dupont",
    "email": "jean@example.com"
  }
}
```

### `POST /refresh`

Body JSON :

```json
{
  "refresh_token": "..."
}
```

Réponse succès :

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

## Rapports médicaux (protégés JWT)

En-tête requis :

```http
Authorization: Bearer <access_token>
```

### `POST /reports`

Upload PDF via `multipart/form-data` (champ `file`).

Réponse succès :

```json
{
  "success": true,
  "document_id": "65f..."
}
```

### `GET /reports`

Retourne les rapports du user connecté.

Réponse succès :

```json
{
  "success": true,
  "reports": []
}
```

### `GET /reports/{report_id}`

Retourne un rapport précis (si propriétaire).

Réponse succès :

```json
{
  "success": true,
  "report": {}
}
```

---

## 9) Exemple rapide avec curl

```bash
# 1) Register
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"Jean Dupont","email":"jean@example.com","password":"MotDePasse123!"}'

# 2) Login
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"jean@example.com","password":"MotDePasse123!"}'

# 3) Refresh
curl -X POST "http://localhost:8000/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"REFRESH_TOKEN"}'

# 4) Upload PDF
curl -X POST "http://localhost:8000/reports" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -F "file=@rapport.pdf"

# 5) Lister les rapports
curl -X GET "http://localhost:8000/reports" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

---

## 10) Codes d’erreur fréquents

- `400` : validation métier (PDF invalide, document non médical, etc.)
- `401` : authentification/token invalide ou expiré
- `403` : accès à un rapport non autorisé
- `404` : rapport introuvable
- `500` : erreur serveur interne

---

## 11) Limites connues (état actuel)

- Le service LLM est codé en dur sur `http://localhost:11434/api/generate` avec le modèle `mistral`.
- L’API dépend de la qualité de réponse du LLM pour la classification/extraction JSON.
- Les messages d’erreur sont partiellement en français et partiellement en anglais.

---

## 12) Sécurité (recommandations)

- Utiliser une valeur forte pour `JWT_SECRET`.
- Activer HTTPS en production.
- Restreindre `CORS_ORIGINS` aux domaines frontend autorisés.
- Ne jamais versionner `.env`.
- Ajouter rate limiting et audit logs pour un déploiement public.

---
