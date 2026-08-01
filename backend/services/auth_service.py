"""
services/auth_service.py
-------------------------
Business logic for registration and login, kept separate from the Flask
route handlers so it can be unit-tested (or reused, e.g. by an admin CLI)
without spinning up a request context.
"""

import re
from functools import wraps
from flask import session, jsonify

from database import db
from models.user import User

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def require_login(view_func):
    """
    Route decorator that rejects the request with 401 unless a user is
    logged in (session cookie present), and injects the User object as
    the first argument to the wrapped view.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Authentication required."}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Authentication required."}), 401

        return view_func(user, *args, **kwargs)

    return wrapper


def require_admin(view_func):
    """Like require_login, but also requires the user to be an admin."""
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        user = User.query.get(user_id) if user_id else None
        if not user:
            return jsonify({"error": "Authentication required."}), 401
        if not user.is_admin:
            return jsonify({"error": "Admin privileges required."}), 403

        return view_func(user, *args, **kwargs)

    return wrapper


class AuthError(Exception):
    """Raised for expected, user-facing auth failures (bad input, etc.)."""
    pass


def validate_registration(name, email, password):
    if not name or not name.strip():
        raise AuthError("Name is required.")
    if not email or not EMAIL_RE.match(email):
        raise AuthError("A valid email is required.")
    if not password or len(password) < 6:
        raise AuthError("Password must be at least 6 characters long.")


def register_user(name, email, password):
    validate_registration(name, email, password)

    if User.query.filter_by(email=email.lower().strip()).first():
        raise AuthError("An account with this email already exists.")

    user = User(name=name.strip(), email=email.lower().strip())
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(email, password):
    if not email or not password:
        raise AuthError("Email and password are required.")

    user = User.query.filter_by(email=email.lower().strip()).first()
    if not user or not user.check_password(password):
        raise AuthError("Invalid email or password.")

    return user
