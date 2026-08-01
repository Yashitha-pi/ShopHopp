"""
models/cart.py
---------------
Cart table. Each row is one product line in one user's cart.
"""

from database import db


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    product = db.relationship("Product")

    def to_dict(self):
        product = self.product.to_dict() if self.product else None
        subtotal = round(self.product.price * self.quantity, 2) if self.product else 0
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "product": product,
            "subtotal": subtotal,
        }
