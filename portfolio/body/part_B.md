# Part B — Technical Core

## Task B1 — Architecture Selection, ER Model & Normalization

**Weighted trade-off.** Four enterprise patterns were scored 1 (worst) to 5 (best) against six criteria. Weights are derived from SRG's constraint set, not from a generic architecture scorecard.

| Criterion | Weight | Centralized | Decentralized | Federated | Hub-and-spoke |
|---|---:|:-:|:-:|:-:|:-:|
| C1 Resilience under intermittent connectivity | 25% | 1 | 5 | 4 | **4** |
| C2 Fit for the four-person team's skills | 20% | 3 | 2 | 2 | **4** |
| C3 Budget fit (UGX 480,000,000/yr envelope) | 20% | 2 | 3 | 3 | **5** |
| C4 Time-to-value by month 6 | 15% | 2 | 3 | 2 | **5** |
| C5 Single version of truth | 10% | 5 | 1 | 3 | **4** |
| C6 Scalability to Kenya and Rwanda | 10% | 4 | 2 | 5 | **4** |
| **Weighted total** | **100%** | **2.45** | **3.00** | **3.10** | **4.35** |

**Why the weights sit where they do.** Connectivity takes 25% because several stores lose links for hours daily — the least negotiable fact and the one an always-on design breaks on first. Skills (20%) and budget (20%) follow the roster and the envelope: two of four IT staff write SQL, none have data-engineering experience, and UGX 480,000,000 (~USD 130,000) must carry licences, cloud and hires together. Month-6 time-to-value takes 15% because the Board expects visible quick wins; single version of truth takes only 10% because a delayed but governed core still restores one truth, whereas an outage cannot be negotiated away; expansion across the border (10%) is a 12–18 month concern. Full analysis: Appendix H.

**Recommendation: hub-and-spoke, 4.35 / 5.00** — one central governed core (immutable landing, staging, warehouse, golden records, DQ rules) fed by offline-first spokes that capture locally, buffer and sync in a 23:00–02:00 window. Three reasons decide it. First, it leads on every non-negotiable criterion simultaneously: connectivity, skills, budget and the month-6 deadline. Second, one pipeline in SQL and pandas with one run log is operable by the existing four-person team, with no unattended streaming platform in the critical path. Third, the outcome is provably deliverable inside two quarters: the repaired pipeline holds 10,000 lines to a control total of UGX 252,382,814.16 net and reports self-test 3/3 PASS.

**Rejected alternatives.** Centralized (2.45) turns every store outage into lost sales and spends the month-6 window on network remediation before a single dashboard ships. Decentralized (3.00) is the current disease, not a hypothesis: 23 MySQL silos, 22.84% duplicate customers, five identifiers per product, an 11-day monthly close and an 8.4% stock variance. Federated (3.10) needs domain owners, stewards and published data contracts that do not exist yet — correct as a year-3 posture, wrong as the year-1 backbone. An enterprise commercial integration or MDM suite falls outside the UGX 480,000,000 envelope and would still fail the connectivity test.

**From decision to delivered build.** The pattern shows up in what shipped. Offline capture is a designed state rather than an error: walk-in rows load with `customer_sk = 0` ("Unknown / Walk-in") and missing mobile-money references become `payment_ref = 'PENDING_RECON'` with status PENDING instead of aborting the run. Sync is asynchronous and windowed, never always-on, with a single-writer lock so replay cannot deadlock the nightly job. The core fails visibly rather than silently — quarantine table, run log and post-load control total replace the diagnosed stale-fallback anti-pattern — and golden records return to the spokes nightly, keyed by E.164 phone.

**The ER model.** Eight entities — Customer, Product, Store, Order, OrderLine, Payment, Supplier and LoyaltyAccount — form the consolidated operational core.

![Fig. B1 — Consolidated operational core: Crow's Foot ER model, 8 entities with keys and cardinalities](figures/B1_er_model_1.png){width=80%}

**Cardinalities and assumptions.** Every order resolves to exactly one selling location but at most one customer, so a walk-in sale never violates the model; an order must carry at least one line, lines are the only place a price is frozen, and split tender is represented as multiple payment rows rather than nullable columns. Three assumptions are embedded, each kept deliberately soft: a customer *may* belong to a household (a non-identifying grouping, not an identity link), one customer holds one phone number (`phone_e164` unique and reused as the MDM deterministic key), and one product is supplied by one supplier (mandatory M:1 foreign key). Modelling them as optional, versioned or soft is what lets the observed exception survive. Alignment to the warehouse is direct: OrderLine becomes `fact_sales`, Customer and Product become SCD2 dimensions, Store stays Type 1, and Payment splits into a method dimension plus reconciliation columns on the fact. ER and normalization evidence: Appendix I.

**Normalization, one pass.**

| Form | Violation | Fix | Rationale |
|---|---|---|---|
| 1NF | Repeating multi-value group — `items` and `unit_prices` cells hold `COC1001×2; KAK1002×1` | One atomic row per transaction line; composite PK `(tx_id, line_no)` | The row states one fact at one grain, identical to `fact_sales`, so no delimited string is ever parsed |
| 2NF | Partial dependencies — customer, store and payment attributes repeat on every line | Extract Customer, Store and Payment relations under their own keys | One name correction touches one row; a store rename stops being a mass update across 10,000+ sales rows |
| 3NF | Transitive dependencies — district → region, line → product → supplier — plus a stored `order_total` | Extract District, Product and Supplier masters; drop the derived total and compute Σ `line_net_ugx` | Region re-mapping and supplier phone changes no longer rewrite sales history; `unit_price_ugx` stays on the line as a time-of-sale snapshot, which is a fact, not a dependency |

**Denormalization memo.** Two labels — `category_label` and `store_city` — are carried onto a nightly-rebuilt reporting view over the star schema, turning a category-by-city card into a single scan for a four-person team. Both labels are always read from the SCD2 dimension version stamped at `event_ts`, never from `is_current`, so a re-categorisation cannot silently rewrite Q3 history. The view is an idempotent projection and is never edited in place: performance is bought with a decoration, not with a copy of the truth.

**Think deeper.** The household grouping breaks in Jinja, where three unrelated students rent rooms under the landlord's surname and share the house phone — merge them and one person's purchases and consent sit on another's record. Phone uniqueness breaks in Mbarara, where a family answers whichever handset rings and one `+2567…` legitimately belongs to four people. Single-supplier breaks during shortages, when the same sugar SKU arrives from Kakira and an importer with two costs in one week, falsifying margin history. Each assumption stays safe only while it remains optional or versioned; the moment it hardens into a UNIQUE or mandatory constraint, the observed exception returns as a defect.

## Task B2 — Data Quality Assessment & Cleansing (Hands-On)

**Profiling before and after.** The same functions ran on raw and cleansed states, so every delta below is measured rather than asserted. Composite measures are reported honestly: customer composite validity reaches 68.51%, not 100%, because 110 suspected duplicates stay open by design — declaring completion would mean silently merging people the evidence cannot separate.

| Dataset | Metric | Before | After | Change |
|---|---|---:|---:|---:|
| Customers | Confirmed duplicate rows, auto-matched | 22.84% | 0.00% | −22.84 pp |
| Customers | Total duplicate-person flag rate | 25.06% | 2.85% | −22.21 pp |
| Customers | Exact duplicate rows (all fields but ID) | 14.88% | 0.29% | −14.59 pp |
| Customers | Distinct raw district labels | 127 | 42 | −85 |
| Customers | Distinct phone format variants | 6 | 1 | −5 |
| Customers | Phone already in E.164 format | 22.76% | 91.96% | +69.20 pp |
| Customers | Gender stored in canonical domain {M, F} | 32.88% | 100.00% | +67.12 pp |
| Customers | Composite record validity, all four rules | 17.30% | 68.51% | +51.21 pp |
| Products | Unit of measure in {kg, pcs, liters} | 15.33% | 100.00% | +84.67 pp |
| Products | Composite product validity, all rules | 3.25% | 100.00% | +96.75 pp |

**Matching logic in one sentence.** Candidates are blocked on canonical district and must reach name similarity ≥90 before any score is computed; weights run +60 (or +70 for near-exact spelling) for name, +20 for district, +20 / +10 / 0 for phone and +15 / +5 / −10 for email, after deterministic E.164 phone equality executes first and unions 953 pairs — auto-merge requires score ≥85 *and* a positive identifier, 65–84 routes to stewardship review, below 65 stays separate, and conflicting non-empty emails hard-reject the pair, yielding 1,142 of 1,150 injected duplicates merged, 365 homonym pairs rejected, 110 rows held for review, and 5,000 raw rows resolving to 3,858 golden records.

**How the cleanse worked.** Standardisation always ran before matching, because scoring six phone formats would hide the clusters they belong to: an input mask plus E.164 collapse for phone, an alias dictionary with fuzzy matching at an 88 WRatio threshold for district, and label maps for gender, unit of measure, category and date. Every standardised value sits beside its original in a `*_raw` column — 5,000 raw rows became 3,858 golden records with a `merged_customer_ids` audit trail. What could not be automated was flagged, not fixed: 141 rows sharing a duplicate SKU, 69 SKUs mapped to more than one product name and margin anomalies where selling price sits below cost stay open under stewardship — a machine must not choose between two products or reprice a shelf.

**Validation rules.** Twelve rules span customers, products and payments, mixing technical conditions (phone mask, PK uniqueness, RFC-5322-lite email, ISO-8601 dates) with business vocabularies (official district list, unit of measure in {kg, pcs, liters}, six-class merchandise hierarchy, one SKU = one product name, MoMo reference within 24 hours). Every rule declares an action on failure — block the save, quarantine the row, flag for steward or escalate — plus a severity, so no violation depends on someone noticing a report. VR-007 is the linchpin: normalized phone unique across golden records *or* the record sits in the review queue, with loyalty point posting blocked until identity resolves. Full catalogue VR-001…VR-012: Appendix J.

**Root cause: the 8.4% stock variance.** Book stock minus physical stock averages 8.4% across every store, reported simply as "nobody knows why". Two properties frame the analysis: the variance is *systemic*, appearing at every store rather than one, which rules out a single-site explanation such as theft at one branch or one bad manager; and it is *unattributed*, because no store keeps an adjustment log, so the gap cannot yet be split between process loss, measurement error and capture error. Six cause categories — People, Method, Measurement, Systems, Data and Environment — were examined and every leaf cause classified by the type of fix it needs.

![Fig. B2 — Ishikawa (fishbone) analysis of the 8.4% stock variance: red = systemic, blue = point-of-entry](figures/B2_stock_variance_fishbone.png){width=92%}

**Verdict: 11 systemic causes against 7 point-of-entry causes.** That ratio is the finding — cleansing at entry would recover at most about 39% of the identified causes, while the remaining 61% are produced by process design and regenerate the variance however carefully staff type, which is why a one-off stock-take cannot fix 8.4%. The first three fixes are: pull stock-adjust rights out of the cashier role and route every correction through a propose-approve-log workflow; make transfer posting mandatory with scan-out/scan-in and a per-transfer variance check; and put controlled entry lists for unit of measure, category and SKU on every form. Targets follow the same logic — book-to-physical variance at or below 2.0% by month 12 and 1.5% at 18 months.

**What each class demands.** Point-of-entry causes stop at the form — a validation list, a blocked field, a permission removed — and they are the minority. The systemic eleven need process design instead: an adjustment approval workflow with a retained log, a quantity-change audit table recording who, when, old and new value and reason, ABC cycle counts replacing the annual scramble, a single stock ledger so that "book stock" stops being 23 private opinions, and sequence-numbered store-and-forward so queued sales become visible latency rather than phantom stock. Both five-whys branches converge there — one on no named stock owner below head office, the other on no master data and no validation at capture — which makes the variance a governance symptom, not a counting problem.

**Monitoring.** Daily checks convert the rule catalogue into owned alerts with thresholds and escalation paths.

| Metric | Threshold | Alert path | Owner |
|---|---|---|---|
| DQC-01 duplicate-person rate | > 1.0% daily; > 2.0% = P1 | CRM Officer → Data Governance Council after 3 days above 2% | CRM Officer |
| DQC-05 product UOM / category conformance | < 99.0% | Nightly check → block non-conforming item setup in Odoo | Merchandising Officer |
| DQC-06 SKU uniqueness violations | > 0 (zero tolerance, nightly) | Collision report → quarantine batch, re-issue SKU | Merchandising Officer → IT Manager |
| DQC-07 ETL quarantine rate | > 0.5% or > 100 rows per run | On-call alert → inspect quarantine, fix source, replay | IT Operations Lead |
| DQC-08 MoMo refs pending > 24h | > 0 daily; > 50 = P1 | Reconciliation queue → daily digest to CFO | Finance Reconciliation Officer |

DQC-01…DQC-10 run as one daily suite; phone validity below 99%, district resolution below 99.5%, core-field completeness, future-dated registrations and weekly margin anomalies complete the set. Each check ships its own remediation command, so an alert arrives with the first step named; queue age is reviewed weekly so growth triggers a form fix at the offending store. Full DQ evidence — profiles, rules, monitoring and the fishbone source: Appendix J.

**Think deeper.** Each defect class has a root behaviour behind it, not a typing error. Duplicates and five identifiers come from systems that each mint their own IDs with no enterprise key, so the fix is capture-side enforcement: controlled pickers, an input mask and a golden key at signup. Unit and category errors come from free-text fields that reward speed, stopped by vocabularies on the form. Systemic variance comes from unowned processes — no approval, no audit table, no count calendar — so the fix that ends it is named stock ownership, an approver on every adjustment, and ABC cycle counts posted the same day.

## Task B3 — Master Data Management Design

**Style selection.** Four MDM styles were tested against budget, connectivity, duplicate control and time-to-value.

| Style | Verdict | Why |
|---|---|---|
| Registry | Rejected | No survivorship: every system keeps its own copy, so the 23% duplicate load regenerates at the next signup |
| Consolidation | **Adopted** | SQL + Python on the existing estate, built for batch sync, and the hard part is already delivered: one golden table, enforced survivorship, stewardship queue |
| Coexistence | Rejected for now | Bidirectional propagation assumes links that are down for hours daily; last-writer-wins would overwrite verified goldens with clerk-typed variants |
| Centralized (transactional) | Rejected | Suites and the skills to run them sit outside the UGX 480,000,000 envelope, and a coordinator call per signup would block the till at ST19 in an outage |

**Golden-record survivorship.**

| Attribute | Winning source | Justification |
|---|---|---|
| full_name | Most complete registration record; tie → earliest registration date → lowest customer ID | The name a human recognises at the till; earliest is the name given when the relationship started |
| phone | Loyalty app E.164-verified number, else the most recent valid value | Phone is SRG's operational key for till lookup, MoMo linkage and loyalty SMS; OTP-verified beats merely typed |
| email | E-commerce checkout-validated address; conflicts flag review and are never silently picked | Only a checkout-proven address is guaranteed to reach the customer, and two different emails suggest two people |
| district | Latest POS-verified value checked against the official Uganda district list | Catchment analysis needs current residence; the official list keeps reporting stable across 127 raw labels |
| consent and contact preferences | CRM, by recency of consent capture | Consent must reflect the most recent evidenced opt-in or opt-out under DPPA s.7 and GDPR Art.7 |
| loyalty tier and points balance | Loyalty platform | Points are a financial liability owned by the loyalty ledger; a second stored balance would compete with the truth |

**Matching rules and thresholds.** Deterministic phone equality runs first on the standardised value, never on empty keys; probabilistic candidates are then blocked on canonical district and scored on name, district, phone and email. Auto-merge requires score ≥85 *and* a positive identifier match; 65–84 goes to stewardship review with a 48-hour steward SLA; below 65 stays as separate records; conflicting non-empty emails hard-reject the pair. Name similarity alone never merges.

**The trade-off is deliberately asymmetric: a false merge is strictly costlier than a missed match.** A missed match leaves a duplicate contact — annoying, visible and fixable later with full context. A false merge absorbs one customer's loyalty history and points into another's, corrupts consent records so one person's marketing opt-out can be inherited or overwritten by another, and causes a data-subject request to return a stranger's purchase history — breaches of DPPA s.7 and GDPR Art.7 accuracy duties that no audit trail fully repairs once the merge has propagated. That is why automation is capped at identifier-backed merges, why 365 homonym pairs were rejected rather than merged, and why the 110-row queue is a feature rather than a backlog: the design accepts a missed match as the price of avoiding irreversible privacy harm.

**Hierarchies.** Customer to household is a *soft* grouping — same normalized address or district, surname and shared phone with activity inside 90 days, stored as a confidence score 0–1 and never as an identity link. It may drive catchment counts, delivery batching and household-penetration metrics; it may never drive loyalty accrual, consent inheritance or single-customer-view roll-ups, because three Jinja students under a landlord's surname would otherwise exchange purchase histories. Product runs category to subcategory on the canonical six-class hierarchy — Beverages, Grains & Cereals, Snacks, Household, Personal Care, Stationery — collapsing 30 raw labels, with one golden SKU per product and every legacy code kept as an alias: the "same product, five identifiers" case resolves to one golden SKU under VR-008, which flags 141 duplicate-SKU rows and 69 SKU-to-multi-name rows for stewardship and never auto-merges them.

**Governance.** *Attribute approval* runs quarterly: a steward submits business need, source system, PII classification and retention class; the Data Governance Council approves and a schema-change ticket follows, with a 10-working-day fast track for regulatory items. *Dispute resolution* starts with the domain steward inside 48 hours on evidence, escalates to the Council within five working days, and falls to a tie-break that retires after 12 months. *Propagation* lands in the next scheduled sync within 24 hours, or immediately and out-of-band for consent withdrawal, wrongful merge or breach-related suppression. Every merge stores `merged_customer_ids` and a stewardship flag in a read-only change log, so any decision can be undone and re-adjudicated; queue ageing reports weekly under DQC-01.

![Fig. B3 — Golden-record integration flows back into POS, e-commerce, loyalty and CRM](figures/B3_mdm_design_1.png){width=88%}

Full MDM design: Appendix K.

**Think deeper.** The store manager creating quick local records during an outage is behaving rationally — blocking a sale to satisfy an MDM rule is a worse outcome than a duplicate. Technically, capture forms run offline on the same rules as the hub, issue namespaced temp IDs such as ST17-LOCAL-0042, and reconcile through the normal matchers on the next sync; walk-ins stay `customer_sk = 0`, never an invented identity, and points and marketing credit release only after a golden match. Politically, managers co-design the form, the KPI becomes "unreconciled local records over 48 hours" rather than a punishment for outages, and the steward answers within 48 hours, so cooperation survives the connectivity constraint.

## Task B4 — Data Integration & Real-Time Architecture (Hands-On)

**Star schema.**

![Fig. B4 — Star schema: fact_sales with five conformed dimensions; SCD2 on customer and product](figures/B4_etl_workflow_1.png){width=68%}

`fact_sales` sits at one row per sales line, keyed by `sale_sk = SHA1(transaction_id)`, with additive UGX measures and returns carried as negative quantity — 500 lines totalling −UGX 10,224,221 (~3.9% of gross). It is fed from five sources — 23 MySQL POS, SavannaShop PostgreSQL, the loyalty cloud database, SaaS CRM and Odoo ERP — all landing in staging first. Load order is a hard rule: `dim_date → dim_store → dim_payment_method → dim_product → dim_customer → fact_sales`, dimensions always before facts.

**Extraction methods.**

| Source | Method | Connectivity reality |
|---|---|---|
| 23× MySQL POS (ST01–ST23) | Local CSV spool → SFTP, window 23:00–02:00 | Offline > 3 hours defers to the next window; UPS tills keep capturing, spool replays idempotently |
| E-commerce PostgreSQL (SavannaShop) | CDC via logical replication / Debezium | HQ-side link is stable, so CDC decouples entirely from store connectivity |
| Loyalty cloud DB (180,000 members) | Nightly delta CSV via SFTP/API at 02:15 | API rate limits respected; a weekly full snapshot acts as backstop |
| CRM SaaS | Paged REST API with `updated_since` cursor at 02:30 | Throttled by contract; the cursor checkpoint resumes after a mid-run failure |
| Odoo ERP (HQ) | Scheduled export / RPC at 01:45 | HQ LAN only — no wide-area dependency |
| *Supporting:* MoMo CSVs (MTN, Airtel) | Daily download to a drop folder | Pending refs age under DQC-08 |

**Transformation and load sequence.** Type coercion comes first: `N/A`, empty strings and null literals become SQL NULL, never a fake zero, and anything uncoercible such as `UGX cheap` in a quantity is quarantined while the batch continues. Currency strings strip to numeric, phone collapses from six variants to one E.164 form, district resolves from 127 raw labels to 42 canonical, dates normalise to ISO-8601, unit of measure maps to {kg, pcs, liters} and category maps to the six-class hierarchy. Dedupe and enrichment then remap source customer IDs to golden IDs through `golden_map`, COALESCE unresolved identities to `customer_sk = 0`, and read product price and cost from the SCD2 version valid at the moment of sale, with MoMo references stamped MATCHED, PENDING, MISSING or NOT_REQUIRED. Dimensions load next under SCD2 — close the old version when the row hash changes, insert the new one, keep exactly one current row — and only then does the fact load run, delete-then-insert per key under a single-writer advisory lock so offline store-sync replay cannot deadlock it. Post-load checks must pass before anything reaches BI: zero orphan product and customer foreign keys, row counts, quarantine rate and the control total of UGX 252,382,814.16 net across 10,000 lines at an average basket of UGX 25,238. Consumption is BI views over masking views with five default-deny RBAC roles; the pipeline runs on SQLite/Python and RBAC SQL is documented with expected-output evidence.

**Diagnosis of the broken nightly job.** The 11 March run left `fact_sales` unchanged for four days, blocking the 11-day monthly consolidation, and alerted a mailbox last opened a week earlier.

| ID | Root cause | Evidence | Corrective action |
|---|---|---|---|
| RC-1 | No schema or type contract between source and staging | `invalid input syntax for type integer: "N/A"` at COPY line 12044 — 0 of 21,562 rows staged | Staged landing with per-row coercion; bad rows to `etl_quarantine`, batch continues |
| RC-2 | No surrogate key for unknown customers | 63 walk-in rows against a `NOT NULL` fact foreign key → transaction abort | Insert `customer_sk = 0` "Unknown / Walk-in" and COALESCE unknown keys |
| RC-3 | Offline store-sync replay collides with the nightly ETL | `DeadlockDetected`, process 18442 vs 18501 on `dim_store` for ST17 Gulu | Advisory lock plus a 23:00–01:45 sync window; dimension updates ordered by key |
| RC-4 | Silent "partial mode" fallback on the previous day's staging | Log line 02:00:13; wrong results propagated for four days | Fail fast — non-zero exit, `etl_run_log` status FAILED, no stale reuse |
| RC-5 | Dimensions loaded after facts | 412 fact rows referencing SKUs absent from `dim_product` | Load SCD2 dimensions first, then facts; replay quarantined orphans afterwards |
| RC-6 | Alerting to an unmonitored mailbox | Mailbox last opened seven days earlier; no run-state dashboard | Alert the on-call rotation by SMS/WhatsApp plus a 06:00 run-state check |

Prevention is structural: a schema contract per source, quarantine instead of abort, idempotent replay, offline capture modelled as a designed state, single-writer discipline, and alerts a human reads — with the quarantine rate monitored under DQC-07. ETL workflow, diagnosis and ELT analysis: Appendix L.

**ETL versus ELT for the cloud migration.**

| Criterion | Verdict | Why |
|---|---|---|
| Cost inside the UGX 480,000,000 envelope | ETL now | pandas and SQL are already owned; an always-on cloud warehouse adds an indicative UGX 60–90M/yr that displaces something else |
| Skills and ops burden for four staff | ETL now | One pipeline, one run log, one alert rotation; warehouse modelling and dbt-style habits must be trained *before* adoption, not during |
| Connectivity and auditability | ETL now | Spools are validated before transit, so an outage delays a file rather than corrupting a cloud load; immutable landing plus control totals satisfy the PDPO audit |
| Latency and scalability at 23-store plus expansion volume | ELT after the triggers | A window-bound single node breaks at tens of millions of rows; migrate once cloud budget is approved, two staff ship a model unassisted, two pipelines hold 60 green runs and sites stay ≥99% available for six months |

Staged, this is a hybrid: file and ETL staging now, transformation-in-warehouse later, with the VR and DQC catalogue unchanged and only its runtime replaced.

**Real-time, judged per use case.**

*Live stock visibility — near-real-time micro-batch, 30 to 60 seconds, not sub-second streaming.* SKU-level availability comes from POS and CDC sales decrements plus Odoo receipts, while footfall contributes only store-level demand pressure, because zones map to categories and sensors cannot see SKUs. The consumer publishes `store × SKU` quantities to Redis, feeding the SavannaShop availability badge with a confidence flag and a handheld restock queue ranked by on-hand and browse minutes. Malformed events drop at the edge and a sequence gap raises a freshness alert, so an outage becomes labelled latency rather than a silent zero. The economics decide the cadence: a stock-out at ST07 makes the storefront promise an item that does not exist and loses the sale in-aisle, so cost is per-minute, not per-millisecond — and a 60-second-stale quantity sits inside the shrink envelope anyway, where the 8.4% variance surfaces as visible drift.

*MoMo fraud patterns — a 5 to 15 minute micro-batch over a 24-hour sliding window, not real-time authorization.* Mobile money carries 73.2% of revenue, and the rules that matter are velocity and pattern checks: one reference reused across more than one store in 24 hours, refund loops per cashier per day, off-hours baskets beyond three standard deviations, walk-in high-value combinations, and references still unsettled past 48 hours under DQC-08. State sits in per-reference and per-cashier counters, so a replayed spool cannot manufacture a hit. True real-time authorization would have to sit inside the MTN and Airtel gateway callback — a path SRG does not control — while settlement risk is T+1, so a 15-minute window catches the same losses as a 15-second one at a fraction of the operational cost. Alerts queue to the Finance Reconciliation Officer with a daily digest to the CFO and carry replayable event IDs; revisit only if measured fraud losses exceed the annualized cost of gateway integration. Full real-time architecture: Appendix M.

**Think deeper.** Real-time earns its keep where latency converts directly to revenue or loss: stock availability, where every minute the storefront promises an empty shelf costs a sale in one channel while stock sits in another, and the MoMo fraud window, where patterns are only detectable before the money is gone. Both pay a person making a decision. It burns budget where nothing changes inside the window: continuous Odoo replication on human-speed master data, sub-second analytics for a Board that reads monthly, and "real-time everything" across stores that drop links for hours, which would turn an honestly labelled batch dashboard into a silently wrong one.

*Evidence: Appendices H–M; repo: module2_data_quality/, module3_etl/, module5_warehouse/.*
