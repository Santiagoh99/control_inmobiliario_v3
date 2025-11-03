import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "cambiame_por_una_clave_segura")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///control_inmobiliario.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False