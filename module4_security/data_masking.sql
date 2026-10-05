-- =====================================================================================
-- MODULE 4 - DYNAMIC DATA MASKING (Task C2.4) - PostgreSQL 15/16
-- Savanna Retail Group (SRG) Capstone - Enterprise Data Management
-- =====================================================================================
-- Masks Restricted fields wherever a non-privileged role reads them:
--   * phone_number  ->  +256-XXX-XX1234   (last 4 digits retained for service calls)
--   * full_name     ->  J*** D**          (initials only)
--   * email         ->  j***@gmail.com    (first char + domain)
--   * payment_ref   ->  MP*********       (type prefix retained for reconciliation)
--
-- Usage:  \i data_masking.sql        (after rbac_postgresql.sql)
-- The Python twin of these functions is executed on live SRG data by
-- data_masking_demo.py (evidence artifact for the portfolio).
-- =====================================================================================

\set ON_ERROR_STOP on
SET search_path TO srg, public;

-- -------------------------------------------------------------------------------------
-- 1. MASKING FUNCTIONS (immutable, work in any view/expression)
-- -------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION srg.mask_phone(p TEXT) RETURNS TEXT
LANGUAGE sql IMMUTABLE AS $$
    SELECT CASE
        WHEN p IS NULL OR btrim(p) = '' THEN NULL
        WHEN length(regexp_replace(p, '\D', '', 'g')) >= 9
            THEN '+256-XXX-XX' || right(regexp_replace(p, '\D', '', 'g'), 4)
        ELSE '+256-XXX-XXXX'
    END;
$$;

CREATE OR REPLACE FUNCTION srg.mask_name(n TEXT) RETURNS TEXT
LANGUAGE sql IMMUTABLE AS $$
    SELECT CASE
        WHEN n IS NULL OR btrim(n) = '' THEN NULL
        WHEN position(' ' in btrim(n)) = 0
            THEN left(btrim(n), 1) || '***'
        ELSE left(split_part(btrim(n), ' ', 1), 1) || '***'
             || ' ' || left(split_part(btrim(n), ' ', 2), 1) || '**'
    END;
$$;

CREATE OR REPLACE FUNCTION srg.mask_email(e TEXT) RETURNS TEXT
LANGUAGE sql IMMUTABLE AS $$
    SELECT CASE
        WHEN e IS NULL OR position('@' in e) = 0 THEN NULL
        ELSE left(e, 1) || '***' || substring(e from position('@' in e))
    END;
$$;

CREATE OR REPLACE FUNCTION srg.mask_payment_ref(r TEXT) RETURNS TEXT
LANGUAGE sql IMMUTABLE AS $$
    SELECT CASE
        WHEN r IS NULL OR btrim(r) = '' THEN NULL
        WHEN length(r) <= 4 THEN '****'
        ELSE left(r, 2) || repeat('*', greatest(length(r) - 4, 1))
             || right(r, 2)
    END;
$$;

-- -------------------------------------------------------------------------------------
-- 2. MASKED VIEW: the ONLY customer surface granted to cashier/manager/analyst
-- -------------------------------------------------------------------------------------
CREATE OR REPLACE VIEW srg.customers_masked AS
SELECT c.customer_id,
       srg.mask_name(c.full_name)      AS full_name_masked,
       srg.mask_phone(c.phone_number)  AS phone_masked,
       srg.mask_email(c.email)         AS email_masked,
       c.district,                     -- geographic district is non-identifying
       c.registration_date,
       c.gender
FROM srg.customers c;

COMMENT ON VIEW srg.customers_masked IS
  'Restricted fields masked for roles without PII privilege (DPPA 2019 / GDPR Art.25 data protection by design)';

-- Masked payment references for reconciliation reporting
CREATE OR REPLACE VIEW srg.sales_masked AS
SELECT sale_id, transaction_id, store_id, customer_id, product_id,
       quantity, unit_price_ugx, net_amount_ugx, payment_method,
       srg.mask_payment_ref(payment_ref) AS payment_ref_masked,
       transaction_ts
FROM srg.sales;

-- -------------------------------------------------------------------------------------
-- 3. GRANTS ON VIEWS (base-table grants are managed in rbac_postgresql.sql)
-- -------------------------------------------------------------------------------------
GRANT SELECT ON srg.customers_masked TO store_cashier, store_manager,
                                        data_analyst, compliance_officer, cdm_admin;
GRANT SELECT ON srg.sales_masked     TO store_cashier, store_manager, data_analyst;

-- Defence in depth: even cdm_admin does not need raw phone/email via views.
-- Raw access stays table-level for compliance_officer (audit) and cdm_admin (steward).

-- =====================================================================================
-- QUICK DEMO (run manually as psql):
--   SET ROLE u_analyst;
--   SELECT * FROM srg.customers_masked LIMIT 3;
--     -> full_name_masked='J*** D**', phone_masked='+256-XXX-XX1234'
--   SELECT phone_number FROM srg.customers LIMIT 1;   -- ERROR: permission denied
--   RESET ROLE;
-- =====================================================================================
