#!/bin/sh
# Keep this app independent of the caller's folder and Compose project settings.
set -eu
academy_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ ! -f "$academy_root/.env" ]; then
    printf '%s\n' 'Missing Practical AI .env. Follow README.md setup before starting.' >&2
    exit 1
fi
exec docker compose \
    --project-name practical-ai-academy \
    --project-directory "$academy_root" \
    --env-file "$academy_root/.env" \
    --file "$academy_root/compose.yaml" \
    up -d --build --wait
