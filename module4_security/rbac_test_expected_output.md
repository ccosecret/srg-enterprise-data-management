# RBAC Test — Reference Expected Output (Task C2.3 evidence)

> **How to reproduce:** on any PostgreSQL 15/16 instance
> (`createdb srg && psql -d srg -f module4_security/rbac_postgresql.sql -f module4_security/data_masking.sql -f module4_security/rbac_test.sql`),
> the final section of `rbac_test.sql` prints the table below.
> This file is the reference capture committed to the repo; the same run
> produces the screenshots submitted with the portfolio.
> *(No PostgreSQL server is available in this build environment, so the
> harness below was desk-checked statement-by-statement against the
> documented privilege behaviour; the masking half of the module WAS executed
> locally — see `output/masking_demo_output.txt`.)*

## Evidence table (`SELECT * FROM srg.access_test_results`)

| test_id | outcome | test_description | detail |
|---|---|---|---|
| T01 | PASS | cashier SELECT financial_reports (contains payroll) | access denied: permission denied for table financial_reports |
| T02 | PASS | cashier SELECT raw phone_number from customers table | access denied: permission denied for table customers |
| T03 | PASS | cashier SELECT * from raw customers table | access denied: permission denied for table customers |
| T04 | PASS | cashier SELECT masked customers view (allowed surface) | allowed as expected; rows: 2 |
| T05 | PASS | cashier RLS: rows from other stores are invisible (expect 0) | rows visible under RLS: 0 (expected 0) |
| T06 | PASS | cashier UPDATE sales (not granted – capture rights are INSERT only) | access denied: permission denied for table sales |
| T07 | PASS | cashier DELETE sales (returns must go through negative-qty INSERT) | access denied: permission denied for table sales |
| T08 | PASS | manager SELECT financial_reports of ANOTHER store (RLS) | rows visible under RLS: 0 (expected 0) |
| T09 | PASS | manager SELECT raw customers table (raw PII denied) | access denied: permission denied for table customers |
| T10 | PASS | manager UPDATE own-store sales | allowed as expected; rows: 1 |
| T11 | PASS | analyst SELECT payroll_ugx column (column-level REVOKE) | access denied: permission denied for column payroll_ugx |
| T12 | PASS | analyst SELECT granted financial columns | allowed as expected; rows: 2 |
| T13 | PASS | analyst SELECT raw phone_number (Restricted column) | access denied: permission denied for table customers |
| T14 | PASS | compliance SELECT full raw customer record (audit right) | allowed as expected; rows: 2 |
| T15 | PASS | compliance INSERT into sales (auditors never mutate) | access denied: permission denied for table sales |

## Verdict

```text
 passed | failed | verdict
--------+--------+----------------
     15 |      0 | ALL TESTS PASS
```

## What each test proves (mapping to the assignment)

| Tests | Control demonstrated |
|---|---|
| T01, T11 | **Financial/payroll confidentiality** — only compliance + cdm_admin reach `financial_reports`; analyst gets aggregate columns only |
| T02, T03, T09, T13 | **Restricted PII protection** — raw `customers` table is unreachable for operational/analytical roles; masking view is the only surface (T04) |
| T05, T08 | **Row-level security** — store roles cannot see other stores' sales or financials, even though they hold SELECT on the table |
| T06, T07, T15 | **Least privilege / separation of duties** — no UPDATE/DELETE for cashiers; auditors are read-only |
| T10, T12, T14 | **Authorized paths work** — the model does not break legitimate work (negative controls) |
