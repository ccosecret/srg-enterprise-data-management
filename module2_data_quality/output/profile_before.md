# SRG Data Quality Profile - BEFORE Cleansing

### SRG_Customers - BEFORE cleansing

| Dimension | Metric | Value |
|---|---|---|
| Uniqueness | Confirmed duplicate rows - auto-matched by rules (%) | 22.84 |
| Uniqueness | Open stewardship review rows - suspected duplicates (count) | 111 |
| Uniqueness | Total duplicate-person flag rate (confirmed + open review, %) | 25.06 |
| Uniqueness | Exact duplicate rows (all fields except ID, %) | 14.88 |
| Uniqueness | Unique customer_id (%) | 100.0 |
| Completeness | Present values: full_name (%) | 100.0 |
| Completeness | Present values: phone_number (%) | 90.28 |
| Completeness | Present values: email (%) | 93.6 |
| Completeness | Present values: district (%) | 99.76 |
| Completeness | Present values: registration_date (%) | 94.7 |
| Completeness | Present values: gender (%) | 84.56 |
| Completeness | Cell-level completeness across 6 fields (%) | 93.82 |
| Consistency | Distinct phone format variants (count) | 6 |
| Consistency | Records in dominant phone format (%) | 25.7 |
| Consistency | Distinct date format variants (count) | 3 |
| Consistency | Records in ISO-8601 date format (%) | 54.4 |
| Consistency | Distinct raw district labels (count) | 127 |
| Consistency | Distinct gender label variants (count) | 4 |
| Timeliness | Registration date parseable (%) | 94.7 |
| Timeliness | Dates not in the future (%) | 94.7 |
| Timeliness | Records registered <= 4 years ago (%) | 59.62 |
| Accuracy | District stored as official name (no repair needed, %) | 89.8 |
| Accuracy | Phone is plausible Ugandan MSISDN (%) | 90.28 |
| Accuracy | Gender stored in canonical domain {M,F} (%) | 32.88 |
| Validity | Phone already in E.164 (+2567XXXXXXXX) (%) | 22.76 |
| Validity | Email RFC-5322 lite conforming (or null) (%) | 92.94 |
| Validity | Registration date conforming (%) | 94.7 |
| Validity | Gender value conforming (%) | 84.56 |
| Validity | Composite record validity - all 4 rules pass (%) | 17.3 |

### SRG_Products - BEFORE cleansing

| Dimension | Metric | Value |
|---|---|---|
| Uniqueness | Rows sharing a duplicate SKU (count) | 141 |
| Uniqueness | product_id unique and non-null (%) | 97.0 |
| Uniqueness | Exact duplicate rows (all fields except ID, %) | 3.0 |
| Completeness | Present values: sku (%) | 97.0 |
| Completeness | Present values: product_name (%) | 97.0 |
| Completeness | Present values: category (%) | 98.17 |
| Completeness | Present values: unit_of_measure (%) | 97.0 |
| Completeness | Present values: cost_ugx (%) | 97.0 |
| Completeness | Present values: selling_price_ugx (%) | 97.0 |
| Completeness | Cell-level completeness across 6 fields (%) | 97.19 |
| Consistency | Distinct unit-of-measure labels (count) | 18 |
| Consistency | Distinct category labels (count) | 30 |
| Consistency | Price stored as free-text currency string (%) | 3.83 |
| Consistency | SKUs mapped to >1 product name (count) | 69 |
| Timeliness | Refreshable via key: product_id AND SKU present (%) [proxy - source has no last_updated column] | 97.0 |
| Accuracy | Selling price below cost - margin anomaly (%) | 5.17 |
| Accuracy | Prices parseable to numeric (%) | 97.0 |
| Accuracy | Cost and price non-negative (%) | 97.0 |
| Validity | Unit of measure in {kg, pcs, liters} (%) | 15.33 |
| Validity | Category in master list (%) | 22.0 |
| Validity | SKU matches ^[A-Z0-9]{3,10}$ (%) | 97.0 |
| Validity | Composite product validity - all rules pass (%) | 3.25 |

---

## Think-deeper answer (Task B2): why did each phone pattern form, and what did the cleaning decision reveal about data ownership?

(The task's "18% of phones are malformed" is illustrative; SRG's measured equivalent is worse — **77.24% of present phone numbers are not E.164-conforming, only 25.7% share one dominant format, 6 format variants coexist, and 9.72% are absent entirely.** Each pattern has a different upstream cause, and therefore a different owner.)

**1. Absent phones (9.72%) — a capture design that rewarded speed, not identity.** The POS signup screen makes the phone field optional because store queues must move: during the hours-daily connectivity drops, staff skip optional fields to keep selling. That is not carelessness, it is an incentive working exactly as designed — and no KPI anywhere said "records with a reachable phone." Completeness was nobody's job, so completeness decayed.

**2. Six format variants, 22.76% in E.164 — three channels, three private conventions, zero standards.** The loyalty app emits locally formatted numbers through a masked input; the CRM accepts free text, so agents typed `+256 772 369 9332`, `07723699332` and `0772 3699332` side by side; supplier and Excel imports pasted whatever the source held. A format is a standard, and a standard is an owned artifact — SRG had no phone standard (no input mask, no entry validation, no reference rule), so each system expressed "correct" differently and the ambiguity surfaced only when records met during dedupe. The cleaning decision — normalize to E.164 both at capture and over the back-catalog — looked like a regex, but it forced the governance question nobody had answered: *who owns the canonical form?* Resolution: the customer-domain steward (CRM/Marketing Officer) owns the standard, enforced technically as VR-001 at form and ETL boundaries; IT owns the plumbing, business owns the meaning. That split is what `docs/A2_governance_charter.md` later formalises.

**3. The same phone on many `customer_id`s (feeding the 22.84% duplicate rate) — offline capture with no identity reconciliation.** Outage-period sales create local records on the store box; when connectivity returns the customer also registers through the app or e-commerce, and a second identity is born. No golden-key reconciliation existed across channels, stores were measured on queue time, and the loyalty team — not the stores — discovered points landing on the wrong member. The discoverer was not the owner, and identity resolution was left to no one.

**4. What the cleaning itself revealed.** Technically the phone fix was the easiest in the module — a variant map and a normaliser. The hard part was that no department would claim the field as theirs until the numbers forced the conversation ("who is accountable for 9,000 unreachable customers?"). And even a phone-led match had limits: 365 homonym pairs were rejected because phones are shared across family members, which is why a stewardship queue (110 pairs) exists at all — ownership is sometimes a *judgement call per record*, not a rule per column. The durable lesson: cleansing without a named owner and capture-time enforcement is a mood, not a state; the defects re-enter at the first busy queue on the first day after go-live. Hence binding entry rules (POL-002), stewardship assignments, and DQC-01 as the alarm that would catch the regression.
