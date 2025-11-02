from pathlib import Path

# Contenido del README.md
readme_content = """# 🏠 Control Inmobiliario v3

Aplicación de gestión financiera e inmobiliaria desarrollada con **Flask** y **SQLAlchemy**.  
Permite registrar ingresos, gastos, cierres mensuales, generar backups y visualizar estadísticas en un panel de control.

---

## 🚀 Características principales

- 📊 Panel de control con resumen de ingresos y gastos (ARS / USD).  
- 💾 Backups automáticos y manuales.  
- 🧾 Registro de movimientos con formulario.  
- 📈 Exportación de datos a CSV y Excel.  
- 🔐 Restricción de escritura por IP autorizada.  
- 🧱 Base de datos SQLite (`data/inmo_v3.db`).  

---

## ⚙️ Instalación

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/usuario/control_inmobiliario_v3.git
cd control_inmobiliario_v3
