# Executive Summary

**The mandate.** Savanna Retail Group hired its first Enterprise Data Management Consultant to take the organization from data chaos to data-driven in 18 months, inside a fixed envelope of **UGX 480,000,000**, with visible results by month 6 and a PDPO audit expected within 12 months. This package is the board-ready consultancy deliverable: diagnosis, governance, technical build, protection, insight, roadmap, and an honest defense of every decision in it.

**The diagnosis.** SRG's symptoms are one disease. Twenty-three store POS databases plus seven other siloed systems produce **~23% duplicate customer records**, **five identifiers for the same product**, an **11-day monthly close**, and an **8.4% book-vs-physical stock variance** that nobody can attribute. The Jinja incident — an unencrypted laptop holding 9,000 customer records, reported 11 days late, with no breach notification — is the same failure at its most expensive: data treated as a by-product rather than a managed asset. The Board's working remedy ("hire two more DBAs") addresses storage, not ownership: nothing in the current estate assigns an owner, a standard, or a gate from data creation to deletion.

**What has been built and proven.** The technical work in this package was executed, not sketched:

| Deliverable | Evidence |
|---|---|
| Profiling & cleansing of 5,000 customers / 1,200 products | Duplicates **22.84% → 0.00%** (5,000 → 3,858 golden records); districts 127 → 42; UOM conformance 15.33% → 100%; composite validity 3.25% → 100% |
| Repaired nightly ETL into a star schema | Pipeline self-test **3/3 PASS**; control total **UGX 252,382,814.16** across 10,000 sales lines (Jul–Dec 2024) |
| Customer MDM design | Golden record with attribute-level survivorship; deterministic + weighted matching (auto-merge ≥85, review 65–84) |
| Security & privacy | RBAC matrix with GRANT/REVOKE scripts and failed-access test evidence; field masking demonstrated; DPIA for the EU-facing loyalty rollout; DPPA s.23 / GDPR Art.33 breach procedure |
| Metadata | 25-attribute classified data dictionary; annotated lineage for the Board's "monthly active customers" KPI; catalog tool evaluation |
| Interactive dashboard | Live at **https://ccosecret.github.io/srg-enterprise-data-management/** — filters, five chart types, drill-down, published from the executed warehouse |

**Three findings the Board should act on.** First, **e-commerce already delivers 20.3% of revenue from one node** — about 5.9× an average store's share — while the estate carries 8.4% unexplained stock variance, so every availability decision inherits a measurement error the firm can now decompose. Second, **new customers fell from 1,272 to 148 (−88%)** across the window with a churn proxy of **69.4%**: SRG has a retention problem wearing an acquisition costume, and the cleansed identity layer is what makes segment-level answers possible at all. Third, **mobile money is 73.2% of net revenue (MTN 48.2% + Airtel 25.1%)** yet **11.5% of MoMo lines (849 of 7,385 ≈ UGX 21.2M) sit unreconciled**: the payment rail the business depends on is the reconciliation rail it does not control.

**The plan and the money.** The 18-month roadmap runs three phases — Foundation (M1–M6), Scale (M7–M12), Intelligence (M13–M18) — and totals **exactly UGX 480,000,000** (People 150,650,000; Foundation 105,000,000; Security 72,000,000; Cloud 60,000,000; Governance 21,000,000; Training 18,000,000; Licences 15,000,000; Contingency 38,350,000 = 8.0%), planned to the stricter reading that the envelope covers the full programme rather than each year. Quick wins are visible by month 6: the dashboard is live now, duplicate-person rate falls below 1.0%, the monthly close compresses from 11 days to ≤5, and device encryption plus a breach procedure close the exposure the Jinja laptop opened. Four governance gates (G1–G4) release each phase; G1 must confirm three things — the payroll treatment of the existing four IT staff, the budget-reading interpretation, and tooling — before Phase 2 spend commits.

**How to read this package.** The body (40 pages maximum) carries the executive narrative, the decisions, and the evidence that matters most. Appendices A–AA hold the full registers, policies, matrices, DPIA, red-team dossier, and execution outputs; the GitHub repository holds every script, DDL, and test. The defense of individual choices is recorded in the 26-entry decision log, and the strategy's weakest points are attacked in the red-team section — because a package that only argues for itself is marketing, not consultancy.

*The single ask: approve the roadmap, confirm the three G1 items, and authorize the three hires by month 5 — the rest is already running.*
