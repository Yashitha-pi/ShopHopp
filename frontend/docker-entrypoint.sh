#!/bin/sh
# docker-entrypoint.sh
# Rewrites js/config.js with the real backend URL at container startup,
# using the API_BASE_URL environment variable set in the Kubernetes
# Deployment / docker-compose file. This lets one built image be pointed
# at any backend address without rebuilding.
set -e

if [ -n "$API_BASE_URL" ]; then
  sed -i "s|window.API_BASE_URL = \".*\";|window.API_BASE_URL = \"$API_BASE_URL\";|" /usr/share/nginx/html/js/config.js
  echo "[entrypoint] API_BASE_URL set to $API_BASE_URL"
fi

exec nginx -g 'daemon off;'
