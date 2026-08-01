"""
routes/auth.py
----------------
POST /api/register
POST /api/login
POST /api/logout
GET  /api/me

Session-based auth: on login we store user_id in Flask's signed session
cookie. `require_login` (used by other route modules) reads that cookie.
"""

from flask import Blueprint, request, jsonify, session

from services.auth_service import register_user, authenticate_user, AuthError

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    try:
        user = register_user(
            name=data.get("name"),
            email=data.get("email"),
            password=data.get("password"),
        )
    except AuthError as e:
        return jsonify({"error": str(e)}), 400

    session["user_id"] = user.id
    return jsonify({"message": "Registration successful.", "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    try:
        user = authenticate_user(data.get("email"), data.get("password"))
    except AuthError as e:
        return jsonify({"error": str(e)}), 401

    session["user_id"] = user.id
    return jsonify({"message": "Login successful.", "user": user.to_dict()}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out."}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    from models.user import User

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"user": None}), 200

    user = User.query.get(user_id)
    return jsonify({"user": user.to_dict() if user else None}), 200
