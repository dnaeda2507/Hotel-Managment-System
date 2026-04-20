from fastapi import FastAPI
from app.routes.admin import router as admin_router
from app.routes.room import router as room_router
from app.routes.pricing import router as pricing_router
from app.routes.maintenance import router as maintenance_router
from app.routes.housekeeping import router as housekeeping_router
from app.routes.reservation import router as reservation_router
from app.routes.reviews import router as reviews_router
from app.routes.pricing_ai import router as pricing_ai_router
from app.routes.review_ai import router as review_ai_router
from app.routes.checkout_ai import router as checkout_ai_router
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
app.include_router(reservation_router)
app.include_router(reviews_router)
app.include_router(pricing_ai_router)

app.include_router(review_ai_router, prefix="/agents/review-ai")
app.include_router(checkout_ai_router, prefix="/agents/checkout-ai")
app.include_router(pricing_ai_router, prefix="/agents/dynamic-pricing")


@app.get("/")
def root():
    return {"message": "Backend is up. Use /auth/login and /auth/me"}