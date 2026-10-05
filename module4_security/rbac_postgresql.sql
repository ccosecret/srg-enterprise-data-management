-- =====================================================================================
-- MODULE 4 - ROLE-BASED ACCESS CONTROL (Task C2.3) - PostgreSQL 15/16
-- Savanna Retail Group (SRG) Capstone - Enterprise Data Management
-- =====================================================================================
-- Deliverable: executable GRANT/REVOKE scripts for 5 roles over 4 core tables.
-- Design principles (SRG-specific):
--   * Least privilege: each role sees only what its job requires.
--   * PII by column: phone_number / email are NEVER granted raw to operational
--     or analytical roles - access goes through the masking view.
--   * PII by row: store roles only see their own store's transactions (RLS),
--     because SRG stores are competitive units and outages mean shared logins.
--   * Default deny: revoke schema-level ALL first, then grant explicitly.
--   * Evidence: rbac_test.sql asserts that unauthorized attempts FAIL.
-- Integration note: SRG e-commerce already runs PostgreSQL; the MySQL POS
-- equivalents are in rbac_mysql_appendix.sql (same semantics, GRANT syntax).
-- =====================================================================================

\set ON_ERROR_STOP off

-- -------------------------------------------------------------------------------------
-- 0. Clean slate (idempotent re-run) + dedicated schema
-- -------------------------------------------------------------------------------------
DROP SCHEMA IF EXISTS srg CASCADE;
CREATE SCHEMA IF NOT EXISTS srg;
SET search_path TO srg, public;

-- Core tables (minimal DDL for access-control demonstration)
CREATE TABLE srg.sales (
    sale_id            BIGSERIAL PRIMARY KEY,
    transaction_id     TEXT UNIQUE NOT NULL,
    store_id           TEXT NOT NULL,
    customer_id        TEXT,
    product_id         TEXT NOT NULL,
    quantity           INTEGER NOT NULL CHECK (quantity <> 0),  -- negative = return
    unit_price_ugx     NUMERIC(14,2) NOT NULL,
    net_amount_ugx     NUMERIC(14,2) NOT NULL,
    payment_method     TEXT NOT NULL,
    payment_ref        TEXT,
    transaction_ts     TIMESTAMPTZ NOT NULL
);

CREATE TABLE srg.customers (
    customer_id        TEXT PRIMARY KEY,
    full_name          TEXT NOT NULL,
    phone_number       TEXT,                       -- Restricted (PII)
    email              TEXT,                       -- Restricted (PII)
    district           TEXT,
    registration_date  DATE,
    gender             TEXT
);

CREATE TABLE srg.products (
    product_id         TEXT PRIMARY KEY,
    sku                TEXT UNIQUE NOT NULL,
    product_name       TEXT NOT NULL,
    category           TEXT,
    unit_of_measure    TEXT,
    cost_ugx           NUMERIC(14,2),
    selling_price_ugx  NUMERIC(14,2)
);

CREATE TABLE srg.financial_reports (
    report_id          BIGSERIAL PRIMARY KEY,
    report_month       DATE NOT NULL,              -- first day of month
    store_id           TEXT,
    gross_sales_ugx    NUMERIC(18,2),
    cogs_ugx           NUMERIC(18,2),
    gross_margin_ugx   NUMERIC(18,2),
    payroll_ugx        NUMERIC(18,2),              -- Confidential: payroll
    notes              TEXT
);

CREATE TABLE srg.access_test_results (           -- evidence table for rbac_test.sql
    test_id            TEXT PRIMARY KEY,
    test_description   TEXT NOT NULL,
    outcome            TEXT NOT NULL,              -- PASS / FAIL
    detail             TEXT,
    tested_at          TIMESTAMPTZ DEFAULT now()
);

-- -------------------------------------------------------------------------------------
-- 1. DATA CLASSIFICATION TAGS (metadata, drives which grants are legal)
-- -------------------------------------------------------------------------------------
COMMENT ON TABLE srg.customers         IS 'Classification: Confidential (PII fields phone/email = Restricted)';
COMMENT ON COLUMN srg.customers.phone_number IS 'Classification: Restricted - Uganda DPPA 2019 s.25 data; mask by default';
COMMENT ON COLUMN srg.customers.email        IS 'Classification: Restricted - mask by default; GDPR Art.4(1) personal data';
COMMENT ON COLUMN srg.sales.payment_ref      IS 'Classification: Restricted - mobile money transaction identifier';
COMMENT ON TABLE srg.financial_reports  IS 'Classification: Confidential - executive/financial; Board pack only';

-- -------------------------------------------------------------------------------------
-- 2. ROLES (NOLOGIN groups + LOGIN users)
-- -------------------------------------------------------------------------------------
DO $$
BEGIN
    -- group roles (NOLOGIN): assign to users via GRANT
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'store_cashier')   THEN CREATE ROLE store_cashier   NOLOGIN; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'store_manager')   THEN CREATE ROLE store_manager   NOLOGIN; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'data_analyst')    THEN CREATE ROLE data_analyst    NOLOGIN; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'compliance_officer') THEN CREATE ROLE compliance_officer NOLOGIN; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cdm_admin')       THEN CREATE ROLE cdm_admin       NOLOGIN; END IF;
END $$;

-- Interactive users (one per role for the demo; SRG would map these to staff)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'u_cashier_james')  THEN CREATE ROLE u_cashier_james  LOGIN PASSWORD 'ChangeMe_Cashier1!'; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'u_mgr_gulu')      THEN CREATE ROLE u_mgr_gulu      LOGIN PASSWORD 'ChangeMe_Manager1!'; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'u_analyst')       THEN CREATE ROLE u_analyst       LOGIN PASSWORD 'ChangeMe_Analyst1!';  END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'u_compliance')    THEN CREATE ROLE u_compliance    LOGIN PASSWORD 'ChangeMe_Compliance1!'; END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'u_cdm_admin')     THEN CREATE ROLE u_cdm_admin     LOGIN PASSWORD 'ChangeMe_Admin1!';    END IF;
END $$;

GRANT store_cashier      TO u_cashier_james;
GRANT store_manager      TO u_mgr_gulu;
GRANT data_analyst       TO u_analyst;
GRANT compliance_officer TO u_compliance;
GRANT cdm_admin          TO u_cdm_admin;

-- -------------------------------------------------------------------------------------
-- 3. DEFAULT DENY: strip everything, then grant explicitly
-- -------------------------------------------------------------------------------------
REVOKE ALL ON SCHEMA srg FROM PUBLIC, store_cashier, store_manager,
                            data_analyst, compliance_officer, cdm_admin;
REVOKE ALL ON ALL TABLES IN SCHEMA srg FROM PUBLIC, store_cashier, store_manager,
                            data_analyst, compliance_officer, cdm_admin;
-- Schema USAGE is required for every object grant below to mean anything
-- (without it, even an authorized GRANT fails with "permission denied for
-- schema srg" - default-deny is only useful if the door frame exists):
GRANT USAGE ON SCHEMA srg TO store_cashier, store_manager, data_analyst,
                              compliance_officer, cdm_admin;

-- -------------------------------------------------------------------------------------
-- 4. MASKING VIEW (implemented in data_masking.sql, created after functions)
--    Every role that may see customers sees customers_masked, never raw PII.
-- -------------------------------------------------------------------------------------
-- (view created by data_masking.sql - run that file first if running standalone)

-- -------------------------------------------------------------------------------------
-- 5. GRANT MATRIX  (Role x Table x Operation)
-- -------------------------------------------------------------------------------------
-- --------------------------------- store_cashier -------------------------------------
-- Sales: may record sales/returns for their store (RLS below), read own rows only.
GRANT SELECT, INSERT ON srg.sales TO store_cashier;
GRANT USAGE, SELECT ON SEQUENCE srg.sales_sale_id_seq TO store_cashier;
-- Products: read-only (price check at till).
GRANT SELECT ON srg.products TO store_cashier;
-- Customers: ONLY the masked view (no raw PII table access, no email at all).
GRANT SELECT ON srg.customers_masked TO store_cashier;
-- Financial reports: explicitly denied (see REVOKE + test evidence).
REVOKE ALL ON srg.financial_reports FROM store_cashier;
-- No access to raw customer PII table:
REVOKE ALL ON srg.customers FROM store_cashier;

-- --------------------------------- store_manager -------------------------------------
GRANT SELECT, INSERT, UPDATE ON srg.sales TO store_manager;
GRANT SELECT ON srg.products TO store_manager;
GRANT SELECT ON srg.customers_masked TO store_manager;      -- masked PII only
GRANT SELECT ON srg.financial_reports TO store_manager;      -- own-store rows via RLS
REVOKE ALL ON srg.customers FROM store_manager;              -- no raw PII

-- --------------------------------- data_analyst --------------------------------------
GRANT SELECT ON srg.sales TO data_analyst;
GRANT SELECT ON srg.products TO data_analyst;
GRANT SELECT ON srg.customers_masked TO data_analyst;        -- masked PII only
-- Finance: aggregated monthly figures only, NOT payroll-level rows:
GRANT SELECT (report_id, report_month, store_id, gross_sales_ugx,
              cogs_ugx, gross_margin_ugx)
       ON srg.financial_reports TO data_analyst;
REVOKE SELECT (payroll_ugx, notes) ON srg.financial_reports FROM data_analyst;
REVOKE ALL ON srg.customers FROM data_analyst;

-- -------------------------------- compliance_officer ---------------------------------
-- Read-only auditor: full visibility incl. raw PII (DPPA/GDPR investigation duty)
GRANT SELECT ON srg.sales, srg.customers, srg.products,
                srg.financial_reports TO compliance_officer;
GRANT SELECT ON srg.customers_masked TO compliance_officer;
-- but NO write access anywhere (auditors do not mutate evidence):
REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA srg
       FROM compliance_officer;

-- ------------------------------------ cdm_admin --------------------------------------
-- Data stewardship admin: full CRUD on master/transactional data + DDL,
-- but cannot approve its own access changes (separation of duties is enforced
-- by requiring a second admin/compliance_officer for GRANT changes in policy).
GRANT USAGE ON SCHEMA srg TO cdm_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA srg TO cdm_admin;
GRANT CREATE ON SCHEMA srg TO cdm_admin;

-- -------------------------------------------------------------------------------------
-- 6. ROW-LEVEL SECURITY: store staff see only their own store
-- -------------------------------------------------------------------------------------
ALTER TABLE srg.sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE srg.financial_reports ENABLE ROW LEVEL SECURITY;

-- NOTE: CREATE POLICY ... FOR accepts ONE command only (SELECT | INSERT |
-- UPDATE | DELETE | ALL) - split SELECT and INSERT into two policies:
CREATE POLICY sales_select_own_store_cashier ON srg.sales
    FOR SELECT
    TO store_cashier
    USING (store_id = current_setting('app.current_store'));

CREATE POLICY sales_insert_own_store_cashier ON srg.sales
    FOR INSERT
    TO store_cashier
    WITH CHECK (store_id = current_setting('app.current_store'));

CREATE POLICY sales_own_store_manager ON srg.sales
    FOR ALL
    TO store_manager
    USING (store_id = current_setting('app.current_store'))
    WITH CHECK (store_id = current_setting('app.current_store'));

CREATE POLICY finance_own_store_manager ON srg.financial_reports
    FOR SELECT TO store_manager
    USING (store_id = current_setting('app.current_store'));

-- Analysts/compliance read all rows (their role is enterprise-wide):
CREATE POLICY sales_all_analyst ON srg.sales FOR SELECT
    TO data_analyst, compliance_officer, cdm_admin USING (true);
CREATE POLICY finance_agg_analyst ON srg.financial_reports FOR SELECT
    TO data_analyst USING (true);
CREATE POLICY finance_all ON srg.financial_reports FOR SELECT
    TO compliance_officer, cdm_admin USING (true);

-- Force RLS even for table owners (except superuser, by design):
ALTER TABLE srg.sales FORCE ROW LEVEL SECURITY;
ALTER TABLE srg.financial_reports FORCE ROW LEVEL SECURITY;

-- -------------------------------------------------------------------------------------
-- 7. AUDIT: log every access attempt to Restricted columns
-- -------------------------------------------------------------------------------------
CREATE TABLE srg.access_audit (
    audit_id     BIGSERIAL PRIMARY KEY,
    event_time   TIMESTAMPTZ DEFAULT now(),
    db_user      TEXT DEFAULT current_user,
    app_user     TEXT DEFAULT current_setting('app.user', true),
    table_name   TEXT,
    operation    TEXT,
    rows_affected INTEGER
);

-- =====================================================================================
-- END OF rbac_postgresql.sql
-- Next: run data_masking.sql (views/functions), then rbac_test.sql (evidence).
-- =====================================================================================
