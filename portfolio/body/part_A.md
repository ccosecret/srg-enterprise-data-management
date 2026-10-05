# Part A — Foundations & Governance

## Task A1 — EDM Diagnostic & Data Lifecycle Mapping

**To:** Board of Directors, Savanna Retail Group (SRG)

**From:** Enterprise Data Management Consultant

**Date:** Month 1 of the 18-month EDM transformation programme

**Subject:** Why our data problems are structural, not technical

The proposal before the Board is to hire two more database administrators. It is a plausible answer to a question not yet asked: what is broken at SRG — the engines, or the enterprise's command of its data?

**Traditional database management administers engines.** Uptime, backups, indexes, query tuning, replication, patching: it asks whether the database is healthy. **Enterprise data management governs data across systems** — policies, ownership, standards, quality loops, metadata, lifecycle and cross-system meaning. It asks whether "customer", "product" and "revenue" mean one thing everywhere, and who is accountable for that. Four pieces of SRG's own evidence decide the question.

| SRG symptom | What a DBA would fix | What actually causes it |
|---|---|---|
| The same product carries **5 identifiers** across POS, e-commerce and supplier files | Nothing — the identifiers sit in five healthy databases | No master-data standard, no product owner, no golden SKU |
| **23% duplicate customer records**; loyalty points posted to wrong members | Nothing — no query returns "too fast" | No shared customer identity key and no entry rules across 23 POS databases, e-commerce, loyalty and CRM |
| **11-day monthly reporting cycle** | Speed up each of 23 databases individually | Absent data architecture and absent KPI definitions — consolidation happens in Excel because no integrated layer exists |
| Board cannot answer segment growth or churn | Nothing | No conformed customer, product or revenue definitions to segment on |

**The decisive proof is the cleanse already executed.** Taking confirmed duplicates from **22.84% → 0.00%** (total duplicate-flag rate 25.06% → 2.85%) required cross-system matching rules — 953 deterministic phone matches plus 189 fuzzy Levenshtein matches — a survivorship policy, **365 homonym pairs deliberately rejected** by the email-conflict rule, **110 pairs held in stewardship review**, and standardisation of 6 phone formats into 1 (E.164) and 127 district labels into 42, with product UOM conformance 15.33% → 100%. Not one index, tuning pass or backup produced a single customer view. Those results came from matching rules and stewardship decisions SRG never had.

**Two more DBAs would deepen the problem.** They would keep the **23 silos** — per-store MySQL databases — healthier, faster and better backed up: better management of a *by-product*. Databases are containers; customer identity, product meaning and revenue definition are the assets. Hiring DBAs increases investment in the wrong asset class while the assets remain ownerless.

**One problem, three symptoms.** Each clean-up so far has treated data as disposable output: extract, fix, admire, discard. Three control loops were missing, and each now has a name. **No upstream enforcement:** the validation rules **VR-001..VR-012** (E.164 phone mask, district dropdown, SKU uniqueness, MoMo `payment_ref` within 24 hours or PENDING) existed at no capture point, so defects re-entered at source the day after cleansing. **No data ownership:** nobody was accountable for the customer, product or payment domain, so nobody could declare a field mandatory or rule that two records are the same person. **No monitoring:** checks **DQC-01..DQC-10** did not exist, so drift stayed invisible until the next manual audit — the ETL diagnosis shows the same pattern under root cause **RC-6**, alerts to an unmonitored mailbox and four days of silent failure. The 8.4% stock variance, the duplicate customers and the 11-day report are therefore not three problems. They are one — *nobody owns data quality from creation to deletion* — surfacing in three places. Cleansing without enforcement is a recurring cost, not an improvement.

**Data as by-product or as managed asset.** Treated as a by-product, data is exhaust from selling: created incidentally by whoever typed it, owned by nobody, kept until inconvenient, repaired only when a report embarrasses someone, and deleted — if ever — by hand. That framing explains all three chronic symptoms: the 8.4% variance stays "unexplained" because it has no owner; the 11-day report persists because nobody owns the *definition* of revenue; duplicates return because identity was never a rule, only a keystroke. Treated as a managed asset, each stage acquires an owner, an enforced gate and a measurable standard: rules at creation, continuous measurement, scheduled retention, retirement with evidence.

**Recommended Board actions.** **Adopt the Data Governance Charter in Month 2** — a Council, seven domain owners and stewards from existing job titles, zero headcount, a fortnightly 30-minute stand-up. **Approve POL-001 first, Month 2** — four-tier classification, default-deny grants, encrypted-export approval: the exact path the unencrypted laptop walked out of. **Bind quality at entry, Months 2–4** — VR-001..VR-012 on forms and in the ETL quarantine, DQC-01..DQC-10 as a daily scorecard. **One definition per KPI and one reporting layer by Month 6**, collapsing the 11-day cycle. **Fund it inside the UGX 480,000,000 envelope — an 18-month programme total on the stricter reading — phased**: quick wins in Months 1–6, PDPO-audit-ready by Month 12.

**The lifecycle map.** It traces customer data across **creation → storage → usage → sharing → archiving → deletion**, naming the system, the stakeholder and the failure point at every stage. Its sharpest findings sit at *sharing* (e-mailed supplier Excels, manual MoMo CSV downloads against a mobile-money share of **73.2%** of revenue, unencrypted laptop exports) and at *deletion* (no retention or erasure process at all, contrary to the DPPA 2019 (Cap.97) s.3 protection principles and s.28 erasure right). Every failure point is a *control* that does not exist, not a *tool* that is missing — which is why the same defects recur after each clean-up. The Jul–Dec 2024 baseline carries a control total of **UGX 252,382,814.16**: sound rows, still no Board answer without owners and definitions.

![Fig. A1 — Customer data lifecycle: systems, stakeholders, failure points and control gates](figures/A1_data_lifecycle_map_1.png){width=95%}

**DAMA-DMBOK gap mapping.** Against the eleven knowledge areas, SRG shows two emerging (Data Quality, Data Security), five partial and four effectively absent. The six most striking:

| Knowledge area | SRG state | What SRG lacks entirely |
|---|---|---|
| **Data Governance** | Absent | Policy issuance, governance council, RACI decision rights, funding of data work |
| **Data Architecture** | Absent | Enterprise architecture blueprint, integration/consolidation layer, architecture standards |
| **Documents & Content** | Absent | Content and records management, versioning and retention, DLP over e-mail and endpoints |
| **Reference & Master Data** | Partial (emerging) | Named master-data owners, approved survivorship rules, authoritative product → category hierarchy maintained in Odoo |
| **Data Security** | Partial (emerging) | Classification policy, endpoint and export controls, access recertification, access/audit-log review |
| **Data Quality** | Present (emerging) | Binding rules at the point of capture, a stewardship loop with SLAs, a monthly scorecard to the Council |

**The three most consequential gaps.** **No governance decision rights** — every other gap is a symptom of it, and it is the cheapest to close (Charter, Month 2). **No architecture or integration layer** — the direct cause of the 11-day cycle, five product identifiers and 23% duplicates. **No lifecycle end** — archiving and deletion, leaving SRG unable to demonstrate retention periods or honour erasure inside the 12-month audit window.

**Think deeper.** Why do the same symptoms keep returning after every clean-up? Because cleaning is an event applied to a stock, while quality is a property of a flow. SRG scrubs the stock and re-opens the taps: with no validation at capture, no owner and no monitoring, defects re-enter within days — the 22.84% duplicate rate was measured on data already cleaned in earlier exercises. Each exercise intervened in usage while defects were manufactured at creation and copied out at sharing. As a by-product, data is repaired when a report embarrasses someone; as a managed asset, every stage has an owner and an enforced gate. The test after any cleansing: what stops this recurring on Monday?

## Task A2 — Governance Framework & Compliance Register

**Vision.** SRG's data is owned by named people, defined once, validated at entry, protected by default and retired on schedule — so any Board question is answered from one trusted source within a day rather than eleven. Sized for a four-person IT team and a ~200-staff retailer, it takes effect on Board resolution in Month 2 with no new headcount.

**Six principles:**

| Principle | What it means at SRG |
|---|---|
| **Data is a managed asset, not a by-product** | Every domain has a named owner; data work is budgeted, measured and reported like inventory |
| **Enforce technically, not by poster** | If a rule can be a constraint, dropdown, mask or quarantine, it must be; documentation is the fallback, not the control |
| **One definition per KPI, one master per entity** | Revenue, active customer and stock on hand defined once and signed by the Council; Odoo is product master, golden record is customer master |
| **Quality is built at entry, never cleaned after** | VR-001..VR-012 bind at the form and the ETL gate; cleansing is remediation, not the operating model |
| **Privacy by default** | Masked until proven otherwise; default-deny access; classify before you grant; collect the minimum (DPPA s.3, GDPR Art.5, Art.25) |
| **Ownership before tooling** | No new platform, licence or hire before the receiving domain has a named owner and steward |

**Scope.** Seven domains are governed, each with one definition, its systems, a Domain Data Owner and a Data Steward drawn from **existing SRG job titles only**: Customer & Loyalty (180,000 members plus walk-ins), Product (one product = one SKU), Store & Organisation (ST01–ST23 and ECOM01), Supplier (14 Excel files into a controlled repository), Price & Promotion, Transaction & Payment (MoMo/Airtel references) and HR-restricted (highest sensitivity):

| Domain | Domain Data Owner | Data Steward |
|---|---|---|
| Customer & Loyalty | CRM/Marketing Officer | Store Operations Manager |
| Product | Merchandising Manager | Procurement Officer |
| Store & Organisation | Store Operations Manager | Head of IT Operations |
| Supplier | Procurement Officer | Finance/Reconciliation Officer |
| Price & Promotion | Merchandising Manager | Finance/Reconciliation Officer |
| Transaction & Payment | CFO | Finance/Reconciliation Officer |
| HR-restricted | HR & Payroll Officer | Compliance Officer (DPO) |

**Out of scope, deferred rather than rejected:** footfall-sensor content and biometric processing (pending a DPIA, Month 12); HR analytics beyond payroll accuracy; predictive segmentation or automated decisions (blocked until DPPA s.27 / GDPR Art.22 review); cloud migration and real-time streaming; Kenya and Rwanda localisation; document management beyond a supplier-contract pilot at Month 9.

**Operating structure.** The **Data Governance Council** is sponsored by the **Managing Director** and chaired by the **CFO**; members are the Head of IT, Merchandising Manager, CRM/Marketing Officer, Store Operations Manager, Finance/Reconciliation Officer and Compliance Officer. The Council owns the policy set, resolves domain disputes and approves exceptions. DPPA 2019 (Cap.97) **s.6** requires a designated data protection officer: the Board designates the **Compliance Officer as DPO** in Month 1 — an existing role, no hire — reporting independently to the Managing Director for breach matters and owning PDPO registration (s.29). **Domain Data Owners** are accountable for their domain's meaning, quality targets and access decisions; **Data Stewards** run checks, triage the stewardship queue (110 items today) and propose rule changes. Escalation runs stewards → owners after 14 days, owners → Council for disputes, Council → Board for P1 incidents and budget, DPO → Managing Director for breach declaration. Cadence stays light: a 30-minute stewards' stand-up fortnightly, a 60-minute Council monthly, a one-page Board report quarterly against the UGX 480,000,000 envelope, and an incident cell — Head of IT, DPO, domain owner — within 24 hours under DPPA s.23 and GDPR Art.33. Adoption is one signature page in Month 2 with POL-001..POL-003 attached.

![Fig. A2 — Governance operating structure: data council, stewardship, ownership — existing SRG roles only](figures/A2_governance_charter_1.png){width=72%}

**Decision rights (RACI).** Responsible, Accountable, Consulted and Informed roles are assigned across fourteen activities: customer record creation at POS, e-commerce and loyalty signup; master-data change approval for product, price and promotions; breach declaration; retention and deletion execution under POL-003; quarterly access recertification; data-quality rule exceptions; ETL failure triage and quarantine release; KPI definition sign-off; mobile-money reconciliation sign-off; supplier file ingestion; PDPO registration and audit response; loyalty points dispute resolution; dashboard publication approval; and data-subject erasure or access requests under DPPA s.24, s.28 and GDPR Art.15, Art.17. Accountability attaches to job titles, not committees: the CFO signs KPI definitions and reconciliation, the Compliance Officer (DPO) owns breach declaration, and the Council is informed of every exception. Full RACI matrix (14 activities): Appendix D.

**Three enforceable policies.** POL-001 and POL-002 take effect in Month 2 and POL-003 in Month 3, each an annex to the Charter binding to a control that fails closed:

| ID & policy | Owner (job title) | Measurable requirement | Enforcement mechanism |
|---|---|---|---|
| **POL-001 — Data Access & Classification** | Head of IT (day-to-day control owner); Compliance Officer / DPO owns the classification taxonomy | One of four tiers (Public, Confidential, Restricted, Prohibited) on 100% of attributes by Month 3; **0 standing ad-hoc grants**; recertification ≥95% each quarter; extracts above 100 Restricted records need Head of IT + DPO approval, encryption and 7-day expiry; endpoint ≥98% | Default-deny `GRANT`/`REVOKE` with column grants and row-level security; masking views as the only analytic surface; Restricted reads logged and reviewed monthly for 12 months; export workflow refuses unencrypted containers |
| **POL-002 — Data Quality** | Head of IT (control operation); Domain Data Owners (quality targets); CRM/Marketing Officer (customer domain) | VR-001..VR-012 bound client- and server-side — Month 2 at ETL, Month 4 for 100% of capture forms; DQC-01..DQC-10 daily at 06:00 (duplicates >1.0%, phone validity <99.0%, quarantine >0.5%); SLAs: critical <24 hours, high <3 days, medium <10; **0 unticketed production edits** | Blocked saves at the form; ETL quarantine with reason codes and no batch aborts; alerts to the on-call rotation and Council dashboard, **never an unmonitored mailbox** (RC-6); store scorecard on store-manager KPIs |
| **POL-003 — Retention & Deletion** | Compliance Officer / DPO (schedule and erasure workflow); Head of IT Operations (purge jobs) | Transactions and MoMo references **7 years**; loyalty **24 months** after inactivity; marketing consent 24 months; supplier records 6 years; backups **90 days**; monthly purge with deletion certificate; erasure acknowledged in **5 working days**, fulfilled in **30** | Scheduled purge jobs with append-only logs; cryptographic erasure at backup cycle end; automatic revocation at 24 months' inactivity; quarterly spot audit of 10 records per domain tabled with certificates |

**Compliance register.** Obligations are scored Risk = Likelihood × Impact (1–5 each), with P1 at 20–25 or a statutory deadline already running; ten rows are P1. Three frameworks are carried: the Uganda Data Protection and Privacy Act (DPPA) 2019 / Cap.97 as the binding regime, EU GDPR because a European distributor's due-diligence team is asking about SRG now, and CCPA/CPRA as comparative reference — §1798.140 thresholds below range today, §1798.100 and §1798.130's 45-day response unattainable, §1798.105/§1798.120/§1798.150/§1798.155 benchmarking deletion, opt-out and liability. The five most severe P1 gaps:

| Obligation | Current practice | Gap | Risk priority |
|---|---|---|---|
| DPPA 2019 (Cap.97) **s.29** — data protection register | No registration; processing 180,000 members, e-commerce and app data | Unregistered controller; audit-critical failure | 5 × 5 = 25 — **P1** |
| DPPA **s.23** incl. **s.23(4)** content — breach notification | Jinja incident: internal report 11 days late, **no notification ever made** | Missed immediate notification; incomplete incident record | 5 × 5 = 25 — **P1** |
| DPPA **s.20** and **s.21** — security measures (controller and processor) | No endpoint encryption, no export approval, unencrypted 9,000-record export | Direct cause of the Jinja incident | 5 × 5 = 25 — **P1** |
| GDPR **Art.33** (72 hours) and **Art.34** (high-risk subject notification) | No procedure of any kind | Hard deadline would be missed on day one of EU data flows | 5 × 5 = 25 — **P1** |
| DPPA **s.6** — data protection officer | No DPO; breach and consent decisions unowned | Accountability vacuum | 5 × 4 = 20 — **P1** |

A row closes only when the remediation artifact exists and has been demonstrated at the Council — CMP-05 closes on the export-approval workflow and RBAC assertion suite, not on a statement of intent. Any P1 open beyond 30 days goes to the Board with a named owner and recovery date; by Month 12, registration, DPO designation, the breach procedure and drill, the ROPA, the DPIA and POL-001..POL-003 records form the PDPO audit pack. Full register: Appendix F.

**The absence of governance already has a price tag.** **The Jinja incident, priced** (consultant estimates, to be validated): notification at UGX 6,000 per record-contact (SMS and letter) — 9,000 × 6,000 = **UGX 54,000,000**; an incident-response retainer at **UGX 15,000,000**; internal staff time at 6 people × 15 days × UGX 250,000 = **UGX 22,500,000**. Direct cost: **UGX 91,500,000 — 19% of the UGX 480,000,000 envelope** — spent replacing data, not building anything. Worse, the theft was reported internally **11 days late** and **never notified**, against DPPA 2019 (Cap.97) s.23, which requires the Authority to be notified *immediately*. Beyond that: compensation exposure under DPPA Part VII (s.33, verify with counsel), a PDPO investigation within 12 months, and the trust of 180,000 members.

**Two comparable industry cases.** The UK Information Commissioner fined **Marriott International GBP 18.4 million (October 2020)** after a breach in acquired Starwood systems lacking security **due diligence**; converted, **UGX 86 billion** — roughly **180 times** the UGX 480,000,000 envelope. The ICO fined **British Airways GBP 20 million (October 2020, GDPR Art.83)** after about **400,000 customers** were affected by a web-skimming attack — a single control gap producing roughly **UGX 94 billion**. Integrating with unassessed systems inherits their liability, and the distributor's due-diligence team is asking that question about SRG now — mid-market retailers are the affordable target.

**The monthly drag.** Reporting: 4 staff × 11 days × 12 months = 528 person-days × UGX 150,000 = **UGX 79,200,000 per year** to build one month's report. Duplicates: 23% of 180,000 ≈ 41,400 profiles × 4 campaigns × UGX 150 per SMS = **UGX 24,840,000 per year** wasted. Stock variance: UGX 504.8M revenue × ~70% cost of goods = UGX 353.3M × 8.4% = **UGX 29,700,000 per year** unexplained. Total drag ≈ **UGX 133,700,000 yearly — 28% of the data budget**, plus the one-off UGX 91.5M incident: **UGX 225M+, about 47% of the envelope, spent on the absence of governance.** Meanwhile 849 of 7,385 mobile-money lines (11.5%) sit as PENDING — cash finance cannot prove it received.

**The ask and the rebuttal.** No new money: Phase 1 (Months 1–6) commits roughly **UGX 96M — 20% of the existing UGX 480,000,000 envelope** — to classification and encryption, the export-approval workflow, entry validation and one reporting layer. By Month 6: reporting from 11 days to 2 or fewer, duplicates below 1%, PDPO registration filed (DPPA s.29), a signed evidence trail for the distributor. Without classification and access rules, every future export is another 9,000-record laptop waiting to happen; the cheapest line in this programme is POL-001, the most expensive is doing nothing.

**Think deeper.** POL-001 (Access & Classification) is the single policy that would have prevented the Jinja incident: the 9,000 records were Restricted, the export required dual approval and encryption, and the copy would never have left. POL-002 is the one violated daily — free-text phones and districts at the till, e-mailed supplier Excels, ad-hoc spreadsheets, unticketed production edits — because each is individually convenient. Enforcement becomes real when controls fail closed rather than persuade: default-deny grants, masking views as the only analytic surface, a workflow that refuses unencrypted containers, quarantine instead of silent passes, and a store scorecard attached to manager KPIs. Non-compliance must become visible to a manager with authority; every month skipped re-books the UGX 91.5M.

*Evidence: Appendices B–G; repo: docs/.*
