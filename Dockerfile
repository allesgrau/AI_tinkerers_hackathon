FROM python:3.11-slim AS base

WORKDIR /app

# System deps for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# ── Python backend ────────────────────────────────────────────────
COPY pyproject.toml voiceguard.yml ./
COPY voiceguard/ voiceguard/

RUN pip install --no-cache-dir -e .

# ── Frontend build (Node stage) ──────────────────────────────────
FROM node:20-slim AS ui-builder

WORKDIR /app
COPY package.json ./
RUN npm install

COPY vite.config.js voice-monitor.html index.html ./
COPY ui/ ui/
COPY ui_2/ ui_2/

RUN npm run build

# ── Final image ──────────────────────────────────────────────────
FROM base

# Copy built UI into the location FastAPI expects
COPY --from=ui-builder /app/dist/ /app/ui/dist/

EXPOSE 8000

CMD ["voiceguard", "serve", "--host", "0.0.0.0"]
