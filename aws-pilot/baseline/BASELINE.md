# Baseline — travel-packing-tool (pre-AWS)

## Source alignment
- Repo: `atypical-chai/travel-packing-tool`, branch `master`
- HEAD matches Vercel production commit: `f91b832ebe794bf905d7f4f8724c169e33d35f4d`

## Live hosts
- Frontend: https://travel-packing-tool.vercel.app (HTTP 200)
- Backend: https://travel-packing-tool-backend.onrender.com (HTTP 200)
- Frontend root directory on Vercel: `frontend`
- Frontend analytics: Vercel Web Analytics script (`/_vercel/insights/script.js`) — will not load on AWS; expected for pilot

## SQLite catalog
- Path: `backend/database/items.db`
- Size: 16384 bytes
- Rows in `items_master`: 85
- `json_each` tag queries work
- Seed helper deletes rows — **do not run** against the packaged catalog

## API fixtures (Render)
| Case | Status | pack/buy/do totals |
| --- | --- | --- |
| vacation_domestic (general) | 200 | 25 / 2 / 5 (32) |
| work_international | 200 | 35 / 4 / 12 (51) |
| outdoor_cold_rain | 200 | 44 / 3 / 5 (52) |
| invalid body (missing required fields) | 422 | n/a |

Raw JSON saved beside this file.

## Packaging approach
- Frontend: static files → S3 + CloudFront (OAC)
- Backend: FastAPI via Mangum on Lambda Python 3.13 + HTTP API
- Catalog: ship `items.db` with the function; open read-only; no RDS

## Manual UI checks (Vercel)
Recorded expectations for AWS comparison:
- Dark theme default; toggle persists after refresh (`localStorage`)
- Trip form → personalized checklist (not the hardcoded fallback)
- Add / complete / delete items; restart clears; refresh restores saved trip
- Mobile layout usable (existing “Mobile UI fixes” commit)
