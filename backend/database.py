"""
database.py
-----------
Central place for the SQLAlchemy `db` object and database lifecycle
helpers (init + demo seeding). Keeping this separate from app.py avoids
circular imports between app.py and the model modules.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Bind the SQLAlchemy instance to the Flask app and create tables."""
    db.init_app(app)

    with app.app_context():
        # Import models so SQLAlchemy knows about them before create_all().
        from models.user import User          # noqa: F401
        from models.product import Product     # noqa: F401
        from models.cart import CartItem       # noqa: F401
        from models.order import Order, OrderItem  # noqa: F401

        db.create_all()


def seed_if_empty():
    """
    Populate the database with demo products (and an admin user) the first
    time the app runs against an empty database. This is what makes the
    app immediately usable for demos / load testing without a manual data
    entry step.
    """
    from models.product import Product
    from models.user import User

    if Product.query.count() == 0:
        demo_products = [
            Product(
                name="Wireless Headphones",
                description="Over-ear noise cancelling wireless headphones with 30hr battery life.",
                category="Electronics",
                price=59.99,
                quantity=40,
                image="https://picsum.photos/seed/headphones/400/400",
            ),
            Product(
                name="Mechanical Keyboard",
                description="Hot-swappable mechanical keyboard with RGB backlighting.",
                category="Electronics",
                price=89.50,
                quantity=25,
                image="https://picsum.photos/seed/keyboard/400/400",
            ),
            Product(
                name="Running Shoes",
                description="Lightweight breathable running shoes for daily training.",
                category="Footwear",
                price=74.99,
                quantity=60,
                image="https://picsum.photos/seed/shoes/400/400",
            ),
            Product(
                name="Canvas Backpack",
                description="Durable 20L canvas backpack with laptop sleeve.",
                category="Accessories",
                price=45.00,
                quantity=35,
                image="https://picsum.photos/seed/backpack/400/400",
            ),
            Product(
                name="Stainless Water Bottle",
                description="Insulated 1L stainless steel water bottle, keeps drinks cold 24h.",
                category="Accessories",
                price=19.99,
                quantity=100,
                image="https://picsum.photos/seed/bottle/400/400",
            ),
            Product(
                name="Yoga Mat",
                description="Non-slip 6mm yoga mat with carry strap.",
                category="Fitness",
                price=24.99,
                quantity=50,
                image="https://picsum.photos/seed/yogamat/400/400",
            ),
            Product(
                name="Smart Watch",
                description="Fitness smart watch with heart-rate and sleep tracking.",
                category="Electronics",
                price=129.99,
                quantity=20,
                image="https://picsum.photos/seed/smartwatch/400/400",
            ),
            Product(
                name="Ceramic Coffee Mug",
                description="350ml ceramic mug, microwave and dishwasher safe.",
                category="Home",
                price=9.99,
                quantity=150,
                image="https://picsum.photos/seed/mug/400/400",
            ),
        ]
        db.session.bulk_save_objects(demo_products)
        db.session.commit()
        print("[seed] Inserted demo products.")

    if User.query.filter_by(email="admin@shop.com").first() is None:
        admin = User(
            name="Admin",
            email="admin@shop.com",
            is_admin=True,
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("[seed] Created default admin user (admin@shop.com / admin123).")
