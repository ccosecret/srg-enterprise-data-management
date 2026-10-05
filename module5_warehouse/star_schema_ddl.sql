-- =====================================================================================
-- MODULE 5 - STAR SCHEMA DDL (Task B4.1 / C1) - ANSI SQL (PostgreSQL 15/16)
-- Savanna Retail Group (SRG) Capstone - Enterprise Data Management
-- =====================================================================================
-- Conformed retail warehouse fed by all five transactional sources:
--   Legacy POS (23x MySQL) | E-commerce (PostgreSQL) | Loyalty (cloud CSV)
--   CRM (SaaS export)      | ERP/Odoo (HQ)
--
-- Shape:  fact_sales  +  5 dimensions
--   dim_customer        SCD Type 2 (identity/PII changes need audit history
--                                  for DPPA 2019 / GDPR data-subject requests)
--   dim_product         SCD Type 2 (price/category/UOM changes rewrite history)
--   dim_store           Type 1 + effective attributes (store rarely redefines
--                       history; relocations logged in store_relocation_note)
--   dim_date            standard calendar dimension (UG trading calendar)
--   dim_payment_method  Type 1 conformed lookup (MTN MoMo, Airtel, Card, Cash)
--
-- Naming: fact_*/dim_* tables; *_sk surrogate keys; *_bk business keys;
--         is_current + valid_from/valid_to for SCD2; etl metadata columns.
-- =====================================================================================

SET search_path TO warehouse, public;

-- -------------------------------------------------------------------------------------
-- DIMENSION: dim_customer  (SCD Type 2)
-- -------------------------------------------------------------------------------------
CREATE TABLE warehouse.dim_customer (
    customer_sk        BIGINT       PRIMARY KEY,      -- surrogate key (hash/bk+version)
    customer_bk        TEXT         NOT NULL,         -- business key (CRM/loyalty id)
    full_name          TEXT         NOT NULL,
    phone_e164         TEXT,                          -- Restricted (PII)
    email              TEXT,                          -- Restricted (PII)
    district           TEXT,
    gender             TEXT,
    loyalty_tier       TEXT,                          -- Gold/Silver/Bronze/None
    registration_date  DATE,
    consent_marketing  BOOLEAN      NOT NULL DEFAULT FALSE,   -- DPPA/GDPR lawful basis
    consent_gdpr_eu    BOOLEAN      NOT NULL DEFAULT FALSE,   -- GDPR Art.6 flag
    valid_from         TIMESTAMPTZ  NOT NULL,
    valid_to           TIMESTAMPTZ  NOT NULL DEFAULT '9999-12-31 00:00:00+00',
    is_current         BOOLEAN      NOT NULL DEFAULT TRUE,
    row_hash           TEXT         NOT NULL,         -- change-detection hash
    source_system      TEXT         NOT NULL,         -- POS | ECOM | LOYALTY | CRM
    etl_run_id         TEXT         NOT NULL,
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT now()
);

COMMENT ON TABLE warehouse.dim_customer IS
  'SCD2 customer master: one row per identity version; survivorship applied upstream by MDM golden record';

-- -------------------------------------------------------------------------------------
-- DIMENSION: dim_product  (SCD Type 2)
-- -------------------------------------------------------------------------------------
CREATE TABLE warehouse.dim_product (
    product_sk         BIGINT       PRIMARY KEY,
    product_bk         TEXT         NOT NULL,         -- ERP/POS product_id
    sku                TEXT         NOT NULL,         -- one SKU = one product (VR-008)
    product_name       TEXT         NOT NULL,
    category           TEXT         NOT NULL,         -- canonical 6-class hierarchy
    subcategory        TEXT,
    unit_of_measure    TEXT         NOT NULL CHECK (unit_of_measure IN ('kg','pcs','liters')),
    cost_ugx           NUMERIC(14,2) NOT NULL,
    selling_price_ugx  NUMERIC(14,2) NOT NULL,
    supplier_bk        TEXT,
    valid_from         TIMESTAMPTZ  NOT NULL,
    valid_to           TIMESTAMPTZ  NOT NULL DEFAULT '9999-12-31 00:00:00+00',
    is_current         BOOLEAN      NOT NULL DEFAULT TRUE,
    row_hash           TEXT         NOT NULL,
    source_system      TEXT         NOT NULL,
    etl_run_id         TEXT         NOT NULL,
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT now()
);

COMMENT ON TABLE warehouse.dim_product IS
  'SCD2 product master: price/category/UOM changes versioned so historic facts keep the price valid AT TIME OF SALE';

-- -------------------------------------------------------------------------------------
-- DIMENSION: dim_store
-- -------------------------------------------------------------------------------------
CREATE TABLE warehouse.dim_store (
    store_sk           BIGINT       PRIMARY KEY,
    store_bk           TEXT         NOT NULL UNIQUE,  -- ST01..ST23 / ECOM01
    store_name         TEXT         NOT NULL,
    store_type         TEXT         NOT NULL CHECK (store_type IN ('PHYSICAL','ECOMMERCE','OMNICHANNEL')),
    city               TEXT         NOT NULL,         -- Kampala | Jinja | Mbarara | Gulu
    district           TEXT         NOT NULL,
    region             TEXT,
    opening_date       DATE,
    has_pos_offline_mode BOOLEAN    NOT NULL DEFAULT TRUE,  -- outage reality flag
    store_relocation_note TEXT,
    is_current         BOOLEAN      NOT NULL DEFAULT TRUE,
    etl_run_id         TEXT         NOT NULL
);

-- -------------------------------------------------------------------------------------
-- DIMENSION: dim_date
-- -------------------------------------------------------------------------------------
CREATE TABLE warehouse.dim_date (
    date_sk            INTEGER      PRIMARY KEY,      -- yyyymmdd integer key
    calendar_date      DATE         NOT NULL UNIQUE,
    day_of_week        TEXT         NOT NULL,         -- Monday..Sunday
    day_of_month       SMALLINT     NOT NULL,
    week_of_year       SMALLINT     NOT NULL,
    month              SMALLINT     NOT NULL,
    month_name         TEXT         NOT NULL,
    quarter            SMALLINT     NOT NULL,
    year               SMALLINT     NOT NULL,
    is_weekend         BOOLEAN      NOT NULL,
    is_public_holiday  BOOLEAN      NOT NULL DEFAULT FALSE,  -- Uganda public holidays
    holiday_name       TEXT,
    trading_week       SMALLINT                       -- SRG fiscal week numbering
);

-- -------------------------------------------------------------------------------------
-- DIMENSION: dim_payment_method
-- -------------------------------------------------------------------------------------
CREATE TABLE warehouse.dim_payment_method (
    payment_sk         BIGINT       PRIMARY KEY,
    payment_bk         TEXT         NOT NULL UNIQUE,  -- MTN_MOMO | AIRTEL_MOMO | CARD | CASH
    payment_method     TEXT         NOT NULL,         -- display name
    provider           TEXT,                          -- MTN | Airtel | Bank | -
    channel            TEXT         NOT NULL CHECK (channel IN ('MOBILE_MONEY','CARD','CASH')),
    is_mobile_money    BOOLEAN      NOT NULL,
    settlement_lag_days SMALLINT    NOT NULL DEFAULT 0,  -- MoMo T+1 vs cash T+0
    requires_payment_ref BOOLEAN    NOT NULL DEFAULT FALSE,  -- VR-012
    is_current         BOOLEAN      NOT NULL DEFAULT TRUE
);

-- -------------------------------------------------------------------------------------
-- FACT: fact_sales  (transaction grain: one row per sales line)
-- -------------------------------------------------------------------------------------
CREATE TABLE warehouse.fact_sales (
    sale_sk            BIGINT       PRIMARY KEY,      -- SHA1(transaction_id)
    transaction_id     TEXT         NOT NULL UNIQUE,  -- source txn id (lineage)
    store_sk           BIGINT       NOT NULL,
    customer_sk        BIGINT       NOT NULL,         -- 0 = Unknown / Walk-in
    product_sk         BIGINT       NOT NULL,
    date_sk            INTEGER      NOT NULL,
    payment_sk         BIGINT       NOT NULL,
    quantity           INTEGER      NOT NULL,         -- negative = return
    unit_price_ugx     NUMERIC(14,2) NOT NULL,        -- price at time of sale (SCD2 product)
    gross_amount_ugx   NUMERIC(14,2) NOT NULL,        -- quantity * unit_price
    discount_ugx       NUMERIC(14,2) NOT NULL DEFAULT 0,
    net_amount_ugx     NUMERIC(14,2) NOT NULL,        -- gross - discount
    cost_of_goods_ugx  NUMERIC(14,2),                 -- from product SCD2 cost (margin analysis)
    is_return          BOOLEAN      NOT NULL,
    is_mobile_money    BOOLEAN      NOT NULL,
    payment_ref        TEXT,                          -- Restricted; NULL allowed offline
    reconciliation_status TEXT      NOT NULL DEFAULT 'MATCHED'
        CHECK (reconciliation_status IN ('MATCHED','PENDING','MISSING','NOT_REQUIRED')),
    source_system      TEXT         NOT NULL,         -- POS | ECOM | APP
    event_ts           TIMESTAMPTZ  NOT NULL,         -- business event time
    etl_run_id         TEXT         NOT NULL,
    loaded_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT fk_fact_store    FOREIGN KEY (store_sk)
        REFERENCES warehouse.dim_store (store_sk),
    CONSTRAINT fk_fact_customer FOREIGN KEY (customer_sk)
        REFERENCES warehouse.dim_customer (customer_sk),
    CONSTRAINT fk_fact_product  FOREIGN KEY (product_sk)
        REFERENCES warehouse.dim_product (product_sk),
    CONSTRAINT fk_fact_date     FOREIGN KEY (date_sk)
        REFERENCES warehouse.dim_date (date_sk),
    CONSTRAINT fk_fact_payment  FOREIGN KEY (payment_sk)
        REFERENCES warehouse.dim_payment_method (payment_sk)
);

COMMENT ON TABLE warehouse.fact_sales IS
  'Sales transaction line fact; additive measures in UGX; returns carried as negative quantity';

-- -------------------------------------------------------------------------------------
-- INDEXES (analytics access patterns: time series, store, customer 360)
-- -------------------------------------------------------------------------------------
CREATE INDEX ix_fact_sales_date      ON warehouse.fact_sales (date_sk);
CREATE INDEX ix_fact_sales_store     ON warehouse.fact_sales (store_sk, date_sk);
CREATE INDEX ix_fact_sales_customer  ON warehouse.fact_sales (customer_sk, date_sk);
CREATE INDEX ix_fact_sales_payment   ON warehouse.fact_sales (payment_sk, date_sk);
CREATE INDEX ix_fact_sales_txn       ON warehouse.fact_sales (transaction_id);
CREATE INDEX ix_dim_customer_current ON warehouse.dim_customer (customer_bk)
       WHERE is_current;
CREATE INDEX ix_dim_product_current  ON warehouse.dim_product (product_bk)
       WHERE is_current;
CREATE INDEX ix_dim_product_sku      ON warehouse.dim_product (sku)
       WHERE is_current;

-- -------------------------------------------------------------------------------------
-- SCD2 HELPER VIEW: point-in-time customer for "as-of" reporting
-- -------------------------------------------------------------------------------------
CREATE OR REPLACE VIEW warehouse.v_customer_as_of AS
SELECT *
FROM   warehouse.dim_customer
WHERE  is_current
   OR  (valid_from <= now() AND valid_to > now());

-- =====================================================================================
-- END star_schema_ddl.sql
-- Load order: dim_date -> dim_store -> dim_payment_method
--             -> dim_product (SCD2) -> dim_customer (SCD2) -> fact_sales
-- (dimensions ALWAYS before facts - the RC-5 lesson from etl_diagnosis.md)
-- =====================================================================================
