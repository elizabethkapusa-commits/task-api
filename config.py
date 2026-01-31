import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

DEMO_USERNAME = os.getenv("DEMO_USERNAME", "demo")
DEMO_PASSWORD_HASH = os.getenv("DEMO_PASSWORD_HASH", "")

