# A2 — Memorandum to the Chief Financial Officer

**To:** Chief Financial Officer, Savanna Retail Group (SRG)
**From:** Enterprise Data Management Consultant
**Date:** Month 1 of the 18-month EDM programme
**Subject:** Governance is not bureaucracy — the absence of it already has a price tag
**Classification:** Confidential

---

## Task A2 — Governance Framework & Compliance Register (C2)

You called governance bureaucracy. Below is what its absence has already cost, priced in our own currency.

**1. The Jinja incident, priced.** *ASSUMPTIONS (consultant estimates, to be validated):* customer notification at UGX 6,000 per record-contact for an SMS + letter campaign; incident-response and forensics retainer UGX 15,000,000; internal staff time at 6 people × 15 days × UGX 250,000 fully loaded. Arithmetic: 9,000 × 6,000 = **UGX 54,000,000**; plus **UGX 15,000,000**; plus 6 × 15 × 250,000 = **UGX 22,500,000** → **UGX 91,500,000 direct**, equal to 19% of our UGX 480,000,000 annual data budget — spent replacing data, not building anything. Worse, the response we skipped: the theft was reported internally **11 days late** and **no breach notification was ever made**, against DPPA 2019 (Cap.97) s.23, which requires the Authority to be notified *immediately*. Then: compensation exposure under DPPA Part VII (s.33, compensation for failure to comply — **verify with counsel**), a PDPO investigation in the audit expected within 12 months, and the loss of trust of members of a 180,000-member programme.

**2. The European partnership, priced.** The UK Information Commissioner fined **Marriott International GBP 18.4 million (October 2020)** after a breach rooted in acquired Starwood systems that lacked adequate security **due diligence**. Illustrative conversion: 18.4M × ~1.27 USD/GBP × 3,700 UGX/USD ≈ **UGX 86 billion** — roughly 180 times our entire annual data budget. It is the closest possible analogue to what we are doing: integrating with systems we have not assessed inherits their liability. Our distributor's due-diligence team is asking that question about *us* right now.

**3. What one control gap costs at our scale.** The ICO fined **British Airways GBP 20 million (October 2020, GDPR Art.83)** after about **400,000 customers** were affected by a web-skimming attack — a single control gap producing roughly **UGX 94 billion**. The GDPR ceiling is EUR 20 million or **4% of global annual turnover**, whichever is higher. Mid-market retailers are not exempt; they are the affordable target.

**4. The monthly drag.** Reporting: 4 staff × 11 days × 12 months = 528 person-days × UGX 150,000 = **UGX 79,200,000 per year** to build one month's report. Duplicates: 23% of 180,000 ≈ 41,400 duplicate profiles × 4 campaigns × UGX 150 per SMS = **UGX 24,840,000 per year** of contact wasted, some of it to people who already opted out. Stock variance: annualised revenue UGX 504.8M × ~70% cost of goods = UGX 353.3M × 8.4% = **UGX 29,700,000 per year** unexplained. Total drag ≈ **UGX 133,700,000 yearly — 28% of the data budget**, plus the one-off UGX 91.5M incident: **UGX 225M+, about 47% of the annual envelope, spent on the absence of governance.** And the same gap hides money we have already collected: 849 of 7,385 mobile-money lines (11.5%) sit unexplained as PENDING — cash received that finance cannot yet prove it received.

**The ask.** No new money. Phase 1 (Months 1–6) commits roughly **UGX 96M — 20% of the existing UGX 480,000,000 envelope** — to classification and encryption tooling, the export-approval workflow, entry validation, and one consolidated reporting layer. Board-visible results by Month 6: reporting cycle cut from 11 days to 2 or fewer, duplicates held below 1%, PDPO registration filed (DPPA s.29), and a signed evidence trail for the distributor.

**The rebuttal.** Without classification and access rules, every future export is another 9,000-record laptop waiting to happen. The cheapest line on this page is POL-001; the most expensive is doing nothing.

### Think-deeper answer

POL-001 (Access & Classification) is the single policy that would have prevented Jinja: the 9,000 records were Restricted, the export required dual approval and encryption, and the copy would never have left. POL-002 is the one staff break daily — free-text entry, e-mailed supplier files, ad-hoc exports. Making both enforceable rather than decorative means controls that fail closed: default-deny grants, masking views, a workflow that refuses unencrypted extracts, ETL quarantine instead of silent passes, and a store quality scorecard attached to manager KPIs. Every month we skip them, we re-book the UGX 91.5M.
