# syntax=docker/dockerfile:1

# --- Build stage: install workspace deps and build the static bundle ---
# Build context is the repo root so the pnpm workspace files are available.
FROM node:24-slim AS build
WORKDIR /repo

RUN corepack enable && corepack prepare pnpm@11.21.0 --activate

# Install dependencies (leverages layer caching on lockfile changes).
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY frontend/package.json ./frontend/package.json
RUN pnpm install --frozen-lockfile

# Build the frontend. VITE_API_BASE_URL is baked in at build time and must
# point at the browser-reachable backend (host-published port).
ARG VITE_API_BASE_URL=http://localhost:8080
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
COPY frontend ./frontend
RUN pnpm --filter @glo-4003/frontend build

# --- Runtime stage: serve the static build with nginx ---
FROM nginx:1.27-alpine AS runtime
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /repo/frontend/dist /usr/share/nginx/html

EXPOSE 80
