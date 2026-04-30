# syntax=docker/dockerfile:1.7
# ─── Build stage ──────────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_LIVEKIT_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_LIVEKIT_URL=$NEXT_PUBLIC_LIVEKIT_URL \
    NEXT_TELEMETRY_DISABLED=1

RUN npm install -g pnpm@9.15.0

# 1. Copy only the files needed to resolve the dependency graph.
#    This layer is cached as long as lock files don't change.
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/frontend/package.json ./apps/frontend/package.json

# 2. Install deps — the pnpm store is cached across builds via BuildKit.
RUN --mount=type=cache,id=pnpm-store,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# 3. Copy source and build — only re-runs when source changes.
COPY apps/frontend ./apps/frontend

WORKDIR /app/apps/frontend
RUN pnpm build

# ─── Runtime stage ────────────────────────────────────────────────────────────
# standalone output bundles server.js + only the node_modules it needs.
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

COPY --from=builder --link /app/apps/frontend/.next/standalone ./
COPY --from=builder --link /app/apps/frontend/.next/static     ./apps/frontend/.next/static
COPY --from=builder --link /app/apps/frontend/public           ./apps/frontend/public

EXPOSE 3000
CMD ["node", "apps/frontend/server.js"]
