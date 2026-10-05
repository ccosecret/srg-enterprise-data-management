# Task C2 Deliverable — Data Protection Impact Assessment: SavannaShop Loyalty App, EU-Facing Rollout

## Task C2 — Security & Privacy (C8)

**Client:** Savanna Retail Group (SRG) · **Prepared by:** Lead Enterprise Data Management Consultant
**Document:** DPIA-2026-001 · **Version:** 1.0 (draft for sign-off) · **Classification:** Confidential
**Trigger for a DPIA:** GDPR **Art.35** — large-scale processing of member data (180,000 loyalty members scaling with the EU rollout), systematic monitoring of purchase behaviour (personalisation/segmentation), and **data flows to a European distributor**; the "likely high risk" threshold is met, and Uganda's DPPA 2019 (Cap. 97) requires privacy-by-design diligence under s.3 principles, s.7 consent, s.10 protection of privacy and s.20 security measures (Cap. 97 consolidated numbering — verify against official gazette before external use).

> **Template note (honesty statement):** the client's DPIA template and its appendices were **not supplied in this environment**. This assessment therefore follows the **standard EDPB / Art.35 DPIA structure** (WP248-rev.01 methodology: systematic description → necessity/proportionality → risk assessment → measures → sign-off) and is **cross-mapped field-by-field to a generic DPIA template** in §8 below, so it can be pasted into the corporate template unchanged once supplied.

**Related deliverables:** `docs/C2_threat_model_risk_register.md` (R4, R8, R11), `docs/C2_encryption_masking_spec.md` (controls), `docs/C2_breach_response_plan.md` (Art.33/34 clock), `docs/C2_compliance_audit_checklist.md` (CHK-21/CHK-24), `module4_security/*`, `module5_warehouse/data_dictionary.md`.

---

### 1. Scope & purpose

| Field | Content |
|---|---|
| **Processing activity** | Loyalty programme operation for the SavannaShop loyalty app, extended to EU residents/travellers, including personalised offers and **sharing of fulfilment data with SRG's European distributor partner** |
| **Purpose(s)** | (P1) administer points & rewards (contract); (P2) personalised offers & segment marketing (consent); (P3) order fulfilment & delivery (contract); (P4) fraud prevention, reconciliation and statutory record-keeping (legitimate interests / legal obligation) |
| **Data subjects** | Loyalty members (adults), prospective members (app signup), **EU residents and travellers** in scope of GDPR via Art.4(1) "in the context of an establishment in the Union" and offering services to them; children excluded by age gate (§5, R6) |
| **Scale** | 180,000 members today, growing with the EU rollout; ~5,000-record warehouse sample used in engineering builds; Jul–Dec 2024 baseline: 3,362 known active customers, 2,447 repeat buyers (72.8%) driving 90.1% of known-customer transactions |
| **Geography of processing** | Store & cloud processing in **Uganda**; fulfilment disclosure to a **European distributor**; planned Kenya/Rwanda expansion (out of scope of this version, re-assess on entry) |
| **Why a DPIA now** | EU partner requires GDPR-equivalent practice; PDPO audit expected within 12 months; the Jinja incident (`docs/C2_threat_model_risk_register.md` R1) proves bulk-customer-data loss is not hypothetical |
| **DPIA owner / decision maker** | EDM Consultant (author) → **Data Protection Officer** (per DPPA s.6, pending appointment — CHK-02) → Data Governance Council → Executive sponsor |
| **Review** | **12 months**, or immediately on material change (new data category, new third country, new profiling logic, or a breach affecting this processing) |

---

### 2. Systematic description of the processing (Art.35(7)(a))

| Stage | What happens | Systems / artifacts | Data & volume | Frequency | Controls in place |
|---|---|---|---|---|---|
| **Collect** | Signup and in-app profile; POS/checkout linkage; consent capture for marketing; transaction capture at 23 stores + SavannaShop | Loyalty app, POS forms, ECOM01 checkout | Name, phone (E.164), email, consent flags, transaction lines; **no national ID/passport; no precise GPS unless opt-in**; 180k members | Continuous / per transaction | VR-001 (phone), VR-005 (dates), VR-006 (name), consent checkbox separate from T&Cs |
| **Store** | Cloud database + local POS stores in Uganda; warehouse copies | PostgreSQL warehouse, 23× MySQL POS, cloud DB | Full member profile + purchase history | Continuous | Encryption at rest & in transit (`docs/C2_encryption_masking_spec.md` §a), backups, `etl_quarantine` integrity path |
| **Match / MDM** | Deterministic phone/email matching → golden record; homonyms rejected | `module2_data_quality/dq_assessment_cleansing.py` | 5,000 → 3,858 golden records; 1,142/1,150 dupes merged; **365 homonym pairs rejected**; 110 in stewardship review | Nightly / on change | **Name similarity never auto-merges**; VR-007 blocks point posting until resolved; merge audit trail |
| **Personalise** | Segmentation (e.g., Personal Care 50.9M / Grains & Cereals 44.7M category buyers), tiering, next-best-offer | CRM + BI (masked views) | Derived segments, RFM scores, category affinities | Weekly / on transaction | Analysts see masked PII only (`+256-XXX-XX1234`, `J*** D**`, `j***@domain`); RLS store scoping |
| **Share** | Order-fulfilment data to the European distributor (name, delivery address, phone, item lines) | Partner API / SFTP channel | Fulfilment records; count scales with EU orders | Per order | **Pending: SCCs + transfer impact assessment (Art.44–49)** — blocking gate for go-live (R11) |
| **Retain** | Active membership + 24 months from last activity; transaction records per POL-003 & statutory accounting retention | Warehouse + operational DBs | Full history | Continuous | Retention policy written; **purge job pending** (CHK-28); DQC monitoring on stale-flag counts |
| **Delete / rectify** | Rights requests (access, rectification, erasure, objection, portability) | Manual procedure (to be formalised) | Per request | On demand | DPPA s.24/s.25/s.28; GDPR Art.15/16/17/20/21 — procedure is a P2 remediation (CHK-13/14) |

**Metadata recorded:** lawful basis per purpose, retention clock, processing location, third-country flag, classification tags (POL-001), DPIA reference `DPIA-2026-001` (feeds the Art.30 record — §7).

---

### 3. Necessity & proportionality (Art.35(7)(b))

| Requirement | Assessment |
|---|---|
| **Lawful basis — GDPR** | **Art.6(1)(a) consent** for marketing & personalisation (explicit, granular, withdrawable); **Art.6(1)(b) contract** for points/rewards and order fulfilment; **Art.6(1)(c)** where statutory retention applies. Consent captured separately per purpose (Art.7: unbundled, as easy to withdraw as to give, recorded with timestamp + version) |
| **Lawful basis — DPPA** | **s.7 consent** to collect/process personal data; **s.11** notice at collection (what, why, retention, sharing with the European distributor, rights incl. s.24 access and s.25 objection) |
| **Transparency (Art.13/14)** | Layered notice at signup + in-app Privacy tab; EU-specific notice naming the distributor, SCCs, and the Art.15–21 rights; versioned and dated |
| **Data minimisation** | **No national ID or passport** in the loyalty record; **no precise GPS** from the app unless separately opt-in (delivery accuracy uses coarse district/city, structured under `CHG-ADDR-001`); no special personal data (DPPA s.9 prohibition honoured) |
| **Purpose limitation** | Points, personalisation, fulfilment, anti-fraud — no secondary sale of data; sharing limited to fulfilment fields (name, address, phone, items); **data is never sold** (keeps CCPA §1798.120 out of scope as a matter of policy, see `docs/C2_compliance_audit_checklist.md` CHK-31) |
| **Storage limitation** | 24 months inactivity → profile flagged, then erased/anonymised per POL-003; consent records retained only as long as needed to prove consent |
| **Accuracy** | Golden-record survivorship + DQC-01/02/03 keep identity accurate; self-service profile edit + rectification path (Art.16 / DPPA s.28) |
| **Proportionality verdict** | **Proportionate**: the programme processes ordinary contact + purchase data, minimises identifiers, and gates the highest-risk step (third-country sharing) behind SCCs. Residual risks are listed in §5 with measures. |

---

### 4. Consultation (Art.35(9) — views of data subjects sought where appropriate)

| Party | Role | Status |
|---|---|---|
| **Data Protection Officer** | Independent advice, formal consultation per **DPPA s.6** | **Pending appointment (P1, CHK-02)** — interim: EDM Consultant performs the DPO function and records the gap honestly |
| **Data Governance Council** | Governance decision body (Task A2 charter) | Scheduled at sign-off (§6) |
| **European distributor's DPO** | Joint-flow clarity: fields, purposes, SCCs, breach SLA | Requested; response needed before go-live (R11) |
| **Representative member panel (optional)** | Data-subject views on personalisation & footfall sensitivity (Art.35(9)) | Recommended: 6–8 members, 1 workshop, month 4 — cheap insight into "chilling effect" concerns |
| **Executive sponsor** | Resourcing decisions | Sign-off block (§6) |

---

### 5. Risks to rights & freedoms (Art.35(7)(c)) — with measures (Art.35(7)(d))

| # | Risk to data subjects | Likelihood | Severity | Measures (preventive / detective) | Residual |
|---|---|---|---|---|---|
| **R1** | **Excessive collection creep** — app adds fields over time beyond what members expect | Medium | Medium | Minimisation baseline in §3 (no national ID, opt-in GPS); new field = DPIA change-review trigger; POL-001 classification on every new attribute; dictionary PR required (`docs/C1_catalog_tools.md` governance) | **Low** |
| **R2** | **Wrongful identity merge** linking two different people's purchase histories (MDM false merge) → wrong personalised content, wrong disclosures, corrupted rights records | Medium | **High** | **Auto-merge only on positive identifier match (equal phone/email); name similarity NEVER auto-merges**; 365 homonym pairs already rejected; 110 rows in stewardship queue; VR-007 blocks point posting until resolved; full merge audit trail + unmerge path; DQC-01 threshold > 1% → escalate | **Low** |
| **R3** | **Chilling effect from behavioural monitoring** — members feel watched in stores | Medium | Medium | **No facial recognition anywhere** (explicit prohibition); footfall sensors produce **aggregate counts only**, never individual tracks; in-store signage at entrances; member panel consultation (§4) | **Low** |
| **R4** | **Automated tier/benefit decisions** — tier downgrade or offer exclusion made without human involvement | Medium | Medium | No fully automated adverse decisions: **GDPR Art.22 / DPPA s.27 human-review path** — any adverse tier/benefit outcome can be requested for human re-review; logic disclosed in plain language; only positive personalisation is automated | **Low** |
| **R5** | **Unlawful third-country transfer** — fulfilment data leaves Uganda/EEA without a valid transfer mechanism | Medium | **High** | **SCCs + transfer impact assessment** before any EU flow (GDPR Art.44–49); Uganda has **no adequacy decision** → SCCs are the mechanism; encryption in transit & at rest (B2/B3 lines); Art.30 record updated; **go-live gate** | **Low once gate enforced; HIGH until signed** |
| **R6** | **Breach of the loyalty database** — mass disclosure of names/phones/purchase history (the Jinja pattern at 180k scale) | Medium | **High** | AES-256 at rest, TLS 1.2+ in transit, masking-by-default for analysts, default-deny RBAC + RLS (`rbac_test.sql` 15/15 reference PASS), FDE for export-capable devices (B1), `docs/C2_breach_response_plan.md` (1h report, s.23/Art.33 clocks), encrypted backups (B4) | **Low–Medium** (FDE rollout is P1) |
| **R7** | **Consent fatigue / dark patterns** — bundled consent, hard-to-withdraw opt-ins | High | Medium | Unbundled toggles, no pre-ticked boxes, one-tap withdrawal (Art.7), consent versioning + audit of every grant/withdraw, A/B-tested plain language, frequency capping on notifications | **Low** |
| **R8** | **Children's data** — minors enrolling or being marketed to | Medium | **High** | **Age gate: 13+ enrolment (parental consent below), 18+ for marketing**, per DPPA s.8 handling of children's data; age-verification question + anomaly screening (e.g., child-like name/purchase patterns) → account review; no behavioural profiling of minors | **Low** |
| **R9** | **Rights requests ignored or mishandled** (access/erasure/portability) | Medium | Medium | Documented rights procedure with 30-day SLA (GDPR Art.15/16/17/20; DPPA s.24/s.25/s.28), DPO intake channel, request log; P2 remediation CHK-13/14 | **Medium → Low after P2** |
| **R10** | **Vendor/processor breach** (loyalty cloud, SaaS CRM) | Medium | High | DPAs per **GDPR Art.28 / DPPA s.21**, breach notification SLA ≤ 24h, portability/exit terms, vendor register (R8 in risk register) | **Low after P2** |

---

### 6. Outcome, measures & sign-off (Art.35(7)(d)–(e))

**Overall residual risk: LOW** — conditional on the measures below; **two conditions are blocking for EU go-live**: (i) SCCs + transfer impact assessment (R5), (ii) DPO appointment (§4). While unmet, residual risk for R5 is **HIGH** and rollout must not include EU members.

| Measure ID | Measure | Control reference | Owner | Due |
|---|---|---|---|---|
| M-01 | Masking-by-default + column-level access for all analyst surfaces | `module4_security/data_masking.sql`, `rbac_postgresql.sql` (evidence: demo 4/4, RBAC 15/15 reference run) | Head of IT | Month 3 (deployment) |
| M-02 | FDE + remote wipe for any device able to export Restricted data | `docs/C2_encryption_masking_spec.md` B1 | Head of IT | Month 3 |
| M-03 | SCCs + transfer impact assessment with European distributor | Art.44–49; `docs/C2_compliance_audit_checklist.md` CHK-22 | DPO / EDM Consultant | Before EU go-live |
| M-04 | Appointment of DPO | DPPA s.6 | CEO | Month 1–3 |
| M-05 | Consent rework: unbundled, versioned, withdrawable | Art.7 / DPPA s.7; CHK-04 | CRM Officer | Month 4–6 |
| M-06 | Human-review path for tier/benefit decisions | Art.22 / DPPA s.27 | CRM Officer | Month 4–6 |
| M-07 | Rights-request procedure (30-day SLA) | Art.15/16/17/20/21; DPPA s.24/25/28 | DPO | Month 4–6 |
| M-08 | Retention purge job (24-month inactivity) | POL-003; CHK-28 | IT Operations Lead | Month 7–9 |
| M-09 | Breach plan adoption + tabletop including loyalty-DB scenario | `docs/C2_breach_response_plan.md` | Head of IT | Month 1–3 plan; Month 9 tabletop |
| M-10 | No-facial-recognition / aggregate-only sensor policy + signage | §5 R3; DPPA s.10 | Store Operations | Month 4 |

**Sign-off**

| Role | Name | Decision | Date |
|---|---|---|---|
| Data Protection Officer (DPPA s.6) | *pending appointment* | □ Approve □ Approve with conditions □ Reject | |
| Data Governance Council (chair) | | □ Approve □ Approve with conditions □ Reject | |
| Executive sponsor (CEO/CFO) | | □ Approve (resourcing) | |
| EDM Consultant (author) | | Submitted | |

**Review date:** 12 months from sign-off, or on any material change (new data category, new third country, new profiling logic, or a breach affecting this processing) — logged in the DPIA register (§7).

---

### 7. Records & accountability

| Record | Content | Reference |
|---|---|---|
| **DPIA register entry** | DPIA-2026-001, status, residual risk, sign-off dates, review date | Internal DPIA log (Council secretary) |
| **Art.30 record of processing (RoPA)** | This processing's entry: purposes, categories, recipients (EU distributor), transfers (Uganda → EU, SCCs), retention, security measures M-01…M-10 | Linked to catalog seed (`docs/C1_catalog_tools.md`) — CHK-17 |
| **PDPO register** | Registration of SRG as data collector/controller under **DPPA s.29**; public register access per **s.30** | CHK-01 (P1 — currently **FAIL**) |
| **Breach register** | Any incident touching this processing logged regardless of notifiability | `docs/C2_breach_response_plan.md` (CHK-12) |
| **Consent record** | Per-member consent grants/withdrawals with version + timestamp | CRM; Art.7 / DPPA s.7 evidence |

---

### 8. Cross-map to the generic DPIA template fields

*(Template Appendices not supplied in this environment — mapping below lets the Council paste this content into the corporate template unchanged.)*

| Generic template field | Section in this DPIA |
|---|---|
| 1. Description of the processing | §2 (plus §1 scope/purpose) |
| 2. Necessity & proportionality | §3 |
| 3. Consultation | §4 |
| 4. Assessment of risks to rights & freedoms | §5 (risk / likelihood / severity columns) |
| 5. Measures envisaged to address risks | §5 (measures column) + §6 measure table M-01…M-10 |
| 6. Residual risk conclusion | §6 (LOW, with two blocking conditions) |
| 7. Sign-off & approval | §6 sign-off block |
| 8. Review date / triggers | §1 and §6 |
| 9. Annexes (data-flow diagram, RoPA extract, vendor list) | §2 data-flow table; Art.30 record (§7); annexes to be attached from `module5_warehouse/data_dictionary.md` and the vendor register when issued |

---

### Think-deeper answer

**Prompt: a DPIA is often filed as a launch checkbox — what makes this one *load-bearing* for SRG?**

Three things. **First, it is a gate, not a report:** §6 explicitly withholds EU go-live until SCCs (Art.44–49) and the DPO (DPPA s.6) exist — the assessment converts "the European distributor wants data" from an unexamined flow into a condition precedent, which is precisely the exposure that would surface in the expected PDPO audit within 12 months. **Second, it encodes the hardest technical truth in the MDM design as a privacy control:** the false-merge risk (§5 R2) is where data quality meets fundamental rights — merging two people's histories destroys one person's record of their own life and can misdirect their data to a stranger; SRG's rule that name similarity never auto-merges (365 homonym pairs rejected, 110 queued for humans) is a *privacy measure living inside a data-quality script*, and a DPIA is the only document that would notice and name it. **Third, it is honest about the interim state:** marking residual risk LOW *conditional* on M-01…M-10, and HIGH for transfers until signed, resists the common failure of declaring safety while the controls are merely designed — module4 is proven as artifacts (RBAC 15/15 reference run, masking 4/4) but not yet deployed in production, and a DPIA that blurred that distinction would repeat the Jinja lesson: documentation mistaken for protection.
