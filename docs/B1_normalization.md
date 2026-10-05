# Task B1 — Architecture & Data Modeling (C3)

**Client:** Savanna Retail Group (SRG) — Kampala, Uganda
**Deliverable:** Part B(iii) — Normalization 1NF → 2NF → 3NF of the sales extract; Part B(iv) — justified denormalization with performance-vs-integrity trade-off memo
**Source artefact:** `SRG_sales_extract_unnormalized` (composite extract standing in for the 23 POS + e-commerce + app exports feeding `module3_etl`)

---

## Task B1(iii) — Normalization (C3)

### 1. The unnormalized extract (as received)

`SRG_sales_extract_unnormalized` — four representative rows out of the batch. Note the four defect classes called out in the brief: a **repeating multi-value group** (`items`/`unit_prices` cells), **partial dependencies** (customer/store attributes repeated on every line), **transitive dependencies** (`district → region`; `product → supplier`), and **mixed-formatted fields**.

| tx_id | tx_date | store_id | store_name | store_city | cashier_name | customer_id | customer_name | customer_phone | customer_district | customer_region | items (multi-value) | unit_prices (multi-value) | payment_method | payment_ref | supplier_name | supplier_phone | order_total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TXN90000101 | 12/07/2024 10:42 | ST07 | ST07 Nakawa | Kampala | Okello J. | CUST100088 | Ssempebwa Wasswa | 077-123-4567 | Kampala | Central | COC1001×2; KAK1002×1 | UGX 15,000; UGX 12,500 | MTN MoMo | AM289043610 | Kakira Sugar Industries | +256 41 420 111 | UGX 42,500 |
| TXN90000102 | 2024-07-12 11:05 | ST17 | ST17 Gulu | Gulu | Aciro Betty | CUST100002 | Robert Kyebambe | 256723699332 | Gulu City | Northern | EXE1953×5 | UGX 2,500 | Cash | (empty) | Nile Stationers Ltd | 0752 111 222 | UGX 12,500 |
| TXN90000103 | 07/08/2024 18:33 | ST17 | ST17 Gulu | Gulu | Aciro Betty | (empty) | Walk-in | (empty) | Gulu City | Northern | KAK1002×1; SUC4410×2 | 12500; UGX 8,000 | Airtel Money | (empty) | Kakira Sugar Industries | +256 41 420 111 | UGX 28,500 |
| TXN90000104 | 2024-08-07 09:15 | ECOM01 | SavannaShop | (online) | web_checkout | CUST100002 | Robert Kyebambe | +256 72 369 9332 | Gulu City | Northern | COC1001×1; EXE1953×2 | UGX 7,500; 2,500 | Airtel Money | AUTH83951 | KLE Bottlers Ltd | 031 234 5566 | UGX 12,500 |

**Violations inventory (what is wrong, precisely):**

| Violation | Evidence in the sample | Formal problem |
|---|---|---|
| Repeating group | `items` holds 2–3 `code×qty` pairs per row; `unit_prices` mirrors it | Not atomic — row semantics depend on parsing a delimited string |
| Partial dependency | `customer_name/customer_phone/customer_district`, `store_name/store_city/cashier_name` repeat on every row and depend on `tx_id` **alone**, not on the full line key | Attributes dependent on a proper subset of the candidate key |
| Transitive dependency #1 | `customer_district → customer_region` (Kampala → Central; Gulu City → Northern) — region is reached *through* district | Non-key → non-key dependency: update anomaly (renaming a region touches every sales row) |
| Transitive dependency #2 | `supplier_name/supplier_phone` reached via `items → product → supplier_id → supplier` | Supplier phone change would require editing every historical sales line |
| Mixed formats | `12/07/2024` vs `2024-07-12`; `077-123-4567` vs `256723699332` vs `+256 72 369 9332`; `UGX 15,000` vs `12500` | Attribute domains not enforced (companion defect — resolved by the Module 2 standardizers, not by normalization alone) |
| Derived value stored | `order_total` duplicates Σ(line amounts) | Insert/update anomaly: total drifts when a line is edited (500 return rows make this live) |

### 2. First Normal Form (1NF)

**Action taken:**

1. **Made every value atomic** — split each `items`/`unit_prices` pair into one row per line, assigned `line_no` (1, 2, 3…); `qty` and `unit_price_ugx` become single-valued columns.
2. **Removed the repeating group** — one row per (transaction × product line).
3. **Composite primary key: `PK = (tx_id, line_no)`** — transaction-level attributes (`tx_date`, `store_id`, `customer_id`, `payment_*`) now depend on `tx_id`, a *part* of the key (see 2NF); line-level attributes (`product_id`, `qty`, `unit_price_ugx`) depend on the whole key.
4. Format normalization (`date → ISO-8601`, `phone → E.164`, `price → numeric UGX`) executed in the same pass by the Module 2 standardizers — noted separately because **1NF is structural; format consistency is a data-quality (VR-001/VR-005) concern**, but both are applied before load.

**1NF result (TXN90000101 exploded):**

| tx_id | line_no | tx_date | store_id | customer_id | customer_name | product_id | qty | unit_price_ugx | customer_district | customer_region | supplier_name |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TXN90000101 | 1 | 2024-07-12T10:42 | ST07 | CUST100088 | Ssempebwa Wasswa | COC1001 | 2 | 15000.00 | Kampala | Central | KLE Bottlers Ltd |
| TXN90000101 | 2 | 2024-07-12T10:42 | ST07 | CUST100088 | Ssempebwa Wasswa | KAK1002 | 1 | 12500.00 | Kampala | Central | Kakira Sugar Industries |

**Rationale:** the row now states exactly one fact at one grain — *one product line of one transaction*. Every non-key attribute is single-valued, and `(tx_id, line_no)` uniquely determines all others (no ambiguity from parsing `"COC1001×2; KAK1002×1"`). Note also what the explosion exposes: the UNF extract carried **one** supplier cell for a two-product basket (`Kakira Sugar Industries`) — correct for at most one line. Resolving `product_id` per line (`COC1001 → KLE Bottlers Ltd`, `KAK1002 → Kakira Sugar Industries`) is the first visible step of the transitive dependency removed in 3NF. The grain is now identical to `warehouse.fact_sales` (one row per sales line), so 1NF is the contract between the extract and the warehouse.

### 3. Second Normal Form (2NF)

**Definition applied:** 1NF + no partial dependencies (no attribute may depend on only *part* of the composite key).

**What moved where, and why it violated:**

| Attributes moved out | New relation & key | Dependency that violated 2NF |
|---|---|---|
| `customer_name`, `customer_phone`, `customer_district`, `customer_region` | **Customer** (`customer_id` PK) | Functionally dependent on `customer_id`, which is known from `tx_id` alone → depends on part of the key `(tx_id, line_no)`, not the key itself. Repetition across all lines of TXN90000101 (and every other of Robert Kyebambe's transactions) means a name correction would have to touch every historical row |
| `store_name`, `store_city`, `cashier_name` | **Store** (`store_id` PK; cashier held as `store_id` + shift attribute) | Dependent on `store_id` ⊂ key. ST17's city appearing on 10,000+ sales rows is pure redundancy; a store rename (or the ECOM01 → "SavannaShop" rebrand) becomes a mass update |
| `payment_method`, `payment_ref` | **Payment** (`tx_id` PK, 1:M resolved to payment line keys) | Transaction-level, not line-level; duplicated across lines of the same basket — and with split tender (MoMo + cash) the single column cannot even represent the truth |

**Remains after 2NF:** `tx_id, line_no, tx_date, store_id, cashier?, customer_id, product_id, qty, unit_price_ugx, payment…` — all now dependent on the *whole* key or on non-key attributes (addressed in 3NF).

**Rationale:** 2NF here is not academic tidiness — it is what stops SRG's observed "same customer, differently spelled on line 2" drift, because a customer attribute now exists in exactly one place, keyed by `customer_id`.

### 4. Third Normal Form (3NF)

**Definition applied:** 2NF + no transitive dependencies (non-key attribute must not determine another non-key attribute).

**What moved where, and why it violated:**

| Dependency removed | Move | Violation explained |
|---|---|---|
| `customer_district → customer_region` | District reference table **District** (`district` PK, `region`, canonical name per official Uganda district list) — Customer keeps only `customer_district` FK | Region was *reached through* district. If Gulu were re-assigned in a boundary review, SRG would have to rewrite every sales and customer row carrying "Northern" (127 raw district labels before cleansing proves how volatile this domain is) |
| `product_id → supplier_name`, `supplier_phone` | **Supplier** (`supplier_id` PK) reached via `Product.supplier_id` FK | Transitive through the line: `line → product → supplier`. A supplier's phone changing (or, in the shortage scenario, one SKU dual-sourced) must not require editing historical fact rows |
| `product_id → product_name`, `category`, `unit_of_measure` | **Product** (`product_id` PK, `sku` UK, canonical 6-class category) | Same class: product name corrections ("Kakvra Sugar" typo in the raw file) belong on the product master, not on 10,000 sales lines |
| `order_total` (stored derived) | **Dropped** — computed as Σ `line_net_ugx` at query time | Storing a derived measure is an update anomaly waiting to fire on the 500 return rows |

**Explicit price-snapshot decision (not a violation):** `unit_price_ugx` **stays on the line**. Its determinant is not `product_id` alone but *(product, transaction, time)* — the price *at time of sale*. Deleting it would break margin analysis (the warehouse stores `unit_price_ugx`, `cost_of_goods_ugx` per line against the SCD2 product version valid at `event_ts`; `dim_product` versions price changes via `valid_from/valid_to`). A copied-at-write fact value is a snapshot, not a transitive dependency; its integrity is protected by immutability (facts are never UPDATEd; corrections are new versions/returns).

**3NF result set:** `Customer(customer_id PK)`, `Store(store_id PK)`, `District(district PK)`, `Product(product_id PK)`, `Supplier(supplier_id PK)`, `Payment(payment_id PK, tx_id FK)`, `SalesLine(tx_id, line_no PK, store_id FK, customer_id FK, product_id FK, qty, unit_price_ugx)`.

**Rationale:** every non-key column now depends on *the key, the whole key, and nothing but the key*. Update anomalies are confined to masters (Customer/Product/Supplier/District), which is exactly where SRG's stewardship and validation rules VR-001…VR-012 operate.

### 5. Normalization summary (audit trail)

| Step | Normal form | Operation | Violation class removed | SRG defect it prevents |
|---|---|---|---|---|
| 0 | UNF | — | multi-value cells, mixed formats | `"COC1001×2; KAK1002×1"` parsing errors; `UGX 50,000` vs `50000` COPY aborts (RC-1) |
| 1 | 1NF | Atomic rows, `PK=(tx_id,line_no)` | Repeating groups | Line-level sales can't be counted/aggregated reliably |
| 2 | 2NF | Customer / Store / Payment extracted | Partial dependencies | Customer field drift across a customer's own transactions; store rename mass-update |
| 3 | 3NF | District, Product, Supplier extracted; derived total dropped | Transitive dependencies | Region re-mapping storms; supplier phone change rewriting history; total-vs-lines drift on returns |

---

## Task B1(iv) — Justified Denormalization for Reporting (C3)

### 6. The proposal

**Add two conformed labels to the reporting layer — `category_label` (6-class merchandise hierarchy) and `store_city` — as a nightly-rebuilt denormalized reporting view over the star schema** (optionally materialized into `fact_sales_reporting` for the BI tools):

```sql
-- Reporting projection: labels are DECORATIONS on facts, never the source of truth
CREATE OR REPLACE VIEW bi.v_fact_sales_denorm AS
SELECT f.sale_sk, f.transaction_id, f.event_ts, f.date_sk,
       f.quantity, f.net_amount_ugx, f.cost_of_goods_ugx, f.is_return,
       f.reconciliation_status,
       p.category   AS category_label,      -- from dim_product version valid AT f.event_ts
       p.subcategory,
       s.city       AS store_city,          -- from dim_store (Type 1)
       s.store_bk, s.store_type,
       c.district   AS customer_district    -- masked per RBAC before BI sees PII
FROM   warehouse.fact_sales f
JOIN   warehouse.dim_product p ON p.product_sk = f.product_sk
JOIN   warehouse.dim_store   s ON s.store_sk   = f.store_sk
JOIN   warehouse.dim_customer c ON c.customer_sk = f.customer_sk;
```

(Grain is unchanged — one row per sales line. Only *labels* are carried, reached through the SCD2 versions already stamped on the fact.)

### 7. Trade-off memo: performance vs. integrity

| | Position |
|---|---|
| **To** | Board Reporting; Store Operations; Finance (month-end) |
| **From** | Lead Enterprise Data Management Consultant |
| **Subject** | Denormalizing category/city onto fact rows — performance vs. integrity |

**Benefits (why we do it):**

| # | Benefit | Quantified/observed |
|---|---|---|
| B1 | **Single-scan dashboards for a 4-person team** | A "sales by category × city" card becomes one table scan; no 3-way join gymnastics to maintain when one of the two SQL-capable staff is on leave |
| B2 | **Fewer joins on large facts** | Facts grow ~10k lines/6 months today and into the 10s of millions across 23 stores + e-comm once Odoo/POS history is backfilled; star joins to 3 large SCD2 dims (customer 3,858→180k members) dominate BI latency |
| B3 | **BI-tool simplicity / tool-agnostic performance** | Power BI/Tableau extracts and live connections both prefer flat wide tables; label columns let a business user build a matrix without understanding surrogate keys or `is_current` |
| B4 | **Downstream stability** | Dashboards bind to stable column names (`category_label`), so a dim refactor doesn't break 14 published report pages |

**Costs (what we pay):**

| # | Cost | Reality at SRG |
|---|---|---|
| C1 | **Stale labels** if populated from a non-SCD2 source (e.g., POS current category, not the version valid at sale) | History would silently rewrite: Q3 Beverages sales would appear under the new category after an item re-categorisation |
| C2 | **Storage growth** | ~15–25% wider fact rows; acceptable at 10k–100M rows, but materializing *all* label columns would eventually dwarf measures |
| C3 | **Update anomaly risk returns** | If anyone UPDATEs `category_label` in place, source-of-truth ambiguity follows — the exact anomaly class 3NF removed |
| C4 | **Masking/RBAC interplay** | `customer_district` on a wide table must pass through the masking views (`module4_security/data_masking.sql`) or it becomes a PII leak path into BI |

**Mitigations (how integrity is retained):**

| Cost | Mitigation |
|---|---|
| C1 | Labels are **always derived from the SCD2 dim version valid at `f.event_ts`** (join on `product_sk` stamped at load — never re-joined to `is_current`), so re-categorisation cannot rewrite history |
| C3 | The view (or nightly-materialized table) is **rebuildable by one idempotent job** — it is a *projection*, never edited in place; source of truth stays 3NF/`star_schema_ddl.sql` |
| C2 | Materialize only if the nightly rebuild cost exceeds the query cost; default = view over indexed dims (facts already carry `product_sk`/`store_sk` indexes) |
| C4 | BI connects through the masking views; `customer_district` is coarse-grained (district, not address) and column grants apply as in the RBAC matrix |

**Decision:** *Approved* as a nightly-rebuildable reporting view — **performance is bought with a decoration, not with a copy of the truth.** Revisit if fact volume forces materialization; the mitigations make that a cost decision, not a correctness decision.

### Think-deeper answer

Normalization did not fail to prevent SRG's 23% duplicates — normalization was never the layer where they were created. Every violation above is *inside* one table or *between* a table and its masters; SRG's duplicates arise *between* systems (POS record + e-commerce checkout + loyalty signup + CRM import each create their own `customer_id`), which no 1NF–3NF pass can see, because 3NF constrains structure within a single schema, not identity across schemas. That is precisely why the fix sequence is 3NF → (B2) cleansing → (B3) MDM golden records → (B4) warehouse: the model gives each system a clean shape, the golden record gives the enterprise one person, and only integration makes the two agree. The second lesson is about the price snapshot: keeping `unit_price_ugx` on the line while everything else moved to masters shows that the correct question is never "is it normalized?" but "what is the grain of the fact, and what is the grain of the master?" — a price is neither a duplicate of the product master nor safe inside it: it is a property of the *event*, frozen at write time, exactly as `dim_product`'s `valid_from/valid_to` freezes it for history.
