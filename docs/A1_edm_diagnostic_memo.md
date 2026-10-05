# A1 — Executive Briefing Memo to the Board

**To:** Board of Directors, Savanna Retail Group (SRG)
**From:** Enterprise Data Management Consultant
**Date:** Month 1 of the 18-month EDM transformation programme
**Subject:** Why our data problems are structural, not technical
**Classification:** Confidential — Board distribution only
**Annexes:** `A1_data_lifecycle_map.md`, `A2_governance_charter.md`, `A2_policies.md`, `A2_compliance_register.md`, `A2_cfo_memo.md`

---

## Task A1 — The EDM Diagnostic (C1)

### (a) Enterprise Data Management vs. traditional database management — tested against our own evidence

The proposition before the Board is to hire two more database administrators. It is a plausible answer to a question we have not yet asked: **what is broken at SRG — the engines, or the enterprise's command of its data?**

Traditional **database management** administers engines: uptime, backups, indexes, query tuning, replication, patching, storage growth. It asks *"is the database healthy?"* **Enterprise data management (EDM)** governs the data across systems: policies, ownership, standards, quality loops, metadata, lifecycle, and cross-system meaning. It asks *"does 'customer', 'product' and 'revenue' mean one thing everywhere, and is a named person accountable for that?"*

Four pieces of our own evidence decide the question:

| SRG symptom | What a DBA would do | What actually causes it |
|---|---|---|
| The same product carries **5 identifiers** across POS, e-commerce and supplier files | Nothing — the identifiers sit in five healthy databases | No master-data standard, no product owner, no golden SKU (rule VR-008 did not exist) |
| **~23% duplicate customer records**; loyalty points posted to wrong members | Nothing — no query returns "too fast" | No shared customer identity key and no entry rules across 23 POS databases, e-commerce, loyalty and CRM |
| **11-day monthly reporting cycle** | Speed up each of 23 databases individually | Absent data architecture and absent KPI definitions — consolidation happens in Excel because no integrated layer exists |
| Board cannot answer segment growth/churn | Nothing | No conformed customer, product or revenue definitions to segment *on* |

The decisive proof is the cleanse we have already executed. Taking confirmed duplicates from **22.84% → 0.00%** (total duplicate-flag rate 25.06% → 2.85%) required cross-system matching rules — 953 deterministic phone matches plus 189 fuzzy Levenshtein matches — a survivorship policy, **365 homonym pairs deliberately rejected** by the email-conflict rule, **110 pairs held in stewardship review**, and standardisation of 6 phone formats into 1 (E.164) and 127 district labels into 42, with product UOM conformance 15.33% → 100%. Not one index, tuning pass, backup or uptime improvement produced a single customer view. Those results came from *matching rules and stewardship decisions that had to be invented*, because SRG never had them.

Two more DBAs would, if anything, deepen the problem. They would keep the **23 per-store MySQL silos** healthier, faster and better backed up: better management of a *by-product*. Databases are containers; customer identity, product meaning and revenue definition are the assets. Hiring DBAs increases investment in the wrong asset class while the assets remain ownerless.

### (b) Why the same symptoms return after every "clean-up exercise"

Each clean-up so far has treated data as disposable output: extract, fix, admire, discard. Three control loops were missing, and each now has a name:

1. **No upstream enforcement.** The validation rules that now exist — **VR-001..VR-012** (E.164 phone mask, district dropdown, SKU uniqueness, controlled UOM vocabulary, MoMo `payment_ref` within 24h or PENDING) — existed at no capture point. A cashier could still type anything, so defects re-entered at source the day after cleansing.
2. **No data ownership.** Nobody was accountable for the customer, product or payment domain, so nobody was authorised to declare a field mandatory or to rule that two records are the same person. Quality cannot be owned by a committee of nobody.
3. **No monitoring.** The checks **DQC-01..DQC-10** (duplicate rate above 1%, phone validity below 99%, quarantine rate above 0.5%, MoMo references pending beyond 24h) did not exist, so drift stayed invisible until the next manual audit. The ETL diagnosis shows the identical pattern: root cause **RC-6**, alerts routed to an unmonitored mailbox, four days of silent failure and no owner of the nightly run.

The 8.4% stock variance, the duplicate customers and the 11-day report are therefore not three problems. They are one — *nobody owns data quality from creation to deletion* — surfacing in three places. Cleansing without enforcement is a recurring cost, not an improvement.

### (c) Where this is documented next

`A1_data_lifecycle_map.md` traces customer data across **creation → storage → usage → sharing → archiving → deletion**, naming the system, the stakeholder and the failure point at every stage. Its sharpest findings sit at *sharing* (e-mailed supplier Excels, manual MoMo CSV downloads, unencrypted laptop exports) and at *deletion* (no retention or erasure process at all, contrary to the DPPA 2019 (Cap.97) s.3 protection principles and s.28 erasure right). The same file maps SRG across all eleven **DAMA-DMBOK** knowledge areas: two emerging (Data Quality, Data Security), five partial, and four effectively absent — Data Governance, Data Architecture, Documents & Content, and Reference & Master Data ownership.

### Recommended Board actions

1. **Adopt the Data Governance Charter in Month 2** — a Council, seven domain owners and stewards drawn only from existing job titles; zero headcount, a fortnightly 30-minute stand-up.
2. **Approve POL-001 (Access & Classification) first, Month 2** — four-tier classification, default-deny grants, encrypted-export approval. This closes the exact path the unencrypted laptop walked out of, and addresses P1 gaps under DPPA s.20 and s.29.
3. **Bind quality at entry, Months 2–4** — VR-001..VR-012 on forms and inside the ETL quarantine; DQC-01..DQC-10 as a daily scorecard to the Council.
4. **One definition per KPI and one reporting layer by Month 6** — collapses the 11-day cycle and answers the Board's segment-growth and churn question as the visible quick win.
5. **Fund it inside the UGX 480,000,000 envelope, phased** — Months 1–6 quick wins; PDPO-audit-ready by Month 12 (register under DPPA s.29, appoint the officer required by s.6).

### Think-deeper answer

*Why do the same symptoms keep returning after every clean-up? What does that say about data as a by-product versus a managed asset?*

Because cleaning is an **event applied to a stock**, while quality is a **property of a flow**. SRG scrubs the stock and then re-opens the taps: with no VR rules at capture, no owner and no DQC monitoring, the same defects re-enter within days — our own 22.84% duplicate rate was measured on data already "cleaned" in earlier exercises.

Treating data as a by-product means it is exhaust from selling: created incidentally by whoever typed it, owned by nobody, kept until inconvenient, repaired only when a report embarrasses someone, and deleted — if ever — by hand. That framing explains all three chronic symptoms at once: the 8.4% variance has no owner so it stays "unexplained"; the 11-day report persists because no one owns the *definition* of revenue; duplicates return because identity was never a rule, only a keystroke.

Treating data as a managed asset inverts each of those: creation under enforced rules, a named domain owner per domain, continuous measurement, scheduled retention and erasure, and retirement with evidence. The practical test the Board should ask after any cleansing: *what stops this recurring on Monday?* Today the honest answer is "nothing". Task A2 exists to install that answer — ownership, entry rules, monitoring and a lifecycle — at a cost of hours and discipline, not headcount.
