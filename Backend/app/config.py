from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

def get_access_token_expiry():
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)