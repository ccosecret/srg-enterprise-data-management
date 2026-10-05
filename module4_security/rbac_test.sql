-- =====================================================================================
-- MODULE 4 - RBAC TEST SCRIPT (Task C2.3 evidence) - PostgreSQL 15/16
-- Savanna Retail Group (SRG) Capstone - Enterprise Data Management
-- =====================================================================================
-- Proves that unauthorized access attempts FAIL and authorized access WORKS.
--
-- Run order:   psql -f rbac_postgresql.sql
--              psql -f data_masking.sql
--              psql -f rbac_test.sql
--
-- Every test writes a row into srg.access_test_results; the final SELECT is
-- the evidence table to screenshot for the portfolio.
-- Expected result: 15/15 PASS  (see rbac_test_expected_output.md)
-- =====================================================================================
\set ON_ERROR_STOP off
SET search_path TO srg, public;

-- Roles need to record their own test outcomes (evidence table only):
GRANT INSERT, SELECT ON srg.access_test_results
      TO store_cashier, store_manager, data_analyst, compliance_officer, cdm_admin;

-- -------------------------------------------------------------------------------------
-- Test harness: executes a query as the CURRENT (SET ROLE) user and records outcome.
--   p_expect = 'DENY'      -> query MUST raise insufficient_privilege
--   p_expect = 'ALLOW'     -> query must succeed (>=0 rows)
--   p_expect = 'ZERO_ROWS' -> query must succeed with 0 rows (RLS proof)
-- SECURITY INVOKER (default): privileges are evaluated for the impersonated role.
-- -------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION srg.run_priv_test(p_test_id TEXT, p_desc TEXT,
                                             p_sql TEXT, p_expect TEXT)
RETURNS VOID LANGUAGE plpgsql AS $fn$
DECLARE
    v_outcome TEXT;
    v_detail  TEXT := '';
    v_count   BIGINT := 0;
BEGIN
    EXECUTE p_sql;
    GET DIAGNOSTICS v_count = ROW_COUNT;
    IF p_expect = 'DENY' THEN
        v_outcome := 'FAIL';
        v_detail  := 'query SUCCEEDED but was expected to be denied: ' || p_sql;
    ELSIF p_expect = 'ZERO_ROWS' THEN
        v_outcome := CASE WHEN v_count = 0 THEN 'PASS' ELSE 'FAIL' END;
        v_detail  := 'rows visible under RLS: ' || v_count ||
                     ' (expected 0)';
    ELSE
        v_outcome := 'PASS';
        v_detail  := 'allowed as expected; rows: ' || v_count;
    END IF;
EXCEPTION
    WHEN insufficient_privilege THEN
        IF p_expect = 'DENY' THEN
            v_outcome := 'PASS';
            v_detail  := 'access denied: ' || SQLERRM;
        ELSE
            v_outcome := 'FAIL';
            v_detail  := 'unexpected denial: ' || SQLERRM;
        END IF;
    WHEN OTHERS THEN
        v_outcome := 'ERROR';
        v_detail  := SQLERRM;
END;
$fn$;

-- -------------------------------------------------------------------------------------
-- Seed demo data (as superuser)
-- -------------------------------------------------------------------------------------
INSERT INTO srg.customers (customer_id, full_name, phone_number, email,
                           district, registration_date, gender) VALUES
 ('CUST100001', 'John Doe',    '+256771234567', 'john.doe@gmail.com',
  'Kampala', '2023-04-11', 'M'),
 ('CUST100002', 'Mary Nakato', '0772000111',    'mary.nakato@yahoo.com',
  'Gulu',    '2022-09-01', 'F')
ON CONFLICT DO NOTHING;

INSERT INTO srg.products (product_id, sku, product_name, category,
                          unit_of_measure, cost_ugx, selling_price_ugx) VALUES
 ('PRD200001', 'COC1001', 'Coca-Cola 500ml', 'Beverages', 'pcs', 1500, 2000),
 ('PRD200002', 'KAK1002', 'Kakira Sugar 1kg','Grains & Cereals', 'kg', 4500, 5500)
ON CONFLICT DO NOTHING;

INSERT INTO srg.sales (transaction_id, store_id, customer_id, product_id,
                       quantity, unit_price_ugx, net_amount_ugx,
                       payment_method, payment_ref, transaction_ts) VALUES
 ('TXN70000001','ST01','CUST100001','PRD200001',2, 2000, 4000,
  'MTN_MOMO','MP123456789','2025-03-10 10:00+03'),
 ('TXN70000002','ST01',NULL,        'PRD200002',1, 5500, 5500,
  'CASH',   'CASH-1',      '2025-03-10 11:30+03'),
 ('TXN70000003','ST17','CUST100002','PRD200001',3, 2000, 6000,
  'AIRTEL_MOMO','AM987654321','2025-03-10 12:00+03')
ON CONFLICT DO NOTHING;

INSERT INTO srg.financial_reports (report_month, store_id, gross_sales_ugx,
                                   cogs_ugx, gross_margin_ugx, payroll_ugx)
VALUES ('2025-03-01','ST01', 9500000, 6200000, 3300000, 1800000),
       ('2025-03-01','ST17', 7300000, 4900000, 2400000, 1500000);

TRUNCATE srg.access_test_results;

-- =====================================================================================
-- GROUP A: store_cashier  (must NOT read financial_reports or raw customer PII)
-- =====================================================================================
SET ROLE u_cashier_james;
-- Cashier works at ST23 (seeded data lives in ST01/ST17) to prove RLS hides
-- every other store's rows:
SELECT set_config('app.current_store', 'ST23', false);

SELECT srg.run_priv_test('T01',
  'cashier SELECT financial_reports (contains payroll)',
  'SELECT * FROM srg.financial_reports', 'DENY');

SELECT srg.run_priv_test('T02',
  'cashier SELECT raw phone_number from customers table',
  'SELECT phone_number FROM srg.customers', 'DENY');

SELECT srg.run_priv_test('T03',
  'cashier SELECT * from raw customers table',
  'SELECT * FROM srg.customers', 'DENY');

SELECT srg.run_priv_test('T04',
  'cashier SELECT masked customers view (allowed surface)',
  'SELECT * FROM srg.customers_masked', 'ALLOW');

SELECT srg.run_priv_test('T05',
  'cashier RLS: rows from other stores are invisible (expect 0)',
  'SELECT * FROM srg.sales', 'ZERO_ROWS');

SELECT set_config('app.current_store', 'ST01', false);
SELECT srg.run_priv_test('T06',
  'cashier UPDATE sales (not granted - capture rights are INSERT only)',
  'UPDATE srg.sales SET quantity = quantity WHERE store_id = current_setting(''app.current_store'')',
  'DENY');

SELECT srg.run_priv_test('T06',
  'cashier UPDATE sales (not granted - capture rights are INSERT only)',
  'UPDATE srg.sales SET quantity = quantity WHERE store_id = current_setting(''app.current_store'')',
  'DENY');

SELECT srg.run_priv_test('T07',
  'cashier DELETE sales (returns must go through negative-qty INSERT)',
  'DELETE FROM srg.sales', 'DENY');

RESET ROLE;

-- =====================================================================================
-- GROUP B: store_manager  (own-store financials only, no raw PII)
-- =====================================================================================
SET ROLE u_mgr_gulu;
-- Manager of ST07: no financial_reports rows exist for ST07 -> RLS hides all
SELECT set_config('app.current_store', 'ST07', false);

SELECT srg.run_priv_test('T08',
  'manager SELECT financial_reports of ANOTHER store (RLS)',
  'SELECT * FROM srg.financial_reports', 'ZERO_ROWS');

SELECT srg.run_priv_test('T09',
  'manager SELECT raw customers table (raw PII denied)',
  'SELECT * FROM srg.customers', 'DENY');

SELECT set_config('app.current_store', 'ST17', false);
SELECT srg.run_priv_test('T10',
  'manager UPDATE own-store sales',
  'UPDATE srg.sales SET quantity = quantity WHERE transaction_id = ''TXN70000003''',
  'ALLOW');

RESET ROLE;

-- =====================================================================================
-- GROUP C: data_analyst  (aggregates yes, payroll columns and raw PII no)
-- =====================================================================================
SET ROLE u_analyst;

SELECT srg.run_priv_test('T11',
  'analyst SELECT payroll_ugx column (column-level REVOKE)',
  'SELECT payroll_ugx FROM srg.financial_reports', 'DENY');

SELECT srg.run_priv_test('T12',
  'analyst SELECT granted financial columns',
  'SELECT report_month, gross_sales_ugx FROM srg.financial_reports', 'ALLOW');

SELECT srg.run_priv_test('T13',
  'analyst SELECT raw phone_number (Restricted column)',
  'SELECT phone_number FROM srg.customers', 'DENY');

RESET ROLE;

-- =====================================================================================
-- GROUP D: compliance_officer  (read-only everywhere; cannot mutate evidence)
-- =====================================================================================
SET ROLE u_compliance;

SELECT srg.run_priv_test('T14',
  'compliance SELECT full raw customer record (audit right)',
  'SELECT * FROM srg.customers', 'ALLOW');

SELECT srg.run_priv_test('T15',
  'compliance INSERT into sales (auditors never mutate)',
  'INSERT INTO srg.sales (transaction_id, store_id, product_id, quantity,
     unit_price_ugx, net_amount_ugx, payment_method, transaction_ts)
   VALUES (''TXN99999999'',''ST01'',''PRD200001'',1,1,1,''CASH'',
     now())', 'DENY');

RESET ROLE;

-- =====================================================================================
-- EVIDENCE SUMMARY (screenshot this for the portfolio)
-- =====================================================================================
SELECT test_id,
       outcome,
       left(test_description, 62)        AS test_description,
       left(detail, 74)                  AS detail
FROM   srg.access_test_results
ORDER  BY test_id;

SELECT COUNT(*) FILTER (WHERE outcome = 'PASS') AS passed,
       COUNT(*) FILTER (WHERE outcome <> 'PASS') AS failed,
       CASE WHEN COUNT(*) FILTER (WHERE outcome <> 'PASS') = 0
            THEN 'ALL TESTS PASS' ELSE 'TESTS FAILED' END AS verdict
FROM   srg.access_test_results;

-- =====================================================================================
-- Expected: 15 rows, all PASS, verdict 'ALL TESTS PASS'
--           (reference capture: rbac_test_expected_output.md)
-- =====================================================================================
