# APIs d’Analyse de Rapports Médicaux (FastAPI)

APIs REST pour :
- authentifier des utilisateurs avec JWT,
- recevoir un rapport PDF médical,
- extraire et structurer les données du document,
- sauvegarder le résultat dans MongoDB,
- restituer les rapports d’un utilisateur connecté.

Le projet suit une architecture simple en couches : `routers` (HTTP), `services` (logique métier), `repositorys` (accès base de données).

---

## 1) Fonctionnalités

- **Authentification JWT** : inscription, connexion, token bearer.
- **Pipeline PDF** :
  1. validation du format PDF,
  2. extraction du texte (`PyPDF2`),
  3. classification “rapport médical ou non” via LLM,
  4. extraction JSON structurée via LLM,
  5. insertion en base,
  6. retour de l’identifiant du document.
- **Sécurité d’accès** : toutes les routes `/reports` nécessitent un token valide.
- **Isolation des données** : un utilisateur ne peut lire que ses propres rapports.

---

## 2) Stack technique

- **Backend** : FastAPI
- **Base de données** : MongoDB (`pymongo`)
- **Authentification** : JWT (`python-jose`) + hash mot de passe (`bcrypt`)
- **Traitement PDF** : `PyPDF2`
- **Appel LLM** : HTTP via `requests`

> Dans l’implémentation actuelle, le service d’analyse appelle `http://localhost:11434/api/generate` avec le modèle `mistral`.

---

## 3) Structure du projet

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
│   ├── register_router.py
│   └── report_router.py
├── schemas/
│   ├── user_schema.py
│   └── report_schema.py
├── services/
│   ├── login_service.py
│   ├── register_service.py
│   ├── inputs_validator_service.py
│   └── report_service.py
├── main.py
├── requirements.txt
└── Procfile
```

---

## 4) Prérequis

- Python **3.10+** recommandé
- MongoDB accessible (local ou distant)
- Un service LLM local actif sur `localhost:11434` (ex: Ollama avec modèle `mistral`)

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

### Installer et lancer le LLM Mistral (Ollama)

Le backend appelle localement l’endpoint `http://localhost:11434/api/generate` avec le modèle `mistral`.

1. Installer Ollama

- Windows: télécharger et installer depuis https://ollama.com/download/windows
- macOS: `brew install ollama`
- Linux: `curl -fsSL https://ollama.com/install.sh | sh`

2. Démarrer Ollama

```bash
ollama serve
```

3. Télécharger le modèle Mistral

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

### Variables obligatoires

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

# CORS (séparer les origines par des virgules)
CORS_ORIGINS=https://pfa-s1.vercel.app,http://localhost:3000,http://127.0.0.1:3000

```

---

## 7) Démarrer le projet

### En développement

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API : `http://localhost:8000`
- Swagger : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

### En production (exemple Procfile)

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 8) Endpoints

## Authentification

### `POST /register`
Crée un utilisateur.

Body JSON :

```json
{
  "name": "Jean Dupont",
  "email": "jean@example.com",
  "password": "MotDePasse123!"
}
```

### `POST /login`
Retourne un token JWT.

Body JSON :

```json
{
  "email": "jean@example.com",
  "password": "MotDePasse123!"
}
```

Réponse (exemple) :

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
Génère un **nouvel access token** sans reconnexion utilisateur.

Body JSON :

```json
{
  "refresh_token": "..."
}
```

Réponse (exemple) :

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

## Rapports médicaux (protégés JWT)

Toutes les routes `/reports` nécessitent :

```http
Authorization: Bearer <access_token>
```

### `POST /reports`
Upload d’un PDF (`multipart/form-data`, champ `file`).

Réponse :

```json
{
  "success": true,
  "document_id": "65f..."
}
```

### `GET /reports`
Retourne les rapports du user connecté.

### `GET /reports/{report_id}`
Retourne un rapport précis si l’utilisateur est propriétaire.

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

# 3) Upload PDF (remplacer TOKEN)
curl -X POST "http://localhost:8000/reports" \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@rapport.pdf"

# 4) Lister les rapports
curl -X GET "http://localhost:8000/reports" \
  -H "Authorization: Bearer TOKEN"
```

---

## 10) Codes d’erreur fréquents

- `400` : fichier invalide, contenu non médical, erreur de validation métier.
- `401` : token manquant/expiré/invalide.
- `403` : tentative d’accès à un rapport qui n’appartient pas à l’utilisateur.
- `404` : rapport introuvable.
- `500` : erreur interne (DB, service externe, etc.).

---

## 11) Notes de sécurité

Pour un déploiement réel :
- Utiliser une valeur forte pour `JWT_SECRET`.
- Activer HTTPS.
- Restreindre CORS à vos domaines frontend.
- Ne jamais versionner `.env`.
- Ajouter rate limiting + journalisation d’audit.

---

## 12) License

Projet académique/interne (adapter selon votre contexte).