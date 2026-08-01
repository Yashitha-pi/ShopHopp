# frontend/Dockerfile
# Serves the static HTML/CSS/JS with nginx. The entrypoint script rewrites
# js/config.js at container startup so the image can be pointed at any
# backend URL via the API_BASE_URL env var (no rebuild needed).

FROM nginx:1.27-alpine

COPY . /usr/share/nginx/html
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
