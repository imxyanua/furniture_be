import os
from dotenv import load_dotenv

# Load .env file from project root
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

# Print for debugging
print(f"Loading .env from: {env_path}")
print(f"DATABASE_URL loaded: {os.getenv('DATABASE_URL', 'NOT FOUND')}")


class Settings:
    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/furniture_db")
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))


settings = Settings()
