# Savanna Retail Group (SRG) — Enterprise Data Management Portfolio

Consultancy deliverables for the **Project Savanna EDM Capstone**: the complete
portfolio for SRG's 18-month data turnaround — executed technical artifacts
(cleansing, ETL, security, warehouse, dashboard) plus the board-ready written
portfolio (governance, compliance, architecture, MDM, metadata, security &
privacy, analytics, roadmap, reflection).

**Published dashboard:** https://ccosecret.github.io/srg-enterprise-data-management/
(self-contained `module6_dashboard/dashboard.html` served via GitHub Pages —
filters, drill-down, KPI recompute; substituted for a Power BI/Tableau licence
because no per-user licence fits inside the UGX 480M envelope — rationale in
`docs/D2_decision_log.md` D-08)

## Repository layout

| Path | Task | Contents |
|---|---|---|
| `module1_synthetic_data/` | — (input generation) | `generate_srg_datasets.py` → `output/SRG_Customers.csv` (5,000 rows), `output/SRG_Products.csv` (1,200), `output/SRG_Sales.csv` (10,000), `output/injection_report.json` (ground-truth defect counts) |
| `module2_data_quality/` | **B2** | `dq_assessment_cleansing.py` — profiling (6 dimensions), standardization (phone E.164 / districts / UOM / dates / gender), deterministic + fuzzy dedupe, before/after metrics, 12 validation rules, daily monitoring spec → `output/*` |
| `module3_etl/` | **B4** | `etl_error_log.txt` (broken nightly job), `etl_diagnosis.md` (root-cause trail, RC-1…RC-6), `srg_etl_pipeline.py` (repaired pipeline: schema contracts, quarantine, idempotency, unknown-member handling, MoMo graceful path, advisory lock, run audit) |
| `module4_security/` | **C2** | `rbac_postgresql.sql` (5 roles, GRANT/REVOKE, column-level PII, RLS), `rbac_test.sql` (15 automated privilege tests), `rbac_test_expected_output.md` (reference evidence), `data_masking.sql` (mask functions + views), `data_masking_demo.py` (executed on live data), `rbac_mysql_appendix.sql` |
| `module5_warehouse/` | **B4/C1** | `star_schema_ddl.sql` (fact_sales + 5 dims, SCD2 customer/product), `data_dictionary.md` (25 attributes with classification + source) |
| `module6_dashboard/` | **C3** | `build_dashboard.py` (reads `module3_etl/etl_demo.db` only; control-total guard), `dashboard_template.html`, `vendor/chart.umd.min.js` (inlined, no CDN), `dashboard.html` (self-contained output) |
| `module7_realtime/` | **B4** | `footfall_stream_sample.json` — representative sensor stream sample (instructor file unavailable in this build environment; schema documented in `docs/B4_realtime_architecture.md`) |
| `docs/` | **A1–D2 (written portfolio)** | 31 consultancy documents — see coverage map below |

## Written portfolio coverage map

| Task | Primary artifact(s) in `docs/` |
|---|---|
| **A1** EDM diagnostic memo + lifecycle map + DAMA mapping | `A1_edm_diagnostic_memo.md`, `A1_data_lifecycle_map.md` |
| **A2** Governance charter, RACI, policies, compliance register, CFO rebuttal | `A2_governance_charter.md`, `A2_policies.md`, `A2_compliance_register.md`, `A2_cfo_memo.md` |
| **B1** Architecture trade-off, ER model, normalization, denormalization | `B1_architecture_decision.md`, `B1_er_model.md`, `B1_normalization.md` |
| **B2** Data-quality assessment & cleansing (executed) | `module2_data_quality/output/` (before/after metrics, 12 rules, monitoring spec) |
| **B3** MDM design (golden record, survivorship, matching, hierarchies) | `B3_mdm_design.md` |
| **B4** ETL: diagnosis, pipeline (executed), workflow doc, ETL vs ELT, real-time | `module3_etl/`, `B4_etl_workflow.md`, `B4_etl_vs_elt.md`, `B4_realtime_architecture.md`, `module7_realtime/` |
| **C1** KPI lineage, impact analysis, catalog tool comparison, metadata governance | `C1_lineage_kpi.md`, `C1_impact_analysis.md`, `C1_catalog_tools.md` |
| **C2** Threat model & 10+ risk register, encryption/masking spec, DPIA, breach response, audit checklist (+ executed RBAC/masking) | `C2_threat_model_risk_register.md`, `C2_encryption_masking_spec.md`, `C2_dpia_loyalty_app.md`, `C2_breach_response_plan.md`, `C2_compliance_audit_checklist.md`, `module4_security/` |
| **C3** Business questions, dashboard (published), executive insight brief, cloud/AI verdicts, maturity assessment | `C3_business_questions.md`, `C3_dashboard.md`, `C3_executive_insight_brief.md`, `C3_emerging_tech.md`, `C3_analytics_maturity.md`, `module6_dashboard/` |
| **D1** 18-month roadmap, budget within UGX 480M, coherence narrative | `D1_roadmap_18months.md` |
| **D2** Decision log (26 entries), red-team critique, reflective essay, viva prep | `D2_decision_log.md`, `D2_red_team.md`, `D2_reflective_essay.md`, `D2_viva_prep.md` |

Every task's "Think deeper" prompt is answered under an explicit
`### Think-deeper answer` heading in the relevant document.

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

# 5) rebuild the self-contained dashboard from the warehouse output
$PY module6_dashboard/build_dashboard.py     # -> module6_dashboard/dashboard.html
                                             #    + index.html (GitHub Pages root)

# 6) SQL artifacts (needs PostgreSQL 15/16)
psql -d srg -f module4_security/rbac_postgresql.sql
psql -d srg -f module4_security/data_masking.sql
psql -d srg -f module4_security/rbac_test.sql      # -> 15/15 PASS
psql -d srg -f module5_warehouse/star_schema_ddl.sql
```

SQL artifacts are parse-validated with `sqlfluff` (postgres + mysql dialects,
0 errors). The dashboard build refuses to publish if `etl_demo.db` is missing
or the control total ≠ UGX 252,382,814.16, so a stale or half-built page can
never go live.

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

**Dashboard** (`module6_dashboard/dashboard.html`, ~0.6 MB self-contained):
6-month net revenue **UGX 252,382,814** over 10,000 lines; average basket
UGX 25,238; mobile money 73.2% of revenue; new known customers collapsing
1,272 → 148/month; 69.4% churn proxy (Nov actives absent in Dec); 849 of 7,385
MoMo lines (11.5%) pending reconciliation; 8.7% of revenue walk-in/unattributed —
every figure recomputes under the page's filters.

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
7. **Round once, disclose provenance.** Headline percentages are computed then
   rounded once (MoMo share 73.2%, not the 48.2+25.1 component sum); all
   quantitative claims carry their six-month, course-provided-extract caveat.
