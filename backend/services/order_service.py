"""
services/order_service.py
----------------------------
Checkout logic: turns the current cart into an Order + OrderItems,
decrements stock, and empties the cart — all inside one DB transaction
so a failure partway through doesn't leave stock or the cart inconsistent.
"""

from database import db
from models.cart import CartItem
from models.order import Order, OrderItem


class OrderError(Exception):
    pass


def checkout(user_id):
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        raise OrderError("Cart is empty.")

    # Validate stock for every line before mutating anything.
    for item in cart_items:
        if not item.product:
            raise OrderError("A product in your cart no longer exists.")
        if item.quantity > item.product.quantity:
            raise OrderError(f"Only {item.product.quantity} unit(s) of '{item.product.name}' available.")

    total = round(sum(item.product.price * item.quantity for item in cart_items), 2)

    order = Order(user_id=user_id, total_price=total)
    db.session.add(order)
    db.session.flush()  # assigns order.id without committing yet

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price,
        )
        item.product.quantity -= item.quantity
        db.session.add(order_item)
        db.session.delete(item)  # empty the cart as part of the same transaction

    db.session.commit()
    return order


def get_orders(user_id):
    return Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
