# Part C — Protection, Metadata & Insight

## Task C1 — Metadata: Dictionary, Lineage & Catalog Strategy

**The dictionary.** The warehouse dictionary documents 25 core attributes across `fact_sales`, `dim_customer`, `dim_product`, `dim_store`, `dim_date` and `dim_payment_method`, pairing a plain-language business definition with technical metadata (column types, surrogate and business keys, SCD2 versioning, NUMERIC(14,2) money columns) and administrative metadata (classification, steward, source system). Each attribute carries one of three POL-001 sensitivity classes: Public (safe for external reporting), Confidential (internal business data whose leak harms competitiveness) and Restricted (personal or financial identifiers under DPPA 2019 s.25 and GDPR Art.4(1), reachable only by explicit grant plus masking). Restricted stays deliberately narrow — `payment_ref`, `full_name`, `phone_e164`, `email`, `consent_gdpr_eu` — which is what makes targeted masking and column-level grants possible instead of blanket encryption. Full dictionary: Appendix N.

**Lineage.** The Board reads one customer number each month: Monthly Active Customers (KPI-CRM-001), produced by a chain crossing 23 offline-capable POS databases, SavannaShop (ECOM01), a 180,000-member loyalty app, an MDM golden-record step and a star schema, in an estate with a documented history of silent failure (RC-1…RC-6, including four days of invisible failure). Lineage is therefore not documentation overhead but the control that makes the KPI defensible (DPPA s.3, GDPR Art.5(2)) and change impact-analysable. The nine documented hops condense to five stages, each carrying rule IDs, survivorship decisions and failure handling rather than folklore. Full lineage and impact analysis: Appendix O.

![Fig. C1 — Lineage of the Board KPI "monthly active customers": raw fields through every transformation to the dashboard](figures/C1_lineage_kpi_print.png){width=92%}

| Hop | What happens | Control / evidence |
|---|---|---|
| 1 | Raw fields (`customer_id`, `phone`, `email`, `signup_ts`) from 23 POS stores, SavannaShop, the loyalty app and CRM imports land under a schema contract with manifest and batch ID — no destructive transforms | Contract violation rejects the whole file (RC-1: never partial-load); row counts and control totals captured; a missing file marks the run `SOURCE_MISSING` |
| 2 | Validated then standardised: type coercion, `NULLIF`/`TRIM`, "N/A" to NULL; phone to E.164 (6 variants to 1), district to the official list (127 to 42), dates to ISO-8601 | Bad rows go to `etl_quarantine` with an error reason, never a silent fallback (RC-4); DQC-07 alerts above 0.5%; rule ID and before/after value stored per row |
| 3 | Golden record into `dim_customer`: deterministic phone or email match, auto-merge at score ≥ 90, name similarity never auto-merges; `row_hash` opens and closes SCD2 versions | 1,142 of 1,150 duplicates merged, 365 homonym pairs rejected, 110 to stewardship review, 5,000 → 3,858 golden records; dimensions load before facts (RC-5) |
| 4 | `fact_sales.customer_sk` assignment, then month aggregation: `COUNT(DISTINCT customer_sk)` with `customer_sk > 0`, `is_return = FALSE`, `event_ts` in month (Africa/Kampala), close at T+2 | `COALESCE` to 0 keeps walk-ins loadable while identity resolves; control-total mismatch halts the run (fail-fast, CA-4); `etl_run_log` records period and row counts |
| 5 | Least-privilege presentation: analysts read the masked view, the aggregate feeds the dashboard tile | Default-deny GRANTs, column REVOKE, store-scoped RLS; denied queries evidenced in the 15-test reference run (15/15 PASS); stale-data banner on the tile (RC-6) |

**Tagging taxonomy.** Three tag classes travel with every dictionary row: domain, sensitivity and quality. Domain tags scope ownership and vocabulary (`sales`, `customer`, `product`, `store`, `payment`, `calendar`), sensitivity tags drive the GRANT matrix and the masking views (`Public`, `Confidential`, `Restricted`), and quality tags record how a value became trustworthy (`standardized`, `mastered`, `derived`).

**Impact analysis.** Proposed change `CHG-ADDR-001` replaces free-text `district TEXT` with a structured address block and a `dim_district` foreign key, and the 15-dependency register shows this is not a column change. Six dependencies break hardest: the POS signup form at 23 offline stores (DEP-08), where a naive key turns a metadata edit into a checkout outage; `row_hash` inputs (DEP-03), where all 3,858 golden records would look changed in one run and restate history-dependent marts; the `customers_masked` view (DEP-04), which stops resolving for every analyst and could leak `address_line1` and GPS as identifying data; dictionary row #14 and the DDL (DEP-05); three geo tiles splitting on legacy labels (DEP-06); and VR-002/DQC-03 (DEP-01), rewritten around the key. Effort: six small, eight medium, one large — 10–14 weeks for a four-person team. Full analysis: Appendix O.

**Catalog verdict.**

| Option | Cost fit (25) | Team fit (20) | Glossary & lineage UX (15) | Weighted /100 | Recommendation |
|---|---|---|---|---|---|
| OpenMetadata (self-hosted) | 5 | 4 | 4 | 89.0 | Adopt as the Phase 2 pilot at UGX 15–25M/yr |
| DataHub (self-hosted) | 5 | 3 | 3 | 82.0 | Hold as reserve option at the Phase 2 exit gate |

Metadata-as-code scores 79.0 at near-zero licence cost and already runs as Phase 1; Collibra is rejected at indicative UGX 110M–220M per year — 23%–45% of the UGX 480,000,000 envelope — and Apache Atlas on stack and skills, not price. Budget: Phase 1 costs no licence; Phase 2 costs UGX 15–25M/yr (3.1%–5.2% of the envelope), no new FTE, one SQL-capable owner. Appendix P.

**Metadata governance.** Domain stewards own their glossary entries and dictionary rows — Marketing owns customer, Merchandising product, Finance payments, the CRM Officer board KPIs — while the EDM Consultant curates technical lineage and no edit is anonymous. Every change lands as a pull request naming the affected artifacts and DQ rule IDs, reviewed quarterly across all 25 attributes plus event-driven on any schema change, with disputes ruled in five working days and escalated unresolved to the Data Governance Council. The Task A2 charter supplies role names and POL-001 tags so one taxonomy governs classification, masking and catalog search; superseded entries are deprecated, not deleted.

**Think deeper.** A catalog cannot own a definition; a person must. The real asset is the rule that no term is edited anonymously, that each has one named steward, and that a challenge to Monthly Active Customers lands on a rule ID and an owner in a pull request rather than in a meeting. Buying stewardship workflows before a steward model exists automates a vacancy, and ingesting today's inconsistent sources would automate the inconsistency. Phase 1 therefore earns ownership — one owner per term, definitions that survive audit — and Phase 2's entry gate (two stable pipelines plus PDPO filing) makes the tool spend conditional on proven adoption. Ownership is the precondition for the catalog, not its output.

## Task C2 — Security Risk Assessment, Access Controls & Privacy

**Threat model.** The asset-centred model applies STRIDE across eight assets and seven trust boundaries, weighting actors by SRG's realities. The realised class is theft: an unencrypted laptop holding 9,000 records (names, phones, purchase history) was stolen at Jinja, reported 11 days late and never notified — trust boundary TB-3 (portable media) has no control at all. Store connectivity is an environmental actor: 23 offline MySQL boxes sit offline hours daily, masking ransomware detection and driving duplicate captures. Insider risk is amplified by shared till logins, no leaver checklist and no export logging, so logs name nobody; accidental exposure runs through misdirected CSVs, phishing attachments and manual Excel edits. External classes — credential stuffing on 180,000 SavannaShop accounts, checkout skimming, SaaS breach without DPAs — rank below the realised endpoint exposure. Full diagram: Appendix Q.

**Top eight risks (5×5, Likelihood × Impact).**

| ID | Risk | L | I | Score | Mitigation |
|---|---|---|---|---|---|
| R1 | Stolen-device PII export (Jinja, realised): 9,000 records, unencrypted laptop | 5 | 5 | 25 | Mandatory FDE + export control (UGX 15M), 1-hour reporting rule, s.23 notification, retrospective PDPO engagement; ≤ 8 by month 6 |
| R2 | PDPO registration / notification failure (DPPA s.29, s.23) | 5 | 4 | 20 | PDPO registration month 1–3, DPO appointed (s.6), breach plan and register adopted |
| R9 | Shadow HR/supplier Excel leakage — payroll and national IDs | 4 | 5 | 20 | Controlled stores, POL-001 file labels, encrypted laptops, training, need-to-know on national ID |
| R13 | Systemic endpoint encryption gap — every laptop a potential Jinja | 5 | 4 | 20 | FDE and device compliance for export-capable devices; export blocked on non-compliant devices |
| R12 | Key-person dependency: zero data-engineering capacity, tribal knowledge | 4 | 4 | 16 | Cross-train both SQL-capable staff, named deputy per artifact, quarterly knowledge transfer |
| R3 | Ransomware on the 23 per-store MySQL boxes | 3 | 5 | 15 | Network segmentation, central patching, encrypted store backups, admin MFA (UGX 6M), quarterly threat-hunt (UGX 10M) |
| R6 | Unexplained 8.4% stock variance from manual edits and offline capture | 5 | 3 | 15 | Store cycle counts, adjustment approval workflow, variance dashboard |
| R11 | GDPR exposure via the EU partnership (Art.33/34, Art.44–49) | 3 | 5 | 15 | SCCs and transfer impact assessment before any EU flow, DPO appointed, 72-hour clock, DPIA signed |

The amber band — R4 insider misuse, R5 MoMo reconciliation, R7 residual duplicates, R8 vendor breach, R10 sync collisions (10–12) — is reduced by controls already built, each with a residual target. The tail is correlation, not individual score: R12 degrades every other mitigation at once and R9 turns one phishing click into identity-theft harm — hence no green cell, since SRG cannot yet demonstrate registration, notification readiness or full-disk encryption.

**Access control matrix (extract).**

| Role | Data object | Operation | Result |
|---|---|---|---|
| store_cashier | `financial_reports` (contains payroll) | SELECT | Denied — permission denied for table financial_reports (T01) |
| store_cashier | `customers` raw table | SELECT | Denied — permission denied for table customers (T02, T03) |
| store_cashier | `customers_masked` view | SELECT | Allowed as expected — 2 rows (T04) |
| store_manager | rows of another store (RLS) | SELECT | 0 rows visible, expected 0 (T05, T08) |
| data_analyst | `payroll_ugx` column | SELECT | Denied — permission denied for column payroll_ugx (T11) |
| compliance_officer | full raw customer record / `sales` | SELECT / INSERT | SELECT allowed for audit (T14); INSERT denied — auditors never mutate (T15) |

Access is proved, not asserted: `rbac_postgresql.sql` grants nothing by default, `rbac_test.sql` writes fifteen assertions into `srg.access_test_results`, and the committed reference capture shows 15 passed, 0 failed, every failed attempt denied by the database itself. This is documented-and-tested evidence, not a live-server claim: the expected output is committed in `rbac_test_expected_output.md` and reproduces verbatim on PostgreSQL 15/16, while no PostgreSQL server exists in the build environment, so `rbac_test.sql` was desk-checked statement by statement against documented privilege behaviour; the masking half ran on live data, 4/4 PASS. Appendix R.

**Encryption and masking requirements.**

| Layer | Control | Standard / reference | Owner |
|---|---|---|---|
| At rest | FDE on any device able to export Restricted data, screen lock ≤ 10 min, remote wipe; cloud objects and backups encrypted, restore tested quarterly | AES-256 via BitLocker/LUKS under device-compliance policy; documented restore-test evidence | Head of IT; IT Operations Lead (restore) |
| In transit | TLS 1.2+ everywhere; WireGuard/OpenVPN tunnels store→HQ, SFTP with key auth where tunnels cannot hold, never an unencrypted fallback | TLS 1.2+ (RFC 8446 baseline), certificate lifecycle with expiry alerts; OWASP ASVS | Head of IT; IT Operations Lead (store links) |
| Key management | Central KMS, annual rotation, split custody, no developer access to production keys, break-glass tested annually | Cloud or self-hosted HSM-less KMS; dual control on key export; key register | Head of IT administers; CFO holds recovery-key escrow |

**Masking demonstration.**

| Field | Raw (compliance_officer / cdm_admin only) | Served to analysts |
|---|---|---|
| `phone_e164` | full E.164 number | `+256-XXX-XX1234` |
| `email` | full address | `j***@domain` |
| `payment_ref` | full MoMo / Airtel reference | `MP******89` |

Raw columns are reachable only by column-level GRANT to `compliance_officer` or `cdm_admin`, always audited; `payment_ref` is tokenised in analytics copies, keeping the last four characters for reconciliation.

**DPIA verdict.** DPIA-2026-001 covers the loyalty app's EU-facing rollout — 180,000 members, purchase monitoring and fulfilment sharing with a European distributor — under GDPR Art.35, alongside DPPA 2019 s.3, s.7, s.10 and s.20. Overall residual risk is LOW, conditional on ten measures (M-01…M-10) spanning masking, full-disk encryption, consent rework, human review of tier decisions, rights handling, retention purge and breach response. Two conditions block EU go-live: Standard Contractual Clauses plus a transfer impact assessment under GDPR Art.44–49 — Uganda has no adequacy decision — and a Data Protection Officer under DPPA s.6. While either is unmet the transfer residual stays HIGH and EU members are excluded; the assessment is reviewed 12 months after sign-off or on material change. Appendix S.

**Breach notification timeline.**

| Clock | Obligation | Basis | Owner |
|---|---|---|---|
| ≤ 1 hour | Discovery timestamp recorded, then escalation to the Incident Lead with a P1 ticket — investigating before reporting is prohibited | Internal target, abolishing the 11-day delay | Any staff → Head of IT |
| ≤ 2 hours | Containment: wipe/disable, sessions revoked, credentials and keys rotated | DPPA 2019 s.20 | Technical Containment |
| ≤ 4 hours | Assessment: categories, record count, encryption at time of breach, risk | s.23(4) content readiness | DPO |
| Same business day | Notify the Authority — "immediately notify the Authority" of the unauthorised access and remedial action, by registered or electronic mail | DPPA 2019 s.23 | DPO |
| ≤ 48 hours after direction | Notify data subjects if the Authority so decides | DPPA s.23(2)–(3), content per s.23(4) | Communications |
| ≤ 72 hours from awareness | Notify the lead supervisory authority, with reasons for any delay; subjects without undue delay where risk is high | GDPR Art.33(1),(3); Art.34(1),(3) | DPO |
| Always, even if not notifying | Internal breach-register entry with facts, effects, remedial action | GDPR Art.33(5); DPPA s.3 | DPO |

**The Jinja failure, rewritten as procedure.** The 11-day delay and the missing notification are abolished by rule: hour 0 opens the clock, any staff member calls the on-call phone within one hour, reporting before investigating. Containment starts by hour 2, the hour-4 assessment rates 9,000 unencrypted records as high risk, and the PDPO is notified the same business day under s.23 with the remedial action taken; if EU loyalty members sat in the export, the Art.33 72-hour clock runs from awareness with Art.34 notice without undue delay. Data subjects are notified within 48 hours of PDPO direction (s.23(4)), the incident enters the breach register at hour 4 regardless of notifiability, remediation (FDE, export ban, retraining) is evidenced within seven days, with Council review at 30 days.

**Audit checklist.** The month-0 baseline runs 31 checks against DPPA 2019, GDPR and CCPA: 9 FAIL (29%), 19 PARTIAL (61%), 2 PASS (6%), 1 monitored N/A — failures are registration, DPO, endpoint encryption, s.23 notification, rights handling, SCCs, vendor DPAs and training. P1 in months 1–3 closes the audit-critical four — registration, DPO, full-disk encryption (UGX 15M) and breach plan plus register with the Jinja entry — then retrospective PDPO engagement on the unnotified breach. Appendix T.

**Think deeper.** Under a fixed envelope the omissions carry the argument. UGX 66,000,000 over 18 months — inside the UGX 480,000,000 envelope so catalog, cloud, licences and hires still fit — buys endpoint encryption (UGX 15M, closing R1, R13, R9), store tunnels, encrypted backup, MFA, a penetration test with PDPO readiness and an IR retainer. Not funded: enterprise DLP, since a four-person team has no SOC to triage alerts, while export approval, FDE-gated devices and masking-by-default block that vector; a 24/7 SOC, replaced by quarterly threat-hunts and the one-hour reporting clock; an on-prem HSM, since SRG holds no payment cryptography and cloud KMS with split custody costs about 1% as much; Public-tier field encryption, which protects nothing an attacker values; homegrown cryptography, prohibited outright; a zero-trust mesh until identity and FDE exist. Each omission keeps a named residual and its cheaper alternative — no risk dropped, none unsigned.

## Task C3 — BI Dashboard & Emerging Technology Evaluation

**Five strategic Board questions.**

| Question | Method | Output → decision |
|---|---|---|
| Q1 Which segments are churning, why, and what is the monthly revenue at risk? | RFM scoring plus cohort retention curves (SQL window functions) | Churn segment table, retention heatmap, revenue-at-risk waterfall → reactivation budget and new-customer floor |
| Q2 Which districts and categories are genuinely growing rather than merely shifting? | Contribution decomposition (new buyers, frequency, basket, price/mix) plus location quotient | Growth-contribution matrix and ranked double-down list → promo capex by district × category |
| Q3 What explains the 8.4% book-vs-physical variance, and which cells need new reorder rules? | Pareto analysis, variance waterfall by cause, deterministic safety-stock model | Variance attribution and reorder-policy change list → fund the task force, change reorder points |
| Q4 How much revenue sits in unreconciled mobile-money lines, and what fraud patterns appear? | Rule-based exception engine plus velocity analytics (VR-012 aging, duplicate refs) | Daily pending register and exception scorecard → 48-hour Finance sign-off SLA, provider escalation |
| Q5 Which expansion move is justified first: Kampala stores, Kenya, Rwanda or deeper e-commerce? | Catchment and location quotient, digital penetration, gravity-style demand index | Ranked expansion scorecard with gate conditions → capex sequence at gates G2–G4 |

Business questions and decision rationale: Appendix U.

**Analytics workflow.** Sources are the warehouse in `etl_demo.db` — `fact_sales` plus five dimensions, 10,000 lines for Jul–Dec 2024 — plus MoMo and Airtel statements, with an Odoo feed and footfall pilot to follow. Preparation runs once and is reused: duplicates 22.84% → 0.00% (5,000 → 3,858 golden records), phones to E.164, districts 127 → 42, UOM 15.33% → 100%, quarantine, idempotent loads, masking before analysis, SCD2 star schema. Methods stay inside SQL and pandas the team already has — RFM and cohorts, decomposition and location quotients, Pareto and variance waterfalls, exception rules, catchment indices — machine learning gated to later pilots. Outputs are the dashboard, growth and variance packs, daily pending register, expansion scorecard and monthly brief, each mapped to a named decision D1–D5 with one accountable owner.

**Dashboard.** Live at https://ccosecret.github.io/srg-enterprise-data-management/, the build carries month-range, city, category and payment-method filters; KPI cards, a multi-series monthly revenue line, a sorted category bar, a payment-mix donut, grouped new-versus-returning bars and a sortable store/city table; click-through drill-down from a table row to its categories; and one reset control — rendering 10,000 lines against the control total UGX 252,382,814.16 net, average basket UGX 25,238. Full specification and screenshots: Appendix V.

![Fig. C2 — Published executive dashboard: KPI cards, monthly revenue trend, category and payment mix (live: https://ccosecret.github.io/srg-enterprise-data-management/)](figures/dashboard_overview.png){width=97%}

Refresh is a build, not a query: `build_dashboard.py` reads only `etl_demo.db`, embeds every series as JSON into a self-contained HTML file, and refuses to publish unless the control total is UGX 252,382,814.16, so the previous page stays live rather than a half-built one; a git push redeploys via GitHub Pages with the run id in the header. Equally deliberate is logged decision D-13: the published HTML build substitutes for licensed BI tooling, carries the identical specification, and loads into Power BI without redesign.

**Executive insight brief.**

**F1 — growth is running on old fuel.** New known customers fell from 1,272 to 148 per month (−88%), the churn proxy stands at 69.4% (858 of 1,237 November actives bought nothing in December), and December revenue fell 13.6% month on month. *Actions:* Kampala/Jinja reactivation and referral campaign by M7; new-customer floor ≥ 600 per month and churn proxy ≤ 50% by M9; unattributed revenue below 3% by M9 via till phone-capture.

**F2 — cash is sitting in a reconciliation gap.** Mobile money carries 73.2% of revenue while 849 of 7,385 MoMo lines (11.5%) lack payment references — ≈ UGX 21.2M of six-month revenue (≈ UGX 3.54M/month) unconfirmed. *Actions:* stand up automated MoMo reconciliation — matching, not new plumbing, since the ETL already flags `PENDING_RECON`; enforce a 48-hour Finance sign-off SLA escalating above 50 pending/day (Finance/Reconciliation Officer, M5); zero lines pending beyond 24 hours by M6, pending share below 0.5% by M12.

**F3 — channel demand outpaces stock control.** ECOM01 delivers 20.3% of revenue from one node, about 5.9× an average physical store's 3.47%, against 8.4% unexplained book-vs-physical variance and returns of −UGX 10,224,221 (~3.9% of gross). *Actions:* variance task force with Odoo stock feeds, safety-stock rules on top-SKU and high-velocity cells, three-store footfall/POS pilot at M10–M12 (Merchandising Manager, M9); variance ≤ 5.0% by M9 and ≤ 2.0% by M12.

The Board is asked to approve the reconciliation programme and SLA, fund the task force and pilot, and adopt the segment targets. Appendix W.

**Emerging technology verdicts.**

| Technology | Verdict | Justification |
|---|---|---|
| Cloud EDM stack — Azure (managed PostgreSQL, Data Factory, Power BI), 4.25/5 | **ADOPT — phased** | Budget: cloud line capped at UGX 90,000,000 per 18 months, of which UGX 43,330,000 is planned. Skills: one accountable vendor, low-code BI for four staff with zero data engineers. Connectivity: no Ugandan region, so batch-first design to South Africa or Europe fits stores offline hours daily; migration waits for trigger T1–T6. |
| AI-driven trend — AI-powered data quality (ML anomaly detection) | **PILOT — from month 12** | Budget: subscription cost sits in the contingency line, no licence before gate G3. Skills: tuning and false-positive triage need capability still being built. Connectivity: neutral — batch profiling suits offline reality — but anomaly detection is only as good as the normal it learned, so VR-001…VR-012 and DQC-01…DQC-10 need six months of history first. |

DataOps is adopted lite at near-zero licence cost because the pipeline already runs self-tests, quarantine and run-state logging; Data mesh is rejected outright — six domains inside one four-person team would charter the silos the warehouse removed. Appendix X.

**Analytics maturity.**

| Dimension | Baseline level | Target M12 → M18 |
|---|---|---|
| Strategy & decision alignment | L0 — no KPI tree, reporting 11 days late | L3 → L3 |
| Data foundation & quality | L0 — defects unknown until profiled | L2+ → L3 |
| Platform & architecture | L1 — silent nightly failures, no run-state visibility | L2+ → L3 |
| Analytics & BI delivery | L0 — manual spreadsheet pack, no dashboard | L3 → L3 |
| Security, privacy & compliance | L0/L1 — the incident itself; no RBAC, masking or SOP | L2+ → L3 |
| People, skills & data culture | L0 — no stewards, no shared vocabulary | L2 → L2+ |

The composite baseline sits at about L0.3, and the realistic two-year path is:

- **By month 6 — composite L2, carried by artefacts already executed:** golden records cleansed (22.84% → 0.00%), 12 rules and 10 checks live, repaired pipeline self-test 3/3 PASS, 25-attribute dictionary, dashboard and brief adopted, RBAC and masking deployed with the notification SOP, stewards assigned, reporting lag 11 → ≤ 5 days.
- **By month 12 — L2.5 to L3, carried by organisational change:** three hires onboarded (Analytics/Data Engineer, BI Analyst, Data Steward), six staff certified, entry-point quality enforcement, Odoo stock feed closing the variance loop, reporting lag ≤ 3 days, PDPO audit passed, SCC pack for the distributor, churn and segment views used in trading meetings.
- **By month 18 and the year beyond — L3 sustained:** annual decision calendar, quality economics in UGX, cloud migration judged against triggers T1–T6, catalog and lineage automation, twice-yearly recertification; no dimension claims L4 inside that horizon — it would not survive audit.

**Think deeper.** The chart deleted was a 24-slice pie of store revenue shares, and it misled in three specific ways: with the top physical store at ≈4.1% and most stores in the 2–4% band, adjacent wedges differ by one or two degrees of arc, below the ranking threshold; pie reading depends on angle and area, the least accurate channel, so rounding noise read as movement and a stable estate looked volatile; and part-to-whole hides the decision variable — whether any store materially outperforms its peers, which none does at city indices of 0.94–1.04. The replacement, a sorted store/city table with printed values and click-through to category, reads length on a common baseline, makes flatness self-evident through sorting, and answers the follow-up question without a second page. 3-D bars, a dual-axis revenue-versus-customer chart and single-KPI gauges were rejected pre-build for the same reason: they spend ink distorting instead of encoding.

*Evidence: Appendices N–X; repo: module4_security/, module5_warehouse/, module6_dashboard/.*
