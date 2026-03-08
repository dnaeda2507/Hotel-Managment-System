import http

from fastapi import FastAPI
from app.routes.admin import router as admin_router
from app.routes.room import router as room_router
from app.routes.pricing import router as pricing_router
from app.routes.maintenance import router as maintenance_router
from app.routes.housekeeping import router as housekeeping_router

from app.routes.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PROD: Sadece frontend URL'sini ekle
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(room_router)
app.include_router(pricing_router)
app.include_router(maintenance_router)
app.include_router(housekeeping_router)


@app.get("/")
def root():
        return {"message": "Backend is up. Use /auth/login and /auth/me"}