"""
services/product_service.py
-----------------------------
Query-building logic for the product catalog: search, category filter,
and sorting. Kept out of routes/products.py so the route stays a thin
HTTP adapter.
"""

from models.product import Product


def query_products(search=None, category=None, sort=None):
    query = Product.query

    if search:
        like = f"%{search.strip()}%"
        query = query.filter(Product.name.ilike(like))

    if category:
        query = query.filter(Product.category.ilike(category.strip()))

    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.id.asc())

    return query.all()


def get_categories():
    rows = Product.query.with_entities(Product.category).distinct().all()
    return sorted({row[0] for row in rows})
