#!/usr/bin/env python3
"""Build the SRG executive dashboard (Task C3.3).

Reads ONLY ``module3_etl/etl_demo.db`` — the output of the executed ETL
(``srg_etl_pipeline.py``) — and emits a self-contained
``module6_dashboard/dashboard.html``:

* Chart.js v4.4.1 inlined from ``module6_dashboard/vendor/chart.umd.min.js``
  (no CDN, no server, no database credentials in the browser);
* all fact rows embedded as dictionary-encoded JSON; every KPI, chart and
  drill-down recomputes client-side under the active filters;
* aggregated, non-PII measures only — no name/phone/email/payment_ref ever
  leaves ``module4_security`` masked views (see docs/C3_dashboard.md).

Documented failure behaviour (docs/C3_dashboard.md, "Failure behaviour"):
exit non-zero WITHOUT touching the previous ``dashboard.html`` when the
database is missing or the control total differs from
UGX 252,382,814.16 — a half-built page is never published.

Usage:
    python3 module6_dashboard/build_dashboard.py
"""
from __future__ import annotations

import json
import math
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DB_PATH = ROOT / "module3_etl" / "etl_demo.db"
TEMPLATE_PATH = HERE / "dashboard_template.html"
VENDOR_JS = HERE / "vendor" / "chart.umd.min.js"
OUT_PATH = HERE / "dashboard.html"

# Control total of the committed dataset as loaded by srg_etl_pipeline.py
# (evidence: module3_etl/output/selftest_evidence.txt, etl_run_log).
EXPECTED_CONTROL_TOTAL = 252_382_814.16

# Store -> city mapping used consistently across the portfolio
# (docs/B1_*, docs/B4_realtime_architecture.md, docs/C3_*).
CITY_ORDER = ["Kampala", "Jinja", "Mbarara", "Gulu", "E-commerce"]

STORE_CITIES = {}
for _i in range(1, 11):
    STORE_CITIES[f"ST{_i:02d}"] = "Kampala"
for _i in range(11, 15):
    STORE_CITIES[f"ST{_i:02d}"] = "Jinja"
for _i in range(15, 19):
    STORE_CITIES[f"ST{_i:02d}"] = "Mbarara"
for _i in range(19, 24):
    STORE_CITIES[f"ST{_i:02d}"] = "Gulu"
STORE_CITIES["ECOM01"] = "E-commerce"

# Canonical merchandise hierarchy (docs/B3_mdm_design.md).
CATEGORY_ORDER = [
    "Beverages",
    "Grains & Cereals",
    "Snacks",
    "Household",
    "Personal Care",
    "Stationery",
]
PAY_ORDER = ["MTN_MOMO", "AIRTEL_MOMO", "CASH", "CARD"]
PAY_LABELS = {
    "MTN_MOMO": "MTN MoMo",
    "AIRTEL_MOMO": "Airtel Money",
    "CASH": "Cash",
    "CARD": "Card",
}
MOMO_KEYS = {"MTN_MOMO", "AIRTEL_MOMO"}


def fail(msg: str) -> "NoReturn":  # noqa: F821 — documented non-zero exits
    print(f"[build_dashboard] ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    # ---- guards: never publish a half-built page -------------------------
    if not DB_PATH.exists():
        fail(
            f"{DB_PATH} not found — run module3_etl/srg_etl_pipeline.py "
            "--self-test first (previous dashboard.html left untouched)"
        )
    if not TEMPLATE_PATH.exists() or not VENDOR_JS.exists():
        fail("template or vendored Chart.js missing under module6_dashboard/")

    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    # ---- provenance: the ETL run this page is built from ----------------
    run = con.execute(
        "SELECT run_id, finished_at, status, rows_loaded, control_total_amount_ugx "
        "FROM etl_run_log ORDER BY finished_at DESC LIMIT 1"
    ).fetchone()
    if run is None:
        fail("etl_run_log is empty — no successful ETL run to publish from")

    # ---- control-total guard -------------------------------------------
    total = math.fsum(r[0] for r in con.execute("SELECT net_amount_ugx FROM fact_sales"))
    if abs(round(total, 2) - EXPECTED_CONTROL_TOTAL) >= 0.005:
        fail(
            f"control total UGX {total:,.2f} != expected "
            f"UGX {EXPECTED_CONTROL_TOTAL:,.2f} — dataset changed? "
            "update EXPECTED_CONTROL_TOTAL deliberately before publishing"
        )

    # ---- conformed dimensions ------------------------------------------
    cat_of = {
        r["product_sk"]: r["category"]
        for r in con.execute("SELECT product_sk, category FROM dim_product")
    }
    facts = con.execute(
        "SELECT transaction_ts, store_id, product_sk, payment_method, "
        "net_amount_ugx, customer_sk, is_return FROM fact_sales"
    ).fetchall()
    if not facts:
        fail("fact_sales is empty")

    # ---- dictionary encoding -------------------------------------------
    months = sorted({r["transaction_ts"][:7] for r in facts})
    month_labels = [
        datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in months
    ]
    month_idx = {m: i for i, m in enumerate(months)}

    stores = sorted({r["store_id"] for r in facts if r["store_id"] != "ECOM01"})
    if "ECOM01" in {r["store_id"] for r in facts}:
        stores.append("ECOM01")
    store_idx = {s: i for i, s in enumerate(stores)}
    store_city_idx = [
        CITY_ORDER.index(STORE_CITIES.get(s, "E-commerce")) for s in stores
    ]

    cats_present = {cat_of.get(r["product_sk"], "Uncategorised") for r in facts}
    unknown = cats_present - set(CATEGORY_ORDER)
    if unknown:
        fail(f"unexpected categories in dim_product: {sorted(unknown)}")
    cat_idx = {c: i for i, c in enumerate(CATEGORY_ORDER)}

    pays_present = [p for p in PAY_ORDER if any(r["payment_method"] == p for r in facts)]
    pay_idx = {p: i for i, p in enumerate(pays_present)}

    # first-ever purchase month per known customer (for new vs returning)
    first_month: dict[int, str] = {}
    for r in facts:
        sk = r["customer_sk"]
        if sk and sk > 0:
            m = r["transaction_ts"][:7]
            if sk not in first_month or m < first_month[sk]:
                first_month[sk] = m

    rows = []
    for r in facts:
        m = month_idx[r["transaction_ts"][:7]]
        s = store_idx.get(r["store_id"])
        if s is None:
            fail(f"store {r['store_id']} not in store dictionary")
        c = cat_idx[cat_of.get(r["product_sk"], "Uncategorised")]
        p = pay_idx.get(r["payment_method"])
        if p is None:
            fail(f"payment method {r['payment_method']} not in dictionary")
        sk = r["customer_sk"] or 0
        is_new = int(sk > 0 and first_month.get(sk) == r["transaction_ts"][:7])
        rows.append(
            [m, s, c, p, round(r["net_amount_ugx"], 2), sk, is_new, int(bool(r["is_return"]))]
        )

    meta = {
        "run": {
            "id": run["run_id"],
            "finished": run["finished_at"],
            "status": run["status"],
            "rowsLoaded": run["rows_loaded"],
            "controlTotal": run["control_total_amount_ugx"],
        },
        "builtAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "months": month_labels,
        "cities": CITY_ORDER,
        "stores": stores,
        "storeCity": store_city_idx,
        "cats": CATEGORY_ORDER,
        "pays": [PAY_LABELS[p] for p in pays_present],
        "momoIdx": [pay_idx[p] for p in pays_present if p in MOMO_KEYS],
    }

    # ---- assemble the self-contained page ------------------------------
    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    for token, value in (
        ("__CHARTJS__", VENDOR_JS.read_text(encoding="utf-8")),
        ("__META_JSON__", json.dumps(meta, separators=(",", ":"))),
        ("__ROWS_JSON__", json.dumps(rows, separators=(",", ":"))),
    ):
        if token not in html:
            fail(f"template token {token} missing")
        html = html.replace(token, value, 1)

    tmp = OUT_PATH.with_suffix(".html.tmp")
    tmp.write_text(html, encoding="utf-8")
    tmp.replace(OUT_PATH)  # atomic: readers only ever see a complete page

    # GitHub Pages serves the repository root, so publish the same page as
    # index.html there as well (single source: identical bytes, both emitted
    # from this one build — never edit either by hand).
    root_index = ROOT / "index.html"
    root_tmp = root_index.with_suffix(".html.tmp")
    root_tmp.write_text(html, encoding="utf-8")
    root_tmp.replace(root_index)

    print("[build_dashboard] control_total=UGX 252,382,814.16 OK")
    print(
        f"[build_dashboard] run={run['run_id']} status={run['status']} "
        f"finished={run['finished_at']} rows_loaded={run['rows_loaded']}"
    )
    print(
        f"[build_dashboard] rows_embedded={len(rows)} months={len(months)} "
        f"stores={len(stores)} categories={len(CATEGORY_ORDER)} "
        f"payments={len(pays_present)}"
    )
    print(f"[build_dashboard] wrote {OUT_PATH} ({OUT_PATH.stat().st_size:,} bytes)")
    print(f"[build_dashboard] wrote {root_index} ({root_index.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
