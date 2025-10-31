from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Movimiento(Base):
    __tablename__ = "movimientos"
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    tipo = Column(String(10), nullable=False)  # ingreso o gasto
    descripcion = Column(String(300), nullable=True)
    monto = Column(Float, nullable=False)
    moneda = Column(String(3), nullable=False, default='ARS')  # ARS o USD
    medio_pago = Column(String(50), nullable=True)  # Efectivo, MercadoPago, etc.
    mes = Column(Integer, nullable=False)
    anio = Column(Integer, nullable=False)
    cerrado = Column(Boolean, default=False)  # si el movimiento pertenece a un mes cerrado

class CierreMensual(Base):
    __tablename__ = "cierres_mensuales"
    id = Column(Integer, primary_key=True)
    mes = Column(Integer, nullable=False)
    anio = Column(Integer, nullable=False)
    total_ingresos_ars = Column(Float, default=0.0)
    total_gastos_ars = Column(Float, default=0.0)
    total_ingresos_usd = Column(Float, default=0.0)
    total_gastos_usd = Column(Float, default=0.0)
    saldo_ars = Column(Float, default=0.0)
    saldo_usd = Column(Float, default=0.0)
    fecha_cierre = Column(DateTime, default=datetime.utcnow)

def get_engine():
    os.makedirs("data", exist_ok=True)
    return create_engine("sqlite:///data/inmo_v3.db", connect_args={"check_same_thread": False})

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

def init_db(engine):
    Base.metadata.create_all(engine)
