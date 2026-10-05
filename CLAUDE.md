# amin-travels-hajj-core

FastAPI backend for Amin Travels & Tours (multi-agency Hajj/Umrah management). Module docs live in [docs/README.md](docs/README.md).

## Workspace layout (always applies)

This folder holds three separate things. Never mix their commits:

| Folder | What it is | Git |
|---|---|---|
| `./` (everything else) | Core API | this repo, PRs into `dev` |
| `amin-scraping-service/` | PRP scraper sidecar (port 8001) | **its own repo** `Tasmim-Adib/amin-scraping-service`, gitignored here; commit/push from inside that folder |
| `frontend-ref/` | Frontend, read-only reference | never edit, commit, push or deploy; list needed FE changes for the user instead |

- Scraper code belongs in `amin-scraping-service/`, never in core's `app/`. The scraper files in `app/core/utils/` (`prp_data_fetch.py`, `save_fetched_data.py`, `data_clean.py`) are stale copies and do not run in prod.
- Core's `POST /private/fetch-prp-data` is only a proxy to `http://localhost:8001/fetch-prp-data`. Any PRP sync behaviour change is a scraper change.

## Production (always applies)

- "Check / connect db" means the **prod** DB. Server SSH details are in `ssh/ssh.txt` (never print them). Postgres runs in the `pg17` docker container; the DB name is `aminapi`, not the one in local `.env`. Use read-only sessions (`PGOPTIONS='-c default_transaction_read_only=on'`) unless a write was asked for.
- Deploys are manual over SSH; GitHub Actions deploy is not reliable.
  - Core: container `amin-travels-hajj-dev`.
  - Scraper: `/root/amin-scraping-service`, container `prp-scraper`, deploy with `docker compose up -d --build` there. Its `.env` (DB password, credential encryption key) lives only on the server.
- Back up any prod file before editing it in place, and get the change into git afterwards so prod and the repo don't drift.

## PRP auto-sync rule (always applies)

- The scraper's nightly cron (3:05 AM Asia/Dhaka) syncs only rows in `core.agency_prp_credential` with `is_active AND auto_sync`.
- `auto_sync` defaults to FALSE. As of 2026-10-05 only **Amin Travels & Tours** has it TRUE; all other agencies are manual fetch only.
- A manual fetch saves or updates the agency's login but must never turn `auto_sync` on. Don't use `is_active` as the auto switch, because every manual fetch resets it to TRUE.
- To turn an agency on or off, run SQL only (no deploy):
  `UPDATE core.agency_prp_credential SET auto_sync = TRUE|FALSE WHERE LOWER(BTRIM(agency_name)) = LOWER('<agency>');`
