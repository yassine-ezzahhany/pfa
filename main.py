from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.register_router import register_router 
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