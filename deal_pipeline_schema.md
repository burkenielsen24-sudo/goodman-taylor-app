Deal Pipeline CSV Schema

Purpose
- Canonical CSV for sourced deals used by the Streamlit pipeline (`app/pipeline.py`) and downstream scripts (enrichment, sanctions, diligence).

Filename
- `data/deal_pipeline.csv`

Primary columns (required)
- `id` (string): unique id, e.g. `uuid4().hex`.
- `project_name` (string): short human-friendly name for the opportunity.
- `company_name` (string): legal / operating name.
- `country` (string): ISO 3166-1 alpha-2 country code (preferred) or full country name.
- `stage` (string): one of `sourced`, `screening`, `diligence`, `term_sheet`, `negotiation`, `closed_won`, `closed_lost`.
- `lead_source` (string): e.g., `direct`, `partner`, `pitch_event`, `referral`.
- `owner` (string): internal owner (email or user id).
- `ask_amount` (decimal): numeric amount requested (in `currency`), e.g. `250000.00`.
- `currency` (string): ISO 4217 currency code (e.g. `USD`, `GBP`, `KES`).
- `equity_offered` (decimal): percentage or fraction, store as numeric percent (e.g., `12.5`).
- `tags` (string): comma-separated tags (e.g., `family-first,pet-care,active-lifestyle`).
- `impact_theme` (string): short label for impact area (e.g., `health`, `education`, `agriculture`).
- `created_at` (datetime ISO8601): e.g., `2025-11-18T14:30:00Z`.
- `notes` (string): free text / short description (PII caution).

Enrichment columns (added by `scripts/enrich_deals.py`)
- `opencorporates_id` (string): OpenCorporates URI or id if found.
- `jurisdiction` (string): registration jurisdiction (from registry).
- `incorporation_date` (date): `YYYY-MM-DD` if available.
- `lei` (string): LEI code if available.
- `employees_estimate` (int): estimate if available.
- `revenue_estimate` (decimal): estimate (local currency or USD depending on enrichment config).
- `currency_standard` (string): normalized currency code used for enrichment.
- `fx_rate_to_usd` (decimal): FX rate applied for normalization; include `fx_rate_date` in enrichment.
- `sanctions_match` (bool): `true` if any sanctions/PEP match flagged.
- `sanctions_match_source` (string): e.g., `OFAC,UN,OpenSanctions`.
- `sanctions_match_confidence` (string): `high|medium|low` (heuristic; human review required).
- `last_enriched_at` (datetime ISO8601).

Diligence columns (optional, populated during diligence)
- `last_funding_round` (string)
- `last_funding_amount` (decimal)
- `last_funding_date` (date)
- `financials_snapshot_id` (string): reference to `data/financials.csv` snapshot.

Validation rules / notes
- `id` must be unique.
- `country` should be an ISO code where possible—use a mapping table if user entry is free text.
- `ask_amount` must be parseable as numeric; prefer storing in smallest currency unit for ledger accuracy in `transactions.csv`.
- `tags` should be canonicalized on ingestion (lowercase, trimmed) to match playbook tags.
- `sanctions_match` must never be auto-published outward; any `true` requires human review and an audit log.

PII & Sensitive data guidance
- `notes` may contain PII or partner-sensitive items — treat `data/deal_pipeline.csv` as sensitive until sanitized.
- Create a sanitized export (`tools/sanitize_deal_pipeline.py`) before sharing externally.

Example minimal header (CSV)
- `id,project_name,company_name,country,stage,lead_source,owner,ask_amount,currency,equity_offered,tags,impact_theme,created_at,notes`

Recommended companion files
- `data/deal_pipeline_enriched.csv`
- `data/sanctions_report.csv`
- `data/financials.csv` (per-deal snapshots)

Schema versioning
- Add a `schema_version` comment or column in the CSV metadata when making structural changes. Keep schema changelog in this file.

Contact
- For schema changes, coordinate with `app/pipeline.py` maintainers and update `INVESTMENT_PLAYBOOK.md`.
