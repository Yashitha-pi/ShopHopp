"""
app.py
------
Application entrypoint. Creates the Flask app, wires up the database,
registers all route blueprints, and exposes a couple of infrastructure
endpoints (health check, root info) that will be useful later when this
service is containerized and monitored in Kubernetes.

Run locally with:
    python app.py
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS

from database import db, init_db
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.orders import orders_bp
from routes.admin import admin_bp


def create_app():
    """
    Application factory.

    Using a factory (instead of a bare module-level `app = Flask(__name__)`)
    keeps the project testable and makes it trivial to create multiple app
    instances with different configs (e.g. a separate config for automated
    tests, or for Locust load-testing runs later in the MLOps pipeline).
    """
    app = Flask(__name__)

    # --- Core configuration -------------------------------------------------
    # SECRET_KEY signs the session cookie used for login state.
    # In production (Docker/K8s) this should come from an environment
    # variable / Kubernetes secret rather than being hard-coded.
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'shopping.db')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Cross-site session cookie settings. Only needed once frontend and
    # backend live on different domains (same-site "Lax" default is fine
    # for local dev where both run on 127.0.0.1). Set COOKIE_CROSS_SITE=1
    # in production; it requires HTTPS on both domains, which most hosts
    # (Render, Railway, etc.) provide automatically.
    if os.environ.get("COOKIE_CROSS_SITE") == "1":
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
        app.config["SESSION_COOKIE_SECURE"] = True

    # --- CORS ----------------------------------------------------------------
    # The frontend is plain HTML/JS served from a different origin/port
    # (e.g. a static file server on :5500, or a separate hosting domain in
    # production) so we need CORS enabled. supports_credentials=True lets
    # the session cookie travel with fetch() requests.
    #
    # FRONTEND_ORIGIN can be a single URL or a comma-separated list, e.g.:
    #   FRONTEND_ORIGIN=https://your-frontend.onrender.com
    # Defaults to "*" for local development only — set this explicitly
    # once frontend and backend are hosted on different domains, since
    # browsers reject wildcard origins on credentialed requests.
    frontend_origin = os.environ.get("FRONTEND_ORIGIN", "*")
    origins = [o.strip() for o in frontend_origin.split(",")] if frontend_origin != "*" else "*"
    CORS(app, supports_credentials=True, origins=origins)

    # --- Database --------------------------------------------------------
    init_db(app)

    # Seed demo data on first run (only inserts if the DB is empty).
    # This must run here — inside create_app() — rather than only under
    # `if __name__ == "__main__"`, because gunicorn (used in production/
    # Docker) imports `app` directly and never executes that block.
    with app.app_context():
        from database import seed_if_empty
        seed_if_empty()

    # --- Blueprints (modular route groups) --------------------------------
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(products_bp, url_prefix="/api")
    app.register_blueprint(cart_bp, url_prefix="/api")
    app.register_blueprint(orders_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # --- Infra endpoints ----------------------------------------------------
    @app.route("/")
    def root():
        return jsonify({
            "service": "shopping-app-backend",
            "status": "running"
        })

    @app.route("/health")
    def health():
        """
        Lightweight health check.
        Kubernetes liveness/readiness probes will hit this endpoint later,
        and the MLOps monitoring agent can poll it to confirm the pod is up
        before pulling deeper runtime metrics.
        """
        return jsonify({"status": "healthy"}), 200

    return app


app = create_app()

if __name__ == "__main__":
    # host=0.0.0.0 so the server is reachable from outside the container
    # once this is dockerized.
    app.run(host="0.0.0.0", port=5000, debug=True)