import os, shutil, sqlite3, datetime

DB_PATH = "data/inmo_v3.db"
BACKUP_DIR = "backups"
MAX_REGISTROS = 5000
MAX_MB = 5

os.makedirs(BACKUP_DIR, exist_ok=True)

def check_backup():
    if not os.path.exists(DB_PATH):
        print("[BACKUP] DB no encontrada")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM movimientos")
        total = cur.fetchone()[0]
    except sqlite3.OperationalError:
        print("[BACKUP] Tabla 'movimientos' no encontrada, se omite backup.")
        conn.close()
        return
    conn.close()

    size_mb = os.path.getsize(DB_PATH)/(1024*1024)
    if total >= MAX_REGISTROS or size_mb >= MAX_MB:
        fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"backup_{fecha}.db")
        shutil.copy2(DB_PATH, backup_path)
        print(f"[BACKUP] Backup automático generado: {backup_path}")
