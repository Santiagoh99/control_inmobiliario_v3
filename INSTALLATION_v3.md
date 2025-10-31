Control Inmobiliario v3 - Instalación y Uso

Requisitos:
- Python 3.10+
- pip

Pasos (macOS / Windows):
1) Descomprimir control_inmobiliario_v3.zip en una carpeta (ej: C:\inmo-ctrl-v3 o ~/control_inmobiliario_v3)
2) Abrir terminal / PowerShell y moverse a la carpeta
   cd /ruta/a/control_inmobiliario_v3
3) Crear y activar entorno virtual:
   - macOS:
     python3 -m venv venv
     source venv/bin/activate
   - Windows:
     python -m venv venv
     venv\Scripts\activate
4) Instalar dependencias:
   pip install -r requirements.txt
5) Ejecutar:
   python app.py
6) Abrir en el navegador manualmente:
   http://127.0.0.1:5000

Funciones principales:
- Alta de movimientos (tipo, descripción, monto, moneda ARS/USD, medio de pago)
- Cierre mensual y re-apertura
- Exportar CSV y Excel (.xlsx)
- Totales mensuales y anuales por moneda
