# Task C1 Deliverable — Change Impact Analysis: Customer Address Schema Restructure

## Task C1 — Metadata Management (C7)

**Client:** Savanna Retail Group (SRG) · **Prepared by:** Lead Enterprise Data Management Consultant
**Status:** Draft for Data Governance Council · **Version:** 1.0
**Proposed change ID:** `CHG-ADDR-001` — replace single free-text `district TEXT` with a structured address block.
**Classification:** Confidential (internal) · **Regulatory anchor:** DPPA 2019 (Cap. 97) s.3 (accuracy/principles), s.11 (collection from data subject), s.24/s.28 (access, rectification); GDPR Art.5(1)(d) accuracy, Art.16 rectification, Art.25 protection by design where EU members are in scope (Cap. 97 consolidated numbering — verify against official gazette before external use).
**Cross-references:** `docs/C1_lineage_kpi.md` (KPI-CRM-001 lineage hops 3–6), `docs/C1_catalog_tools.md` (catalog change record), Task A2 charter (steward/Council roles, POL-001 tags).

---

### 1. Change description

| Field | Value |
|---|---|
| **Change ID** | CHG-ADDR-001 |
| **From** | `district TEXT` (free text; standardised post-hoc to the official district list, 127 raw labels → 42 canonical) |
| **To** | `address_line1 TEXT NULL`, `address_line2 TEXT NULL`, `city TEXT NULL`, `district TEXT REFERENCES dim_district(district_code)` (FK to official list), `region TEXT` (lookup from district — Northern/Eastern/Central/Western), `postal_code TEXT NULL`, `gps_lat/gps_lon NUMERIC NULL` **optional, opt-in only** |
| **Why** | Free text is why SRG had 127 district labels; a FK enforces VR-002 *structurally* instead of by rule; `region` unlocks trade-area/logistics zone reporting; structured lines enable delivery routing for the omnichannel model |
| **New reference table** | `dim_district (district_code PK, district_name, region, valid_from, valid_to)` seeded from the official Uganda district list (42 labels after cleansing) |
| **Privacy note** | Address fields are **Confidential**; precise GPS stays **opt-in** (no silent collection — DPPA s.7/s.11; GDPR Art.6(1)(a) + Art.25 for app consent; see `docs/C2_dpia_loyalty_app.md` §3 minimisation) |
| **Default risk rating** | **MEDIUM-HIGH**: touches capture forms, MDM, ETL, security views, warehouse, and 3 dashboard surfaces |

---

### 2. Dependency analysis

Impact counts (summary): **15 downstream dependencies** · **3 dashboard tiles/filters** · **3 data-quality rules/checks** (VR-002, DQC-03, DQC-04) · **6 code paths/SQL artifacts** · **4 capture forms/templates** · **2 report packs** · **1 data-dictionary row** (#14) · **1 survivorship rule** · **1 MDM attribute policy**.

| Dependency ID | Downstream artifact / process | Current usage | What breaks | Change required | Owner | Effort |
|---|---|---|---|---|---|---|
| DEP-01 | `module2_data_quality/output/profile_before.md` + `before_after_metrics.md` — profile metric *"District stored as official name"* + **`DISTRICT_VARIANTS` variant maps** (127 → 42 labels) + **VR-002** + **DQC-03** | Profiling counts distinct raw district labels; standardisation maps variants → canonical; VR-002 validates membership of the official list; DQC-03 alerts at < 99.5% resolution | With a FK, "distinct raw labels" and "alias map" become vestigial — but **removing them too early breaks legacy-row backfill and re-profiling of pre-migration data**; DQC-03's "new unresolved label pattern > 50 rows/day" trigger can no longer fire (input is constrained), giving false green | Keep alias map for backfill only; **rewrite VR-002** as "FK resolves AND `district = dim_district.district_name`"; **re-baseline DQC-03** to FK-violation count + orphan count (threshold: > 0 = incident); add DQC-04 field split (`city`, `region` completeness) | Data Steward (Marketing Officer) + EDM Consultant | M |
| DEP-02 | `module2_data_quality` **survivorship rule** *"district: latest POS-verified"* | When merging duplicate identities, district value from the most recent POS-verified record wins | Merged records mix old free-text district with new FK value → survivorship compares incompatible types; a stale free-text value could beat a valid FK | Version the survivorship rule: after cutover, survivorship selects the **latest valid FK row**; free-text rows are auto-downgraded to "unverified" and never win | EDM Consultant | S |
| DEP-03 | `module3_etl/srg_etl_pipeline.py` — `dim_customer` load (SCD2, `row_hash`) | Reads cleansed customer files, computes `row_hash`, opens/closes SCD2 versions; golden-map remap | New columns change `row_hash` inputs → **every existing customer row looks "changed"** → mass SCD2 version churn (3,858 golden records re-versioned in one run, bloating history and restating history-dependent marts) | Add columns to the hash *selectively* (hash new fields only after backfill verified); staged rollout flag; pre/post row-count control totals; dimensions still load before facts (CA-5) | IT Operations Lead (SQL-capable) | M |
| DEP-04 | `module4_security/data_masking.sql` — `customers_masked` view (**district passthrough**) + `rbac_postgresql.sql` **RLS** | Analysts see non-identifying `district` (comment: *"geographic district is non-identifying"*); RLS scopes by `store_sk` | View column list no longer resolves (SQL error for every analyst role); new columns `address_line1/2` and GPS **are identifying** and would leak through an unchanged passthrough; masking demo expectations shift | Extend view with new columns **explicitly classified**: `district`, `city`, `region` pass through; `address_line1/2`, `gps_*` masked/omitted for `data_analyst`, raw only via column GRANT to `compliance_officer`/`cdm_admin`; **RLS logic unaffected** (store-scoped, not address-scoped) — regression-test only | Head of IT | M |
| DEP-05 | `module5_warehouse/star_schema_ddl.sql` — `dim_customer` + **`data_dictionary.md` row #14** (`dim_customer.district`, TEXT, Confidential, "POS signup (enriched/cleansed by ETL)") | Warehouse DDL + 25-attribute dictionary with classification and source | DDL, dictionary row #14 and tagging taxonomy become wrong; geo segmentation metadata stale; catalog seed (Phase 1) inherits the error | Extend DDL (new columns + `dim_district` + FK); **split dictionary row #14 into rows #14a–#14g** with per-attribute classification (`address_line1/2` = Restricted-adjacent Confidential, GPS = Restricted); update source/lineage hop notes | EDM Consultant | M |
| DEP-06 | **Dashboard district/geo filters — 3 tiles** (revenue by district/city map, store trade-area comparison, customer-home-district mix) | Filter/group on free-text `district` | Any tile grouping by raw text splits on legacy variants; new `city`/`region` fields not present historically → blank groups; KPI footnotes in `docs/C1_lineage_kpi.md` (walk-in caveat) unaffected but geo tiles must re-point | Re-point to canonical FK/`dim_district`; backfill-dependent tiles get a "geo completeness from <date>" banner; retire one free-text filter | CRM Officer (tile owner) + EDM Consultant | S |
| DEP-07 | **MDM golden record** (match + survivorship + review queue) | District used as corroborating attribute in the weighted score and in stewardship review display | Type mismatch in scoring inputs; stewards see blank district for migrated rows if backfill lags → wrong review decisions | Add structured address to golden-record display; hold district's score weight at 0 until backfill verified ≥ 99.5% | EDM Consultant | S |
| DEP-08 | **POS signup form** (23 stores, offline-capable) | Free-text or loosely-typed district entry at till | Form writes column that no longer exists / can't satisfy FK offline → **checkout blocked during outages** (stores are already offline hours daily) | Dropdown/alias picker (VR-002 intent made structural), **offline-friendly**: store district *code* locally, queue FK resolution on sync; keep free-text fallback disabled after cutover; cashier retraining | Retail Systems Manager | L |
| DEP-09 | **E-commerce checkout (SavannaShop ECOM01)** | Address block for delivery; district free text | Checkout API contract break → failed orders; address validation latency | Version the API (additive first, deprecate old field after 1 ETL cycle); server-side district picker; validate against `dim_district` | E-commerce Lead (SQL-capable) | M |
| DEP-10 | **CRM import template** (spreadsheets + SaaS CRM) | Analysts import member lists with `district` column | Imports rejected by FK → campaign uploads fail silently downstream | Re-issue template with `district_code` + `city` + `region` + data-validation dropdowns; add template version column; reject stale templates at load (schema contract, hop 1) | CRM Officer | S |
| DEP-11 | **Loyalty profile capture (app / in-store forms)** | Profile completion screen stores district; 180k members | Profile save failures; existing members keep old free-text value until they edit | App: structured picker; **do not force re-entry** — migrate server-side; in-app edit triggers the new format | CRM Officer + Product Owner | M |
| DEP-12 | **Delivery / logistics zone reports** | Manual zone assignment from district text | Misrouted deliveries where legacy variants differ; `region` not available → zones re-cut | Rebuild zone mapping on `dim_district.region`; validate 100% of active delivery addresses post-backfill | Logistics Officer | M |
| DEP-13 | **Store trade-area reports** (customer home district → store trade area) | Group customers by district text, then by store | Grouping splits on legacy labels; double counting across 42 vs 127 labels | Recut on canonical FK; restate Jul–Dec 2024 trade-area baselines; document restatement in board pack | Merchandising Officer + EDM Consultant | S |
| DEP-14 | `module4_security/rbac_test.sql` seed inserts + `rbac_mysql_appendix.sql` column list | 15-test RBAC fixture inserts a `district` value; MySQL appendix lists `district` in column grants | Fixture INSERT fails → test suite red; appendix GRANTs miss new identifying columns (privilege gaps) | Update fixtures and both GRANT scripts; re-run suite (reference evidence: 15/15 PASS → must stay 15/15 PASS on PostgreSQL 15/16) | Head of IT | S |
| DEP-15 | Monitoring: **`scripts/dq_check.py`** district metrics used by DQC-03/DQC-04 + `dq_monitoring_spec.md` | Daily district resolution & completeness checks with remediation commands | Metrics measure the old reality; alerts either fire permanently or never fire | Re-point metrics to FK/orphan logic; update escalation text and remediation commands in `dq_monitoring_spec.md`; keep DQC-03 threshold at 99.5% | IT Operations Lead | S |

**Effort totals:** S = 6 · M = 8 · L = 1 (POS form). Calendar estimate with SRG's 4-person IT team (2 SQL-capable, 0 data-engineering): **10–14 weeks elapsed**, POS form on the critical path.

---

### 3. Migration plan

| Phase | Weeks | Activities | Exit criteria (gate) |
|---|---|---|---|
| **P0 — Prep & design** | 1–2 | Council approval (Task A2 charter); create `dim_district` seeded from the 42 canonical districts + region lookup; freeze the address contract (column list, nullability, codes); classify new attributes in `data_dictionary.md` (POL-001 tags); notify all 15 dependency owners (`docs/C1_catalog_tools.md` governance process) | Signed change record; `dim_district` reviewed by Data Steward; API/form designs agreed |
| **P1 — Dual-write** | 3–5 | Ship additive schema (new columns **nullable**, old `district` retained); POS/ECOM/CRM/loyalty write **both** old text and new structured fields; dashboard unchanged; ETL loads both | 7 days of dual-write with **≥ 99% of new signups carrying a valid `district_code`**; zero checkout/form outages |
| **P2 — Backfill** | 6–8 | Backfill `district` FK from the official list using the existing alias map (127 → 42); derive `region` from `dim_district` lookup; `city` from store/delivery profile where derivable, else NULL (never fabricated); unmatched → stewardship queue; re-run standardisation stage of `module2_data_quality/dq_assessment_cleansing.py` | ≥ 99.5% FK resolution (DQC-03 threshold); **0 unmatched rows left silently**; backfill report to Council |
| **P3 — Rule & view update** | 8–9 | Rewrite VR-002 (FK + name equality); re-baseline DQC-03/DQC-04; extend `customers_masked` view (passthrough for district/city/region, suppression for address lines/GPS); update `rbac_test.sql` fixtures + MySQL appendix; update survivorship rule (DEP-02) | Rule tests green; RBAC suite 15/15 PASS (reference procedure on PostgreSQL 15/16); masking demo still 4/4 checks |
| **P4 — Cutover** | 10 | Make `district` FK **NOT NULL** for new rows; disable free-text entry at all 4 capture points; re-point the 3 dashboard tiles; rebuild delivery zones + trade-area reports; update dictionary rows #14a–#14g; PR merged (metadata-as-code change control) | All gates P1–P3 green; tiles show no blank groups; Logistics sign-off on zones |
| **P5 — Monitor & close** | 11–14 | Daily DQC-03 (FK/orphan) + DQC-04 watch for 30 days; `row_hash` churn monitored in `etl_run_log`; hold rollback switch (old column retained) for 30 days post-cutover; then deprecate free-text column (drop only after one full quarterly dictionary review) | 30 days with zero P1 DQ incidents attributable to address; Council closes CHG-ADDR-001 |

### 4. Validation queries

```sql
-- V1: FK integrity — must return 0 rows after cutover
SELECT c.customer_sk, c.district
FROM dim_customer c
LEFT JOIN dim_district d ON d.district_name = c.district AND d.valid_to IS NULL
WHERE c.is_current AND c.district IS NOT NULL AND d.district_code IS NULL;

-- V2: Backfill coverage (gate: >= 99.5%)
SELECT COUNT(*) FILTER (WHERE district_code IS NULL) * 100.0 / COUNT(*) AS pct_unresolved
FROM dim_customer WHERE is_current;

-- V3: Region derivability — no customer without a region after P2
SELECT COUNT(*) AS missing_region FROM dim_customer WHERE is_current AND region IS NULL;

-- V4: SCD2 churn guard — version-per-customer must stay ~1 (alert if > 1.05 avg)
SELECT COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT customer_sk), 0) AS versions_per_customer
FROM dim_customer;

-- V5: Fact integrity — no orphan facts, unknown-member band unchanged
SELECT COUNT(*) AS orphan_facts FROM fact_sales f
LEFT JOIN dim_customer c ON c.customer_sk = f.customer_sk
WHERE c.customer_sk IS NULL;

-- V6: Legacy label leakage (raw landing) — expect 0 after P4
SELECT COUNT(*) FROM raw_customers
WHERE district IS NOT NULL AND district_code IS NULL;

-- V7: Re-run the district profile metric for before/after evidence
--     python module2_data_quality/dq_assessment_cleansing.py --stage profile
-- V8: Monitoring re-baseline evidence
--     DQC-03 = FK violation count + orphan count; DQC-04 = city/region completeness
```

### 5. Rollback plan

| Trigger | Action | Data safety |
|---|---|---|
| Cutover-day SQL/view failure, > 1% checkout or POS signup failures, FK constraint blocking offline sync replay, tile outage > 2h | **Revert to Phase P1 state**: re-enable free-text writes, point views/tiles back to legacy `district`, restore prior VR-002 and DQC-03 definitions from git, revert API version | Old `district TEXT` column is **retained and maintained through P5** — no data loss; dual-written rows remain compatible in both shapes |
| Partial failure (e.g., only POS offline-sync broken) | Feature-flag the FK enforcement **off** for offline queue only; online paths stay on new schema; fix forward within 48h | Quarantine table keeps rejected rows; replay after fix (never silent drop) |
| Backfill produced wrong district mapping | Restore from pre-P2 snapshot of `dim_customer` + raw landing (backup taken at P2 start), correct alias map, re-run backfill | SCD2 history preserved; correction is a new version, not an overwrite |
| Rollback after cutover | Council notified within 4h; incident logged; monitoring reverts to legacy DQC-03 for the rollback window | Rollback decision + reason recorded in change register (accountability, DPPA s.3) |

**Rollback owner:** Head of IT (Incident Lead per `docs/C2_breach_response_plan.md` roles). **Authority to roll back:** Head of IT, no waiting for Council (Council informed, not consulted, to protect the 4-hour target).

### 6. Communication to affected owners

| Audience | Channel & timing | Message | Owner |
|---|---|---|---|
| Data Governance Council | Change review, week 0; gate reviews weeks 5, 9, 14 | Approve CHG-ADDR-001, Effort totals, rollback authority, restatement policy | EDM Consultant |
| 15 dependency owners (DEP-01…DEP-15) | Dependency notice pack + 45-min walkthrough, week 1; reminder 5 working days before cutover | What changes in *their* artifact, dates, their action, and the escalation path | EDM Consultant |
| Store managers (23 stores) | Ops briefing + 1-page till notice, week 8; cashier micro-training at cutover | New district picker, offline behaviour, what to do if the list is missing (do not free-type) | Retail Systems Manager |
| IT team of 4 | Sprint planning weeks 1–2; runbook handover week 10 | Runbook: validation queries V1–V8, rollback switch, monitoring re-baseline | Head of IT |
| Finance / Logistics / Merchandising | Report re-cut notice, week 9 | Trade-area and zone baselines restated for Jul–Dec 2024; figures change *because* definitions changed, not because sales changed | EDM Consultant |
| CRM / Marketing | Template re-issue, week 5 | New import template version; old templates rejected from week 10 | CRM Officer |
| EU distributor partner (GDPR Art.13/14 transparency) | Partner notice before cutover if address fields are shared for fulfilment | Field-level change, lawful basis unchanged, updated Art.30 record entry | DPO (once appointed — see `docs/C2_compliance_audit_checklist.md` CHK-02) |

**Metadata rule for this change:** no artifact in the table above is "done" until its row in `module5_warehouse/data_dictionary.md` and its lineage hop in `docs/C1_lineage_kpi.md` are updated in the same pull request (metadata-as-code, see `docs/C1_catalog_tools.md`).

---

### Think-deeper answer

**Prompt: is this "just a column change"? What does the dependency table reveal that a naive migration would miss?**

It is not — and the register exposes three traps a naive migration hits. **First, the row_hash trap (DEP-03):** adding columns to `dim_customer` makes every one of the 3,858 golden records look *changed* in one nightly run, generating 3,858 SCD2 versions, restating history-dependent marts, and destroying trust in `valid_from/valid_to` — the fix (staged hashing, gated by verified backfill) is invisible unless you understand SCD2 semantics. **Second, the offline trap (DEP-08):** SRG loses connectivity hours daily, so an FK enforced naively at the till turns a metadata change into a *checkout outage* — the constraint must be satisfied asynchronously at sync time, which inverts the usual "just add the constraint" advice. **Third, the security trap (DEP-04):** a masking view that passed through `district` because it was "non-identifying" will, if extended carelessly, pass through `address_line1` and GPS — a confidentiality regression introduced by a *data-modeling* change, caught only because classification metadata (POL-001 tags) rides along with the schema. The broader lesson: in SRG's state of maturity, the real cost of a schema change is not the DDL — it is the **15 artifacts whose metadata must change in the same pull request**, which is precisely the argument for the catalog investment sequenced in `docs/C1_catalog_tools.md`.
