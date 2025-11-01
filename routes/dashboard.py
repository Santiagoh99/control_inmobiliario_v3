from flask import Blueprint, render_template
from models import get_session, get_engine, Movimiento
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)
engine = get_engine()
db = get_session(engine)

@dashboard_bp.route('/')
def dashboard():
    total_ars = db.query(func.sum(Movimiento.monto)).filter(Movimiento.moneda=='ARS').scalar() or 0
    total_usd = db.query(func.sum(Movimiento.monto)).filter(Movimiento.moneda=='USD').scalar() or 0
    movimientos = db.query(Movimiento).order_by(Movimiento.fecha.desc()).limit(10).all()
    return render_template('dashboard.html', total_ars=total_ars, total_usd=total_usd, movimientos=movimientos)
