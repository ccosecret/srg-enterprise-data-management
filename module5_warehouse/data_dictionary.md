# SRG Warehouse Data Dictionary (Task C1.1)

**Scope:** 25 core attributes of the `warehouse` star schema (`star_schema_ddl.sql`)
**Metadata types covered:** business (definition, owner), technical (type, key),
administrative (classification, source system, steward)
**Classification taxonomy:** `Public` (safe for external dashboards/reports) ·
`Confidential` (internal business data; leak harms competitiveness, not a
person directly) · `Restricted` (personal/financial identifiers — Uganda DPPA
2019 s.25 "personal data", GDPR Art.4(1), access only by explicit grant + masking)

| # | Table | Column | Data Type | Business Definition | Classification | Primary Source System |
|---|---|---|---|---|---|---|
| 1 | fact_sales | sale_sk | BIGINT (PK) | Deterministic surrogate key = SHA1(transaction_id); makes loads idempotent | Public | Derived (ETL-generated) |
| 2 | fact_sales | transaction_id | TEXT (UQ) | Source receipt/transaction number printed to the customer; traceability hop back to POS/e-comm | Confidential | Legacy POS / SavannaShop e-commerce |
| 3 | fact_sales | quantity | INTEGER | Units sold on the line; negative values are customer returns (never deleted — returns are facts too) | Confidential | Legacy POS / e-commerce |
| 4 | fact_sales | unit_price_ugx | NUMERIC(14,2) | Price per unit charged at the moment of sale (snapshot from dim_product SCD2 version valid then) | Confidential | Legacy POS / e-commerce |
| 5 | fact_sales | net_amount_ugx | NUMERIC(14,2) | Line revenue after discounts, in UGX; additive KPI base for all sales reporting | Confidential | Derived (quantity × price − discount) |
| 6 | fact_sales | payment_ref | TEXT | Mobile-money/card transaction reference used for provider reconciliation | **Restricted** | MTN MoMo / Airtel Money gateway, bank acquirer |
| 7 | fact_sales | reconciliation_status | TEXT (CHECK) | Whether payment_ref matched a provider statement: MATCHED / PENDING / MISSING / NOT_REQUIRED | Confidential | Derived (ETL + finance reconciliation) |
| 8 | fact_sales | event_ts | TIMESTAMPTZ | Business event time of the sale (not load time) — drives dim_date key and outage-aware reporting | Confidential | Legacy POS / e-commerce / loyalty app |
| 9 | dim_customer | customer_sk | BIGINT (PK) | Surrogate identity version key; 0 = "Unknown / Walk-in Customer" (offline capture path) | Public | Derived (ETL-generated) |
| 10 | dim_customer | customer_bk | TEXT | Source business identifier (CUST…) joining CRM, loyalty and MDM golden record | Confidential | CRM (SaaS) / Loyalty platform |
| 11 | dim_customer | full_name | TEXT | Customer's registered name on the golden record (survivorship: most complete → earliest) | **Restricted** | CRM / Loyalty registration |
| 12 | dim_customer | phone_e164 | TEXT | Mobile number standardized to E.164 `+2567XXXXXXXX`; primary contact + loyalty ID link | **Restricted** | Loyalty app / POS signup / e-commerce checkout |
| 13 | dim_customer | email | TEXT | Email address (lowercased, validated); campaign channel + account login | **Restricted** | E-commerce / CRM |
| 14 | dim_customer | district | TEXT | Official Ugandan district of residence (canonical list); geographic segmentation | Confidential | POS signup (enriched/cleansed by ETL) |
| 15 | dim_customer | loyalty_tier | TEXT | Current loyalty tier (Gold/Silver/Bronze/None) used for segment-growth analysis | Confidential | Loyalty platform |
| 16 | dim_customer | consent_gdpr_eu | BOOLEAN | Lawful basis flag for EU-person data processing (GDPR Art.6 consent/contract) | **Restricted** | CRM consent capture / Loyalty app T&C |
| 17 | dim_product | product_sk | BIGINT (PK) | Surrogate key of the product VERSION valid at sale time (SCD2) | Public | Derived (ETL-generated) |
| 18 | dim_product | sku | TEXT | Stock-keeping unit code shared by POS, e-commerce and supplier files (one SKU = one product, VR-008) | Confidential | ERP/Odoo (master), POS, e-commerce |
| 19 | dim_product | product_name | TEXT | Human-readable product title shown on receipts and dashboards | Public | ERP/Odoo (master) |
| 20 | dim_product | category | TEXT | Canonical merchandise class (Beverages, Grains & Cereals, Snacks, Household, Personal Care, Stationery) | Public | ERP/Odoo (master hierarchy) |
| 21 | dim_product | selling_price_ugx | NUMERIC(14,2) | Current shelf/online price in UGX; SCD2-versioned so history never rewrites | Confidential | ERP/Odoo pricing / e-commerce |
| 22 | dim_store | store_bk | TEXT | Store code ST01–ST23, ECOM01 — conformed across all five sources | Public | ERP/Odoo store master |
| 23 | dim_store | city | TEXT | Trading city (Kampala, Jinja, Mbarara, Gulu) for regional roll-ups | Public | ERP/Odoo store master |
| 24 | dim_date | date_sk | INTEGER | Warehouse calendar key (yyyymmdd) for every fact row; supports week/quarter/holiday slicing | Public | Derived (ETL calendar build) |
| 25 | dim_payment_method | payment_bk | TEXT | Conformed payment code (MTN_MOMO, AIRTEL_MOMO, CARD, CASH) used to join payments to facts | Confidential | Payment gateways / POS tender types |

## Tagging taxonomy applied to the dictionary (Task C1.3)

| Tag class | Values in use | Where enforced |
|---|---|---|
| **Domain** | `sales`, `customer`, `product`, `store`, `payment`, `finance`, `calendar` | Table/column COMMENTs in `star_schema_ddl.sql` |
| **Sensitivity** | `Public`, `Confidential`, `Restricted` | GRANT matrix (`rbac_postgresql.sql`), masking views (`data_masking.sql`), `COMMENT ON` |
| **Quality** | `standardized` (phone/district/UOM), `mastered` (MDM golden record), `derived` (surrogate keys, control totals) | dq status columns from Module 2, `etl_quarantine` outcomes |

## Lineage note (feeds Task C1.2)

`monthly active customers` KPI =
`COUNT(DISTINCT dim_customer.customer_sk)` on `fact_sales` where
`dim_date` in month and `transaction_id` is not a return → sources:
Loyalty app signup + POS capture → cleansed (`dq_assessment_cleansing.py`) →
MDM survivorship (`srg_etl_pipeline.py` golden map) → `dim_customer` SCD2 →
`fact_sales` → dashboard.
