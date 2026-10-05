### Continuous Data Quality Monitoring Spec (daily automated checks)

| Check ID | Metric | Alert Threshold | Escalation Role | Remediation Script |
|---|---|---|---|---|
| DQC-01 | Customer duplicate-person rate | > 1.0% daily; > 2.0% = P1 incident | CRM Officer -> Data Governance Council (if > 2% for 3 days) | python module2_data_quality/dq_assessment_cleansing.py --stage dedupe && open MDM review queue |
| DQC-02 | Phone E.164 validity rate | < 99.0% | CRM Officer (entry-point fix) / IT Operations Lead (integration fix) | python scripts/dq_check.py --metric phone_validity; re-run standardize_phone() backfill |
| DQC-03 | District resolution rate | < 99.5% or any new unresolved label pattern > 50 rows/day | Data Steward (Marketing Officer) | python module2_data_quality/dq_assessment_cleansing.py --stage profile; add alias to DISTRICT_VARIANTS after steward approval |
| DQC-04 | Core-field completeness (phone, email, district) | phone < 92%; email < 85%; district < 99% | CRM Officer -> Store Manager (data capture at POS) | python scripts/dq_check.py --metric completeness; launch capture-form fix at offending stores |
| DQC-05 | Product UOM / category conformance | < 99.0% (any new row entering non-conforming) | Merchandising Officer | python module2_data_quality/dq_assessment_cleansing.py --stage products; block non-conforming item setup in Odoo |
| DQC-06 | SKU uniqueness violations | > 0 (zero tolerance, nightly) | Merchandising Officer -> IT Manager | SQL: sku_collision_report.sql; quarantine batch and re-issue SKU |
| DQC-07 | ETL quarantine rate | > 0.5% or > 100 rows in one run | IT Operations Lead (2 on-call engineers) | python module3_etl/srg_etl_pipeline.py --inspect-quarantine; fix source, replay from quarantine |
| DQC-08 | Mobile-money payment refs pending > 24h | > 0 daily; > 50 = P1 (revenue integrity) | Finance Reconciliation Officer -> CFO | SQL: reconcile_momo_pending.sql (match provider CSV downloads); auto-close or write off with approval |
| DQC-09 | Future-dated / unparseable registration dates | > 0 per run | CRM Officer | python scripts/dq_check.py --metric dates; block offending registration form |
| DQC-10 | Margin-anomaly products (selling < cost) | > 0 weekly review; > 25 rows = escalate | Pricing Analyst -> Finance Manager | SQL: margin_anomaly_report.sql; business decision - never auto-corrected by ETL |
