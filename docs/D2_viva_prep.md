# D2.4 — Viva Preparation (15-minute individual defense)

**Client:** Savanna Retail Group (SRG) | **Author:** Lead Enterprise Data Management Consultant
**Purpose:** anticipatory preparation for the Week-15 viva. The viva tests authorship and depth of reasoning — artifacts I cannot explain earn no marks. Nothing here is a script; it is the evidence map behind the answers.

---

## Task D2 — Decision Log, Red Team & Reflective Essay

### 1. Authorship map — how each artifact was produced (30-second answers)

| If asked… | Answer spine |
|---|---|
| "Did you run this, or just write it?" | Modules 1–5 were executed in this environment: profiling/cleansing produced `module2_data_quality/output/` (5,000 → 3,858 golden records, 1,142 merges, 365 rejections); `srg_etl_pipeline.py` self-test 3/3 PASS with 10,000 rows and control total UGX 252,382,814.16; `data_masking_demo.py` 4/4 checks on live data; all SQL parse-validated with sqlfluff (0 errors); the dashboard builder re-read the warehouse and its output was verified against the same control total. |
| "Why are there no PostgreSQL screenshots?" | No server/container/sudo in the build environment. The RBAC evidence is a committed 15-test script with documented reference output (15/15 PASS), honestly labelled `rbac_test_expected_output.md` — a deployment-time verification target, not a fabricated run. |
| "What is synthetic about this?" | The dataset is the course-provided SRG extract with known injected defects (`injection_report.json`). Provenance is disclosed on every artifact; baselines re-measure from live feeds by M6 (D-26). |

### 2. "Why?" — three decisions most likely to be probed

- **Why hub-and-spoke and not a centralised warehouse?** Connectivity: several stores drop for hours daily; a pure central pattern makes outages = data loss. A governed central core (staging → warehouse → golden records) with offline-tolerant spokes matches what was actually built (local spool → sync window → idempotent replay) and what a 4-person team can operate. Pure decentralised keeps the 23-siloes disease; federated needs domain maturity SRG lacks. Weights and scores are in `B1_architecture_decision.md`.
- **Why not auto-merge on name similarity alone?** False merges destroy a person's loyalty history and consent record irreversibly and asymmetrically; identifier match (phone/email) is required, 365 homonyms were rejected and 110 pairs queued — the measured trade-off is documented in `B3_mdm_design.md`.
- **Why defer machine learning?** Inputs unverifiable (8.7% unattributed, 11.5% unreconciled, 8.4% stock variance); a model would learn measurement error as behaviour, and the method ladder (descriptive → diagnostic → gated pilots) costs nothing to reverse (D-25, and the AI-fairness argument in D2.3).

### 3. "What if the budget is halved?"

Halving the envelope (UGX 240,000,000 over 18 months) is survivable because the plan was built stricter than the brief: it already fits 480M over the *whole* programme. The pre-agreed cut ladder (from the red team, RT-02/RT-12 and the D1 think-deeper) executes in order: cloud line (60M) deferred — Phase 1 is on-premises by design; footfall pilot (25M) deferred — the M17 expansion decision falls back on district/loyalty indices as *conditional*; third hire deferred — stewardship already sits with business roles under the charter; contract support instead of the Data Engineer if recruitment fails. What is never cut: incident remediation and breach SOP (repeating an 11-day/no-notification failure is a regulatory event), the DQC checks, and the PDPO audit date. The answer I must *not* give: "everything stays, we just work harder."

### 4. "Find the flaw in your own ETL design"

Honest flaws, in the order I would volunteer them:

1. **SCD2 fact-key tension.** `fact_sales.customer_sk`/`product_sk` point at the surrogate key version current at load time; late-arriving history corrections require re-keying facts or a type-inferred lookup. The DDL keeps history, but the load logic assumes slow-changing members — I would add an SCD2 reconciliation job before scale-out.
2. **The store dimension is modelled but not loaded in the demo.** `star_schema_ddl.sql` defines `dim_store`, yet the executed demo warehouse derives store attributes from `store_id` in the fact plus a static mapping (the dashboard does this explicitly). A grader may call this out; the fix is a `dim_store` load step, deliberately out of scope for the diagnosis-focused pipeline.
3. **SQLite as the demo warehouse.** Single-writer, no concurrency, advisory-lock only meaningful on the target RDBMS — acceptable for a reproducible demo, not a production architecture.
4. **Reconciliation is a line-count proxy.** The ≈UGX 21.2M exposure assumes pending lines carry average MoMo value; the M5 provider reconciliation re-bases on actual value (RT-05 already flags this).
5. **Batch-only freshness.** Nightly windows fit the budget and connectivity; e-commerce stock visibility needs the near-real-time path that the B4 design specifies but the current pipeline does not implement.
6. **No margin/inventory feeds.** Revenue ≠ profit; Q3 stock questions are honestly gated on the Odoo feed (M8) rather than answered from proxies.

### 5. The professional compromise that still troubles me (think-deeper)

It is treating the original incident as a *documented risk with a remediation plan* rather than as an open legal matter resolved before other work began. The pragmatic argument is sound: notification depends on a legal assessment (was the data likely to result in risk? were any of the 9,000 records EU persons in scope of the partnership?), and that assessment cannot be performed by a data consultant alone — so the correct professional behaviour is to mandate, fund and schedule it (M1), escalate its status at every checkpoint, and refuse to let analytics milestones outrank it. What troubles me is that the pattern — *act where you are rewarded, escalate where you are not* — is exactly how the original failure happened. Someone inside SRG knew about the theft on day one and the organisation still waited 11 days internally and never notified; the failure was diffusion of responsibility, not ignorance. My mitigation is structural: the incident chain (SOP → legal referral → breach register → tabletop → external audit at M12) has binary gates, a named owner, and a Critical red-team finding (RT-01) reported as "overturned until closed." I judge the compromise right *only* as long as the notification question stays on the agenda with a date attached; the moment it becomes background noise, the compromise becomes a repetition of the failure this engagement was meant to correct.

### 6. Closing discipline for the room

- Answer the question asked, then stop; volunteer depth only when probed.
- Every number I quote must be traceable to a committed artifact (control total UGX 252,382,814.16, 10,000 rows, 3,858 golden records, 849 pending MoMo lines, 69.4% churn proxy).
- If I do not know: say so, name the artifact I would check, and give the decision I would defer — the same caveat-discipline the portfolio itself demonstrates.
