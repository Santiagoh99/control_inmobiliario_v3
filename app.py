from flask import Flask, render_template, redirect, url_for, flash, request, send_file, abort, Response
from models import get_engine, get_session, init_db, Movimiento, CierreMensual
from forms import MovimientoForm
from sqlalchemy import func
from datetime import datetime
import io, csv
from openpyxl import Workbook
from functools import wraps
from dotenv import load_dotenv
import os

load_dotenv()  # Carga variables desde .env

ALLOWED_WRITE_IPS = os.getenv("ALLOWED_WRITE_IPS", "")
# Convertimos la cadena en set de IPs
ALLOWED_WRITE_IPS = set(ip.strip() for ip in ALLOWED_WRITE_IPS.split(",") if ip.strip())

def is_mobile():
    ua = request.headers.get('User-Agent','').lower()
    return 'mobile' in ua or 'android' in ua or 'iphone' in ua

def requires_write_permission(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "GET":
            return f(*args, **kwargs)

        client_ip = request.remote_addr
        if client_ip in ALLOWED_WRITE_IPS and not is_mobile():
            return f(*args, **kwargs)

        return Response('No tiene permisos para modificar', 401)
    return decorated



# ----------------- BACKUP AUTOMÁTICO -----------------
import os
import shutil
import sqlite3
import datetime

DB_PATH = "control_inmobiliario.db"
BACKUP_DIR = "backups"
MAX_REGISTROS = 5000  # generar backup cada 5000 movimientos
MAX_MB = 5             # generar backup si DB > 5 MB

os.makedirs(BACKUP_DIR, exist_ok=True)

def check_backup():
    # Contar registros
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM movimientos")
    total = cur.fetchone()[0]
    conn.close()

    # Tamaño DB
    size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)

    # Condición para backup
    if total >= MAX_REGISTROS or size_mb >= MAX_MB:
        fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"backup_{fecha}.db")
        shutil.copy2(DB_PATH, backup_path)
        print(f"[BACKUP] Se generó backup automático: {backup_path}")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cambiame_por_una_clave_segura'

engine = get_engine()
init_db(engine)
db = get_session(engine)

def get_current_month_year():
    now = datetime.now()
    return now.month, now.year

@app.route('/')
def index():
    mes_actual, anio_actual = get_current_month_year()
    movimientos = db.query(Movimiento).filter(Movimiento.mes==mes_actual, Movimiento.anio==anio_actual).order_by(Movimiento.fecha.desc()).all()
    ingresos_ars = db.query(func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.tipo=='ingreso', Movimiento.moneda=='ARS', Movimiento.mes==mes_actual, Movimiento.anio==anio_actual),0)).scalar() or 0
    gastos_ars = db.query(func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.tipo=='gasto', Movimiento.moneda=='ARS', Movimiento.mes==mes_actual, Movimiento.anio==anio_actual),0)).scalar() or 0
    ingresos_usd = db.query(func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.tipo=='ingreso', Movimiento.moneda=='USD', Movimiento.mes==mes_actual, Movimiento.anio==anio_actual),0)).scalar() or 0
    gastos_usd = db.query(func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.tipo=='gasto', Movimiento.moneda=='USD', Movimiento.mes==mes_actual, Movimiento.anio==anio_actual),0)).scalar() or 0

    ingresos_ars_anio = db.query(func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.tipo=='ingreso', Movimiento.moneda=='ARS', Movimiento.anio==anio_actual),0)).scalar() or 0
    gastos_ars_anio = db.query(func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.tipo=='gasto', Movimiento.moneda=='ARS', Movimiento.anio==anio_actual),0)).scalar() or 0
    ingresos_usd_anio = db.query(func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.tipo=='ingreso', Movimiento.moneda=='USD', Movimiento.anio==anio_actual),0)).scalar() or 0
    gastos_usd_anio = db.query(func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.tipo=='gasto', Movimiento.moneda=='USD', Movimiento.anio==anio_actual),0)).scalar() or 0

    cierres = db.query(CierreMensual).order_by(CierreMensual.anio.desc(), CierreMensual.mes.desc()).limit(12).all()
    return render_template('index.html', movimientos=movimientos,
                           ingresos_ars=ingresos_ars, gastos_ars=gastos_ars,
                           ingresos_usd=ingresos_usd, gastos_usd=gastos_usd,
                           ingresos_ars_anio=ingresos_ars_anio, gastos_ars_anio=gastos_ars_anio,
                           ingresos_usd_anio=ingresos_usd_anio, gastos_usd_anio=gastos_usd_anio,
                           cierres=cierres, mes_actual=mes_actual, anio_actual=anio_actual)

@app.route('/nuevo', methods=['GET','POST'])
@requires_write_permission
def nuevo():
    form = MovimientoForm()
    if form.validate_on_submit():
        fecha = form.fecha.data or datetime.now().date()
        mes = fecha.month
        anio = fecha.year
        mov = Movimiento(
            fecha = datetime.combine(fecha, datetime.now().time()),
            tipo = form.tipo.data,
            descripcion = form.descripcion.data,
            monto = float(form.monto.data),
            moneda = form.moneda.data,
            medio_pago = form.medio_pago.data,
            mes = mes,
            anio = anio
        )
        db.add(mov)
        db.commit()

        # --- Llamada a backup automático ---
        check_backup()

        flash('Movimiento guardado','success')
        return redirect(url_for('index'))
    form.fecha.data = datetime.now().date()
    return render_template('nuevo.html', form=form)

@app.route('/cerrar_mes', methods=['POST'])
@requires_write_permission
def cerrar_mes():
    try:
        mes = int(request.form.get('mes'))
        anio = int(request.form.get('anio'))
    except Exception:
        abort(400)
    ingresos_ars = db.query(func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.tipo=='ingreso', Movimiento.moneda=='ARS', Movimiento.mes==mes, Movimiento.anio==anio),0)).scalar() or 0
    gastos_ars = db.query(func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.tipo=='gasto', Movimiento.moneda=='ARS', Movimiento.mes==mes, Movimiento.anio==anio),0)).scalar() or 0
    ingresos_usd = db.query(func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.tipo=='ingreso', Movimiento.moneda=='USD', Movimiento.mes==mes, Movimiento.anio==anio),0)).scalar() or 0
    gastos_usd = db.query(func.coalesce(func.sum(Movimiento.monto).filter(Movimiento.tipo=='gasto', Movimiento.moneda=='USD', Movimiento.mes==mes, Movimiento.anio==anio),0)).scalar() or 0
    saldo_ars = ingresos_ars - gastos_ars
    saldo_usd = ingresos_usd - gastos_usd
    cierre = CierreMensual(mes=mes, anio=anio,
                           total_ingresos_ars=ingresos_ars, total_gastos_ars=gastos_ars,
                           total_ingresos_usd=ingresos_usd, total_gastos_usd=gastos_usd,
                           saldo_ars=saldo_ars, saldo_usd=saldo_usd)
    db.add(cierre)
    movimientos = db.query(Movimiento).filter(Movimiento.mes==mes, Movimiento.anio==anio).all()
    for m in movimientos:
        m.cerrado = True
        db.add(m)
    db.commit()
    flash('Mes cerrado correctamente','success')
    return redirect(url_for('index'))

@app.route('/historico')
def historico():
    cierres = db.query(CierreMensual).order_by(CierreMensual.anio.desc(), CierreMensual.mes.desc()).all()
    return render_template('historico.html', cierres=cierres)

@app.route('/reabrir_mes/<int:id>', methods=['POST'])
@requires_write_permission
def reabrir_mes(id):
    cierre = db.query(CierreMensual).get(id)
    if not cierre:
        flash('Cierre no encontrado','danger')
        return redirect(url_for('historico'))
    movimientos = db.query(Movimiento).filter(Movimiento.mes==cierre.mes, Movimiento.anio==cierre.anio, Movimiento.cerrado==True).all()
    for m in movimientos:
        m.cerrado = False
        db.add(m)
    db.delete(cierre)
    db.commit()
    flash(f'Mes {cierre.mes}/{cierre.anio} reabierto','info')
    return redirect(url_for('historico'))

@app.route('/exportar_mes')
def exportar_mes():
    mes = int(request.args.get('mes') or datetime.now().month)
    anio = int(request.args.get('anio') or datetime.now().year)
    movimientos = db.query(Movimiento).filter(Movimiento.mes==mes, Movimiento.anio==anio).order_by(Movimiento.fecha.asc()).all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['fecha','tipo','descripcion','monto','moneda','medio_pago'])
    for m in movimientos:
        cw.writerow([m.fecha.strftime('%Y-%m-%d %H:%M'), m.tipo, m.descripcion or '', '%.2f'%m.monto, m.moneda, m.medio_pago])
    mem = io.BytesIO()
    mem.write(si.getvalue().encode('utf-8'))
    mem.seek(0)
    filename = f'reportes_{mes}_{anio}.csv'
    return send_file(mem, mimetype='text/csv', download_name=filename, as_attachment=True)

@app.route('/exportar_excel/<int:mes>/<int:anio>')
def exportar_excel(mes, anio):
    movimientos = db.query(Movimiento).filter(Movimiento.mes==mes, Movimiento.anio==anio).order_by(Movimiento.fecha.asc()).all()
    wb = Workbook()
    ws = wb.active
    ws.title = f"{mes}-{anio}"
    ws.append(["Fecha", "Tipo", "Descripción", "Monto", "Moneda", "Medio de Pago"])
    for m in movimientos:
        ws.append([m.fecha.strftime('%Y-%m-%d %H:%M'), m.tipo, m.descripcion or '', float('%.2f'%m.monto), m.moneda, m.medio_pago])
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    filename = f'resumen_{mes}_{anio}.xlsx'
    return send_file(output, as_attachment=True, download_name=filename, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == '__main__':
    print('Iniciando Control Inmobiliario v3 - abrir http://127.0.0.1:5000 manualmente en tu navegador')
    app.run(host='0.0.0.0', port=5001, debug=True)
