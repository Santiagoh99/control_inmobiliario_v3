from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField
from wtforms.validators import DataRequired

class MovimientoForm(FlaskForm):
    tipo = SelectField("Tipo", choices=[("ingreso","Ingreso"),("gasto","Gasto")], validators=[DataRequired()])
    descripcion = StringField("Descripción", validators=[DataRequired()])
    monto = DecimalField("Importe", validators=[DataRequired()])
    moneda = SelectField("Moneda", choices=[("ARS","Pesos - ARS"),("USD","Dólares - USD")], validators=[DataRequired()])
    medio_pago = SelectField("Medio de pago", choices=[("Efectivo","Efectivo"),("MercadoPago","MercadoPago")], validators=[DataRequired()])
    fecha = DateField("Fecha", format="%Y-%m-%d")
