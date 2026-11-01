# Handoff — travel-packing-tool AWS pilot (present)

**Updated:** 2026-11-01  
**Status:** Staging live on AWS. Vercel + Render still untouched for production traffic.  
**Code PR (not required for already-deployed staging):** https://github.com/atypical-chai/travel-packing-tool/pull/1

## Live URLs
| Role | URL |
| --- | --- |
| AWS staging frontend | https://d1ygtemkaj8b77.cloudfront.net |
| AWS staging API | https://55h6y8n93h.execute-api.us-west-2.amazonaws.com |
| Production frontend (unchanged) | https://travel-packing-tool.vercel.app |
| Production API (unchanged) | https://travel-packing-tool-backend.onrender.com |

## Stack
- CloudFormation stack: `travel-packing-tool-staging` (`us-west-2`)
- S3 bucket: `travel-packing-tool-staging-298808185616` (versioned, private, OAC)
- CloudFront distribution: `EI3WG8EWPF3WC`
- Lambda: `travel-packing-tool-staging-api` (Python 3.13, Mangum, read-only SQLite)
- Budget alert: $5/month → `ambujsriv@gmail.com` (alert only, not a hard cap)
- GitHub OIDC role: `arn:aws:iam::298808185616:role/travel-packing-tool-github-deploy`
- Workflow: `.github/workflows/deploy-aws-staging.yml`
- Outputs snapshot: `aws-pilot/staging-outputs.json`

## Verification done
- Branch HEAD matched Vercel commit `f91b832`
- Render baseline fixtures captured under `aws-pilot/baseline/`
- AWS API matches fixtures (`infra/compare_api.py` → 0 failures)
- CloudFront smoke + browser create-checklist returned personalized catalog items (not the JS fallback)
- Rollback demo: S3 previous `index.html` restored + Lambda `staging` alias created (`aws-pilot/rollback-demo.json`)
- Cost estimate ~ **$0.30/month** at low pilot traffic (`aws-pilot/COST-ESTIMATE.md`)

## How to redeploy
```bash
python3 infra/deploy.py --phase all --budget-email ambujsriv@gmail.com
# or phased: infra | frontend-render | backend | frontend-aws-api
python3 infra/compare_api.py --base-url https://55h6y8n93h.execute-api.us-west-2.amazonaws.com
python3 infra/smoke_frontend.py --base-url https://d1ygtemkaj8b77.cloudfront.net --expect-api https://55h6y8n93h.execute-api.us-west-2.amazonaws.com
```

## Launch decisions still open (Phase 5)
- Final custom domain (cannot move `*.vercel.app` to AWS)
- `localStorage` is origin-scoped: Vercel saved trips will not appear on a new hostname unless we add export/import or a notice
- Observation period before any teardown of Vercel/Render — **no deletes without repeated explicit confirmation**

## Lessons to carry to other apps
1. Baseline live behavior + API fixtures before touching infra
2. Static sites → S3 + CloudFront OAC; small Python APIs → Lambda + HTTP API is enough
3. Keep old hosts until staging proves personalized responses (watch for silent frontend fallbacks)
4. Prefer OIDC deploy roles over long-lived AWS keys
5. Reassess separately for Next.js / GPU / AI apps — this pilot is not a one-size architecture
