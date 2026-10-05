# SRG Executive Insight Brief — Jul–Dec 2024 Warehouse

**To:** Board of Directors, Savanna Retail Group (SRG)
**From:** Lead Enterprise Data Management Consultant
**Period:** Jul–Dec 2024 warehouse — `fact_sales`, 10,000 lines, net revenue **UGX 252,382,814**, average basket **UGX 25,238**

---

## Task C3 — Analytics, BI & Emerging Technology (C9)

### F1 — GROWTH IS RUNNING ON OLD FUEL

**Evidence.** New known customers per month collapsed from **1,272 (Jul) to 148 (Dec), −88%**, while returning customers grew from 0 to 910–987. Repeat buyers are 72.8% of known buyers (2,447 of 3,362) and drive **90.1% of identified transactions**. December revenue fell **−13.6% month-on-month** (UGX 41.37M → UGX 35.76M), and **858 of 1,237 (69.4%)** November actives bought nothing in December.

**Implication.** The base is contracting beneath a stable repeat core; acquisition has stalled and roughly seven in ten active customers defect each month.

**Action.** Operate the churn/segment lifecycle view already on the published dashboard; launch a reactivation + referral campaign in Kampala and Jinja — **owner: Marketing Officer, by M7**. Publish a monthly new-customer floor — **KPI: ≥ 600 new known customers/month and churn proxy ≤ 50% by M9**. Close the **8.7%** walk-in gap via loyalty phone-capture at the till — **KPI: unattributed revenue < 3% by M9**.

### F2 — CASH IS SITTING IN A RECONCILIATION GAP

**Evidence.** Mobile money carries **73.2% of revenue** (MTN MoMo 48.2%, Airtel Money 25.1% — components rounded), yet **849 of 7,385 MoMo lines (11.5%) still lack payment references (PENDING)**. Line-count proxy: 0.732 × UGX 252,382,814 × 0.115 ≈ **UGX 21.2M of six-month revenue (~UGX 3.54M/month) is unconfirmed**.

**Implication.** Revenue is recognised but not evidenced — a working-capital and audit exposure, and the firm's largest fraud surface (VR-012, DQC-08).

**Action.** Stand up the automated MoMo reconciliation pipeline — the ETL already flags `PENDING_RECON`; this is matching, not new plumbing. Finance sign-off **SLA 48 hours; escalate above 50 pending/day** — **owner: Finance/Reconciliation Officer, by M5. KPI: zero lines pending > 24h by M6; pending share < 0.5% of MoMo lines by M12**.

### F3 — CHANNEL DEMAND OUTPACES STOCK CONTROL

**Evidence.** E-commerce (ECOM01) already contributes **20.3% of revenue from a single node** — about **5.9× an average physical store's 3.47% share** — while the estate carries **8.4% unexplained book-vs-physical stock variance** and simultaneous stock-outs in high-demand stores and overstock in slow ones. Returns ran at 500 lines, −UGX 10,224,221 (~4% of gross).

**Implication.** We cannot promise availability where demand actually is, and every inventory-led decision (reorder, expansion, promo) inherits an 8.4% measurement error.

**Action.** Unify stock visibility — **footfall + near-real-time POS pilot in 3 stores, M10–M12**; convene a variance reconciliation task force with Odoo stock feeds; apply safety-stock reorder rules to top-SKU/high-velocity store cells — **owner: Merchandising Manager, by M9. KPI: book-vs-physical variance ≤ 5.0% by M9 and ≤ 2.0% by M12; high-velocity stock-out hours halved by M12**.

---

### What the Board must decide

1. **Approve** the automated mobile-money reconciliation programme and 48-hour Finance sign-off SLA (owner Finance/Reconciliation Officer, by M5).
2. **Fund** the stock-variance task force and the 3-store footfall/POS pilot (owner Merchandising Manager, M9–M12).
3. **Adopt** the segment targets — ≥ 600 new known customers/month, churn proxy ≤ 50% — and authorise the Kampala/Jinja reactivation + referral campaign (owner Marketing Officer, by M7).

*Source: `module3_etl/etl_demo.db` (control total UGX 252,382,814.16); dashboard: https://ccosecret.github.io/srg-enterprise-data-management/ — course-provided SRG extract, Jul–Dec 2024.*

---

### Think-deeper answer

**Is a three-finding brief selective storytelling?** Each finding was chosen because its evidence is warehouse-verifiable and its action is funded in `D1_roadmap_18months.md`; the left-out candidates — flat store distribution (top store ≈4.1%) and 72.8% repeat concentration — sit in the dashboard for Board interrogation.
