import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL  = os.getenv("DATABASE_URL", "sqlite:///hr_portal.db")
JWT_SECRET    = os.getenv("JWT_SECRET", "change-me-in-production-secret-key-32chars")
JWT_ACCESS_EX = int(os.getenv("JWT_ACCESS_EXPIRES_MINUTES", 60))
JWT_REFRESH_EX = int(os.getenv("JWT_REFRESH_EXPIRES_DAYS", 7))
DEBUG         = os.getenv("FLASK_DEBUG", "false").lower() == "true"
PORT          = int(os.getenv("PORT", 5000))

# SQLAlchemy
SQLALCHEMY_DATABASE_URI        = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO                = False   # set True to log all SQL
