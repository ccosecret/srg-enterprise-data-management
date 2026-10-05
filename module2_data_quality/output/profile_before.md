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
