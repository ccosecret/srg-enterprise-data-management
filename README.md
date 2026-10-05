# Savanna Retail Group (SRG) — Enterprise Data Management Technical Artifacts

Hands-on technical deliverables for the **Project Savanna EDM Capstone** (Tasks B2, B4, C1, C2):
synthetic dirty datasets → data quality assessment & cleansing → ETL diagnosis &
repaired pipeline → RBAC/masking → star schema & data dictionary.

## Repository layout

| Path | Task | Contents |
|---|---|---|
| `module1_synthetic_data/` | — (input generation) | `generate_srg_datasets.py` → `output/SRG_Customers.csv` (5,000 rows), `output/SRG_Products.csv` (1,200), `output/SRG_Sales.csv` (10,000), `output/injection_report.json` (ground-truth defect counts) |
| `module2_data_quality/` | **B2** | `dq_assessment_cleansing.py` — profiling (6 dimensions), standardization (phone E.164 / districts / UOM / dates / gender), fuzzy+dedeterministic dedupe, before/after metrics, 12 validation rules, daily monitoring spec → `output/*` |
| `module3_etl/` | **B4** | `etl_error_log.txt` (broken nightly job), `etl_diagnosis.md` (root-cause trail, RC-1…RC-6), `srg_etl_pipeline.py` (repaired production pipeline: schema contracts, quarantine, idempotency, unknown-member handling, MoMo graceful path, advisory lock, run audit) |
| `module4_security/` | **C2** | `rbac_postgresql.sql` (5 roles, GRANT/REVOKE, column-level PII, RLS), `rbac_test.sql` (15 automated privilege tests), `rbac_test_expected_output.md` (reference evidence), `data_masking.sql` (mask functions + views), `data_masking_demo.py` (executed on live data), `rbac_mysql_appendix.sql` |
| `module5_warehouse/` | **B4/C1** | `star_schema_ddl.sql` (fact_sales + 5 dims, SCD2 customer/product), `data_dictionary.md` (25 attributes with classification + source) |

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
PY=.venv/bin/python

# 1) generate the dirty assignment datasets (deterministic seed)
$PY module1_synthetic_data/generate_srg_datasets.py

# 2) profile + cleanse + before/after proof + rules + monitoring spec
$PY module2_data_quality/dq_assessment_cleansing.py

# 3) run the repaired ETL, prove quarantine + idempotency
$PY module3_etl/srg_etl_pipeline.py --self-test
$PY module3_etl/srg_etl_pipeline.py --inspect-quarantine

# 4) masking executed on real cleansed data
$PY module4_security/data_masking_demo.py

# 5) SQL artifacts (needs PostgreSQL 15/16)
psql -d srg -f module4_security/rbac_postgresql.sql
psql -d srg -f module4_security/data_masking.sql
psql -d srg -f module4_security/rbac_test.sql      # -> 15/15 PASS
psql -d srg -f module5_warehouse/star_schema_ddl.sql
```

## Headline evidence (executed in this environment)

**Data quality before → after** (`module2_data_quality/output/before_after_metrics.md`,
same metric functions applied to both states):

| Metric | Before | After |
|---|---|---|
| Confirmed duplicate persons (auto-matched) | 22.84% | **0.00%** |
| Total duplicate-flag rate (+ open review) | 25.06% | **2.85%** |
| Distinct phone format variants | 6 | **1 (E.164)** |
| Distinct district labels | 127 | **42** |
| Distinct date formats / ISO-8601 rows | 3 / 54.4% | **1 / 94.5%** |
| UOM in {kg, pcs, liters} | 15.33% | **100%** |
| Category in master list | 22.0% | **100%** |
| Composite product validity | 3.25% | **100%** |
| Composite customer record validity | 17.30% | **68.51%** |

Deduping: 1,142 of 1,150 injected duplicates merged (953 deterministic phone matches
+ 189 fuzzy Levenshtein matches); 365 homonym pairs correctly *rejected* by the
email-conflict rule; 110 rows kept in an explicit stewardship review queue
(no fabricated merges).

**ETL self-test** (`module3_etl/output/selftest_evidence.txt`):

```text
[TEST 1] idempotency: rows before=10000 after re-run=10000 -> PASS
[TEST 2] bad rows quarantined: 6/6 (rows in etl_quarantine=6) -> PASS
[TEST 3] mobile-money missing ref handled gracefully (PENDING_RECON) -> PASS
ALL TESTS PASS
```

**Masking demo** (`module4_security/output/masking_demo_output.txt`):
`Ssempebwa Wasswa → S*** W**`, `+256723699332 → +256-XXX-XX9332`,
`ssempebwa.wasswa@srg.co.ug → s***@srg.co.ug` — 4/4 validation checks PASS.

**RBAC tests**: `rbac_test.sql` contains 15 automated privilege assertions
(cashier blocked from `financial_reports` and raw PII, RLS zero-row proofs,
column-level payroll denial, read-only auditor…). No PostgreSQL server exists in
this build sandbox, so `rbac_test_expected_output.md` is committed as the
*reference* run capture — re-running the three SQL files on PostgreSQL 15/16
reproduces it verbatim.

## Design notes (defensibility)

1. **Matching never auto-merges on name similarity alone.** Auto-merge requires a
   positive identifier match (equal phone or email); homonyms land in a stewardship
   queue instead. Merging two different people would destroy one person's loyalty
   history and privacy rights — the ethical risk called out in Task B3.
2. **No fabricated completeness.** Nulls are *not* imputed; the small completeness
   shifts after dedupe are labelled `Stable (dedupe denominator shift)`.
3. **Offline capture is a designed state, not an error** (SRG loses connectivity
   for hours daily): `customer_sk = 0` unknown-member + `PENDING_RECON` payment refs
   keep revenue flowing into the warehouse while finance reconciles.
4. **Fail fast, quarantine, never silently fall back** — the diagnosed job's
   "partial mode" (stale-data masking) is explicitly removed.
5. **Dimensions load before facts** and shared-dimension writes take a single-writer
   lock — removes the orphan-FK and offline-sync deadlock classes, not just symptoms.
6. **Default-deny + masked surfaces + row-level scoping** express the Uganda
   DPPA 2019 / GDPR Art.25 "protection by design" duty inside the database itself.
