"""
routes/admin.py
------------------
POST   /api/admin/product
PUT    /api/admin/product/<id>
DELETE /api/admin/product/<id>

All endpoints require a logged-in admin user.
"""

from flask import Blueprint, request, jsonify

from database import db
from models.product import Product
from services.auth_service import require_admin

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/product", methods=["POST"])
@require_admin
def create_product(current_admin):
    data = request.get_json(silent=True) or {}

    required = ["name", "category", "price", "quantity"]
    missing = [f for f in required if data.get(f) in (None, "")]
    if missing:
        return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

    try:
        product = Product(
            name=data["name"],
            description=data.get("description", ""),
            category=data["category"],
            price=float(data["price"]),
            quantity=int(data["quantity"]),
            image=data.get("image"),
        )
    except (TypeError, ValueError):
        return jsonify({"error": "price must be a number and quantity must be an integer."}), 400

    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product created.", "product": product.to_dict()}), 201


@admin_bp.route("/product/<int:product_id>", methods=["PUT"])
@require_admin
def update_product(current_admin, product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found."}), 404

    data = request.get_json(silent=True) or {}

    if "name" in data:
        product.name = data["name"]
    if "description" in data:
        product.description = data["description"]
    if "category" in data:
        product.category = data["category"]
    if "image" in data:
        product.image = data["image"]
    if "price" in data:
        try:
            product.price = float(data["price"])
        except (TypeError, ValueError):
            return jsonify({"error": "price must be a number."}), 400
    if "quantity" in data:
        try:
            product.quantity = int(data["quantity"])
        except (TypeError, ValueError):
            return jsonify({"error": "quantity must be an integer."}), 400

    db.session.commit()
    return jsonify({"message": "Product updated.", "product": product.to_dict()}), 200


@admin_bp.route("/product/<int:product_id>", methods=["DELETE"])
@require_admin
def delete_product(current_admin, product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found."}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted."}), 200
