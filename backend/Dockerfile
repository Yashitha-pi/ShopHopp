# backend/Dockerfile
# Builds the Flask API as a standalone container image.
# This is the image whose CPU/Memory requests your MLOps pipeline will
# eventually predict and inject into k8s/deployment_template.yaml.

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first so Docker can cache this layer whenever only
# application code changes (common in the CI pipeline this project targets).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production \
    PYTHONUNBUFFERED=1

EXPOSE 5000

# gunicorn instead of the Flask dev server for anything container-hosted.
# --preload runs create_app() once in the master process *before* forking
# workers, so database setup/seeding happens exactly once no matter how
# many workers are configured — without it, each worker independently
# imports app.py and races to create/seed the same SQLite file, which
# crashes with "table already exists".
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--preload", "app:app"]