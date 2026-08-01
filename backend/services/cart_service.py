"""
services/cart_service.py
--------------------------
Business rules for the shopping cart: adding items (merging quantities if
the product is already in the cart), updating quantities, removing items,
and computing totals. Stock availability is enforced here so it can't be
bypassed by calling the API directly.
"""

from database import db
from models.cart import CartItem
from models.product import Product


class CartError(Exception):
    pass


def get_cart(user_id):
    return CartItem.query.filter_by(user_id=user_id).all()


def cart_total(user_id):
    items = get_cart(user_id)
    return round(sum(item.product.price * item.quantity for item in items if item.product), 2)


def add_to_cart(user_id, product_id, quantity=1):
    if quantity <= 0:
        raise CartError("Quantity must be greater than zero.")

    product = Product.query.get(product_id)
    if not product:
        raise CartError("Product not found.")

    existing = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    new_quantity = (existing.quantity if existing else 0) + quantity

    if new_quantity > product.quantity:
        raise CartError(f"Only {product.quantity} unit(s) of '{product.name}' available.")

    if existing:
        existing.quantity = new_quantity
    else:
        existing = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(existing)

    db.session.commit()
    return existing


def update_cart_item(user_id, cart_item_id, quantity):
    item = CartItem.query.filter_by(id=cart_item_id, user_id=user_id).first()
    if not item:
        raise CartError("Cart item not found.")

    if quantity <= 0:
        raise CartError("Quantity must be greater than zero. Use remove instead.")

    if item.product and quantity > item.product.quantity:
        raise CartError(f"Only {item.product.quantity} unit(s) of '{item.product.name}' available.")

    item.quantity = quantity
    db.session.commit()
    return item


def remove_from_cart(user_id, cart_item_id):
    item = CartItem.query.filter_by(id=cart_item_id, user_id=user_id).first()
    if not item:
        raise CartError("Cart item not found.")

    db.session.delete(item)
    db.session.commit()


def clear_cart(user_id):
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
