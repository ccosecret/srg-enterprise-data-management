#!/usr/bin/env python3
"""
================================================================================
 MODULE 4 - DATA MASKING DEMONSTRATION (Task C2.4)
 Savanna Retail Group (SRG) Capstone - Enterprise Data Management
================================================================================
 Python twin of data_masking.sql, executed on the REAL cleansed SRG dataset so
 the portfolio contains reproducible evidence (not a hand-written example):

   full_name     ->  J*** D**            (initials only)
   phone_number  ->  +256-XXX-XX1234     (last 4 digits for service callbacks)
   email         ->  j***@gmail.com      (first char + domain)
   payment_ref   ->  MP********89        (type prefix + last 2 for reconciliation)

 These functions are what the analytics copy of the dataset runs through before
 it leaves the warehouse - data protection by design (GDPR Art.25), and the
 Uganda DPPA 2019 equivalent duty for SRG.

 Usage:  python data_masking_demo.py
 Output: stdout table + ./output/masking_demo_output.txt
================================================================================
"""

import os
import re

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLEAN = os.path.join(ROOT, "module2_data_quality", "output",
                     "SRG_Customers_clean.csv")
SALES = os.path.join(ROOT, "module1_synthetic_data", "output", "SRG_Sales.csv")
OUT_DIR = os.path.join(HERE, "output")
os.makedirs(OUT_DIR, exist_ok=True)


# ------------------------------------------------------------------------------
# Masking primitives (mirror the SQL functions 1:1)
# ------------------------------------------------------------------------------
def mask_phone(p: str) -> str | None:
    """+256771234567 -> +256-XXX-XX4567 (keeps last 4 digits)."""
    if not p or not str(p).strip():
        return None
    digits = re.sub(r"\D", "", str(p))
    if len(digits) >= 9:
        return "+256-XXX-XX" + digits[-4:]
    return "+256-XXX-XXXX"


def mask_name(n: str) -> str | None:
    """John Doe -> J*** D**  (first initial + 3 stars, last initial + 2)."""
    if not n or not str(n).strip():
        return None
    parts = str(n).strip().split()
    if len(parts) == 1:
        return parts[0][0] + "***"
    return f"{parts[0][0]}*** {parts[1][0]}**"


def mask_email(e: str) -> str | None:
    """john.doe@gmail.com -> j***@gmail.com"""
    if not e or "@" not in str(e):
        return None
    e = str(e).strip()
    return e[0] + "***" + e[e.index("@"):]


def mask_payment_ref(r: str) -> str | None:
    """MP123456789 -> MP*******89 (type prefix + last 2 digits)."""
    if not r or not str(r).strip():
        return None
    r = str(r).strip()
    if len(r) <= 4:
        return "****"
    return r[:2] + "*" * (len(r) - 4) + r[-2:]


def main():
    lines = []
    header = ("=" * 78 + "\n"
              "MODULE 4 - DYNAMIC DATA MASKING ON LIVE SRG DATA (evidence)\n"
              + "=" * 78)
    lines.append(header)
    print(header)

    # --- customers -----------------------------------------------------------
    cust = pd.read_csv(CLEAN, dtype=str).fillna("").head(8)
    rows = []
    for _, r in cust.iterrows():
        rows.append([r["customer_id"],
                     r["full_name"] or "(null)",
                     mask_name(r["full_name"]) or "NULL",
                     r["phone_number"] or "(null)",
                     mask_phone(r["phone_number"]) or "NULL",
                     r["email"] or "(null)",
                     mask_email(r["email"]) or "NULL"])
    tbl = pd.DataFrame(rows, columns=[
        "customer_id", "full_name (RAW)", "-> masked", "phone (RAW)",
        "-> masked", "email (RAW)", "-> masked"]).to_string(index=False)
    sec = "\nCUSTOMERS - Restricted fields masked (analytics copy):\n" + tbl
    lines.append(sec)
    print(sec)

    # --- sales payment refs --------------------------------------------------
    sales = pd.read_csv(SALES, dtype=str).fillna("")
    momo = sales[sales["payment_method"].str.contains("MoMo|Airtel|momo",
                                                      case=False)].head(6)
    rows = []
    for _, r in momo.iterrows():
        rows.append([r["transaction_id"], r["payment_method"],
                     r["payment_ref"] or "(null - offline capture)",
                     mask_payment_ref(r["payment_ref"]) or "NULL (stays NULL)"])
    tbl = pd.DataFrame(rows, columns=[
        "transaction_id", "payment_method", "payment_ref (RAW)",
        "-> masked"]).to_string(index=False)
    sec = "\nSALES - mobile money payment references masked:\n" + tbl
    lines.append(sec)
    print(sec)

    # --- validation ----------------------------------------------------------
    checks = [
        ("phone mask form ^\\+256-XXX-XX\\d{4}$",
         all(v is None or re.fullmatch(r"\+256-XXX-XX\d{4}", v)
             for v in [mask_phone(p) for p in cust["phone_number"]])),
        ("name mask never leaks >1 char of a token",
         all(v is None or re.fullmatch(r"[A-Za-z]\*\*\*(\s[A-Za-z]\*\*)?",
                                       v)
             for v in [mask_name(n) for n in cust["full_name"]])),
        ("email mask keeps only first char + domain",
         all(v is None or re.fullmatch(r"[A-Za-z0-9._%+-]\*\*\*@.+", v)
             for v in [mask_email(e) for e in cust["email"]])),
        ("payment_ref mask preserves prefix + last 2",
         all(v is None or (v.startswith(str(p)[:2]) and v.endswith(str(p)[-2:]))
             for p, v in [(p, mask_payment_ref(p))
                          for p in momo["payment_ref"]] if p)),
    ]
    sec = "\nVALIDATION:" + "\n" + "\n".join(
        f"  [{'PASS' if ok else 'FAIL'}] {name}" for name, ok in checks)
    lines.append(sec)
    print(sec)
    sec = ("\nNOTE: this masked frame is what leaves the warehouse to BI tools."
           "\n      Raw values remain table-side for compliance_officer (audit)"
           "\n      and cdm_admin (steward) only - see rbac_postgresql.sql.")
    lines.append(sec)
    print(sec)

    out_path = os.path.join(OUT_DIR, "masking_demo_output.txt")
    with open(out_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\nEvidence written to: {out_path}")
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
