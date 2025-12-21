from fastapi import FastAPI
from routers.register_router import register_router 
#Le serveur:
app=FastAPI(title="PFA APIs")
#liee les routes:
app.include_router(router=register_router, prefix="/register", tags=["Enregistrement"])