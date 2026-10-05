# SRG Before vs After Quality Metrics

### Before vs After Quality Metrics (exact %, computed by the same functions on both states)

| Dataset | Dimension | Metric | Before (%) | After (%) | Delta (pp) | Status |
|---|---|---|---|---|---|---|
| Customers | Uniqueness | Confirmed duplicate rows - auto-matched by rules (%) | 22.84 | 0.0 | -22.84 | Improved |
| Customers | Uniqueness | Open stewardship review rows - suspected duplicates (count) | 111 | 110 | -1 | Improved |
| Customers | Uniqueness | Total duplicate-person flag rate (confirmed + open review, %) | 25.06 | 2.85 | -22.21 | Improved |
| Customers | Uniqueness | Exact duplicate rows (all fields except ID, %) | 14.88 | 0.29 | -14.59 | Improved |
| Customers | Uniqueness | Unique customer_id (%) | 100.0 | 100.0 | 0.0 | No change |
| Customers | Completeness | Present values: full_name (%) | 100.0 | 100.0 | 0.0 | No change |
| Customers | Completeness | Present values: phone_number (%) | 90.28 | 91.96 | 1.68 | Improved |
| Customers | Completeness | Present values: email (%) | 93.6 | 93.26 | -0.34 | Stable (dedupe denominator shift) |
| Customers | Completeness | Present values: district (%) | 99.76 | 99.59 | -0.17 | Stable (dedupe denominator shift) |
| Customers | Completeness | Present values: registration_date (%) | 94.7 | 94.53 | -0.17 | Stable (dedupe denominator shift) |
| Customers | Completeness | Present values: gender (%) | 84.56 | 84.47 | -0.09 | Stable (dedupe denominator shift) |
| Customers | Completeness | Cell-level completeness across 6 fields (%) | 93.82 | 93.97 | 0.15 | Improved |
| Customers | Consistency | Distinct phone format variants (count) | 6 | 1 | -5 | Improved |
| Customers | Consistency | Records in dominant phone format (%) | 25.7 | 91.96 | 66.26 | Improved |
| Customers | Consistency | Distinct date format variants (count) | 3 | 1 | -2 | Improved |
| Customers | Consistency | Records in ISO-8601 date format (%) | 54.4 | 94.53 | 40.13 | Improved |
| Customers | Consistency | Distinct raw district labels (count) | 127 | 42 | -85 | Improved |
| Customers | Consistency | Distinct gender label variants (count) | 4 | 2 | -2 | Improved |
| Customers | Timeliness | Registration date parseable (%) | 94.7 | 94.53 | -0.17 | Stable (dedupe denominator shift) |
| Customers | Timeliness | Dates not in the future (%) | 94.7 | 94.53 | -0.17 | Stable (dedupe denominator shift) |
| Customers | Timeliness | Records registered <= 4 years ago (%) | 59.62 | 59.62 | 0.0 | Monitored (aging) |
| Customers | Accuracy | District stored as official name (no repair needed, %) | 89.8 | 99.4 | 9.6 | Improved |
| Customers | Accuracy | Phone is plausible Ugandan MSISDN (%) | 90.28 | 91.96 | 1.68 | Improved |
| Customers | Accuracy | Gender stored in canonical domain {M,F} (%) | 32.88 | 100.0 | 67.12 | Improved |
| Customers | Validity | Phone already in E.164 (+2567XXXXXXXX) (%) | 22.76 | 91.96 | 69.2 | Improved |
| Customers | Validity | Email RFC-5322 lite conforming (or null) (%) | 92.94 | 93.21 | 0.27 | Improved |
| Customers | Validity | Registration date conforming (%) | 94.7 | 94.53 | -0.17 | Stable (dedupe denominator shift) |
| Customers | Validity | Gender value conforming (%) | 84.56 | 84.47 | -0.09 | Stable (dedupe denominator shift) |
| Customers | Validity | Composite record validity - all 4 rules pass (%) | 17.3 | 68.51 | 51.21 | Improved |
| Products | Uniqueness | Rows sharing a duplicate SKU (count) | 141 | 141 | 0 | Flagged (VR-008 stewardship) |
| Products | Uniqueness | product_id unique and non-null (%) | 97.0 | 100.0 | 3.0 | Improved |
| Products | Uniqueness | Exact duplicate rows (all fields except ID, %) | 3.0 | 0.0 | -3.0 | Improved |
| Products | Completeness | Present values: sku (%) | 97.0 | 100.0 | 3.0 | Improved |
| Products | Completeness | Present values: product_name (%) | 97.0 | 100.0 | 3.0 | Improved |
| Products | Completeness | Present values: category (%) | 98.17 | 100.0 | 1.83 | Improved |
| Products | Completeness | Present values: unit_of_measure (%) | 97.0 | 100.0 | 3.0 | Improved |
| Products | Completeness | Present values: cost_ugx (%) | 97.0 | 100.0 | 3.0 | Improved |
| Products | Completeness | Present values: selling_price_ugx (%) | 97.0 | 100.0 | 3.0 | Improved |
| Products | Completeness | Cell-level completeness across 6 fields (%) | 97.19 | 100.0 | 2.81 | Improved |
| Products | Consistency | Distinct unit-of-measure labels (count) | 18 | 3 | -15 | Improved |
| Products | Consistency | Distinct category labels (count) | 30 | 6 | -24 | Improved |
| Products | Consistency | Price stored as free-text currency string (%) | 3.83 | 0.0 | -3.83 | Improved |
| Products | Consistency | SKUs mapped to >1 product name (count) | 69 | 69 | 0 | Flagged (VR-008 stewardship) |
| Products | Timeliness | Refreshable via key: product_id AND SKU present (%) [proxy - source has no last_updated column] | 97.0 | 100.0 | 3.0 | Improved |
| Products | Accuracy | Selling price below cost - margin anomaly (%) | 5.17 | 5.33 | 0.16 | Flagged (manual, by design) |
| Products | Accuracy | Prices parseable to numeric (%) | 97.0 | 100.0 | 3.0 | Improved |
| Products | Accuracy | Cost and price non-negative (%) | 97.0 | 100.0 | 3.0 | Improved |
| Products | Validity | Unit of measure in {kg, pcs, liters} (%) | 15.33 | 100.0 | 84.67 | Improved |
| Products | Validity | Category in master list (%) | 22.0 | 100.0 | 78.0 | Improved |
| Products | Validity | SKU matches ^[A-Z0-9]{3,10}$ (%) | 97.0 | 100.0 | 3.0 | Improved |
| Products | Validity | Composite product validity - all rules pass (%) | 3.25 | 100.0 | 96.75 | Improved |
