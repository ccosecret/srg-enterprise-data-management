# D2.3 — Reflective Essay

**Client:** Savanna Retail Group (SRG) | **Author:** Lead Enterprise Data Management Consultant
**Essay body: 900–1,000 words** (target 800–1,000 per task specification).

---

## Task D2 — Decision Log, Red Team & Reflective Essay

### The assumption that reframed the engagement

I arrived believing SRG's problem was technical: 23% duplicates, five identifiers per product, an 11-day reporting lag, a failing nightly job. The Jinja laptop corrected me — an unencrypted export of 9,000 customer records stolen, reported internally 11 days late, never notified. The problem was never that the data was dirty; it was that nobody owned it. Every artefact I built afterwards is the *evidence* of that ownership, not merely a fix.

### Uganda's digital transformation, and what it demands of design

SRG trades in a Uganda where mobile money leapfrogged card rails: 73.2% of revenue now flows through MTN MoMo and Airtel Money — financial inclusion infrastructure built by telecoms, while business intelligence infrastructure barely exists. That asymmetry shaped my choices. I automated reconciliation against provider statements before building churn models, because payments were where value leaked (849 pending references, ≈UGX 21.2M). The Data Protection and Privacy Act 2019 is young, the PDPO's enforcement capacity is still forming, and no mature precedent tells a Ugandan retailer what "adequate" looks like — so I designed to the statute's explicit asks (register, notify *immediately*, document) rather than to a comfortable norm. Infrastructure shaped design too: hours-daily connectivity loss and unreliable power are not edge cases here, so the pipeline treats offline capture as a *designed state* — quarantine rather than abort, idempotent replay, `customer_sk = 0` for walk-ins instead of fabricated identities. Offline-first is not a compromise in Kampala; it is fit for context. The Kenya and Rwanda expansion taught the corollary: data models travel, legal regimes do not — portability of schema, not of compliance.

### Data ethics, by the four choices they forced

**Consent in the loyalty programme.** With 180,000 members, the tempting design bundles points with marketing consent. I refused: consent must be recorded as a first-class, revocable attribute (DPPA s.7, GDPR Art.7), separable from contract performance for points (Art.6(1)(b)), with withdrawal honoured downstream in CRM, not just in a preferences table nobody reads. The credibility test is whether a member's "no" actually stops a campaign.

**Footfall sensor surveillance.** The pilot design counts bodies, not identities: aggregate entrance/zone counts, dwell-time distributions, no facial recognition, no individual tracking, signage at store entrances, DPIA signed before hardware is installed. The ethics line is that the *store* is measured, not the *shopper or the stock clerk*. A cheap camera upgrade to individual recognition will be available and will look technically interesting; the governance charter is what will keep requiring a fresh decision before it.

**Algorithmic bias in matching rules.** Automated merge rules are where ethics quietly becomes arithmetic. Name-similarity ≥90 looks neutral until you note that mononyms and common surnames inflate similarity, and shared family phones mean rural and lower-income households are structurally over-merged — two people collapsed into one, with loyalty value and purchase history reassigned. That is why name similarity alone never auto-merges (identifier match required), why 365 homonym pairs were *correctly rejected*, and why 110 pairs sit in a stewardship queue: a false merge destroys one person's record irreversibly, so the asymmetric cost justifies the human gate.

**AI fairness.** Deferring machine learning (D-25) was partly an ethics decision, not only a competence one. A churn-propensity model trained on data where 8.7% of revenue is unattributed and 11.5% of payments unreconciled would learn *measurement gaps as behaviour* — and those gaps are not random: walk-in, cash-preferring, outage-affected customers are systematically the least measured, so any future scoring would encode their poverty as disengagement. Before any pilot ships, I committed to parity checks across districts and gender, human review before account-affecting decisions (GDPR Art.22), and published model card with known blind spots.

### Career path, mapped to CDMP

My intended path is consultancy → **CDMP Associate within 12 months, then Professional**, with a longer aim of contributing to Uganda's PDPO-era capacity — the country needs practitioners who can explain Art.33 timelines to a store manager, not only lawyers who cite them. The mapping is direct: **Data Governance** (charter, RACI, POL-001/002/003), **Data Quality** (VR-001…012, DQC-01…10, before/after evidence), **Data Modeling & Architecture** (star schema, ER model, 1NF→3NF), **Data Integration** (repaired ETL, quarantine, idempotency), **Security & Privacy** (RLS RBAC, masking, DPIA, breach plan), **Master Data** (golden record, survivorship), **BI & Analytics** (five questions, dashboard, insight brief), and **Metadata** (lineage, catalog decision) — which is also where my self-identified gap sits, and the reason the catalog pilot is on my own development plan, not only SRG's.

### What I would carry forward

Two habits. First, honesty as a scorecard: 2.85% open quality flags reported instead of a fabricated 0%, "Stable (dedupe denominator shift)" instead of dressed-up improvement — credibility lives in the caveats. Second, sequencing: compliance milestones before analytics milestones, every time. Behind every unattributed line and pending payment reference is a customer who trusted the firm with a phone number — the same trust 9,000 of them gave, and lost, when a laptop left the Jinja store unencrypted. That is the sentence I will keep testing against every plan I write.
