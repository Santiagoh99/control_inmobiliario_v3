from flask import Flask
from dotenv import load_dotenv
import os
from routes.movimientos import movimientos_bp
from routes.backup import backup_bp
from routes.dashboard import dashboard_bp
from utils.security import init_ip_security
from models import get_engine, get_session, init_db

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "cambiame_por_una_clave_segura")

# --- Inicializar DB ---
engine = get_engine()
init_db(engine)
db = get_session(engine)

# --- Seguridad IP ---
init_ip_security(app)

# --- Registrar Blueprints ---
app.register_blueprint(movimientos_bp, url_prefix="/")
app.register_blueprint(backup_bp, url_prefix="/backup")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

if __name__ == "__main__":
    print("Iniciando Control Inmobiliario v4 - abrir http://127.0.0.1:5001")
    app.run(host="0.0.0.0", port=5001, debug=True)
