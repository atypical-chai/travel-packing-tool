# AWS cost estimate — travel-packing-tool pilot

**Region:** us-west-2  
**Date:** 2026-11-01  
**Stack:** private S3 + CloudFront (frontend) + Lambda + API Gateway HTTP API (backend)

## Assumptions
- ~10,000 page views / month
- ~5,000 API requests / month
- ~50 KB average transfer per page view (cached assets)
- Lambda: 512 MB, ~400 ms average duration
- Small staging + pilot traffic (current Vercel project is near-idle)

## Monthly estimate (USD, on-demand list rates)
| Service | Approx |
| --- | --- |
| S3 | < $0.10 |
| CloudFront | < $0.15 |
| Lambda | < $0.05 |
| API Gateway HTTP API | < $0.05 |
| CloudWatch Logs | ~ $0.10 |
| **Total** | **~ $0.30 / month** |

Free-tier credits (if still available on the account) can reduce this further.  
A **$5/month AWS Budget alert** will be configured so spend surprises are visible early. Budgets alert; they do not hard-cap spend.

## Notes
- Pricing MCP was unavailable during estimation; figures come from published on-demand rates via a local estimate script.
- This pilot does **not** use EC2 / GPU quota.
