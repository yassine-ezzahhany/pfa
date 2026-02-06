from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers.register_router import register_router 
from routers.login_router import login_router
from routers.report_router import report_router
from core.security import verify_token

app = FastAPI(title="PFA APIs")
origins = [
    "https://pfa-s1.vercel.app",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=register_router, prefix="/register", tags=["Enregistrement"])
app.include_router(router=login_router, prefix="/login", tags=["Authentification"])
app.include_router(router=report_router, prefix="/reports", tags=["Rapports Médicaux"])