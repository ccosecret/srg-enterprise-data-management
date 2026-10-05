# A2 — Data Policies (POL-001 · POL-002 · POL-003)

**Client:** Savanna Retail Group (SRG) · **Prepared by:** Enterprise Data Management Consultant
**Date:** Month 1 of the 18-month EDM programme · **Proposed effective:** Month 2 · **Classification:** Confidential
**Annex to:** `A2_governance_charter.md` · **Supporting evidence:** `module2_data_quality/output/` (VR/DQC catalogues), `module3_etl/` (quarantine, run audit), `module4_security/` (RBAC, masking)

---

## Task A2 — Governance Framework & Compliance Register (C2)

### POL-001 — Data Access & Classification

| Field | Value |
|---|---|
| **Policy ID / title** | POL-001 — Data Access & Classification |
| **Owner** | Head of IT (day-to-day control owner); Compliance Officer / Data Protection Officer (DPPA s.6) owns the classification taxonomy |
| **Approver** | Data Governance Council, ratified by the Managing Director (Month 2) |
| **Effective** | Month 2; full attribute coverage by Month 3 |
| **Scope** | All SRG data at rest, in transit and on endpoints in every domain in the Charter: 23 POS databases, e-commerce PostgreSQL, loyalty cloud DB, SaaS CRM, Odoo ERP, HR/payroll, supplier files, mobile-money extracts, warehouse and dashboards. Applies to employees, contractors, and any processor (GDPR Art.28). |

**Requirements (measurable)**

1. Every attribute in the data dictionary and every new data store is tagged with exactly **one of four tiers** before production release; **100% coverage by Month 3**, verified by a metadata report.
2. **Classification tiers with SRG examples:**

| Tier | Definition | SRG examples | Default access |
|---|---|---|---|
| **Public** | Safe for external publication | product_name, shelf price, store addresses and opening hours, published KPIs | Open |
| **Confidential** | Internal commercial data; leak harms competitiveness, not a person | transaction_id, district, sales aggregates, supplier lead times, pricing logic, promo calendar | Named staff by role |
| **Restricted** | Personal, financial or identifying data (DPPA "personal data", GDPR Art.4(1)) | `full_name`, `phone`, `email`, `payment_ref`, loyalty history, consent flags, HR salary, national IDs | Explicit `GRANT` only, masked by default |
| **Prohibited** | Data SRG must not collect, store or transmit | passwords/PINs/OTPs, full card PAN and CVV, special personal data (DPPA s.9), children's data without guardian consent (DPPA s.8), data with no lawful basis (DPPA s.7) | Not collected; discovered instances quarantined and destroyed within 5 working days, with a record |

3. **Default deny.** No role, service account or new database receives access without an explicit `GRANT`. Target: **0 standing ad-hoc grants**; all grants traceable to a role in the RBAC matrix.
4. **Masked by default for analytics.** Any role other than `compliance_officer`/`cdm_admin` reads Restricted columns only through masking views: phone `+256-XXX-XX9332`, name `S*** W**`, e-mail `s***@srg.co.ug`, payment reference `AU*****51` (executed evidence: `module4_security/output/masking_demo_output.txt`, 4/4 validation checks PASS).
5. **Quarterly access recertification** within **10 working days** of each quarter start, at **≥95% completion**; revocations executed within **2 working days** of sign-off.
6. **Encrypted export rule.** Extracts of more than **100 Restricted records** require prior written approval from the **Head of IT and the Compliance Officer (DPO)**; the export must be encrypted at rest (AES-256 or equivalent), password-delivered out-of-band, logged, and expire within **7 days**. Exports of Prohibited data are never permitted.
7. **Endpoint control:** full-disk encryption and a screen-lock policy on every device that has touched Restricted data; **≥98% compliance** on the monthly check.
8. **Audit logging:** reads of Restricted columns are logged and reviewed monthly; logs retained **12 months**.

**Enforcement mechanism.** *Technical:* `GRANT`/`REVOKE` scripts (default-deny, column-level grants, row-level security — `module4_security/rbac_postgresql.sql`, 15-test assertion suite `rbac_test.sql`); masking views (`data_masking.sql`); database audit logging; export workflow tooling that refuses unencrypted containers. *Procedural:* recertification campaign, export approval ticket, monthly log review by the DPO.

**Exceptions.** Written, logged in the exceptions register, time-bound to a maximum of 90 days, approved by the Council; break-glass access permitted to the Head of IT with post-hoc justification inside 24 hours. Prohibited-data exceptions are not grantable.

**Review cadence.** Semi-annual, and immediately after any incident or regulatory change.

**Violation handling.** Unauthorised access or unencrypted export: report to Head of IT and DPO within 24 hours; disciplinary process under HR rules; where Restricted data is exposed, run the breach assessment (DPPA s.23 / GDPR Art.33) and notify the Authority immediately on confirmation; repeat or wilful violations escalate to the Managing Director.

---

### POL-002 — Data Quality

| Field | Value |
|---|---|
| **Policy ID / title** | POL-002 — Data Quality |
| **Owner** | Head of IT (control operation); Domain Data Owners (quality targets); CRM/Marketing Officer (customer domain) |
| **Approver** | Data Governance Council (Month 2) |
| **Effective** | Month 2 for ETL enforcement; Month 4 for 100% of capture forms |
| **Scope** | All customer, product, store, supplier, price/promotion and transaction/payment data at capture, in integration and at publication. HR-restricted data is in scope for validation only (no profiling of salary content). |

**Requirements (measurable)**

1. **Entry-time validation.** Rules **VR-001..VR-012** are bound at capture, enforced client-side *and* server-side: phone masked to E.164 with save blocked on failure (VR-001), district limited to a dropdown of the 42 official values (VR-002), primary-key and golden-record uniqueness rejected or routed to the stewardship queue (VR-004, VR-007), SKU collisions rejected (VR-008), UOM constrained to `{kg, pcs, liters}` (VR-009), category constrained to the master hierarchy (VR-010), price-below-cost flagged with approver identity (VR-011), MoMo `payment_ref` populated within 24 hours or transaction held as `PENDING` (VR-012).
2. **Monitoring.** Checks **DQC-01..DQC-10** run **daily at 06:00** with defined thresholds (duplicate-person rate >1.0%; phone validity <99.0%; district resolution <99.5%; core-field completeness phone <92%; UOM/category conformance <99.0%; SKU uniqueness violations >0; quarantine rate >0.5% or >100 rows; MoMo refs pending >24h; future-dated registrations >0; margin anomalies >0 weekly). Alerts go to the on-call rotation by SMS/WhatsApp and to the Council dashboard — **never to an unmonitored mailbox** (root cause RC-6).
3. **Remediation SLAs.** Critical: **<24 hours** (identity, primary-key, revenue-attributed defects). High: **<3 working days** (phone validity, UOM/category conformance, MoMo pending). Medium: **<10 working days** (format and enrichment defects). SLA breaches escalate automatically at the next Council meeting.
4. **ETL gate.** Every load validates against schema contracts; failing rows are **quarantined with a reason code and replayed** — no batch aborts and no silent partial-mode fallback (root cause RC-4); quarantine contents visible to stewards within 24 hours.
5. **Monthly DQ scorecard** to the Council: duplicate rate, phone validity, core-field completeness, conformance, quarantine rate, MoMo-pending aging — published **per store** and per channel.
6. **No direct production data edits** (manual `UPDATE`/`DELETE` outside application code) without an approved ticket naming record count, rows affected and business reason; target **0 unticketed edits per month**, reviewed monthly.
7. **Offline-tolerant capture.** Forms validate locally during connectivity outages and sync queued entries later; offline rows are admitted with an explicit state (`customer_sk = 0`, `PENDING_RECON`) rather than degraded data.

**Enforcement mechanism.** *Technical:* form validation with blocked saves; ETL quarantine table with reason codes and run audit (`module3_etl/srg_etl_pipeline.py`); daily monitoring jobs with alerting; database permissions that deny ad-hoc `UPDATE`/`DELETE` outside application roles; idempotent re-runs so fixes are replayable. *Procedural:* stewardship queue triage at the fortnightly stand-up; store scorecard attached to store-manager performance KPIs; ticket gate for production edits.

**Exceptions.** Domain Data Owner approval, capped at 30 days, logged with a compensating check; **no exception** permitted for VR-004 (primary-key integrity), VR-007 (customer identity) or VR-008 (SKU uniqueness).

**Review cadence.** Quarterly (thresholds and rules), or immediately after a P1 incident.

**Violation handling.** Repeated threshold breaches at a store trigger a corrective-action review with the Store Operations Manager; unticketed production edits are treated as a P2 incident (investigated within 3 working days); defects that reach Board reporting uncorrected escalate to the CFO as an accountability failure.

---

### POL-003 — Retention & Deletion

| Field | Value |
|---|---|
| **Policy ID / title** | POL-003 — Retention & Deletion |
| **Owner** | Compliance Officer / Data Protection Officer (schedule and erasure workflow); Head of IT Operations (purge jobs) |
| **Approver** | Data Governance Council, ratified by the Board (Month 3) |
| **Effective** | Month 3 (schedule published) · Month 4 (automated purge) · Month 6 (erasure self-service) |
| **Scope** | All records in operational systems, the warehouse, backups, e-mail/file shares, supplier and HR repositories — including the 180,000 loyalty accounts and ad-hoc extracts. |

**Requirements (measurable)**

1. **Retention schedule** published and enforced:

| Record class | Retention period | Basis | Disposal method | Owner |
|---|---|---|---|---|
| Transaction and sales records (incl. MoMo references) | **7 years** from transaction | Tax, audit and dispute evidence | Automated purge + deletion certificate | Finance/Reconciliation Officer |
| Loyalty account data | **24 months** after inactivity (last purchase, login or contact) | Storage limitation (DPPA s.3; GDPR Art.5(1)(e)) | Anonymise, then purge | CRM/Marketing Officer |
| Marketing consent / contactability record | **24 months** after last response | Consent freshness (DPPA s.7; GDPR Art.7) | Purge contact, retain consent evidence 3 years | CRM/Marketing Officer |
| Supplier contracts and procurement records | **6 years** after contract end | Contractual and statutory limitation | Purge + certificate | Procurement Officer |
| HR and payroll records | Per statutory Employment Act record-keeping (confirm exact periods with counsel) | Employment and tax law | Restricted purge + certificate | HR & Payroll Officer |
| Backups | **90 days** rolling | Operational recovery only | Cryptographic erasure at cycle end | Head of IT Operations |
| ETL quarantine payloads | **12 months** | Defect diagnosis and audit trail | Automated purge + log entry | Head of IT Operations |

2. **Automated purge job** runs monthly; every execution emits a **deletion certificate** (record class, count, basis, job ID, operator, timestamp) retained for 7 years and summarised at the quarterly Board report.
3. **Erasure workflow (DPPA s.28, GDPR Art.17).** Intake via a single published channel → identity verification → acknowledgement within **5 working days** → fulfilment within **30 days** across POS, e-commerce, loyalty, CRM and warehouse. Where a record must be kept (e.g. 7-year transaction history), the response applies **partial erasure/anonymisation** and states exactly what is retained and why.
4. **Lawful-refusal path.** Where erasure is refused (statutory retention, tax, legal claim), issue a **written justification citing the specific ground**, notify the data subject of the decision and of their right to **appeal to the Data Governance Council within 14 days**; the Council decides within 30 days and records the outcome in a refusal register.
5. **Prohibited data and end-of-life extracts** (including any copy such as the Jinja export) are destroyed within **5 working days** of identification, with a certificate.

**Enforcement mechanism.** *Technical:* scheduled purge jobs (cron/pg_cron) with append-only job logs; anonymisation scripts that are idempotent; backups expiring on a 90-day policy; access revocation triggered automatically on account inactivity at 24 months. *Procedural:* quarterly **spot audit of 10 records per domain** against the schedule, tabled at the Council with certificates; refusal register reviewed by the DPO.

**Exceptions.** Legal hold (litigation, audit, investigation) approved by the Managing Director and the DPO, recorded with an expiry date and reviewed every 90 days; no other exception to a statutory retention period.

**Review cadence.** Annual, plus immediate review on any new processing, new market (Kenya/Rwanda) or regulatory change.

**Violation handling.** Failure to execute a scheduled deletion or an approved erasure request is a **P1 incident**: reported to the Council and the DPO within 24 hours, assessed for notification under DPPA s.23 / GDPR Art.33, and remediated with a certificate within 5 working days. Repeated failures by a domain trigger an owner review by the Managing Director.

### Think-deeper answer

*How do these policies become enforceable rather than decorative?*

By binding each one to a control that fails closed. POL-001 is enforced by databases that grant nothing by default and expose Restricted columns only through masking views — so non-compliance is physically unavailable, not merely discouraged; the export workflow refuses unencrypted containers and caps extracts at 100 records without dual approval, which is precisely the control the 9,000-record laptop copy would have tripped. POL-002 is enforced at the two points where defects are born: the capture form (blocked saves on VR-001..VR-012) and the nightly load (quarantine with reason codes, no batch abort, no silent fallback), with DQC-01..DQC-10 alerting an on-call rotation rather than an unmonitored mailbox — and with consequences attached per store, because a scorecard nobody sees is not a control. POL-003 is enforced by jobs, not intentions: a monthly purge that cannot be skipped, deletion certificates that cannot be back-dated, and a quarterly spot audit that samples ten records per domain and asks for the certificate. The three together form a closed loop — **prevent (validation, grants) → detect (monitoring, recertification, audit) → correct (SLA, purge, escalation)** — which is the minimum viable governance that a four-person IT team can actually run.
