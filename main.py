from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers.register_router import register_router 
from routers.login_router import login_router
from routers.refresh_router import refresh_router
from routers.report_router import report_router
from core.security import verify_token
from core.config import settings

app = FastAPI(title="PFA APIs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=register_router, prefix="/register", tags=["Authentification"])
app.include_router(router=login_router, prefix="/login", tags=["Authentification"])
app.include_router(router=refresh_router, prefix="/refresh", tags=["Authentification"])
app.include_router(router=report_router,prefix="/reports",tags=["Rapports Médicaux"],dependencies=[Depends(verify_token)],
)
