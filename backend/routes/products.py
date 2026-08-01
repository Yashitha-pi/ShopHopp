"""
routes/products.py
--------------------
GET /api/products              (supports ?search=&category=&sort=)
GET /api/products/<id>
GET /api/categories
"""

from flask import Blueprint, request, jsonify

from models.product import Product
from services.product_service import query_products, get_categories

products_bp = Blueprint("products", __name__)


@products_bp.route("/products", methods=["GET"])
def list_products():
    search = request.args.get("search")
    category = request.args.get("category")
    sort = request.args.get("sort")  # "price_asc" | "price_desc"

    products = query_products(search=search, category=category, sort=sort)
    return jsonify({"products": [p.to_dict() for p in products]}), 200


@products_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found."}), 404
    return jsonify({"product": product.to_dict()}), 200


@products_bp.route("/categories", methods=["GET"])
def list_categories():
    return jsonify({"categories": get_categories()}), 200
