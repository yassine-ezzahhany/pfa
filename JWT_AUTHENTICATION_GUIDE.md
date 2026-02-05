# PFA JWT Authentication - Complete Implementation Guide

## Overview
This project implements complete JWT (JSON Web Token) authentication for a FastAPI application with MongoDB as the database. The system includes user registration, login, and protected routes.

## What's Implemented

### 1. **Password Management** (`core/security.py`)
- ✅ Password hashing with `bcrypt`
- ✅ Password verification

### 2. **JWT Token Management** (`core/security.py`)
- ✅ Token creation with expiration
- ✅ Token validation and decoding
- ✅ Bearer token authentication dependency

### 3. **User Authentication**
- ✅ Registration endpoint: `POST /register`
- ✅ Login endpoint: `POST /login`
- ✅ Protected routes with JWT verification

## API Endpoints

### 1. Register User
**Endpoint:** `POST /register`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (!@#$%^&*(),.?":{})

**Response:**
```json
{
  "message": "utilisateur ajoute avec succes"
}
```

---

### 2. Login User
**Endpoint:** `POST /login`

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

---

### 3. Access Protected Route
**Endpoint:** `GET /protected`

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "message": "Vous avez accès à cette route",
  "user_email": "john@example.com",
  "user_id": "507f1f77bcf86cd799439011"
}
```

---

## Architecture

### File Structure
```
core/
├── security.py          # JWT operations, password hashing, authentication dependency
services/
├── register_service.py  # Registration business logic
├── login_service.py     # Login business logic & JWT generation
└── inputs_validator_service.py
routers/
├── register_router.py   # /register endpoint
├── login_router.py      # /login endpoint
repositorys/
├── register_repository.py  # Database operations
models/
├── User.py              # User data model
schemas/
├── user_schema.py       # Pydantic schemas (UserRegister, UserLogin)
db/
├── connection.py        # MongoDB connection
main.py                 # FastAPI app setup & protected route example
```

### Key Components

#### 1. **security.py** - Core Security Module
- `hash_password_service()` - Hash passwords with bcrypt
- `verify_password_service()` - Verify password against hash
- `create_access_token()` - Generate JWT token
- `decode_access_token()` - Validate and decode JWT
- `verify_token()` - Dependency function for protected routes

#### 2. **login_service.py** - Authentication Service
- `login_user_service()` - Authenticate user and return JWT token
  - Validates user exists
  - Verifies password
  - Generates JWT with user info

#### 3. **login_router.py** - Login Endpoint
Handles POST requests to `/login` endpoint

#### 4. **main.py** - Application Setup
- Registers routes
- Includes example protected route (`/protected`)
- CORS middleware configuration

## Configuration

### Environment Variables (`.env`)
```env
# MongoDB
MONGO_URI=mongodb://localhost:27017/pfa_db

# JWT Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Debug
DEBUG=True
```

**Important:** Change `SECRET_KEY` in production! Use a strong, random string.

## How to Use JWT

### 1. Register a User
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### 2. Login to Get Token
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Response includes:**
- `access_token`: The JWT token to use for protected routes
- `token_type`: "bearer"
- `user`: User information

### 3. Use Token to Access Protected Route
```bash
curl -X GET "http://localhost:8000/protected" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Creating Protected Routes

### Example 1: Simple Protected Route
```python
from fastapi import Depends
from core.security import verify_token

@app.get("/api/profile")
def get_profile(payload: dict = Depends(verify_token)):
    return {
        "message": "User profile",
        "email": payload.get("sub"),
        "user_id": payload.get("user_id")
    }
```

### Example 2: Protected Route in a Router
```python
from fastapi import APIRouter, Depends
from core.security import verify_token

router = APIRouter()

@router.get("/data")
def get_data(payload: dict = Depends(verify_token)):
    user_id = payload.get("user_id")
    # Access database using user_id
    return {"data": "sensitive information"}
```

## Token Structure

The JWT token contains:
```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "sub": "user@example.com",
  "user_id": "507f1f77bcf86cd799439011",
  "exp": 1709068800,
  "iat": 1708983600
}

Signature: HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret_key)
```

## Security Best Practices

1. ✅ **Secret Key:** Always use a strong, random SECRET_KEY in production
2. ✅ **HTTPS:** Use HTTPS in production (not HTTP)
3. ✅ **Token Expiration:** Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES`
4. ✅ **Password Hashing:** Passwords are hashed with bcrypt, never stored in plain text
5. ✅ **Password Validation:** Strong password requirements enforced
6. ✅ **Bearer Token:** Use Bearer authentication scheme

## Error Handling

### Invalid Credentials (Login)
```json
{
  "detail": "Email ou mot de passe incorrect"
}
```
Status Code: `401 Unauthorized`

### Expired/Invalid Token (Protected Route)
```json
{
  "detail": "Token invalide ou expiré",
  "headers": {"WWW-Authenticate": "Bearer"}
}
```
Status Code: `401 Unauthorized`

### Missing Authorization Header
```json
{
  "detail": "Not authenticated"
}
```
Status Code: `403 Forbidden`

## Testing the Implementation

### Test with Python Requests
```python
import requests

# 1. Register
register_response = requests.post(
    "http://localhost:8000/register",
    json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPass123!"
    }
)
print("Register:", register_response.json())

# 2. Login
login_response = requests.post(
    "http://localhost:8000/login",
    json={
        "email": "test@example.com",
        "password": "TestPass123!"
    }
)
data = login_response.json()
token = data["access_token"]
print("Token:", token)

# 3. Access Protected Route
protected_response = requests.get(
    "http://localhost:8000/protected",
    headers={"Authorization": f"Bearer {token}"}
)
print("Protected:", protected_response.json())
```

## Next Steps (Optional Enhancements)

1. **Refresh Tokens:** Implement token refresh mechanism for longer sessions
2. **Role-Based Access Control (RBAC):** Add user roles and permissions
3. **User Data Endpoint:** Create `/api/me` endpoint to get current user info
4. **Logout:** Implement token blacklisting for logout
5. **Email Verification:** Add email confirmation before activation
6. **Password Reset:** Implement password reset flow

## Dependencies

All required packages are in `requirements.txt`:
- `fastapi` - Web framework
- `python-jose[cryptography]` - JWT handling
- `bcrypt` - Password hashing
- `pymongo` - MongoDB driver
- `pydantic` - Data validation
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variables
- `email-validator` - Email validation

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file from .env.example
copy .env.example .env

# Run the server
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

---

**Authentication is now complete! All routes are ready to use with JWT protection.**
