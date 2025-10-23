# app/security/permissions.py
from functools import wraps
from flask import abort
from flask_login import current_user, login_required

def role_required(*roles):
    """Protect a view so only certain roles can access."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator
