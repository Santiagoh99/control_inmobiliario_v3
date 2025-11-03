from flask import Flask
from dotenv import load_dotenv
import os
from routes.movimientos import movimientos_bp
from routes.backup import backup_bp
from routes.dashboard import dashboard_bp
from models.database import get_engine, init_db

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave_segura_produccion")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///control_inmobiliario.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar la base de datos
engine = get_engine()
init_db(engine)

# Registrar Blueprints
app.register_blueprint(movimientos_bp, url_prefix="/")
app.register_blueprint(backup_bp, url_prefix="/backup")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

# Ejecutar la aplicación
if __name__ == "__main__":
    print("Iniciando Control Inmobiliario - Producción")
    app.run(host="0.0.0.0", port=5000, debug=False)