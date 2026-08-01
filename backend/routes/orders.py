"""
routes/orders.py
------------------
POST /api/checkout
GET  /api/orders
"""

from flask import Blueprint, jsonify

from services.auth_service import require_login
from services.order_service import checkout, get_orders, OrderError

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/checkout", methods=["POST"])
@require_login
def do_checkout(current_user):
    try:
        order = checkout(current_user.id)
    except OrderError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Order placed successfully.", "order": order.to_dict()}), 201


@orders_bp.route("/orders", methods=["GET"])
@require_login
def order_history(current_user):
    orders = get_orders(current_user.id)
    return jsonify({"orders": [o.to_dict() for o in orders]}), 200
