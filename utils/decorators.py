from functools import wraps
from flask_login import login_required, current_user
from flask import abort


def roles_required(*roles):
    def wrapper(func):
        @wraps(func)
        @login_required
        def decorated_view(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)
            return func(*args, **kwargs)
        return decorated_view
    return wrapper