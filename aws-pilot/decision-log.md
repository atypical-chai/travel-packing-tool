# Decision log — travel-packing-tool AWS pilot

Append-only. Newer entries supersede older ones when noted.

## 2026-11-01 — S3 + CloudFront + Lambda HTTP API
- **Decision:** Host static frontend on private S3 behind CloudFront (OAC). Host FastAPI on Lambda + API Gateway HTTP API with packaged read-only SQLite.
- **Why:** Matches the app shape (static HTML/JS + tiny Python API). Avoids always-on EC2; stays inside existing Standard/GPU quotas for unrelated work.
- **Alternatives:** Amplify Hosting (less control for a reusable pipeline lesson); Fargate/EB (heavier ops for this pilot).

## 2026-11-01 — Keep SQLite catalog, do not introduce RDS
- **Decision:** Ship `backend/database/items.db` inside the Lambda zip; open with `mode=ro` when `READ_ONLY_DB=1`.
- **Why:** Catalog is reference data (85 rows). User checklists already live in browser `localStorage`.
- **Alternatives:** RDS/DynamoDB would add cost and migration complexity with no user-data benefit for this pilot.

## 2026-11-01 — CloudFormation + custom zip (no SAM CLI)
- **Decision:** Use raw CloudFormation (`infra/template.yaml`) and `infra/build_lambda.py` / `infra/deploy.py`.
- **Why:** `aws-sam-cli` failed to install on this Windows environment (path-length / incomplete package).
- **Alternatives:** SAM or CDK once tooling is reliable on the deploy machine / GitHub runners.

## 2026-11-01 — Dual-host CORS during pilot
- **Decision:** Allow Vercel + CloudFront staging origins together; do not remove Render/Vercel until an explicit cutover.
- **Why:** Safe rollback while testing AWS.
- **Alternatives:** Hard cutover in one DNS change (higher risk).

## 2026-11-01 — config.js for API base URL
- **Decision:** Frontend reads `window.TRAVEL_PACKING_API_BASE_URL` from `config.js`; AWS deploy overwrites that object in S3 only.
- **Why:** Same git tree can serve Vercel (Render API) and AWS staging (API Gateway) without fighting hosts.
- **Alternatives:** Build-time bundler env (unnecessary for plain static files).
