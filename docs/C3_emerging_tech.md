# Task C3.5 — Emerging Technology Evaluation: Cloud EDM Platform & AI-Driven Trends

**Client:** Savanna Retail Group (SRG) | **Prepared by:** Lead Enterprise Data Management Consultant
**Envelope constraint (non-negotiable):** UGX 480,000,000/year all-in (480,000,000 ÷ 12 = **UGX 40,000,000/month**; 1 USD ≈ UGX 3,700 → ≈ USD 130,000/year), covering licences, cloud **and** hires; IT team of 4 (2 SQL-capable, **zero data-engineering**); several stores offline for hours daily; PDPO audit within 12 months.

---

## Task C3 — Analytics, BI & Emerging Technology (C9)

### (a) ONE Cloud EDM Platform Stack — Azure vs AWS vs GCP vs Snowflake/Databricks

#### Evaluation criteria, weights and scores (1 = poor fit, 5 = excellent fit)

| # | Criterion (weight) | Why it matters at SRG | Azure | AWS | GCP | Snowflake / Databricks |
|---|---|---|---|---|---|---|
| 1 | **Fit with UGX 480M/yr all-in budget (25%)** | Cloud must leave room for 3 hires + licences + security; cloud line capped at ≤ UGX 90,000,000/18 months = **UGX 5,000,000/month** | 4 | 4 | 4 | 2 — consumption pricing (compute/credit) is unpredictable for a team that cannot forecast its own load |
| 2 | **Fit with skills — 4 staff, no data engineers (20%)** | Every managed-service dependency the team cannot operate becomes a consultant invoice | 4 — managed everything + Power BI low-code path | 3 — broad but more assembly required (Glue + MWAA + QuickSight are separate skills) | 3 — strong BigQuery, thinner orchestration/MLOps fit for this team | 2 — Databricks needs data engineers SRG does not have; Snowflake SQL is easy but admin/optimisation is not |
| 3 | **Connectivity realities — stores offline hours daily, no Ugandan cloud region (15%)** | Nearest-region latency + egress; dashboard must tolerate batch, not require always-on | 3 — South Africa North / West Europe nearest; batch-first patterns supported | 3 — af-south-1 / eu-west-1 comparable | 3 — africa-south1 / europe-west comparable | 3 — same latency physics; egress on top of compute credits |
| 4 | **EU-partner alignment / data residency (20%)** | European distributor partnership demands GDPR-equivalent practices; transfers governed by GDPR Art.44–49 + DPPA 2019 s.3 | 5 — mature EU regions, EU Data Boundary commitments, standard contractual clauses out of the box | 4 — EU regions + DPF/SCC support | 4 — EU regions + SCCs | 4 — EU/UK/South Africa regions available; shared-responsibility terms need review |
| 5 | **Integrated EDM services: warehouse + orchestration + catalog + masking (20%)** | One accountable vendor beats five contracts for a 4-person team; masking/RBAC must extend the Module 4 model | 5 — SQL/Postgres + Data Factory + Microsoft Purview catalog + Always Encrypted/dynamic masking | 4 — S3 + Glue + MWAA + Lake Formation + Macie (masking more manual) | 3 — BigQuery + Composer, but catalog/masking story is thinner for mid-market | 4 — excellent warehouse, but catalog/governance/masking are paid add-ons or third-party |
| | **Weighted total (max 5.00)** | | **4.25** | **3.65** | **3.45** | **2.95** |

*Arithmetic example (Azure): (0.25 × 4) + (0.20 × 4) + (0.15 × 3) + (0.20 × 5) + (0.20 × 5) = 1.00 + 0.80 + 0.45 + 1.00 + 1.00 = **4.25**.*

#### Verdicts

| Option | Verdict | Reasoning |
|---|---|---|
| **Microsoft Azure** — Blob/ADLS Gen2 + Azure Database for PostgreSQL + Data Factory (serverless SQL for ad-hoc) + Power BI | **ADOPT — phased** | Highest weighted score (4.25). One vendor spans storage, warehouse, orchestration, catalog and masking; the Power BI route is the cheapest Board-grade BI available to SRG and needs no data engineer; EU regions + SCCs directly serve the European distributor requirement. |
| AWS (S3 + RDS PostgreSQL + Glue/MWAA + QuickSight) | **Fallback — not selected** | Credible (3.65) and equally budget-safe, but requires the team to assemble and own more moving parts; re-evaluated at gate G1 if Azure pricing or EU terms move adversely. |
| Google Cloud Platform | **Not selected** | 3.45 — strong analytics engine, weakest integrated EDM/catalog fit for a 4-person mid-market team. |
| Snowflake / Databricks | **PILOT — deferred (revisit M13+)** | 2.95. Consumption/credit pricing is a real risk when nobody on staff can estimate or tune a workload, and Databricks assumes data-engineering capability SRG does not have. Revisit only if/when trigger T6 (dedicated data-engineering capability hired and load proven) fires. |

#### Cost fit — explicit arithmetic (cloud line ≤ UGX 90,000,000 / 18 months)

| Item | USD basis | UGX arithmetic | UGX / 18 months |
|---|---|---|---|
| Power BI Pro, 5 users | USD 10/user/month | 10 × 3,700 = **UGX 37,000/user/month**; 37,000 × 5 = 185,000/month; 185,000 × 18 = 3,330,000 | **UGX 3,330,000** (booked in the licences line of `D1_roadmap_18months.md`) |
| Managed PostgreSQL (prod + non-prod) | USD 300–600/month | 300 × 3,700 = 1,110,000/month … 600 × 3,700 = 2,220,000/month; × 18 | **UGX 19,980,000 – 39,960,000 (≈ 20–40M)** |
| Object storage, egress, backup, monitoring, orchestration worker | — | allowance within envelope | ≤ **UGX 46,670,000** (90,000,000 − 40,000,000 − 3,330,000 headroom check: 40,000,000 + 3,330,000 = 43,330,000; 90,000,000 − 43,330,000 = **UGX 46,670,000** remains for storage/egress/backup/monitoring) |
| **Cloud total** | | **UGX 3,330,000 + UGX 40,000,000 = UGX 43,330,000 ≤ UGX 90,000,000** cap (≈ USD 11,711 of the ≈ USD 24,324 cap: 90,000,000 ÷ 3,700 = 24,324) | **≤ UGX 90,000,000** — passes with UGX 46,670,000 headroom (≈ USD 12,613) |

#### Phasing and migration triggers

- **Phase 1 (M1–M6): stay on the current on-prem / SQLite + PostgreSQL pattern.** There is genuinely *nothing to migrate*: the committed dataset is a 10,000-line extract and `etl_demo.db` is a single ~2.7 MB file; paying cloud egress/compute for it would be waste, and Phase 1 funds instead the Odoo feed, dashboard and MoMo reconciliation where the value is. Cloud Phase 1 spend is limited to encrypted off-site backup and a non-prod managed PostgreSQL instance.
- **Migration triggers (any ONE authorises Phase 2 migration at gate G1/G3):**
  - **T1 — Volume:** warehouse exceeds ~5M fact rows/quarter or 50 GB, or nightly ETL routinely exceeds the offline sync window.
  - **T2 — Access:** more than 2 concurrent BI users outside HQ, or a Kenya/Rwanda entity needs in-region data.
  - **T3 — Resilience:** on-prem hardware/DR requirement can no longer be met by the 4-person team (second UPS/hardware failure in 6 months).
  - **T4 — Compliance:** the European distributor or the PDPO audit requires a hosted environment with contractual SCCs, documented residency and audited controls.
  - **T5 — Cost:** on-prem extension/UPS/licensing quotes exceed the cloud run-rate (UGX 5,000,000/month equivalent).
  - **T6 — Capability:** a hired data-engineer stabilises credit/consumption tuning — pre-condition for even *piloting* Snowflake/Databricks.

#### Data-residency / EU transfer note (non-negotiable)

No cloud region exists in Uganda, so any Azure/AWS/GCP deployment resolves to the nearest region (South Africa North / West Europe) — **latency and egress must be designed for (batch loads, aggregated extracts, no per-store chatty traffic)**, and the stores' existing offline-hours pattern already forces this design. For the **European distributor partnership**, personal data flowing to or from the EU is a *third-country transfer* under **GDPR Art.44–49**: the transfer mechanism must be **Standard Contractual Clauses plus a transfer impact assessment**, and the vendor must be contractually bound to GDPR-equivalent terms. This sits alongside the Uganda **DPPA 2019 s.3** protection principles (lawfulness, purpose limitation, minimisation, security) already implemented technically by Module 4's default-deny RBAC, RLS and masking — technical controls are necessary but not sufficient: the SCCs, records of processing and the breach-notification SOP are governance artefacts owned by the compliance workstream (`D1_roadmap_18months.md`, M1–M3 and M11–M12).

---

### (b) ONE AI-Driven Trend — AI-powered Data Quality vs Data Mesh vs DataOps

#### Screening against SRG's three hard constraints

| Trend | Budget fit (UGX 480M/yr) | Skills fit (4 staff, 0 data-eng) | Connectivity fit (offline stores) | Sequencing / evidence dependency | Verdict |
|---|---|---|---|---|---|
| **AI-powered data quality** (ML anomaly detection over profiling metrics, auto-remediation suggestions) | Tooling subscriptions would consume licences budget for *uncertain* gains; possible later from the contingency line | Weak — tuning, feature choice and false-positive triage need skills SRG is still building | Neutral — batch profiling suits offline reality | **Depends on a deterministic baseline.** The 12 rules VR-001…VR-012 and 10 checks DQC-01…DQC-10 must first produce 6+ months of profiling history and known anomaly rates (they already caught: duplicates 22.84%, UOM 15.33%, category 22%, pending MoMo 11.5%) | **PILOT — month 12+** |
| **Data mesh** (domain-owned data products, federated governance, self-serve platform) | Neutral on licences, heavy on organisation | **Very poor fit** — mesh assumes mature platform engineering plus a data team *per domain*; SRG has 6 domains (sales, customer, product, store, payment, finance) inside *one* 4-person team | Neutral | Requires platform maturity and domain data-product owners that do not exist; would re-create exactly the silos (5 product identifiers, 127 district labels, 23 disconnected POS) that Modules 2–3 were built to remove | **REJECT** |
| **DataOps** (CI for SQL/Python, scheduled orchestrated pipelines, monitoring, run-state visibility) | **≈ zero licence cost** — Git + existing Python + `etl_run_log`; training only | **Excellent fit** — 2 SQL-capable staff can maintain it; no data engineers required | Fits: idempotent replayable runs and quarantine already assume outages | **Already started:** version-controlled repo, `srg_etl_pipeline.py` self-tests 3/3 PASS, `etl_quarantine`, `etl_run_log`, DQC-07 quarantine-rate alerting, advisory-lock scheduling window | **ADOPT — lite** |

#### Verdicts and rationale

1. **AI-powered data quality — PILOT (from M12).** Anomaly detection is only as good as the normal it learned; SRG's defect history was *unknown* until Module 2 measured it. AI cannot invent missing business definitions (a district reference list, one golden product key, a UOM vocabulary) — those are governance artefacts humans must author first, and they now exist (42 districts, 6 categories, 3 UOMs, VR-008 uniqueness). From M12, feed the daily DQC metric history into unsupervised anomaly detection to catch *novel* defect patterns (e.g., a new store writing a new free-text label); keep every remediation human-approved. Cost: scoped inside the contingency line, no new licence before the pilot paper at gate G3.
2. **Data mesh — REJECT.** Mesh's premise is many domains with autonomous teams and a mature self-serve platform. SRG is *one retailer* with four IT staff (two SQL-capable, zero data-engineering) and six domains in one team — adopting mesh would either be theatre (domains on paper, same people doing the work) or would institutionalise silos by charter, ironically undoing the single golden record, conformed `dim_product`/`dim_customer` and shared star schema that the warehouse already delivers. Revisit only if SRG exceeds ~50 data-producing staff and multiple legal entities — not within this 18-month horizon.
3. **DataOps — ADOPT-LITE.** The high-value subset is free: CI runs `dq_assessment_cleansing.py`, `srg_etl_pipeline.py --self-test` and the 15 RBAC assertions on every commit; scheduled orchestration with alerting to the on-call rotation (fixing RC-6, the unmonitored mailbox); run-state surfaced in the 06:00 routine; quarantine-rate and pending-MoMo monitoring as pipeline KPIs. This codifies what the repaired pipeline already demonstrates and directly prevents the RC-1…RC-6 root causes from returning.

---

### Think-deeper answer

**Does "adopt Azure, but stay on-premises in Phase 1" contradict the GDPR-equivalent commitment to the European distributor — and where is the real sovereignty risk?**

No — but only because the commitment is being interpreted correctly. "GDPR-equivalent" is a *control and accountability* standard (lawful basis, minimisation, security by design, breach notification within 72 hours, transfer mechanism), not a physical location. Module 4 already expresses protection-by-design inside the database (default-deny RBAC, RLS, column-level grants, masking), and the Phase 1 pattern — local PostgreSQL/SQLite with encrypted off-site backup — processes no third-country transfer at all, so Art.44–49 is not even engaged until EU personal data flows. The real risks are different from the ones the vendor debate focuses on: (1) **latency and egress** — with no Ugandan region, the nearest region is South Africa or Europe, so the architecture must stay batch/aggregate (which the offline-hours store reality demands anyway); a chatty real-time sync design would be both expensive and fragile; (2) **lock-in asymmetry** — the cheaper and more integrated the managed stack (4.25 score), the harder the exit, which is why the migration triggers are written as *requirements*, not dates, and why the pipeline is deliberately portable SQL/Python with schema contracts rather than proprietary notebook code; (3) **governance lag** — the greater exposure is not the cloud vendor but the absence of records of processing, a breach register and a notification SOP, all of which must exist by the M12 PDPO audit irrespective of hosting. In other words, the cloud decision is the *least* risky item in this document; the exposure lives in process and organisation, which is precisely where the roadmap front-loads spend (M1–M3 incident remediation and SOP, M11–M12 audit). The deeper lesson for the Board: technology verdicts are only as good as their preconditions — AI-DQ waits for deterministic rules, Snowflake waits for a data engineer (T6), and cloud waits for a trigger that proves the migration pays for itself.
