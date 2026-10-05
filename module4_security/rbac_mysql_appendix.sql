-- =====================================================================================
-- MODULE 4 - RBAC MYSQL APPENDIX (Task C2.3) - MySQL 8.0
-- Savanna Retail Group (SRG) Capstone - Enterprise Data Management
-- =====================================================================================
-- SRG's 23 legacy POS databases are MySQL, so the same privilege model is
-- mirrored here. Differences from PostgreSQL that matter for SRG:
--   * MySQL has NO row-level security pre-8.0 (and 8.0's RLS is enterprise-
--     edition only) -> simulate row scoping with a store-scoped VIEW.
--   * Column-level GRANTs exist -> use them for PII instead of masking views
--     alone; combine both (views for usability, grants for enforcement).
--   * No CREATE ROLE before 5.7 -> assume MySQL 8.0 (GRANT ROLE syntax).
-- =====================================================================================
-- Run: mysql -u root -p < rbac_mysql_appendix.sql

-- -------------------------------------------------------------------------------------
-- 1. ROLES + USERS
-- -------------------------------------------------------------------------------------
-- MySQL's CREATE ROLE has no IF NOT EXISTS clause -> drop-then-create for
-- idempotent re-runs (CREATE USER below does support IF NOT EXISTS).
-- NOTE: sqlfluff's mysql dialect implements neither DROP ROLE nor multi-role
-- CREATE ROLE, hence the inline noqa:PRS (statements are valid MySQL 8.0):
DROP ROLE IF EXISTS 'store_cashier','store_manager','data_analyst','compliance_officer','cdm_admin'; -- noqa:PRS
CREATE ROLE 'store_cashier','store_manager','data_analyst','compliance_officer','cdm_admin'; -- noqa:PRS

CREATE USER IF NOT EXISTS 'u_cashier_james' IDENTIFIED BY 'ChangeMe_Cashier1!';
CREATE USER IF NOT EXISTS 'u_mgr_gulu'      IDENTIFIED BY 'ChangeMe_Manager1!';
CREATE USER IF NOT EXISTS 'u_analyst'       IDENTIFIED BY 'ChangeMe_Analyst1!';
CREATE USER IF NOT EXISTS 'u_compliance'    IDENTIFIED BY 'ChangeMe_Compliance1!';
CREATE USER IF NOT EXISTS 'u_cdm_admin'     IDENTIFIED BY 'ChangeMe_Admin1!';

GRANT 'store_cashier'      TO 'u_cashier_james';
GRANT 'store_manager'      TO 'u_mgr_gulu';
GRANT 'data_analyst'       TO 'u_analyst';
GRANT 'compliance_officer' TO 'u_compliance';
GRANT 'cdm_admin'          TO 'u_cdm_admin';

-- -------------------------------------------------------------------------------------
-- 2. DEFAULT DENY
-- -------------------------------------------------------------------------------------
REVOKE ALL PRIVILEGES, GRANT OPTION FROM 'store_cashier','store_manager',
    'data_analyst','compliance_officer','cdm_admin';

-- -------------------------------------------------------------------------------------
-- 3. GRANT MATRIX (same semantics as the PostgreSQL script)
-- -------------------------------------------------------------------------------------
-- store_cashier --------------------------------------------------------------
GRANT SELECT, INSERT ON srg.sales TO 'store_cashier';
GRANT SELECT ON srg.products TO 'store_cashier';
-- customers: NO table access; masked VIEW only
GRANT SELECT ON srg.customers_masked TO 'store_cashier';
-- financial_reports: explicitly nothing (tested by rbac_test.sql equivalent)

-- store_manager --------------------------------------------------------------
GRANT SELECT, INSERT, UPDATE ON srg.sales TO 'store_manager';
GRANT SELECT ON srg.products TO 'store_manager';
GRANT SELECT ON srg.customers_masked TO 'store_manager';
GRANT SELECT ON srg.financial_reports_view_store TO 'store_manager';

-- data_analyst ---------------------------------------------------------------
GRANT SELECT ON srg.sales, srg.products TO 'data_analyst';
GRANT SELECT ON srg.customers_masked TO 'data_analyst';
-- column-level: aggregate finance columns only (no payroll)
GRANT SELECT (report_id, report_month, store_id, gross_sales_ugx,
              cogs_ugx, gross_margin_ugx)
       ON srg.financial_reports TO 'data_analyst';

-- compliance_officer ---------------------------------------------------------
GRANT SELECT ON srg.sales, srg.customers, srg.products,
                srg.financial_reports TO 'compliance_officer';
-- no INSERT/UPDATE/DELETE: MySQL revokes are implicit by absence of grants

-- cdm_admin ------------------------------------------------------------------
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP
       ON srg.* TO 'cdm_admin';

-- -------------------------------------------------------------------------------------
-- 4. ROW SCOPING (no RLS in MySQL Community): store-scoped views
-- -------------------------------------------------------------------------------------
-- The POS app sets:  SET @app_current_store = 'ST01';
CREATE OR REPLACE VIEW srg.sales_store_v AS
SELECT * FROM srg.sales
WHERE store_id = @app_current_store;

CREATE OR REPLACE VIEW srg.financial_reports_view_store AS
SELECT report_id, report_month, store_id, gross_sales_ugx, cogs_ugx,
       gross_margin_ugx            -- payroll_ugx intentionally excluded
FROM srg.financial_reports
WHERE store_id = @app_current_store;

-- Cashier/manager are granted on the VIEW, not the base table:
REVOKE SELECT ON srg.sales FROM 'store_cashier','store_manager';
GRANT SELECT, INSERT ON srg.sales_store_v TO 'store_cashier';
GRANT SELECT, INSERT, UPDATE ON srg.sales_store_v TO 'store_manager';

-- -------------------------------------------------------------------------------------
-- 5. MASKING VIEW (MySQL equivalents of the pgSQL functions)
-- -------------------------------------------------------------------------------------
-- CREATE FUNCTION-free masking with expression views:
CREATE OR REPLACE VIEW srg.customers_masked AS
SELECT customer_id,
       CONCAT(LEFT(full_name,1), '*** ',
              LEFT(SUBSTRING_INDEX(full_name,' ',-1),1), '**')  AS full_name_masked,
       CONCAT('+256-XXX-XX', RIGHT(REGEXP_REPLACE(phone_number,'[^0-9]',''),4))
                                                                 AS phone_masked,
       CONCAT(LEFT(email,1), '***', SUBSTRING(email, LOCATE('@',email)))
                                                                 AS email_masked,
       district, registration_date, gender
FROM srg.customers;

-- =====================================================================================
-- EQUVALENCE NOTE: run rbac_test.sql against MySQL by replacing the DO-block
-- harness with a mysqltest suite; the privilege matrix is identical by design.
-- =====================================================================================
