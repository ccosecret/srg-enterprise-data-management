# D2.4 — Viva Preparation (15-minute individual defense)

**Client:** Savanna Retail Group (SRG) | **Author:** Lead Enterprise Data Management Consultant
**Purpose:** anticipatory preparation for the Week-15 viva. The viva tests authorship and depth of reasoning — artifacts I cannot explain earn no marks. Nothing here is a script; it is the evidence map behind the answers. Every figure quoted below appears in a committed file or in the written portfolio (appendix letters refer to the portfolio's Appendices A–AA).

---

## 1. The 15-minute running order

| Time | Segment | What must land |
|---|---|---|
| 0:00–0:45 | Opening — one sentence of context | Who I am (kutosi chris, 2024-08-32939), what SRG is, what was delivered: a diagnostic, a protected data platform, a Board-facing dashboard, an 18-month plan |
| 0:45–3:00 | Portfolio walk: Executive Summary → Parts A–D | The through-line: diagnosis → protection → insight → defence; control total **UGX 252,382,814.16** as proof the work executes, not just describes |
| 3:00–4:00 | One artifact I would defend hardest | The ETL self-test (3/3 PASS) plus the dashboard build gate — chosen because they re-run on demand in front of anyone |
| 4:00–12:00 | Examiner questions | Question bank (§4) and the three drills (§3); every answer ≤ 45 seconds, evidence pointer at the end of each |
| 12:00–14:00 | Attack questions | Red-team concessions rehearsed (§6) — concede precisely, with the gate that closes the finding |
| 14:00–15:00 | Closing | Limits first (§8): what I would check, what I would defer; then stop |

---

## 2. Authorship map — how each artifact was produced (30-second answers)

| If asked… | Answer spine |
|---|---|
| "Did you run this, or just write it?" | Modules 1–5 were executed in this environment: profiling/cleansing produced `module2_data_quality/output/` (5,000 → 3,858 golden records, 1,142 merges, 365 rejections); `srg_etl_pipeline.py` self-test 3/3 PASS with 10,000 rows and control total UGX 252,382,814.16; `data_masking_demo.py` 4/4 checks on live data; all SQL parse-validated with sqlfluff (0 errors); the dashboard builder re-read the warehouse and its output was verified against the same control total. |
| "Why are there no PostgreSQL screenshots?" | No server exists in this environment; presenting desk-checked SQL as execution would be a false claim. `rbac_postgresql.sql` is parse-validated (0 errors), `rbac_test.sql` is a 15-assertion suite with a committed expected-output capture (15 pass, 0 fail on documented privilege behaviour), and the masking half — which needed real data, not a server — ran live at 4/4. Assumption AR-10 discloses this; production deployment runs the suite against the target RDBMS. |
| "What is synthetic about this?" | The dataset is the course-provided SRG extract with known injected defects (`injection_report.json`). Provenance is disclosed on every artifact; baselines re-measure from live feeds by M6 (D-26). |
| "Who produced the diagrams?" | Every figure ships with its source file: mermaid sources and the renderer script in `figures/`, the fishbone generated from profiling metrics by `module2_data_quality/output/make_fishbone.py`, the lineage composite assembled from the pipeline's own stage list, and the dashboard figure a screenshot of the published page at the live GitHub Pages URL. Nothing in the portfolio is drawn that does not exist in a file. |
| "Defend the budget line by line." | Eight categories sum to exactly 480,000,000 (People 150,650,000; Foundation & integration 105,000,000; Security & compliance 72,000,000; Cloud 60,000,000; Governance & change 21,000,000; Capability & training 18,000,000; Licences 15,000,000; Contingency 38,350,000), phases 150,750,000 + 182,625,000 + 146,625,000 = 480,000,000, contingency = 480,000,000 − 441,650,000 = 38,350,000 (8.0%), run-rate 26,666,667/month. Appendix Y. |

---

## 3. The three drills the brief names

### 3.1 "Why?" — three decisions most likely to be probed

- **Why hub-and-spoke and not a centralised warehouse?** Connectivity: several stores drop for hours daily; a pure central pattern makes outages = data loss. A governed central core (staging → warehouse → golden records) with offline-tolerant spokes matches what was actually built (local spool → sync window → idempotent replay) and what a 4-person team can operate. Pure decentralised keeps the 23-siloes disease; federated needs domain maturity SRG lacks. Weights and scores are in `B1_architecture_decision.md`.
- **Why not auto-merge on name similarity alone?** False merges destroy a person's loyalty history and consent record irreversibly and asymmetrically; identifier match (phone/email) is required, 365 homonyms were rejected and 110 pairs queued — the measured trade-off is documented in `B3_mdm_design.md`.
- **Why defer machine learning?** Inputs unverifiable (8.7% unattributed, 11.5% unreconciled, 8.4% stock variance); a model would learn measurement error as behaviour, and the method ladder (descriptive → diagnostic → gated pilots) costs nothing to reverse (D-25, and the AI-fairness argument in D2.3).

### 3.2 "What if the budget is halved?"

Halving the envelope means **UGX 240,000,000 over 18 months** — a cut of exactly 240,000,000. The plan survives because the cuts follow the sacrifice ladder that is already written down (D1 think-deeper; RT-02/RT-12), in the order cloud → features → pilot date → hires:

| # | Cut, in execution order | UGX |
|---|---|---|
| 1 | Cloud beyond the Phase-1 pilot: Phase 3 line first (RT-02), then the M7+ Phase 2 step — Phase 1 is on-premises by design, so nothing slips | 55,000,000 |
| 2 | Footfall/POS pilot hardware (3 stores) deferred to post-programme — the expansion decision falls back on district/loyalty indices and is *explicitly* conditional | 25,000,000 |
| 3 | Odoo stock feed deferred — stock questions stay honestly gated (as they are today); the dashboard labels Q3 answers pending rather than answering from proxies | 25,000,000 |
| 4 | Identifier-unification tooling deferred — steward-assisted matching carries the queue | 12,000,000 |
| 5 | BI Analyst hire (M3) deferred — Board pack absorbed by existing SQL-capable staff | 46,000,000 |
| 6 | Data Steward hire deferred — stewards already sit with business roles under the charter (D1 ladder step 4) | 32,200,000 |
| 7 | OpenMetadata catalog pilot deferred — taxonomy ships as the committed documentation | 8,000,000 |
| 8 | Capability & training halved — local providers only, certification exams kept | 9,000,000 |
| 9 | Phase-3 governance workshops internalised (council and stewardship itself untouched) | 5,000,000 |
| 10 | Contingency reduced 38,350,000 → 15,550,000 (still ≈6.5% of the new envelope) | 22,800,000 |
| | **Total** | **240,000,000** |

People after the cuts = 72,450,000: the Data Engineer only (63,000,000 + 15% on-costs 9,450,000) — and if recruitment fails outright, internal promotion at a 1,000,000/month uplift costs 18,000,000 from contingency, exactly as D1 already specifies. **Never cut:** Security & compliance in full (72,000,000), the incident/breach SOP chain (repeating an 11-day, no-notification failure is a regulatory event), DQC-01…DQC-10 with the control-total gate, the council/RACI core, the PDPO audit date, and the dashboard's KPI cards and monthly brief (the Board's minimum viable product). The answer I must *not* give: "everything stays, we just work harder."

### 3.3 "Find the flaw in your own ETL design"

Honest flaws, in the order I would volunteer them:

1. **SCD2 fact-key tension.** `fact_sales.customer_sk`/`product_sk` point at the surrogate key version current at load time; late-arriving history corrections require re-keying facts or a type-inferred lookup. The DDL keeps history, but the load logic assumes slow-changing members — I would add an SCD2 reconciliation job before scale-out.
2. **The store dimension is modelled but not loaded in the demo.** `star_schema_ddl.sql` defines `dim_store`, yet the executed demo warehouse derives store attributes from `store_id` in the fact plus a static mapping (the dashboard does this explicitly). A grader may call this out; the fix is a `dim_store` load step, deliberately out of scope for the diagnosis-focused pipeline.
3. **SQLite as the demo warehouse.** Single-writer, no concurrency, advisory-lock only meaningful on the target RDBMS — acceptable for a reproducible demo, not a production architecture.
4. **Reconciliation is a line-count proxy.** The ≈UGX 21.2M exposure assumes pending lines carry average MoMo value (RT-05 already flags this); the M5 provider reconciliation re-bases on actual value.
5. **Batch-only freshness.** Nightly windows fit the budget and connectivity; e-commerce stock visibility needs the near-real-time path that the B4 design specifies but the current pipeline does not implement.
6. **No margin/inventory feeds.** Revenue ≠ profit; Q3 stock questions are honestly gated on the Odoo feed rather than answered from proxies.
7. **Detection without alarm routing.** The control-total gate stops a bad page from publishing, but nothing pages a human at 02:00 — precisely how the original four-day silence happened. The M1 incident SOP ships *with* the pipeline and the weekly Board pack reconciles to the control total, yet true 24/7 alerting is a Phase-2 capability, not something the delivered pipeline claims.

---

## 4. Part-by-part question bank

Format: **question → answer spine → evidence pointer**. Spines are 20–40 seconds spoken.

### Part A — diagnostic, governance, charter

- **"Why a council of existing roles instead of a new data function?"** — The failure is coordination, not headcount: 23 silos, five identifier types, 127 district labels, nobody accountable for a definition. The charter assigns ownership to roles SRG already pays for, and the envelope funds only three hires (People 150,650,000); new boxes would repaint the silo problem in org-chart colours. → *Appendix D; decision log Z.*
- **"You fixed the data once — why are the rules more important?"** — The cleanse is the demo; the rules are the product. 22.84% duplicates → 0.00% on golden records only holds if VR-001…VR-012 and DQC-01…DQC-10 run after every load; without them the same defects reappear within a quarter of live feeds. → *Appendix J.*
- **"Why report 2.85% rather than driving the number to zero?"** — D-08: force-merging the 110 open-queue records would fabricate completeness. The queue has a 30-day SLA and a named owner; an honest 2.85% total flag beats a clean lie, because fabricated completeness is the failure mode that hides the next defect. → *Appendix Z (D-08).*
- **"Why write policies before buying tooling?"** — Enforcement needs a definition to enforce: the Public/Confidential/Restricted classification drives the GRANT matrix and the retention clocks; the three policies are the contract that SQL, masking and TTLs then implement. Tooling without the contract automates the ambiguity. → *Appendix E.*

### Part B — data quality, MDM, ETL

- **"Why not an ELT tool / warehouse-first load?"** — Scale (10,000-line fact, 5,000-row customer) fits a transparent scripted pipeline where every transform is inspectable and self-tested (3/3 PASS, sqlfluff 0 errors); ELT adds a licence and a database dependency before Phase 1's on-premises decision is even funded. The weighted trade-off is written up, not asserted. → *Appendix L (ETL vs ELT decision).*
- **"Why conservative matching — 953 deterministic plus only 189 fuzzy?"** — False merges are irreversible; they corrupt a person's loyalty history and consent record. Splits are recoverable: 365 homonyms rejected outright and 110 pairs queued with an owner (D-08). Precision-first is the auditable default, and the measured trade-off sits in the MDM design. → *Appendices K, J.*
- **"Star schema and SCD2 for 10,000 rows — is that not over-engineering?"** — The model serves the questions, not the row count: point-in-time truth (D-12) is what separates a price change from organic growth, and history is the deliverable the Board's growth question needs. SCD2 on customer and product only; facts stay append. → *Appendix N; `star_schema_ddl.sql`.*
- **"The fishbone blames systemic causes — prove one."** — Of 11 systemic causes, the load-bearing one is that no stock-adjustment policy or accountable owner existed between store teams and finance — which is a governance gap, not a typing gap. The 8.4% variance decomposes against injection-report metrics, with point-of-entry causes kept separate so the fix list stays assignable. → *fishbone figure; Appendix J root-cause section.*

### Part C — security, compliance, BI

- **"Why no PostgreSQL run?"** — There is no server in this environment; presenting desk-checked SQL as execution would be a fabrication. Scripts are parse-validated (0 errors), RBAC ships as documented SQL plus a 15-assertion expected-output reference (15 pass, 0 fail on documented privilege behaviour), and the masking demo — which needed real data — ran live at 4/4. AR-10 discloses the constraint and the production runbook closes it. → *Appendices R, A.*
- **"How is a static HTML page 'BI'?"** — D-13: the published build carries the identical specification (filters, five-plus visual types, drill-down) with zero licence, zero server and no credentials in the browser, opens offline on UPS power, and loads into Power BI without redesign — Power BI Pro is budgeted (Licences 15,000,000 covers 3,330,000 for five users) for interactive Board use. The substitution is a logged decision, re-reviewed at G2. → *Appendix V; AR-09.*
- **"A breach lands on day one — what happens?"** — The SOP chain: contain → legal referral → breach register, with binary gates and a named owner. DPPA s.23 notification for the Uganda-side obligation is *immediately*; the GDPR 72-hour clock governs where EU partnership processing applies — two clocks, both written into the plan, both funded inside Security & compliance (72,000,000), with the external audit at M12 as the forcing function. → *Appendices S, F.*
- **"Why not bundle loyalty consent with points?"** — Consent is a first-class, revocable attribute (DPPA s.7, GDPR Art.7), separable from contract performance for points (Art.6(1)(b)); the credibility test is whether a member's "no" actually stops a campaign downstream in CRM, not just in a preferences table nobody reads. → *Appendices F, S.*

### Part D — roadmap, budget, defence

- **"Why 18 months?"** — The sequence has gates, not optimism: quick wins by M6 (reporting lag 11 → ≤5 days, duplicates < 1.0%) so value is not deferred; foundation and governance before BI; the PDPO audit at M12; cloud spend only behind triggers T1–T6, never a calendar date. The sacrifice ladder (cloud → features → pilot date → internal promotion) makes the load degradable rather than failed. → *Appendix Y; RT-12.*
- **"RT-02 says the plan is insolvent — isn't it?"** — Concede the ambiguity, never the arithmetic: if the four IT staff (4 × 2,500,000 × 18 = 180,000,000) sit inside the envelope, they exceed the 38,350,000 contingency by 141,650,000 — exact. The assumption is stated (AR-02), the Board rules at G1 (M3), and if the adverse reading lands the first cuts are pre-agreed: Data Steward deferred, footfall deferred, Phase 3 cloud line cut first. → *Appendices A, AA.*
- **"What happens when you leave?"** — The deliverable is institutional, not personal: charter and RACI (D), SOPs and the breach chain (S), DQC checks inside the pipeline, a stewardship queue with SLA and owner, a dashboard that redeploys on git push, training for all six staff (Capability line 18,000,000). Consultant-dependence would be a defect — the red team treats adoption as its own finding, and that is the honest one. → *Appendices D, Y, AA.*
- **"What would you do differently?"** — Name the incident: the 11-day, never-notified laptop theft. It is logged as the Critical red-team finding (RT-01), funded before analytics milestones (M1), and only reportable as "overturned until closed." The reflective essay carries the reasoning; the answer I owe is the gate, not the regret. → *Appendix AA; essay, Part D2.*

---

## 5. Numbers crib sheet — every figure I may quote, and where it lives

| Number | Value | Where |
|---|---|---|
| Control total | UGX 252,382,814.16 over 10,000 lines; average basket UGX 25,238 | ETL self-test output; dashboard header (L, V) |
| Dashboard | live at `https://ccosecret.github.io/srg-enterprise-data-management/` | V |
| MoMo share | 73.2% (MTN 48.2% + Airtel 25.1%) | U, W |
| Pending MoMo | 849 of 7,385 lines = 11.5% ≈ UGX 21.2M at average value — line-count proxy, value re-based at M5 (RT-05) | J, U |
| Golden records | 5,000 → 3,858; 1,142 merges (953 deterministic + 189 fuzzy); 365 rejected; 110 in stewardship queue | J, K |
| Duplicates | 22.84% → 0.00% on golden records | J |
| Product cleanse | composite validity 3.25% → 100%; UOM conformance 15.33% → 100%; category completeness 22% → 100%; district labels 127 → 42 | J |
| Growth signals | new customers 1,272 → 148 (−88%); churn proxy 69.4% (definition to be ratified by the council) | U, W |
| Returns | −UGX 10,224,221 (≈3.9% of revenue) | J |
| Stock variance | 8.4% unexplained → ≤ 2.0% by M12 → ≤ 1.5% by M18 | fishbone; J |
| Quick wins | reporting lag 11 → ≤ 5 days by M6; duplicate-person rate < 1.0% by M6 | Y |
| ETL / security evidence | self-test 3/3 PASS; sqlfluff 0 errors; masking 4/4 on live data; RBAC 15 assertions → 15 pass, 0 fail (expected-output reference) | L, R |
| Budget | UGX 480,000,000 exactly: People 150,650,000 · Foundation & integration 105,000,000 · Security & compliance 72,000,000 · Cloud 60,000,000 · Governance & change 21,000,000 · Capability & training 18,000,000 · Licences 15,000,000 · Contingency 38,350,000 | Y |
| Phases | 150,750,000 + 182,625,000 + 146,625,000 = 480,000,000; run-rate 26,666,667/month | Y |
| Payroll risk | 4 IT staff × 2,500,000 × 18 = 180,000,000 vs contingency 38,350,000 → exceeds by 141,650,000 (AR-02, RT-02) | A, AA |
| Hiring | Data Engineer 3,500,000/mo (M1), BI Analyst 2,500,000 (M3), Data Steward 2,000,000 (M5); internal-promotion fallback +1,000,000/mo = 18,000,000 | Y |
| Breach baseline | laptop with 9,000 records, 11 days, never notified; DPPA s.23 *immediately*, GDPR 72 hours | Q, F, AA |
| Loyalty | 180,000 members; consent separable — Art.6(1)(b) vs Art.7 | F, S |
| E-commerce | 20.3% of revenue, 5.9× the average store | U, W |
| Silos baseline | 23 silos, five identifier types, 127 district labels; 11-day close | B |
| Power BI line | 5 users × 37,000/month × 18 = 3,330,000 (inside Licences) | Y |

---

## 6. Attack questions from the red team — concede or rebut

| Finding | The attack in the room | My answer |
|---|---|---|
| RT-01 (Critical) — original breach | "You left an open legal matter in your scope and called it managed." | Concede. It is reported as *overturned until closed*: notification assessment funded and scheduled M1, SOP → register → tabletop chain with binary gates, external audit M12. What I control is the gate and the date; what I cannot do is perform a legal assessment alone — pretending otherwise would be the repetition of the original failure. |
| RT-02 (High) — budget | "Your own red team says the plan is insolvent." | Concede the ambiguity, defend the arithmetic: 180,000,000 vs 38,350,000 = exceeds by 141,650,000, exact. Assumption AR-02 stated; Board rules at G1; first cuts pre-agreed (steward, footfall, Phase-3 cloud). A consultant who "resolves" it by assertion has not read the envelope. |
| RT-05 (High) — pending framing | "You are calling offline-capture lag 'fraud exposure.'" | Rebut the framing, accept the correction: pending = *unreconciled, unconfirmed revenue — fraud surface*, never "fraud"; UGX 21.2M is a line-count proxy at average value; age bands separate 0–24h lag from >72h loss; M5 reconciliation re-bases on actual value. |
| RT-09 (Medium) — "GDPR-equivalent" | "Technical controls ≠ compliance; you could create false assurance." | Overturned by scope expansion: RoPA, breach register, lawful-basis/consent review and the SCC pack were added to Phase 2 (M11) explicitly ahead of the M12 audit, with privacy/incident training for all six staff and counsel funded in Security & compliance. |
| RT-12 (Medium) — optimism bias | "The same team that let a job fail for four unwatched days will run BAU and transform." | Concede the premise, point to the mechanism: the sacrifice ladder is written into D1 (cloud → features → pilot date → internal promotion) and the non-negotiables (incident SOP, DQC checks, PDPO audit date) are fixed above it. Plans degrade in a defined order or they fail silently — the four-day failure is exactly why the order exists. |
| RT-15 (Low) — self-consistency | "Decision log, roadmap and brief — do they actually agree?" | Walk it: 26 decisions (Z), every part cites its evidence, the build audit re-checks control totals and the 40-page limit mechanically, and where two documents differ the decision log is the system of record. Consistency is demonstrable in one minute, not asserted. |
| "Is the dashboard live?" | Show the URL from the crib sheet — it is in the running header of every page. | Rebut with the artifact: open the live page, the KPI cards, the filter interaction; `build_dashboard.py` refuses to publish unless the control total matches, so the live page and the committed warehouse cannot silently diverge. |

---

## 7. The professional compromise that still troubles me (think-deeper)

It is treating the original incident as a *documented risk with a remediation plan* rather than as an open legal matter resolved before other work began. The pragmatic argument is sound: notification depends on a legal assessment (was the data likely to result in risk? were any of the 9,000 records EU persons in scope of the partnership?), and that assessment cannot be performed by a data consultant alone — so the correct professional behaviour is to mandate, fund and schedule it (M1), escalate its status at every checkpoint, and refuse to let analytics milestones outrank it. What troubles me is that the pattern — *act where you are rewarded, escalate where you are not* — is exactly how the original failure happened. Someone inside SRG knew about the theft on day one and the organisation still waited 11 days internally and never notified; the failure was diffusion of responsibility, not ignorance. My mitigation is structural: the incident chain (SOP → legal referral → breach register → tabletop → external audit at M12) has binary gates, a named owner, and a Critical red-team finding (RT-01) reported as "overturned until closed." I judge the compromise right *only* as long as the notification question stays on the agenda with a date attached; the moment it becomes background noise, the compromise becomes a repetition of the failure this engagement was meant to correct.

---

## 8. Closing discipline for the room

- Answer the question asked, then stop; volunteer depth only when probed.
- Every number I quote must be traceable to a committed artifact — the crib sheet (§5) is that traceability, and if a figure is not on it, I do not quote it from memory.
- If I do not know: say so, name the artifact I would check (`docs/…` or an appendix letter), and give the decision I would defer — the same caveat-discipline the portfolio itself demonstrates.
- Limits precede confidence: no live-server claims, no compliance claims beyond the funded gates, no precision the artifacts cannot carry (line-count proxies labelled as proxies).
- Last sentence, if asked for one: *the portfolio is built to be re-run, not just re-read — the self-tests, the control total and the live dashboard are the argument.*
