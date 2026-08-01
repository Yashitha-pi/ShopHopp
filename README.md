# Shopfront — Demo E-Commerce App

A small, modular full-stack shopping app: **Flask + SQLite** backend, **HTML/CSS/vanilla JS**
frontend. Built as the "guinea pig" application for an AI-based predictive resource allocation
/ MLOps pipeline (Docker → Kubernetes → CI/CD → ML-driven resource prediction → monitoring →
autoscaling) — so it's deliberately containerization- and load-test-friendly from day one.

## Features

- User registration & login (session-based auth, hashed passwords)
- Product catalog with search, category filter, and price sort
- Shopping cart (add / update quantity / remove, stock-aware)
- Checkout → order history (snapshots price-at-purchase-time)
- Admin panel (inline on the Products page for admin accounts): add / edit / delete products
- REST JSON API throughout, Flask Blueprints, business logic separated into a `services/` layer

## Project structure

```
shopping_app/
├── frontend/                # HTML, CSS, vanilla JS — talks to the API via fetch()
│   ├── index.html / products.html / login.html / register.html / cart.html / orders.html
│   ├── css/style.css
│   ├── js/  (config.js, api.js, main.js, auth.js, products.js, cart.js, orders.js)
│   ├── Dockerfile
│   └── docker-entrypoint.sh   # injects API_BASE_URL into config.js at container start
├── backend/
│   ├── app.py                # app factory, blueprint registration, /health
│   ├── database.py           # SQLAlchemy init + demo data seeding
│   ├── models/                # user.py, product.py, cart.py, order.py
│   ├── routes/                # auth.py, products.py, cart.py, orders.py, admin.py
│   ├── services/              # auth_service, product_service, cart_service, order_service
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── k8s/                       # Kubernetes manifests + deployment guide
├── docker-compose.yml         # local multi-container convenience
├── locustfile.py              # starter load test (for the later MLOps/Locust phase)
└── .gitignore
```

## Running locally (no Docker)

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
The API runs at `http://127.0.0.1:5000`. On first run it auto-creates `shopping.db` and seeds
8 demo products plus an admin account: **admin@shop.com / admin123**.

**Frontend** (any static file server works — just don't open the HTML files directly via
`file://`, since fetch() calls need a real origin):
```bash
cd frontend
python -m http.server 5500
```
Open `http://127.0.0.1:5500/index.html`.

> If you serve the frontend from a different host/port in the future, set
> `window.API_BASE_URL` before `js/api.js` loads (e.g. add
> `<script>window.API_BASE_URL = "https://your-api-domain/api";</script>` in each HTML file's
> `<head>`), or edit the default in `frontend/js/api.js`.

## Running with Docker Compose

```bash
docker compose up --build
```
- Frontend: http://localhost:8080
- Backend: http://localhost:5000

Note: with this setup the frontend container serves static files, but the browser still calls
the backend directly at `http://localhost:5000/api` (that's the default in `api.js`), so both
ports need to stay reachable from your machine.

## REST API reference

| Method | Endpoint                     | Auth        | Description                     |
|--------|-------------------------------|-------------|----------------------------------|
| POST   | `/api/register`               | —           | Create an account                |
| POST   | `/api/login`                  | —           | Log in (sets session cookie)     |
| POST   | `/api/logout`                 | —           | Log out                          |
| GET    | `/api/me`                     | —           | Current session user, if any     |
| GET    | `/api/products`                | —           | List products (`?search=&category=&sort=price_asc|price_desc`) |
| GET    | `/api/products/<id>`           | —           | Product detail                   |
| GET    | `/api/categories`               | —           | Distinct category list           |
| GET    | `/api/cart`                    | user        | View cart + total                |
| POST   | `/api/cart/add`                | user        | `{product_id, quantity}`         |
| PUT    | `/api/cart/update`              | user        | `{cart_item_id, quantity}`       |
| DELETE | `/api/cart/remove`              | user        | `{cart_item_id}`                 |
| POST   | `/api/checkout`                 | user        | Create order from current cart   |
| GET    | `/api/orders`                    | user        | Order history                    |
| POST   | `/api/admin/product`             | admin       | Create product                   |
| PUT    | `/api/admin/product/<id>`        | admin       | Update product                   |
| DELETE | `/api/admin/product/<id>`        | admin       | Delete product                   |
| GET    | `/health`                        | —           | Health check (for k8s probes later) |

## Running on Kubernetes (real cluster, publicly reachable)

Two options, both in `k8s/`:
- **Have (or want) a cloud VM?** See [`k8s/README.md`](k8s/README.md) — includes a genuinely-free
  Oracle Cloud option.
- **Want to use your own laptop as the host instead?** See
  [`k8s/local/README.md`](k8s/local/README.md) — runs a real cluster via Minikube and exposes it
  with a public URL via ngrok, no cloud account needed.

Short version (cloud path):
```bash
kubectl create secret generic shopfront-secrets --from-literal=secret-key=<random-value>
kubectl apply -f k8s/
```

## Load testing (Locust)

```bash
pip install locust
locust -f locustfile.py --host=http://127.0.0.1:5000
```
Open `http://localhost:8089` to set concurrent users / spawn rate and start the run. This is
also the natural place to later capture "estimated concurrent users / request rate" features
for the resource-prediction dataset.

## Notes for the MLOps pipeline this feeds into

- `backend/Dockerfile` and `frontend/Dockerfile` are ready for `docker build`.
- `/health` is already exposed for Kubernetes liveness/readiness probes.
- Code is intentionally modular (`models/` / `routes/` / `services/`) so future commits will
  produce clean, meaningful diffs for your feature-extraction step — e.g. touching only
  `services/cart_service.py` vs. touching `models/` + `routes/` + `services/` together should
  read as different "sizes" of change.
- `database.py`'s `SQLALCHEMY_DATABASE_URI` already reads from an environment variable, so
  swapping SQLite for a different DB (or pointing it at a mounted volume in k8s) needs no code
  changes.
