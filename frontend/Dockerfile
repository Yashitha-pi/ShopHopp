# frontend/Dockerfile
# Serves the static HTML/CSS/JS with nginx. The entrypoint script rewrites
# js/config.js at container startup so the image can be pointed at any
# backend URL via the API_BASE_URL env var (no rebuild needed).

FROM nginx:1.27-alpine

COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh

# Strip any Windows-style \r line endings that may have been introduced
# by Git checking out on Windows (belt-and-braces alongside .gitattributes,
# which should prevent this at the source — but this makes the image
# build itself immune regardless of how the file arrived).
RUN sed -i 's/\r$//' /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]