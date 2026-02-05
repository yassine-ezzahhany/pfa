from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers.register_router import register_router 
from routers.login_router import login_router
from routers.report_router import report_router
from core.security import verify_token

#Le serveur:
app=FastAPI(title="PFA APIs")
origins = [
    "https://pfa-s1.vercel.app",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Seules ces URLs sont autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#liee les routes:
app.include_router(router=register_router, prefix="/register", tags=["Enregistrement"])
app.include_router(router=login_router, prefix="/login", tags=["Authentification"])
app.include_router(router=report_router, prefix="/pdf-to-json", tags=["Rapports Médicaux"])

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