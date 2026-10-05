# Task C3.3 — Executive Dashboard: Specification, Publication & Tufte/Few Self-Critique

**Client:** Savanna Retail Group (SRG) | **Deliverable:** `module6_dashboard/dashboard.html` (self-contained), published at **https://ccosecret.github.io/srg-enterprise-data-management/**
**Prepared by:** Lead Enterprise Data Management Consultant

---

## Task C3 — Analytics, BI & Emerging Technology (C9)

### Purpose & Audience

| Aspect | Specification |
|---|---|
| **Purpose** | Give the SRG Board and metric owners a single, always-current view of trading performance, customer quality and payment integrity — replacing the **11-day monthly reporting cycle** with a view that refreshes whenever the ETL runs. |
| **Primary audience** | Board / Executive Committee (KPI cards, trend, mix); Marketing Officer (new vs returning, churn proxy inputs); Merchandising Manager (category + store table); Finance/Reconciliation Officer (MoMo share, returns %). |
| **Secondary audience** | Data Governance Council (quality-sensitive metrics such as active customers, walk-in share); external auditors (consistent figures with `etl_run_log` and the data dictionary). |
| **Design constraint honoured** | Static, self-contained HTML: no server, no database credentials in the browser, no per-user licence, opens on any device — correct for a firm where several stores are offline for hours daily and power is unreliable (UPS-backed POS). |

---

### Data Source Chain (every number is traceable end-to-end)

| Hop | Artefact | What it contributes |
|---|---|---|
| 1 | `module1_synthetic_data/output/SRG_Customers.csv` (5,000), `SRG_Products.csv` (1,200), `SRG_Sales.csv` (10,000) + `injection_report.json` | Course-provided SRG extract, Jul–Dec 2024, with known defect counts |
| 2 | `module2_data_quality/dq_assessment_cleansing.py` → `module2_data_quality/output/*` | Cleansing: duplicates 22.84% → 0.00% (5,000 → 3,858 golden records), phones 6 → 1 (E.164), districts 127 → 42, UOM 15.33% → 100%, category 22% → 100% |
| 3 | `module3_etl/srg_etl_pipeline.py` | Executed ETL: schema contracts, `etl_quarantine`, idempotent loads, `customer_sk = 0` unknown-member path, MoMo `PENDING_RECON`, advisory lock, `etl_run_log` (self-test 3/3 PASS; 10,000 rows loaded; control total UGX 252,382,814.16) |
| 4 | `module5_warehouse/star_schema_ddl.sql` (`fact_sales` + `dim_customer`/`dim_product`/`dim_store`/`dim_date`/`dim_payment_method`, SCD2) | Conformed model the dashboard queries — 25 documented attributes in `module5_warehouse/data_dictionary.md` |
| 5 | `module3_etl/etl_demo.db` — the executed ETL output holding the star-schema data | **Sole data source read by the build script** |
| 6 | `module6_dashboard/build_dashboard.py` | Queries `etl_demo.db`, computes every KPI/series client-side-precomputable, emits `module6_dashboard/dashboard.html` (Chart.js + vanilla JS, all data embedded as JSON) |
| 7 | `module6_dashboard/dashboard.html` → GitHub Pages | Published at **https://ccosecret.github.io/srg-enterprise-data-management/** |

Headline figures rendered (must match warehouse exactly): 6-month net revenue **UGX 252,382,814** over 10,000 lines; average basket **UGX 25,238**; monthly revenue Jul 43.34M, Aug 45.28M (peak), Sep 43.24M, Oct 43.40M, Nov 41.37M, Dec 35.76M (−13.6% vs Nov); city mix Kampala 36.2%, E-commerce 20.3%, Gulu 16.7%, Mbarara 13.8%, Jinja 13.0%; payment mix mobile money 73.2% (MTN MoMo 48.2%, Airtel MoMo 25.1% rounded), Cash 22.7%, Card 4.1%; returns 500 lines, −UGX 10,224,221 (~4%); walk-in/unattributed 8.0% of lines and 8.7% of revenue.

---

### Interaction Specification

| # | Control / behaviour | Exact behaviour | Scope of effect |
|---|---|---|---|
| 1 | **Filter — month range** | Range selector over Jul–Dec 2024 (start/end month) | All KPI cards, all charts, store/city table recompute on the selected window |
| 2 | **Filter — city** | Multi-select: Kampala, Jinja, Mbarara, Gulu, E-commerce | Restricts store rows, revenue series, category and payment breakdowns, customer counts |
| 3 | **Filter — category** | Multi-select across the 6 conformed categories (Beverages, Grains & Cereals, Snacks, Household, Personal Care, Stationery) | Filters revenue/category charts, KPI cards, table rows |
| 4 | **Filter — payment method** | Multi-select: MTN MoMo, Airtel Money, Cash, Card | Filters KPI cards, revenue line, table; donut highlights selection |
| 5 | **KPI recompute** | Net revenue, transactions, active customers, average basket, MoMo share, returns % — every card recomputes from the filtered fact set (average basket = filtered revenue ÷ filtered line count) | KPI cards only (charts reflect the same filter state) |
| 6 | **Series toggle — line chart** | Toggle between "All cities" and a single city series for monthly revenue | Monthly revenue line chart |
| 7 | **Drill-up (click-through)** | Click a store/city table row → panel expands to the **per-category breakdown of the selected row** (revenue UGX, share of row, line count); click again/again to return to the estate view | Table + category panel only; other charts keep the global filter state |
| 8 | **Sort** | Click column headers on the store/city table (revenue, share, lines, returns) — default sort descending by revenue | Table only |
| 9 | **Chart types** | KPI cards; multi-series line (monthly revenue); horizontal bar (revenue by category); donut (payment-method mix); grouped bars (new vs returning customers per month); sortable store/city table | As named |
| 10 | **Reset** | Single "Reset filters" control restores full-window state on all widgets simultaneously | Whole dashboard |

---

### Visualization Inventory

| Chart | Board question served (C3.1) | Type | Why chosen |
|---|---|---|---|
| KPI cards (net revenue, transactions, active customers, avg basket, MoMo share, returns %) | All (scorecard layer) | Statistic cards | One-number-per-decision framing; no axes to misread; first screen tells a Board the health of the business in 5 seconds |
| Monthly revenue, Jul–Dec 2024, with city series toggle | Q1/Q2 (trend, Dec −13.6% signal) | Multi-series line chart | Time comparison is the job; lines encode trend by position on a common baseline; toggle avoids cluttered 5-line spaghetti |
| Revenue by category | Q2 growth / double-down | Horizontal bar (sorted) | Six categories with long labels — horizontal bars give label room and honest length comparison |
| Payment-method mix | Q4 fraud / reconciliation exposure | Donut with value labels | Part-to-whole with 4 categories only (48.2 / 25.1 / 22.7 / 4.1) — slices remain distinguishable; makes "73.2% mobile money" viscerally one shape |
| New vs returning customers per month | Q1 churn (new-customer collapse 1,272 → 148) | Grouped bars | Side-by-side comparison of two series per month; height on a zero baseline shows the −88% collapse without axis tricks |
| Store / city table | Q3 + Q5 (store flatness ≈4.1% top store, ECOM01 20.3%) | Sortable table with click-through | Precise values for accountability; the only honest way to show 24 near-equal shares; drill-up delivers category traceability |

---

### Publication & Refresh Instructions

```bash
# 1) regenerate the warehouse data (idempotent; safe to re-run)
python3 module3_etl/srg_etl_pipeline.py --self-test     # 3/3 PASS expected
#    -> refreshes module3_etl/etl_demo.db (10,000 rows, control total UGX 252,382,814.16)

# 2) rebuild the dashboard (reads ONLY module3_etl/etl_demo.db)
python3 module6_dashboard/build_dashboard.py
#    -> emits module6_dashboard/dashboard.html (self-contained: Chart.js + vanilla JS + embedded JSON)
#    -> also refreshes index.html at the repo root, which is what the
#       GitHub Pages root URL serves (identical bytes, one build)

# 3) publish
git add module6_dashboard/dashboard.html index.html
git commit -m "dashboard: refresh from etl_demo.db"
git push origin main
#    -> GitHub Pages redeploys automatically; verified at
#       https://ccosecret.github.io/srg-enterprise-data-management/
```

| Aspect | Rule |
|---|---|
| **Refresh cadence** | After every successful ETL run (nightly target); mandatory rebuild after any cleanse re-run, so dashboard figures and `before_after_metrics.md` can never diverge |
| **Freshness evidence** | `etl_run_log` (from `srg_etl_pipeline.py`) is the authoritative run record — the dashboard header displays the run id/date it was built from |
| **Failure behaviour** | If `etl_demo.db` is missing or the control total ≠ UGX 252,382,814.16 for the current dataset, the build script exits non-zero and the previous `dashboard.html` stays live (never publish a half-built page) |
| **Access control** | Public GitHub Pages shows only aggregated figures (Public/Confidential classification per `data_dictionary.md`); no `payment_ref`, no phone, no name — restricted PII never leaves `module4_security` masked views |

---

### Tufte / Few Self-Critique

**Deleted during design (and why it was misleading):**
- **A 24-slice pie of store revenue shares — DELETED.** The estate is deliberately flat: the top physical store is ≈4.1% of revenue and most stores sit in the 2–4% band (ECOM01 20.3%, the rest clustered). Twenty-four slices of 2–4% each are visually indistinguishable — the human eye cannot discriminate angles/areas that similar — and adjacent near-identical wedges invite the reader to rank them, which the chart cannot support. It was replaced by the **sorted horizontal bar table with explicit values** (store/city table, default sort desc), which shows both the precise share and the flatness in one glance, and enables the drill-up to category.

**Rejected pre-build:**
- **3D bars** — perspective distorts bar heights (a rear bar reads shorter at equal value) and adds zero information (chartjunk).
- **Dual-axis chart mixing revenue (UGX tens of millions) and customer counts (hundreds)** — the choice of axis scale silently manufactures any correlation the author wants; it is scale manipulation, not analysis.
- **Gauge charts for single KPIs** — one needle per KPI is a very low data-ink ratio: an arc, ticks and a label to transmit one number; six gauges would occupy a screen that six flat KPI cards serve better.

**Data-ink ratio & decluttering choices applied:**
- Zero-baseline axes on all bars and lines (Tufte's lie factor = 1.0); no truncated revenue axis to dramatise the Dec −13.6% dip — the number is stated in the KPI/tooltip instead.
- No 3-D, no drop shadows, no gradients, no background images, no legend where direct labelling fits (category bar, donut values).
- Gridlines reduced to faint horizontal guides on the line chart only; no chart borders; no redundant y-axis label repeated on every grouped bar.
- Colour: ≤5 semantic colours (mobile money / cash / card / returns / neutral), colour-blind-safe, used consistently across donut, table and KPI cards; the donut and the grouped bars encode one variable by colour and one by position — never colour alone for critical meaning.
- Sorted encodings everywhere a ranking matters (bars descending, table descending by revenue) so the reader's eye does not have to do the sort.
- Every filtered state recomputes rather than greys-out: Few's principle that a control must be truthful about what it is showing.

**Limitations (stated on the page itself):**
- **Sample: 6 months only** (Jul–Dec 2024, 10,000 lines) — seasonality claims (Dec −13.6%) are single-observation; cohort/maturity statements require M12 history.
- **Provenance disclosed:** the dataset is the **course-provided SRG extract** (5,000 customers / 1,200 products / 10,000 sales lines) cleansed and loaded by the committed pipeline — figures are pipeline-faithful, not production-certified, until the live POS/e-commerce/Loyalty feeds replace them.
- **Walk-in caveat:** 8.7% of revenue (8.0% of lines) sits on `customer_sk = 0` (unknown member) — district/catchment and "active customer" figures are therefore floors, not exact values, until the M7 loyalty phone-capture fix.
- **No margin or inventory feeds yet:** revenue ranking ≠ profit ranking, and stock questions (Q3) cannot be answered from this dashboard until the Odoo feed lands (M8). Returns % (~4% of gross) is the only cost-side proxy present.

---

### Think-deeper answer

**Critique the dashboard honestly under Tufte/Few: which chart did you delete, why was it misleading, and what replaced it?**

The deleted chart was the **24-slice pie of store revenue shares**, and it was misleading in three specific ways, not merely "ugly": (1) *discrimination failure* — with shares clustered around 2–4% (top physical store ≈4.1%, ECOM01 the sole outlier at 20.3%), adjacent wedges differ by roughly one to two degrees of arc, below the threshold at which viewers can rank them; (2) *false precision of angle perception* — pie reading requires comparing angles/areas, the perceptual channel with the poorest ratio accuracy, so a viewer "sees" differences that are within rounding noise and a stable estate looks volatile; (3) *composition without comparison* — a pie shows part-of-whole but hides the actual decision variable, which is whether any store materially outperforms its peers (it does not — city revenue shares track store-count shares at indices 0.94–1.04). The replacement — a **sorted horizontal bar table with values** plus click-through to the per-category breakdown — fixes all three: length on a common baseline is the most accurately read encoding, the values are printed (no estimation), sorting makes the flatness self-evident, and the drill-up answers the follow-up question ("why is this row what it is?") without a second page.

The pre-build rejections came from the same discipline: 3D bars distort, the dual-axis revenue/customers chart lets axis scaling invent correlation, and single-KPI gauges spend a whole widget to transmit one number (data-ink ≈ near zero). The residual risk I accept rather than hide: a static, self-contained page has no row-level security — mitigated by publishing only aggregated, non-PII measures and by keeping all Restricted fields behind `module4_security` masked views — and a donut still encodes part-to-whole by angle, which is why the payment mix is also printed as a percentage inside each slice and repeated as the "MoMo share" KPI card. The dashboard is deliberately *boring*: every pixel either carries data or labels data, because a Board under time pressure needs the number, not the chart.
