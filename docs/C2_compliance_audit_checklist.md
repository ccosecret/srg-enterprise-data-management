# Task C2 Deliverable — Compliance Audit Checklist vs Task A2 Obligations Register

## Task C2 — Security & Privacy (C8)

**Client:** Savanna Retail Group (SRG) · **Prepared by:** Lead Enterprise Data Management Consultant
**Status:** Draft for Data Governance Council · **Version:** 1.0 · **Assessment date:** Month 0 baseline
**Frameworks assessed:** Uganda **DPPA 2019 (Cap. 97)** — s.3 principles, s.4 establishment of PDPO, s.6 data protection officer, s.7 consent, s.9 prohibition on special personal data, s.10 protection of privacy, s.11 collection of data from data subject, s.20 security measures, s.21 security measures re data processed by processor, s.23 notification of data security breaches, s.24 right to access, s.25 right to prevent processing, s.26 direct marketing, s.27 automated decision-taking, s.28 rectification/blocking/erasure, s.29 data protection register, s.30 public access to register (Cap. 97 consolidated numbering — verify against official gazette before external use); **GDPR** Art.5, 6, 7, 13/14, 15, 16, 17, 20, 21, 22, 25, 28, 30, 32, 33, 34, 35, 44–49, 83; **CCPA/CPRA** §1798.100, .105, .120, .130, .140, .150, .155 (applicability watch only).
**Stakes if unremediated:** GDPR Art.83 penalties up to **EUR 20M or 4% of global annual turnover**; CCPA §1798.155 administrative fines and §1798.150 private right of action of **USD 100–750 per consumer per incident** (only if CCPA thresholds are ever met); PDPO audit expected within **12 months**.
**Evidence base:** `module2_data_quality/*`, `module3_etl/*`, `module4_security/*`, `module5_warehouse/*`, plus the new deliverables in `docs/`.

---

### 1. Checklist (31 checks)

| Check ID | Obligation (framework + section/article) | Control expected | Current state | Evidence or gap | Remediation (artifact link) | Priority | Owner | Target month |
|---|---|---|---|---|---|---|---|---|
| CHK-01 | **DPPA s.29** data protection register (register as data collector/controller/processor with PDPO); **s.30** public access to register | Current registration certificate + register entry | **FAIL** | No filing made with the PDPO to date | File registration; retain acknowledgment; re-file on any change — `docs/C2_dpia_loyalty_app.md` §7 | **P1** | EDM Consultant → CEO | Month 1–3 |
| CHK-02 | **DPPA s.4** (establishment of PDPO) + **s.6** data protection officer | Appointed DPO with mandate, contact point published | **FAIL** | No formally appointed DPO (EDM Consultant acting interim in `docs/C2_breach_response_plan.md` roles) | Appoint DPO (hire or designated officer), publish contact in notices — `docs/C2_dpia_loyalty_app.md` M-04 | **P1** | CEO | Month 1–3 |
| CHK-03 | **DPPA s.3** principles; **GDPR Art.5** (lawfulness, fairness, transparency, accuracy, storage limitation, integrity, accountability) | Written principles + demonstrable accuracy/accountability controls | **PARTIAL** | Cleansing evidence exists (dupes 22.84% → 0.00%, total flags 25.06% → 2.85%, districts 127 → 42, UOM 15.33% → 100%, category 22% → 100%); no consolidated policy statement | Ratify principles in EDM policy (POL-001/002/003) under Task A2 charter | P2 | EDM Council | Month 4–6 |
| CHK-04 | **DPPA s.7** consent to collect or process; **GDPR Art.7** (consent records, easy withdrawal) | Granular, logged, withdrawable consent at every capture point | **PARTIAL** | POS/app capture exists but consent bundled; no withdrawal audit trail; 23% duplicate era shows consent-to-identity linkage weakness | Consent rework: unbundled toggles, versioned consent log, withdrawal parity — `docs/C2_dpia_loyalty_app.md` M-05 | **P2** | CRM Officer | Month 4–6 |
| CHK-05 | **DPPA s.11** collection of data from data subject (notice at collection); **GDPR Art.13/14** transparency | Layered notice stating purpose, retention, sharing, rights | **PARTIAL** | Privacy notice exists for UG operations; no field-level notice for structured address change; EU notice not drafted | Re-issue notices (POS receipt QR, app tab, checkout) naming the European distributor flow — `docs/C1_impact_analysis.md` §6 | **P2** | CRM Officer + DPO | Month 4–6 |
| CHK-06 | **DPPA s.9** prohibition on special personal data | No special/sensitive categories collected unless prohibited-case exemption applies | **PASS** | No special-category fields in schema; loyalty DPIA explicitly excludes national ID/passport; payroll restricted to need-to-know (column REVOKE) | Maintain via POL-001 tags on new attributes; re-verify on any schema change (CHG process) | P3 | EDM Consultant | Month 7–12 (annual) |
| CHK-07 | **DPPA s.10** protection of privacy | No covert monitoring; aggregate-only footfall; masked analytics | **PASS** | No facial recognition (policy in `docs/C2_dpia_loyalty_app.md` R3); masking views for analysts (`data_masking_demo.py` 4/4 PASS) | Keep signage current; sensor policy ratified with Council | P3 | Store Operations | Month 7–12 |
| CHK-08 | **DPPA s.20** security measures (technical + organisational) | Documented security programme: policy, roles, monitoring | **PARTIAL** | Technical controls designed (RBAC/RLS/masking/quarantine); no single security programme document; no security metrics pack | Publish security programme referencing `docs/C2_encryption_masking_spec.md` + DQC/DQC-style security metrics | P2 | Head of IT | Month 4–6 |
| CHK-09 | **DPPA s.20** / **GDPR Art.32** — endpoint encryption | **Mandatory full-disk encryption** + screen lock + remote wipe on any export-capable device | **FAIL** | **Realised gap: the Jinja laptop was unencrypted** (9,000 records: names, phones, purchase history); no device inventory or compliance report | FDE rollout, device-compliance reporting, export gate (B1, UGX 15M) — `docs/C2_encryption_masking_spec.md` §a/§b | **P1** | Head of IT | Month 1–3 |
| CHK-10 | **DPPA s.21** security measures re data processed by processor (technical) | Processors contractually and technically secured | **PARTIAL** | Cloud storage encrypted in transit/at rest by provider defaults; no evidenced processor assurance for CRM/loyalty vendors | Processor security schedule + annual assurance questionnaires — with CHK-23 | P2 | EDM Consultant + Procurement | Month 4–6 |
| CHK-11 | **DPPA s.23** notification of data security breaches — *"immediately notify the Authority"* | Immediate PDPO notification of unauthorised access/acquisition + remedial action | **FAIL** | **The Jinja theft was never notified**; internal report was 11 days late; no s.23(2)–(4) process existed | Adopt `docs/C2_breach_response_plan.md`; retrospective PDPO engagement on the Jinja incident; s.23 templates live | **P1** | DPO (interim: EDM Consultant) | Month 1–3 |
| CHK-12 | **DPPA s.3** accountability; **GDPR Art.33(5)** internal documentation of all breaches | Breach register logging every incident (notifiable or not) | **PARTIAL** | One known incident (Jinja) with no register entry; no register exists | Stand up breach register with the plan; back-enter Jinja entry with dates and gap statement — `docs/C2_breach_response_plan.md` §(b) | **P1** | DPO | Month 1–3 |
| CHK-13 | **DPPA s.24** right to access; **GDPR Art.15** | Documented access-request procedure with SLA and identity verification | **FAIL** | No procedure, no intake channel, no SLA; request would stall across 4-person team | Rights-request procedure (30-day SLA), intake mailbox, request log — `docs/C2_dpia_loyalty_app.md` M-07 | **P2** | DPO | Month 4–6 |
| CHK-14 | **DPPA s.25** right to prevent processing, **s.28** rectification/blocking/erasure; **GDPR Art.16/17/20/21** | Objection, rectification, erasure, portability honoured end-to-end (incl. SCD2 history and golden record) | **FAIL** | No procedure; SCD2 design means erasure must be handled as anonymisation/rectification across versions — never specified until now | Rights runbook covering `dim_customer` versions + golden map; test with 3 sample requests — `docs/C2_dpia_loyalty_app.md` M-07 | **P2** | DPO + EDM Consultant | Month 4–6 |
| CHK-15 | **DPPA s.26** direct marketing; **GDPR Art.21** objection | Opt-in marketing, suppression list honoured across CRM/loyalty/POS | **PARTIAL** | Consent capture exists (CHK-04) but no central suppression list; walk-in attribution (8.7% revenue) complicates honouring objections | Suppression list wired into campaign exports; quarterly audit of sends | P2 | CRM Officer | Month 4–6 |
| CHK-16 | **DPPA s.27** automated decision-taking; **GDPR Art.22** | No solely automated adverse decisions without human review | **PARTIAL** | Tier/benefit logic not yet automated; DPIA defines the human-review path but it is not implemented | Implement human-review route for adverse tier/benefit outcomes + disclosure text — `docs/C2_dpia_loyalty_app.md` M-06 | P2 | CRM Officer | Month 4–6 |
| CHK-17 | **GDPR Art.30** records of processing (RoPA) | Living record of purposes, categories, recipients, transfers, retention, security | **PARTIAL** | Processing inventory derivable from `module5_warehouse/data_dictionary.md` (25 attributes + classification) and DPIA §2; not assembled as an RoPA, no automation | Manual RoPA now; catalog-driven export in Phase 2 — `docs/C1_catalog_tools.md` automation line | P3 (assembly P2) | DPO + EDM Consultant | Month 7–12 (draft at M6) |
| CHK-18 | **GDPR Art.6** lawful bases for EU-resident members | Documented basis per purpose (consent/contract/obligation) | **PARTIAL** | Bases identified in `docs/C2_dpia_loyalty_app.md` §3 but not recorded per processing operation in a register | Lock basis matrix into RoPA + consent rework (CHK-04) | P2 | DPO | Month 4–6 |
| CHK-19 | **GDPR Art.25** protection by design and by default | Default-deny access, masking by default, minimisation in design | **PARTIAL** | **Strong artifacts**: default-deny GRANTs, column-level REVOKE (payroll, phone/email), RLS store scoping, masking views, `customer_sk = 0` design — **deployment to production pending** (RBAC suite 15/15 PASS is a documented *reference run*; no PostgreSQL server in the build environment) | Deploy module4 to production PostgreSQL 15/16 and re-run `rbac_test.sql` for live evidence | P2 | Head of IT | Month 4–6 |
| CHK-20 | **GDPR Art.33** (72 hours to supervisory authority, reasons for delay) / **Art.34** (data subjects, high risk) | Adopted plan with clock discipline, templates, decision tree | **PARTIAL** | Plan now drafted in `docs/C2_breach_response_plan.md`; not yet adopted, tabletop not run, no DPO to own the clock | Council adoption (Month 1), tabletop with Jinja scenario at Month 9 | **P1** (adoption) / P3 (tabletop) | Head of IT + DPO | Adopt: M1–3; tabletop: M9 |
| CHK-21 | **GDPR Art.35** DPIA | Completed, signed DPIA for high-risk processing | **PARTIAL** | **DPIA-2026-001 drafted in this portfolio** (`docs/C2_dpia_loyalty_app.md`); template appendices not supplied (structure follows EDPB/Art.35, cross-mapped); not yet signed; DPO slot empty | Sign-off (Council + DPO + sponsor); refresh at 12 months or on material change | P2 (sign-off) / P3 (refresh) | EDM Consultant → Council | Sign-off M4–6; refresh M7–12 |
| CHK-22 | **GDPR Art.44–49** international transfers (SCCs) | Valid transfer mechanism + transfer impact assessment for EU flows | **FAIL** | No SCCs with the European distributor; **Uganda has no adequacy decision** → sharing is currently ungated | Execute SCCs + transfer impact assessment **before EU go-live** (blocking gate in DPIA §6 M-03) | **P2 (go-live blocking)** | DPO + EDM Consultant | Month 4–6 |
| CHK-23 | **GDPR Art.28** processor contracts (also vendor management under **DPPA s.21**) | Written DPAs with SaaS CRM, loyalty cloud, fulfilment partners: purpose limits, sub-processor control, breach SLA ≤ 24h, audit rights, exit/portability | **FAIL** | No DPAs evidenced; vendor register absent | Vendor register + DPAs; breach SLA; portability/exit clause; annual assurance review | **P2** | Procurement + DPO | Month 4–6 |
| CHK-24 | **DPPA s.20** / **GDPR Art.32** — access control | Default-deny RBAC, column-level REVOKE, row-level store scoping, named logins | **PARTIAL** | Implemented as artifacts: 5 roles (store_cashier, store_manager, data_analyst, compliance_officer, cdm_admin), `rbac_test.sql` 15/15 PASS (reference output committed), RLS proofs — **production deployment pending**; shared till logins still defeat accountability | Deploy to production; enforce named logins (B5 MFA); quarterly access recertification | P2 | Head of IT | Month 4–6 |
| CHK-25 | **DPPA s.10** / **GDPR Art.25/32** — masking of PII in analytics | Masking by default; raw access only to named roles, audited | **PARTIAL** | Masking functions proven: phone `+256-XXX-XX1234`, name `J*** D**`, email `j***@domain`, `payment_ref` `MP******89`; `data_masking_demo.py` executed **4/4 PASS** on live data — views not yet deployed as the production analyst surface | Deploy masked views as the only analyst entry point; audit raw-access use monthly | P2 | Head of IT | Month 4–6 |
| CHK-26 | **DPPA s.20** / **GDPR Art.32(1)(a)** — encryption at rest | AES-256 on laptops, HQ servers, cloud storage, backups | **PARTIAL** | Cloud object storage encrypted (provider default); **laptops unencrypted (see CHK-09 FAIL)**; encrypted backup + tested restore not yet operating (B4) | FDE (B1), encrypted backup + quarterly restore tests (B4), key custody split Head of IT/CFO | P2 (FDE itself P1) | Head of IT | Month 4–6 |
| CHK-27 | **DPPA s.20** / **GDPR Art.32(1)(a)** — encryption in transit | TLS 1.2+ everywhere; tunnels store→HQ; no plain FTP/email attachments | **PARTIAL** | ETL/DB traffic uses parameterised connections; legacy store links and ad-hoc email CSV flows not certified | WireGuard/OpenVPN tunnels + SFTP migration + certificate lifecycle (B2) — `docs/C2_encryption_masking_spec.md` | P2 | Head of IT | Month 4–6 |
| CHK-28 | **GDPR Art.5(1)(e)** storage limitation; retention per **POL-003** (aligned to DPPA s.3) | Enforced retention schedule with automated purge | **PARTIAL** | **Policy written (POL-003): 24-month inactivity rule; purge job pending**; no evidence of deletion runs | Implement purge job + deletion log; report volumes quarterly | P3 | IT Operations Lead | Month 7–9 |
| CHK-29 | **DPPA s.20** / **GDPR Art.32/5(2)** — audit logging & access review | Logs of access to Restricted data; periodic recertification | **PARTIAL** | `etl_run_log` + run-state dashboards (RC-6 fix), DB role model in place; **no access recertification cycle, no export log** (Jinja export was unlogged) | Export approval log (B-line control), quarterly recertification of the 5 roles, log retention 12 months | P2 | Head of IT | Month 4–6 |
| CHK-30 | **DPPA s.20** (organisational measure) — training & awareness | Annual security/privacy training; incident-reporting drill for all staff | **FAIL** | No structured training; the 11-day reporting delay indicates the reporting rule was unknown; post-incident retraining promised but not delivered | Role-based training (cashiers → reporting rule; analysts → export rules), annual refresh, phishing drills | **P2** | DPO + Head of IT | Month 4–6 (annual cycle from M7) |
| CHK-31 | **CCPA/CPRA §1798.140** thresholds (USD 25M revenue / 100k consumers / 50% revenue from selling); §§1798.100/.105/.120/.130/.150/.155 | Applicability test + readiness if thresholds met | **N/A (monitor)** | SRG does not currently meet thresholds (no California sales; data not sold/shared for cross-context behavioural advertising); **policy posture: never sell/share** keeps §1798.120 opt-out moot | Annual applicability re-test at each expansion gate (Kenya/Rwanda/US); if ever met: 45-day response capability (§1798.130) and USD 100–750 per-consumer incident exposure (§1798.150) noted for risk register | P3 | DPO | Month 12 (annual) |

---

### 2. Summary of results

| State | Count | Share | Check IDs |
|---|---|---|---|
| **FAIL** | **9** | 29% | CHK-01 (PDPO registration), CHK-02 (DPO), CHK-09 (endpoint encryption), CHK-11 (s.23 notification), CHK-13 (right to access), CHK-14 (rectify/object/erase), CHK-22 (SCCs/transfers), CHK-23 (vendor DPAs), CHK-30 (training) |
| **PARTIAL** | **19** | 61% | CHK-03, 04, 05, 08, 10, 12, 15, 16, 17, 18, 19, 20, 21, 24, 25, 26, 27, 28, 29 |
| **PASS** | **2** | 6% | CHK-06 (no special personal data), CHK-07 (privacy/aggregate-only monitoring) |
| **N/A (monitor)** | **1** | 3% | CHK-31 (CCPA applicability) |
| **Total** | **31** | 100% | |

**Reading of the baseline:** the *technical* posture is materially better than the *procedural* one — every FAIL except CHK-09/CHK-30 is a governance obligation (registration, DPO, notification, rights handling, contracts, transfers). That pattern is typical of an organisation that built controls in code (`module2`–`module5`) before building them in policy — which is exactly why the P1 list is governance-heavy plus one hard technical fix (FDE).

---

### 3. Prioritized remediation plan

#### P1 — Immediate (Months 1–3)

| # | Action | Checks cleared | Artifact | Owner | Evidence of done |
|---|---|---|---|---|---|
| 1 | **Register with the PDPO** as data collector/controller (file, acknowledge, publish) | CHK-01 → PASS | `docs/C2_dpia_loyalty_app.md` §7 | EDM Consultant → CEO | Filing acknowledgment |
| 2 | **Appoint the DPO** (DPPA s.6), publish contact in all notices | CHK-02 → PASS | DPIA §4 / breach plan roles | CEO | Appointment letter + notice update |
| 3 | **FDE rollout** to every export-capable device + export-approval gate (B1, UGX 15M) | CHK-09 → PASS; CHK-26 → PARTIAL+ | `docs/C2_encryption_masking_spec.md` §a/§b | Head of IT | 100% device-compliance report |
| 4 | **Adopt the breach response plan + stand up the breach register** (back-enter the Jinja incident with dates/gap statement) | CHK-11, CHK-12, CHK-20 → PASS/PARTIAL | `docs/C2_breach_response_plan.md` | Council + DPO | Council minute; register with Jinja entry |
| 5 | **Retrospective PDPO engagement** on the unnotified Jinja breach (s.23 posture repair) | CHK-11 → PASS | Breach plan §(c)/(e) | DPO | Filed correspondence |

#### P2 (Months 4–6) — quick-win window (month-6 mandate)

| # | Action | Checks | Artifact | Owner |
|---|---|---|---|---|
| 6 | **Rights-request handling procedure** (access, rectify, object, erase, portability; 30-day SLA; SCD2/golden-record runbook) | CHK-13, CHK-14 → PASS/PARTIAL | `docs/C2_dpia_loyalty_app.md` M-07 | DPO |
| 7 | **Consent capture rework + notices + suppression list** (unbundled, versioned, withdrawable) | CHK-04, CHK-05, CHK-15, CHK-18 | DPIA M-05; `docs/C1_impact_analysis.md` §6 | CRM Officer |
| 8 | **Vendor DPAs + register** (Art.28 / DPPA s.21: purpose limits, breach SLA ≤ 24h, exit/portability) | CHK-10, CHK-23 → PASS | Threat model R8 | Procurement + DPO |
| 9 | **Access recertification + named logins/MFA + export log** (quarterly cycle over the 5 roles) | CHK-24, CHK-29 → PASS/PARTIAL | `module4_security/rbac_postgresql.sql`; B5 | Head of IT |
| 10 | **Deploy module4 to production** (RBAC, RLS, masking views) and re-run tests for live evidence | CHK-19, CHK-24, CHK-25 → PASS | `rbac_test.sql` 15/15 → live; `data_masking_demo.py` | Head of IT |
| 11 | **SCC pack + transfer impact assessment** with the European distributor (**blocking gate for EU go-live**) | CHK-22 → PASS | DPIA M-03 | DPO |
| 12 | **Security programme + training** (reporting rule ≤ 1h taught to all staff; export rules for analysts) | CHK-08, CHK-30 → PASS/PARTIAL | `docs/C2_encryption_masking_spec.md`; breach plan §(b) | Head of IT + DPO |
| 13 | **Encrypted backup + tested restore** (B4) and store tunnels/TLS lifecycle (B2) | CHK-26, CHK-27 → PASS/PARTIAL | Encryption spec §a | IT Operations Lead |
| 14 | **DPIA sign-off** (Council + DPO + sponsor) and EU transparency notices | CHK-21 → PARTIAL+ , CHK-05 | `docs/C2_dpia_loyalty_app.md` §6 | EDM Consultant |

#### P3 (Months 7–12) — sustainment & audit polish

| # | Action | Checks | Artifact | Owner |
|---|---|---|---|---|
| 15 | **Retention purge job + deletion log** (24-month inactivity, POL-003) | CHK-28 → PASS | DPIA M-08 | IT Operations Lead |
| 16 | **Tabletop exercise** (Jinja scenario, 1h reporting clock, s.23/Art.33 drafts) | CHK-20 → PASS | Breach plan §(e) | Head of IT |
| 17 | **Catalog-driven RoPA automation** (export Art.30 record from catalog attributes + POL-001 tags) | CHK-17 → PASS | `docs/C1_catalog_tools.md` Phase 2 | EDM Consultant |
| 18 | **DPIA refresh + annual applicability re-tests** (CCPA, Kenya/Rwanda expansion) | CHK-21, CHK-31 | DPIA §6 review clause | DPO |
| 19 | **Quarterly governance cadence**: dictionary/glossary review, role recertification, DQ/DQ-security metrics to Council | CHK-03, CHK-29 sustain | `docs/C1_catalog_tools.md` §5 | EDM Consultant |

---

### 4. "PDPO audit readiness in 12 months" trajectory

| Milestone | FAIL | PARTIAL | PASS | N/A | Narrative |
|---|---|---|---|---|---|
| **Baseline (now)** | **9** | **19** | **2** | 1 | Controls exist as *artifacts*; obligations exist nowhere as *filing* |
| **End Month 3 (P1)** | **5** | **19** | **6** | 1 | Registered, DPO appointed, FDE live, breach plan + register adopted — the four audit-critical items are closed |
| **End Month 6 (P2)** | **0** | **19** | **11** | 1 | Rights handling, consent, DPAs, SCCs, deployed RBAC/masking, training — **no failing checks remain** |
| **End Month 12 (P3)** | **0** | **6** | **24** | 1 | Purge automation, tabletop, RoPA automation, refreshed DPIA; residual partials are continuous-improvement items with owners and dates |

**Trajectory statement for the Council:** SRG will move from **9 FAIL / 2 PASS today to zero FAIL / 24 PASS within 12 months**, with every remaining PARTIAL carrying a named owner and a scheduled re-test. By month 3 the four things a PDPO auditor checks first — **registration (s.29), DPO (s.6), security measures incl. endpoint encryption (s.20), and breach notification capability (s.23)** — are demonstrably in place with evidence (filing acknowledgment, appointment letter, device-compliance report, adopted plan + register containing the Jinja entry). By month 12 the audit pack is self-sustaining: catalog-generated RoPA (Art.30), DQC/DQC-security metrics, quarterly recertification minutes, and a signed DPIA register — so the audit is met with *records*, not assurances.

---

### Think-deeper answer

**Prompt: 61% of checks are PARTIAL — is that honest, or is "partial" a comfortable way to avoid failing?**

It is honest only because each PARTIAL here splits a *real* seam: **designed vs deployed**. SRG genuinely has default-deny GRANTs, column-level REVOKE, RLS, and masking that demonstrably work — `rbac_test.sql` 15/15 PASS (documented reference run, no PostgreSQL server in the build environment) and `data_masking_demo.py` 4/4 on live data — yet a judge standing in a store today would find an unencrypted laptop and shared till logins. Marking CHK-19/24/25 FAIL would erase true engineering merit; marking them PASS would repeat the Jinja mistake of confusing documentation with protection. PARTIAL is the only truthful state — *provided* it carries a deployment date, which these rows do (P2, month 4–6). The sharper test of honesty is in the FAIL column: it deliberately includes the three the brief calls out (PDPO registration, s.23 notification, endpoint encryption) **plus six more** (DPO, access rights, objection/erasure, SCCs, DPAs, training) because an obligations register that reports only known headline failures while quietly passing untested rights-handling would be a checklist, not an audit. And the trajectory table exists to stop PARTIAL from becoming permanent: a partial with an owner and a month is a plan; a partial without either is a euphemism.
