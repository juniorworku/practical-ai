## Container release before cloud deployment

First pass the complete local container and isolated-restore experiment in session 31. Use an image registry with immutable revision tags. Never put provider keys in Docker build arguments, image layers or React variables. Supply runtime credentials from the platform's secret manager and use a least-privilege service identity. The voice gateway's static token, SQLite workspace fixture and process-local limits are deliberately local experiments; they are not the production identity, durable multi-replica workflow or shared quota implementation.

## Cloud Run deployment experiment

Prerequisites: an explicitly selected Google Cloud project with billing enabled, permission to deploy, an Artifact Registry repository, an existing managed PostgreSQL database/private connectivity, a configured service account, and Secret Manager entries. These commands can incur costs. Use your own operator-selected names and quotas. No resources are provisioned by this academy.

Save the following as deploy.sh. It refuses missing configuration, builds the supplied production application image, deploys a candidate without unauthenticated access, and bounds instance and request concurrency. `SERVICE_IMAGE_SOURCE` must point to your production HTTP gateway with a dependency-backed `/api/health/` endpoint and a listener on `$PORT`; it is not the unmodified local Compose topology.

```sh
#!/bin/sh
set -eu
: "${CLOUD_PROJECT:?Set your authorized project}"
: "${CLOUD_REGION:?Set your region}"
: "${IMAGE_REPOSITORY:?Set the existing regional registry repository}"
: "${SERVICE_NAME:?Set a new test service name}"
: "${SERVICE_ACCOUNT:?Set the approved runtime service identity}"
: "${SERVICE_IMAGE_SOURCE:?Set the production image source folder}"
: "${DATABASE_SECRET:?Set an existing database URL secret name}"
: "${REVISION_TAG:?Set an immutable source revision tag}"
IMAGE="$CLOUD_REGION-docker.pkg.dev/$CLOUD_PROJECT/$IMAGE_REPOSITORY/$SERVICE_NAME:$REVISION_TAG"
gcloud builds submit "$SERVICE_IMAGE_SOURCE" --project "$CLOUD_PROJECT" --tag "$IMAGE"
gcloud run deploy "$SERVICE_NAME" --project "$CLOUD_PROJECT" --region "$CLOUD_REGION" \
  --image "$IMAGE" --service-account "$SERVICE_ACCOUNT" \
  --no-allow-unauthenticated --min-instances 0 --max-instances 2 \
  --concurrency 8 --timeout 300 --cpu 1 --memory 1Gi \
  --set-secrets "DATABASE_URL=$DATABASE_SECRET:latest"
URL=$(gcloud run services describe "$SERVICE_NAME" --project "$CLOUD_PROJECT" --region "$CLOUD_REGION" --format='value(status.url)')
TOKEN=$(gcloud auth print-identity-token)
curl --fail --max-time 20 -H "Authorization: Bearer $TOKEN" "$URL/api/health/"
```

The values above are small test bounds, not throughput claims. IAM protects this operator experiment; a browser-facing SaaS needs its own authenticated access architecture. Configure the image for its database network and the application’s actual configuration names before running. Run migrations once as a release job against the selected schema, not concurrently in every replica. Pin the tested secret version in the release manifest rather than leaving `latest` in a reproducibility claim. Add a startup/readiness check that verifies the required datastore, and keep provider availability distinct from gateway readiness.

WebSockets are long-lived HTTP requests and remain subject to the platform request timeout. The client must reconnect with bounded backoff, reauthenticate and restore only owner-bound checkpoint state; it must not blindly replay audio or uncertain writes. State, quotas and background jobs must survive replacement of any instance. A configured concurrency of eight is not evidence that eight live audio streams meet the latency target.

## Load, rollback and cleanup evidence

Use a separate synthetic tenant and increment offered concurrency through 1, 2, 4, 8 and 16 with a fixed request/audio/context distribution. Record admitted/completed/rejected/failed work, queue time, p50/p95, review quality, provider requests/usage and total spend. Stop on a critical isolation failure or your configured spend/latency boundary. Budget alerts are notification, not a hard spending cap; enforce admission and maximum work before provider calls.

Record the previous healthy Cloud Run revision name before promotion. To roll back, use `gcloud run services update-traffic "$SERVICE_NAME" --to-revisions "$PREVIOUS_REVISION=100" --region "$CLOUD_REGION" --project "$CLOUD_PROJECT"` only after setting PREVIOUS_REVISION to the verified prior revision. Re-run readiness, owner denial and readback after rollback. Do not roll back a schema destructively; rehearse backward-compatible migration and isolated restore. Delete only this disposable test service when the experiment is finished; review registry, database and secret resources separately because deleting the service does not remove their ongoing costs.

## ECS comparison and GPU decisions

ECS expresses the same boundaries through a task definition, service desired count/autoscaling, private subnets/security groups, an application load balancer, Secrets Manager runtime injection and a separate migration task. Distinguish the task execution role (pull image/logs) from the application task role. Set container CPU/memory, load-balancer readiness, deregistration/draining and graceful termination. Store durable state outside tasks and use the same dataset/report for a platform comparison; more orchestration is a maintenance cost to measure.

A local or hosted Ollama/vLLM service adds a different capacity bottleneck: GPU memory, KV cache, batching and output length. Keep a separate GPU service from the web admission tier, authenticate its endpoint, restrict network exposure and measure its model/quantization-specific capacity. The five-slot arithmetic exercise is not a hardware benchmark. Promote a hybrid routing rule only after the same held-out tasks show an acceptable quality floor, data-residency compliance and useful-output savings over the fixed baseline.
