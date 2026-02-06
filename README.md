# API d'Analyse de PDF Médicaux

Une API REST basée sur FastAPI pour analyser les documents médicaux en utilisant une inférence LLM locale via Ollama. Extrayez des données médicales structurées à partir de rapports PDF avec authentification JWT.

## Fonctionnalités

- 📄 **Analyse PDF**: Extrayez et validez le contenu des rapports médicaux
- 🤖 **LLM Local**: Utilisez Ollama pour l'inférence sur site (aucun appel API externe)
- 🔐 **Authentification JWT**: Authentification utilisateur sécurisée basée sur les jetons
- 📊 **Données Structurées**: Extrayez les informations du patient, diagnostic, symptômes, traitements, examens
- 💾 **Stockage MongoDB**: Persistez les rapports et les données utilisateur
- ⚡ **Traitement Asynchrone**: Support async/await de FastAPI pour les opérations non-bloquantes
- 🔄 **Logique de Retry**: Mécanisme de relance automatique pour les appels LLM
- 📱 **CORS Activé**: Prêt pour l'intégration frontend

## Stack Technologique

- **Framework**: FastAPI
- **Base de données**: MongoDB
- **LLM**: Ollama (Local)
- **Traitement PDF**: PyPDF2
- **Authentification**: JWT avec bcrypt
- **Langage**: Python 3.9+

## Prérequis

### Logiciels Requis

1. **Python 3.9+**
   ```bash
   python --version
   ```

2. **MongoDB** (instance locale ou distante)
   ```bash
   # Vérifier la connexion
   mongosh "mongodb://utilisateur:motdepasse@hote:port/base"
   ```

3. **Ollama** (pour l'inférence LLM locale)
   ```bash
   # Visitez https://ollama.ai pour télécharger et installer
   # Démarrer le service Ollama
   ollama serve
   
   # Télécharger le modèle recommandé (Mistral)
   ollama pull mistral
   # Ou alternatives: neural-chat, llama2, medllama2
   ```

## Installation

1. **Cloner le dépôt**
   ```bash
   git clone <url-du-depot>
   cd pfa
   ```

2. **Créer l'environnement virtuel**
   ```bash
   python -m venv venv
   
   # Activer l'environnement virtuel
   # Sur Windows:
   venv\Scripts\activate
   # Sur macOS/Linux:
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Créez un fichier `.env` à la racine du projet avec les variables suivantes:

```env
# Configuration Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
OLLAMA_TIMEOUT=120
OLLAMA_RETRY_ATTEMPTS=3

# Configuration MongoDB
MONGODB_URL=mongodb://utilisateur:motdepasse@localhost:27017
MONGODB_DB_NAME=pfa_db

# Configuration JWT
JWT_SECRET_KEY=votre-clé-secrète-ici-changez-en-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Application
APP_ENV=development
DEBUG=False
```

### Référence des Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | URL de base de l'API Ollama | `http://localhost:11434` |
| `OLLAMA_MODEL` | Nom du modèle à utiliser (mistral, neural-chat, llama2) | `mistral` |
| `OLLAMA_TIMEOUT` | Délai d'expiration en secondes | `120` |
| `OLLAMA_RETRY_ATTEMPTS` | Nombre de tentatives de relance | `3` |
| `MONGODB_URL` | Chaîne de connexion MongoDB | Requis |
| `MONGODB_DB_NAME` | Nom de la base de données | `pfa_db` |
| `JWT_SECRET_KEY` | Clé secrète pour la signature JWT | Requis |
| `JWT_ALGORITHM` | Algorithme JWT | `HS256` |
| `JWT_EXPIRATION_MINUTES` | Durée d'expiration du jeton | `30` |

## Exécution de l'Application

### Développement Local

```bash
# Démarrer Ollama (dans un terminal séparé)
ollama serve

# Démarrer le serveur FastAPI
python main.py

# Le serveur s'exécute sur: http://localhost:8000
# Documentation API: http://localhost:8000/docs
```

### Déploiement en Production

```bash
# Utiliser Gunicorn avec Uvicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

## Points d'Accès API

### Authentification

#### Enregistrement Utilisateur
**POST** `/register`
```json
{
  "email": "utilisateur@exemple.com",
  "mot_de_passe": "motdepasse123",
  "nom": "Nom Utilisateur"
}
```

**Réponse (201):**
```json
{
  "message": "Utilisateur enregistré avec succès",
  "user": {
    "id": "user_id",
    "email": "utilisateur@exemple.com",
    "nom": "Nom Utilisateur"
  }
}
```

#### Connexion Utilisateur
**POST** `/login`
```json
{
  "email": "utilisateur@exemple.com",
  "mot_de_passe": "motdepasse123"
}
```

**Réponse (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "email": "utilisateur@exemple.com",
    "nom": "Nom Utilisateur"
  }
}
```

### Rapports Médicaux

#### Analyser un Rapport PDF
**POST** `/reports`
- **En-têtes**: `Authorization: Bearer <token>`
- **Corps**: multipart/form-data avec `file` (PDF)

**Réponse (201):**
```json
{
  "success": true,
  "report_id": "report_id_123"
}
```

#### Obtenir les Rapports de l'Utilisateur
**GET** `/reports`
- **En-têtes**: `Authorization: Bearer <token>`

**Réponse (200):**
```json
[
  {
    "_id": "report_id_123",
    "user_id": "user_id",
    "filename": "rapport_medical.pdf",
    "extracted_data": {
      "patient": "...",
      "diagnosis": "...",
      "symptoms": ["...", "..."],
      "treatments": ["...", "..."],
      "exams": ["...", "..."],
      "resume": "..."
    },
    "metadata": {...},
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

## Structure du Projet

```
pfa/
├── core/
│   ├── __init__.py
│   └── security.py              # Utilitaires JWT et mot de passe
├── db/
│   └── connection.py            # Connexion MongoDB
├── models/
│   └── __init__.py
├── repositories/
│   ├── __init__.py
│   ├── register_repository.py   # Opérations DB d'enregistrement
│   └── report_repository.py     # Opérations DB de rapport
├── routers/
│   ├── __init__.py
│   ├── login_router.py          # Points d'accès authentification
│   ├── register_router.py       # Point d'accès enregistrement
│   └── report_router.py         # Points d'accès rapport médical
├── schemas/
│   ├── user_schema.py           # Schémas requête/réponse utilisateur
│   └── report_schema.py         # Schémas requête/réponse rapport
├── services/
│   ├── __init__.py
│   ├── login_service.py         # Logique métier authentification
│   ├── register_service.py      # Logique métier enregistrement
│   ├── pdf_service.py           # Pipeline traitement PDF
│   ├── inputs_validator_service.py  # Validation entrée
│   └── ollama_service.py        # Intégration LLM Ollama
├── main.py                      # Point d'entrée application FastAPI
├── requirements.txt             # Dépendances Python
├── .env                         # Configuration (pas en contrôle de version)
└── Procfile                     # Configuration déploiement Heroku
```

## Pipeline de Traitement PDF

1. **Extraction**: PyPDF2 extrait le texte du PDF téléchargé
2. **Validation**: Ollama confirme que le document est un rapport médical
3. **Analyse**: Ollama extrait les données médicales structurées:
   - Informations du patient
   - Diagnostic
   - Symptômes
   - Traitements
   - Examens médicaux
   - Résumé du rapport
4. **Stockage**: Les données structurées sont persistées dans MongoDB
5. **Retour**: Réponse minimale avec indicateur de succès et ID du rapport

## Gestion des Erreurs

### Réponses d'Erreur Courantes

| Code | Erreur | Résolution |
|------|--------|-----------|
| 400 | Format de fichier invalide | Téléchargez un fichier PDF valide |
| 401 | Non autorisé | Incluez un jeton JWT valide dans l'en-tête Authorization |
| 422 | Erreur de validation | Vérifiez le schéma et les types de champs dans la requête |
| 500 | Ollama indisponible | Assurez-vous qu'Ollama s'exécute: `ollama serve` |
| 500 | Erreur MongoDB | Vérifiez la chaîne de connexion dans `.env` |

### Détails des Erreurs de Débogage

L'API retourne les détails des erreurs au format JSON:
```json
{
  "detail": {
    "error": "Service Ollama indisponible",
    "status": 500
  }
}
```

## Dépannage

### Problèmes de Connexion Ollama

**Problème**: "ConnectionError: Service Ollama indisponible"

**Solution**:
```bash
# Vérifier qu'Ollama s'exécute
ollama serve

# Tester la connexion manuellement
curl http://localhost:11434/api/tags

# Vérifier si le modèle est téléchargé
ollama list

# Télécharger le modèle si nécessaire
ollama pull mistral
```

### Problèmes de Connexion MongoDB

**Problème**: "MongoServerSelectionTimeoutError"

**Solution**:
```bash
# Vérifier que MongoDB s'exécute
# Tester la chaîne de connexion
mongosh "mongodb://utilisateur:motdepasse@hote:port/base"

# Mettre à jour MONGODB_URL dans .env avec les bonnes identifiants
```

### Problèmes de Jeton JWT

**Problème**: "401 Non autorisé"

**Solution**:
- Incluez l'en-tête `Authorization: Bearer <token>`
- Le format du jeton doit être: `Authorization: Bearer eyJhbGciOiJIUzI1NiI...`
- Vérifiez que le jeton n'a pas expiré (défaut: 30 minutes)

### Problèmes de Délai d'Expiration

**Problème**: "Timeout: Ollama a pris trop de temps pour répondre"

**Solution**:
```env
# Augmentez le délai pour les PDF complexes
OLLAMA_TIMEOUT=180

# Réduisez les tentatives de relance si les relances sont trop lentes
OLLAMA_RETRY_ATTEMPTS=2
```

## Exemple d'Utilisation

```bash
# 1. Enregistrer un utilisateur
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"utilisateur@exemple.com","mot_de_passe":"motdepasse123","nom":"Jean Dupont"}'

# 2. Se connecter
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"utilisateur@exemple.com","mot_de_passe":"motdepasse123"}'

# Sauvegarder le access_token de la réponse

# 3. Télécharger un PDF médical
curl -X POST http://localhost:8000/reports \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@rapport_medical.pdf"

# Réponse: {"success": true, "report_id": "..."}

# 4. Récupérer les rapports de l'utilisateur
curl -X GET http://localhost:8000/reports \
  -H "Authorization: Bearer <access_token>"
```

## Considérations de Performance

- **Sélection du Modèle**: Mistral est recommandé pour le texte médical (12 Go RAM). Utilisez neural-chat (6 Go) pour les environnements avec ressources limitées
- **Taille PDF**: Optimal pour les PDF jusqu'à 10 Mo; les fichiers plus volumineux nécessitent un délai d'expiration augmenté
- **Requêtes Simultanées**: Ollama traite séquentiellement; mettez en file d'attente les requêtes pour l'utilisation en production
- **Mémoire**: Assurez-vous d'avoir suffisamment de RAM pour le modèle + MongoDB + FastAPI

## Notes de Sécurité

⚠️ **Liste de Vérification pour la Production**:
- [ ] Changez `JWT_SECRET_KEY` par une valeur aléatoire forte
- [ ] Utilisez HTTPS pour tous les points d'accès
- [ ] Stockez `.env` de manière sécurisée (pas en contrôle de version)
- [ ] Activez l'authentification MongoDB
- [ ] Réglez `DEBUG=False` en production
- [ ] Implémentez une limitation de débit
- [ ] Utilisez des configurations spécifiques à l'environnement
- [ ] Activez CORS uniquement pour les domaines de confiance

## Support

Pour les problèmes ou questions:
1. Consultez la section [Dépannage](#dépannage)
2. Vérifiez la documentation API: `http://localhost:8000/docs`
3. Vérifiez les journaux Ollama: `ollama logs`
4. Vérifiez la connexion MongoDB

## Contribution

[Les directives de contribution vont ici]

## Licence

[Votre licence ici]
