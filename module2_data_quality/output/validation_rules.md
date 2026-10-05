### Validation Rules Catalog (12 rules: technical + business)

| Rule ID | Field | Type | Condition | Action on Failure | Failure Severity |
|---|---|---|---|---|---|
| VR-001 | customers.phone_number | Technical | phone_number must match ^(\+256|0)7[0-9]{8}$ after input-mask normalization | Block save; re-render input with +256 mask; log to dq_violation_log | High |
| VR-002 | customers.district | Business | district must be a member of the official Uganda district reference list (dropdown only, free text disabled) | Block save; force selection from reference list; steward notified for legacy values | Medium |
| VR-003 | customers.email | Technical | email IS NULL OR email ~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ | Allow save but quarantine from campaign exports; nightly re-validation | Medium |
| VR-004 | customers.customer_id | Technical | PRIMARY KEY: NOT NULL AND unique across operational + MDM stores | Reject insert; abort load batch; page on-call data engineer | Critical |
| VR-005 | customers.registration_date | Business | registration_date <= CURRENT_DATE AND registration_date >= '2000-01-01' AND stored as ISO-8601 | Block save (future/backdated signup); default to CURRENT_DATE on retry | High |
| VR-006 | customers.full_name | Technical | TRIM(full_name) length >= 2 AND full_name ~ '^[A-Za-z .-]+$' | Block save; inline prompt (no single-letter placeholder names) | Medium |
| VR-007 | customers (golden record) | Business | NORMALIZED(phone_number) unique across golden records OR record is in stewardship review queue | Route to MDM matching queue (auto-merge >= 90 score, else steward); block loyalty point posting until resolved | Critical |
| VR-008 | products.sku | Technical | sku NOT NULL AND unique among active products (one SKU = one product name) | Reject insert; raise SKU-collision ticket to merchandising; quarantine batch | Critical |
| VR-009 | products.unit_of_measure | Business | unit_of_measure IN ('kg','pcs','liters') - controlled vocabulary enforced at POS/e-commerce item setup | Block save; show UOM picker; existing violations auto-mapped by cleansing script | High |
| VR-010 | products.category | Business | category IN master merchandise hierarchy (Beverages, Grains & Cereals, Snacks, Household, Personal Care, Stationery) | Block save; enforce hierarchy picker; fuzzy-matched values need steward approval | High |
| VR-011 | products.selling_price_ugx / cost_ugx | Business | selling_price_ugx >= cost_ugx UNLESS promo_flag = TRUE AND promo_approved_by IS NOT NULL | Warn at entry; nightly margin-anomaly report to Pricing Analyst; never auto-correct | Medium |
| VR-012 | sales.payment_ref (Mobile Money) | Business | payment_method IN ('MTN MoMo','Airtel Money') implies payment_ref populated within 24h of capture OR reconciliation_status = 'PENDING' | Permit capture offline (store outages) but quarantine transaction from revenue reports until ref arrives; escalate if aged > 24h | High |
