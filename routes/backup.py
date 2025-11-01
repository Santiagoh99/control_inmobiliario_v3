from flask import Blueprint
from utils.backupUtils import check_backup
from utils.security import requires_write_permission

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/backup_manual')
@requires_write_permission
def backup_manual():
    check_backup()
    return "Backup manual generado correctamente."
