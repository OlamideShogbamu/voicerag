#!/usr/bin/env bash
# Deploy frontend (Next.js) and backend (FastAPI) to Google Cloud Run.
# The LiveKit agent runs on LiveKit Cloud — no agent deployment needed.
#
# Prerequisites:
#   gcloud auth login && gcloud auth configure-docker
#
# Usage:
#   export GCP_PROJECT_ID=your-gcp-project
#   export DATABASE_URL=...
#   export LIVEKIT_URL=wss://voicerag-jdjezq2t.livekit.cloud
#   export LIVEKIT_API_KEY=...
#   export LIVEKIT_API_SECRET=...
#   export OPENAI_API_KEY=...
#   bash infra/deploy/cloud-run.sh
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?GCP_PROJECT_ID is not set}"
REGION="${REGION:-us-central1}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

: "${DATABASE_URL:?DATABASE_URL is not set}"
: "${LIVEKIT_URL:?LIVEKIT_URL is not set}"
: "${LIVEKIT_API_KEY:?LIVEKIT_API_KEY is not set}"
: "${LIVEKIT_API_SECRET:?LIVEKIT_API_SECRET is not set}"
: "${OPENAI_API_KEY:?OPENAI_API_KEY is not set}"

BACKEND_IMAGE="gcr.io/$PROJECT_ID/voicerag-backend:latest"
FRONTEND_IMAGE="gcr.io/$PROJECT_ID/voicerag-frontend:latest"

# ─── Step 1: Deploy backend ───────────────────────────────────────────────────
echo "→ Building backend image..."
docker build -t "$BACKEND_IMAGE" \
  -f "$REPO_ROOT/infra/docker/backend.Dockerfile" \
  "$REPO_ROOT/apps/backend"
docker push "$BACKEND_IMAGE"

# Deploy with permissive CORS for now; we'll update it after the frontend URL is known
cat > /tmp/voicerag-backend-env.yaml << EOF
DATABASE_URL: "$DATABASE_URL"
LIVEKIT_URL: "$LIVEKIT_URL"
LIVEKIT_API_KEY: "$LIVEKIT_API_KEY"
LIVEKIT_API_SECRET: "$LIVEKIT_API_SECRET"
OPENAI_API_KEY: "$OPENAI_API_KEY"
CORS_ORIGINS: '["http://localhost:3000"]'
EOF

echo "→ Deploying backend..."
gcloud run deploy voicerag-backend \
  --image "$BACKEND_IMAGE" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8000 \
  --env-vars-file /tmp/voicerag-backend-env.yaml \
  --project "$PROJECT_ID"

BACKEND_URL=$(gcloud run services describe voicerag-backend \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --format 'value(status.url)')

echo "✅  Backend → $BACKEND_URL"

# ─── Step 2: Build and deploy frontend with real backend URL ──────────────────
echo "→ Building frontend image (NEXT_PUBLIC_API_URL=$BACKEND_URL)..."
docker build -t "$FRONTEND_IMAGE" \
  -f "$REPO_ROOT/infra/docker/frontend.Dockerfile" \
  --build-arg NEXT_PUBLIC_API_URL="$BACKEND_URL" \
  "$REPO_ROOT"
docker push "$FRONTEND_IMAGE"

echo "→ Deploying frontend..."
gcloud run deploy voicerag-frontend \
  --image "$FRONTEND_IMAGE" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 3000 \
  --project "$PROJECT_ID"

FRONTEND_URL=$(gcloud run services describe voicerag-frontend \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --format 'value(status.url)')

echo "✅  Frontend → $FRONTEND_URL"

# ─── Step 3: Update backend CORS with the real frontend URL ──────────────────
echo "→ Updating backend CORS to allow $FRONTEND_URL..."

cat > /tmp/voicerag-backend-env.yaml << EOF
DATABASE_URL: "$DATABASE_URL"
LIVEKIT_URL: "$LIVEKIT_URL"
LIVEKIT_API_KEY: "$LIVEKIT_API_KEY"
LIVEKIT_API_SECRET: "$LIVEKIT_API_SECRET"
OPENAI_API_KEY: "$OPENAI_API_KEY"
CORS_ORIGINS: '["$FRONTEND_URL","http://localhost:3000"]'
EOF

gcloud run deploy voicerag-backend \
  --image "$BACKEND_IMAGE" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8000 \
  --env-vars-file /tmp/voicerag-backend-env.yaml \
  --project "$PROJECT_ID"

echo ""
echo "✅  Done!"
echo ""
echo "   Frontend  → $FRONTEND_URL"
echo "   Backend   → $BACKEND_URL"
