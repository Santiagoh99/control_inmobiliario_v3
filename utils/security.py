from flask import request, Response
from functools import wraps
import os

ALLOWED_WRITE_IPS = set(ip.strip() for ip in os.getenv("ALLOWED_WRITE_IPS","").split(",") if ip.strip())

def requires_write_permission(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "GET":
            return f(*args, **kwargs)
        client_ip = request.remote_addr
        print(f"[SECURITY] IP intentando modificar: {client_ip}")
        if client_ip in ALLOWED_WRITE_IPS:
            return f(*args, **kwargs)
        return Response("No tiene permisos para modificar", 401)
    return decorated

def init_ip_security(app):
    @app.before_request
    def log_request():
        print(f"[REQUEST] {request.method} {request.path} desde {request.remote_addr}")
