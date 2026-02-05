from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers.register_router import register_router 
from routers.login_router import login_router
from core.security import verify_token

#Le serveur:
app=FastAPI(title="PFA APIs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tout le monde peut accéder
    allow_credentials=True,  # pas de cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
#liee les routes:
app.include_router(router=register_router, prefix="/register", tags=["Enregistrement"])
app.include_router(router=login_router, prefix="/login", tags=["Authentification"])

# Route protégée par JWT - exemple
# @app.get("/protected", tags=["Protected"])
# def protected_route(payload: dict = Depends(verify_token)):
#     """
#     Route protégée - nécessite un JWT valide dans le header Authorization
#     """
#     return {
#         "message": "Vous avez accès à cette route",
#         "user_email": payload.get("sub"),
#         "user_id": payload.get("user_id")
#     }

# # Route publique - info
# @app.get("/", tags=["Info"])
# def root():
#     return {
#         "message": "Bienvenue sur PFA APIs",
#         "endpoints": {
#             "register": "/register (POST) - Enregistrer un nouvel utilisateur",
#             "login": "/login (POST) - Se connecter et obtenir un JWT",
#             "protected": "/protected (GET) - Route protégée nécessitant un JWT"
#         }
#     }