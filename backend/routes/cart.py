"""
routes/cart.py
----------------
GET    /api/cart
POST   /api/cart/add
PUT    /api/cart/update
DELETE /api/cart/remove

All endpoints require a logged-in user (session cookie).
"""

from flask import Blueprint, request, jsonify

from services.auth_service import require_login
from services.cart_service import (
    get_cart, add_to_cart, update_cart_item, remove_from_cart, cart_total, CartError,
)

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/cart", methods=["GET"])
@require_login
def view_cart(current_user):
    items = get_cart(current_user.id)
    return jsonify({
        "items": [item.to_dict() for item in items],
        "total": cart_total(current_user.id),
    }), 200


@cart_bp.route("/cart/add", methods=["POST"])
@require_login
def cart_add(current_user):
    data = request.get_json(silent=True) or {}
    try:
        item = add_to_cart(
            user_id=current_user.id,
            product_id=data.get("product_id"),
            quantity=int(data.get("quantity", 1)),
        )
    except CartError as e:
        return jsonify({"error": str(e)}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "product_id and quantity must be valid numbers."}), 400

    return jsonify({"message": "Added to cart.", "item": item.to_dict()}), 200


@cart_bp.route("/cart/update", methods=["PUT"])
@require_login
def cart_update(current_user):
    data = request.get_json(silent=True) or {}
    try:
        item = update_cart_item(
            user_id=current_user.id,
            cart_item_id=data.get("cart_item_id"),
            quantity=int(data.get("quantity", 0)),
        )
    except CartError as e:
        return jsonify({"error": str(e)}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "cart_item_id and quantity must be valid numbers."}), 400

    return jsonify({"message": "Cart updated.", "item": item.to_dict()}), 200


@cart_bp.route("/cart/remove", methods=["DELETE"])
@require_login
def cart_remove(current_user):
    data = request.get_json(silent=True) or {}
    try:
        remove_from_cart(user_id=current_user.id, cart_item_id=data.get("cart_item_id"))
    except CartError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"message": "Item removed from cart."}), 200
