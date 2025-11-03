from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from models.database import get_session, get_engine
from models.movimiento import Movimiento
from datetime import datetime
from sqlalchemy import func
import csv
import io

movimientos_bp = Blueprint('movimientos', __name__)
engine = get_engine()
db = get_session(engine)

# Ruta principal: Listar movimientos
@movimientos_bp.route('/')
def index():
    mes_actual, anio_actual = datetime.now().month, datetime.now().year
    movimientos = db.query(Movimiento).filter(
        Movimiento.mes == mes_actual,
        Movimiento.anio == anio_actual
    ).order_by(Movimiento.fecha.desc()).all()

    # Calcular totales mensuales
    totales = {
        "ingresos_ars": db.query(func.sum(Movimiento.monto)).filter(
            Movimiento.tipo == 'ingreso', Movimiento.moneda == 'ARS',
            Movimiento.mes == mes_actual, Movimiento.anio == anio_actual
        ).scalar() or 0,
        "gastos_ars": db.query(func.sum(Movimiento.monto)).filter(
            Movimiento.tipo == 'gasto', Movimiento.moneda == 'ARS',
            Movimiento.mes == mes_actual, Movimiento.anio == anio_actual
        ).scalar() or 0,
        "ingresos_usd": db.query(func.sum(Movimiento.monto)).filter(
            Movimiento.tipo == 'ingreso', Movimiento.moneda == 'USD',
            Movimiento.mes == mes_actual, Movimiento.anio == anio_actual
        ).scalar() or 0,
        "gastos_usd": db.query(func.sum(Movimiento.monto)).filter(
            Movimiento.tipo == 'gasto', Movimiento.moneda == 'USD',
            Movimiento.mes == mes_actual, Movimiento.anio == anio_actual
        ).scalar() or 0,
    }

    # Calcular totales anuales
    totales_anuales = {
        "ingresos_ars": db.query(func.sum(Movimiento.monto)).filter(
            Movimiento.tipo == 'ingreso', Movimiento.moneda == 'ARS',
            Movimiento.anio == anio_actual
        ).scalar() or 0,
        "gastos_ars": db.query(func.sum(Movimiento.monto)).filter(
            Movimiento.tipo == 'gasto', Movimiento.moneda == 'ARS',
            Movimiento.anio == anio_actual
        ).scalar() or 0,
        "ingresos_usd": db.query(func.sum(Movimiento.monto)).filter(
            Movimiento.tipo == 'ingreso', Movimiento.moneda == 'USD',
            Movimiento.anio == anio_actual
        ).scalar() or 0,
        "gastos_usd": db.query(func.sum(Movimiento.monto)).filter(
            Movimiento.tipo == 'gasto', Movimiento.moneda == 'USD',
            Movimiento.anio == anio_actual
        ).scalar() or 0,
    }

    return render_template('index.html', movimientos=movimientos, totales=totales, totales_anuales=totales_anuales)

# Ruta para crear un nuevo movimiento
@movimientos_bp.route('/nuevo', methods=['POST'])
def nuevo():
    descripcion = request.form.get('descripcion')
    monto = float(request.form.get('monto'))
    tipo = request.form.get('tipo')
    moneda = request.form.get('moneda')
    medio_pago = request.form.get('medio_pago')

    nuevo_movimiento = Movimiento(
        descripcion=descripcion,
        monto=monto,
        tipo=tipo,
        moneda=moneda,
        medio_pago=medio_pago,
        fecha=datetime.now(),
        mes=datetime.now().month,
        anio=datetime.now().year
    )
    db.add(nuevo_movimiento)
    db.commit()
    flash("Movimiento creado con éxito", "success")
    return redirect(url_for('movimientos.index'))

# Ruta para eliminar un movimiento
@movimientos_bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    movimiento = db.query(Movimiento).get(id)
    if not movimiento:
        flash("Movimiento no encontrado", "danger")
        return redirect(url_for('movimientos.index'))

    db.delete(movimiento)
    db.commit()
    flash("Movimiento eliminado con éxito", "success")
    return redirect(url_for('movimientos.index'))

# Ruta para editar un movimiento
@movimientos_bp.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    movimiento = db.query(Movimiento).get(id)
    if not movimiento:
        flash("Movimiento no encontrado", "danger")
        return redirect(url_for('movimientos.index'))

    movimiento.descripcion = request.form.get('descripcion')
    movimiento.monto = float(request.form.get('monto'))
    movimiento.tipo = request.form.get('tipo')
    movimiento.moneda = request.form.get('moneda')
    movimiento.medio_pago = request.form.get('medio_pago')
    db.commit()
    flash("Movimiento actualizado con éxito", "success")
    return redirect(url_for('movimientos.index'))

# Ruta para exportar movimientos a CSV
@movimientos_bp.route('/exportar_mes', methods=['GET'])
def exportar_mes():
    mes = request.args.get('mes', type=int, default=datetime.now().month)
    anio = request.args.get('anio', type=int, default=datetime.now().year)

    movimientos = db.query(Movimiento).filter(
        Movimiento.mes == mes,
        Movimiento.anio == anio
    ).order_by(Movimiento.fecha.desc()).all()

    # Crear archivo CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Descripción', 'Monto', 'Tipo', 'Moneda', 'Medio de Pago', 'Fecha'])
    for movimiento in movimientos:
        writer.writerow([
            movimiento.descripcion,
            movimiento.monto,
            movimiento.tipo,
            movimiento.moneda,
            movimiento.medio_pago,
            movimiento.fecha.strftime('%Y-%m-%d %H:%M:%S')
        ])

    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={
            "Content-Disposition": f"attachment;filename=movimientos_{mes}_{anio}.csv"
        }
    )