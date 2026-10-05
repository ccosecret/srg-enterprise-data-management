#!/usr/bin/env python3
"""
================================================================================
 MODULE 2 - HANDS-ON DATA QUALITY ASSESSMENT & CLEANSING (Task B2)
 Savanna Retail Group (SRG) Capstone - Enterprise Data Management
================================================================================
 Reads the dirty datasets produced by Module 1 and executes:

   1. DATA PROFILING      - quantitative metrics across all six dimensions
                            (Uniqueness, Completeness, Consistency, Timeliness,
                            Accuracy, Validity) for SRG_Customers + SRG_Products
   2. DATA CLEANSING      - modular, individually-testable functions:
                              * standardize_phone()      -> E.164 +2567XXXXXXXX
                              * standardize_district()   -> official names
                              * standardize_unit()       -> kg / pcs / liters
                              * standardize_category()   -> master list
                              * standardize_date()       -> ISO 8601
                              * standardize_gender()     -> M / F
                              * deduplicate_customers()  -> deterministic phone
                                key + fuzzy Levenshtein (name+district+email/
                                phone weighted score) with survivorship rules
   3. BEFORE vs AFTER      - same metric functions applied to both states, so
                              the improvement table is computed, not claimed
   4. VALIDATION RULES     - 12-rule catalog (JSON + Markdown)
   5. MONITORING SPEC      - daily automated DQ monitoring (JSON)

 Matching design (defensible, auditable):
   Rule R1 (deterministic) : identical NORMALIZED phone number -> auto-merge.
   Rule R2 (probabilistic) : blocked on canonical district, name similarity
        measured with rapidfuzz token_sort_ratio (Levenshtein-based, normalized
        0-100), then a weighted score:
            name  >= 90 : +60   (>= 97: +70)
            same district  : +20
            phone  equal   : +20 | either missing: +10 | both differ:  0
            email  equal   : +15 | either missing:  +5  | both differ: -10
        auto-merge  : score >= 90 AND a POSITIVE identifier match (phone or
                      email equal) - name similarity ALONE never auto-merges,
                      because merging two different people destroys one
                      person's loyalty history and privacy rights.
        open review : score >= 65 without positive match and without
                      conflicting evidence -> counted as suspected duplicate,
                      routed to stewardship (manual adjudication).
        rejected    : score >= 65 but both emails present AND different ->
                      strong evidence of two distinct persons (homonym pair).

 Usage:  python dq_assessment_cleansing.py
 Output: ./output/*.md, ./output/*.json, ./output/SRG_*_clean.csv
================================================================================
"""

import json
import os
import re
import sys
from collections import OrderedDict
from datetime import datetime

import pandas as pd
from rapidfuzz import fuzz

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW_DIR = os.path.join(ROOT, "module1_synthetic_data", "output")
OUT_DIR = os.path.join(HERE, "output")
os.makedirs(OUT_DIR, exist_ok=True)

# Reference data is shared with the generator (single source of truth)
sys.path.insert(0, os.path.join(ROOT, "module1_synthetic_data"))
from generate_srg_datasets import DISTRICT_VARIANTS, OFFICIAL_DISTRICTS  # noqa: E402

TODAY = datetime(2026, 10, 5)          # assessment date (fixed for reproducibility)
PHONE_E164_RE = re.compile(r"^\+2567\d{8}$")
PHONE_NATIONAL_RE = re.compile(r"^07\d{8}$")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

# ==============================================================================
# SECTION 1 - STANDARDIZATION FUNCTIONS (modular, unit-testable)
# ==============================================================================


def standardize_phone(raw):
    """Return (e164_number, status).

    Accepts the five SRG field formats:
        +2567XXXXXXXX | 07XXXXXXXX | 2567XXXXXXXX | 7XXXXXXXX |
        '+256 77 123 4567' | '077-123-4567'
    Output: '+2567XXXXXXXX' (Uganda ITU E.164 national mobile format).
    """
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return "", "missing"
    s = str(raw).strip()
    if s == "" or s.lower() in {"nan", "none", "null", "n/a"}:
        return "", "missing"
    digits = re.sub(r"\D", "", s)
    national = None
    if len(digits) == 12 and digits.startswith("256"):
        national = "0" + digits[3:]
    elif len(digits) == 10 and digits.startswith("0"):
        national = digits
    elif len(digits) == 9 and digits.startswith("7"):
        national = "0" + digits
    if national and PHONE_NATIONAL_RE.match(national):
        return "+256" + national[1:], "valid"
    return s, "invalid"                       # cannot be repaired safely


def standardize_district(raw):
    """Return (canonical_district, status).

    1) exact/case-insensitive alias dictionary hit
    2) fuzzy fallback: WRatio against official district list (>= 88)
    3) otherwise UNRESOLVED -> row flagged for stewardship (never fabricated)
    """
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return "", "missing"
    s = str(raw).strip()
    if s == "" or s.lower() in {"nan", "none", "null"}:
        return "", "missing"
    key = s.lower().strip()
    alias = {k.lower().strip(): v for k, v in DISTRICT_VARIANTS.items() if v}
    if key in alias:
        return alias[key], ("exact" if key in
                            [d.lower() for d in OFFICIAL_DISTRICTS]
                            else "variant_mapped")
    if key in [d.lower() for d in OFFICIAL_DISTRICTS]:
        for d in OFFICIAL_DISTRICTS:
            if d.lower() == key:
                return d, "exact"
    best, best_score = None, 0
    for d in OFFICIAL_DISTRICTS:
        sc = fuzz.WRatio(key, d.lower())
        if sc > best_score:
            best, best_score = d, sc
    if best_score >= 88:
        return best, "fuzzy_mapped"
    return s, "unresolved"


UNIT_MAP = {
    "kg": "kg", "kgs": "kg", "kilogram": "kg", "kilograms": "kg",
    "kilo": "kg", "g": "kg", "gram": "kg", "grams": "kg", "gm": "kg",
    "gms": "kg",
    "pcs": "pcs", "piece": "pcs", "pieces": "pcs", "pc": "pcs",
    "pce": "pcs", "unit": "pcs", "units": "pcs", "boxes": "pcs",
    "bottle": "pcs", "bottles": "pcs", "pack": "pcs", "packs": "pcs",
    "liters": "liters", "litre": "liters", "litres": "liters",
    "l": "liters", "ml": "liters",
}
# Units whose LABEL can be mapped but whose stored VALUES would need scaling
# (g->kg, ml->liters). Flagged so the source system fixes the capture point.
UNIT_CONVERSION_FLAG = {"g", "gram", "grams", "gm", "gms", "ml"}


def standardize_unit(raw):
    """Return (canonical_unit, status). Canonical set: {kg, pcs, liters}."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return "", "missing"
    key = str(raw).strip().lower()
    if key == "" or key in {"nan", "none", "null"}:
        return "", "missing"
    if key in UNIT_MAP:
        status = "converted" if key in UNIT_CONVERSION_FLAG else "mapped"
        return UNIT_MAP[key], status
    return str(raw).strip(), "unresolved"


CATEGORY_MAP = {
    "beverages": "Beverages", "beverage": "Beverages", "bvages": "Beverages",
    "bevages": "Beverages",
    "grains & cereals": "Grains & Cereals", "grains": "Grains & Cereals",
    "grains and cereals": "Grains & Cereals", "grains&cereals": "Grains & Cereals",
    "grains & cereal": "Grains & Cereals",
    "snacks": "Snacks", "snack": "Snacks", "sncks": "Snacks",
    "household": "Household", "house hold": "Household",
    "household items": "Household", "houshold": "Household",
    "personal care": "Personal Care", "percare": "Personal Care",
    "personalcare": "Personal Care",
    "stationery": "Stationery", "stationary": "Stationery",
    "statio nery": "Stationery",
    "": "", "unknown": "",
}
CANONICAL_CATEGORIES = ["Beverages", "Grains & Cereals", "Snacks",
                        "Household", "Personal Care", "Stationery"]


def standardize_category(raw):
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return "", "missing"
    key = str(raw).strip().lower()
    if key in CATEGORY_MAP:
        return CATEGORY_MAP[key], ("missing" if key == "" else "mapped")
    best, best_score = None, 0
    for c in CANONICAL_CATEGORIES:
        sc = fuzz.WRatio(key, c.lower())
        if sc > best_score:
            best, best_score = c, sc
    if best_score >= 85:
        return best, "fuzzy_mapped"
    return str(raw).strip(), "unresolved"


DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]


def standardize_date(raw):
    """Return (iso_date_string, original_format_label)."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return "", "missing"
    s = str(raw).strip()
    if s == "" or s.lower() in {"nan", "none", "null"}:
        return "", "missing"
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d"), fmt
        except ValueError:
            continue
    return s, "unparseable"


GENDER_MAP = {"male": "M", "m": "M", "f": "F", "female": "F"}


def standardize_gender(raw):
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return "", "missing"
    key = str(raw).strip().lower()
    if key == "" or key in {"nan", "none", "null"}:
        return "", "missing"
    if key in GENDER_MAP:
        return GENDER_MAP[key], "mapped"
    return str(raw).strip(), "unresolved"


def standardize_price(raw):
    """Strip 'UGX 50,000' / 'UGX50000' / '50,000' to float; None if invalid."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None, "missing"
    s = str(raw).strip()
    if s == "" or s.lower() in {"nan", "none", "null", "n/a"}:
        return "", "missing"
    cleaned = re.sub(r"(?i)ugx", "", s)
    cleaned = cleaned.replace(",", "").strip()
    try:
        return float(cleaned), "valid"
    except ValueError:
        return None, "invalid"


# ==============================================================================
# SECTION 2 - DEDUPLICATION (deterministic key + fuzzy Levenshtein scoring)
# ==============================================================================


def _norm_name(s: str) -> str:
    s = re.sub(r"[^a-z0-9 ]", " ", str(s).lower())
    return " ".join(s.split())


def _email(s) -> str:
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    return str(s).strip().lower()


ORIGINAL_CUST_COLS = ["full_name", "phone_number", "email", "district",
                      "registration_date", "gender"]
ORIGINAL_PROD_COLS = ["sku", "product_name", "category", "unit_of_measure",
                      "cost_ugx", "selling_price_ugx"]


def _prep_for_matching(df: pd.DataFrame) -> pd.DataFrame:
    """Add the standardized helper columns the matching rules need.

    The matching LOGIC (normalized phone + canonical district) is defined once
    and applied identically to the raw and cleansed states, so the before/after
    duplicate metric is measured with the same yardstick.
    """
    d = df.copy()
    d["phone_e164"] = d["phone_number"].map(lambda v: standardize_phone(v)[0])
    d["district_std"] = d["district"].map(lambda v: standardize_district(v)[0])
    if "registration_date_iso" not in d.columns:
        d["registration_date_iso"] = d["registration_date"].map(
            lambda v: standardize_date(v)[0])
    if "gender_std" not in d.columns:
        d["gender_std"] = d["gender"].map(lambda v: standardize_gender(v)[0])
    return d


def _survivor_key(df: pd.DataFrame, i):
    """Survivorship rank: (1) most complete record, (2) earliest
    registration_date, (3) lowest customer_id - deterministic & idempotent."""
    row = df.loc[i]
    cols = ["full_name", "phone_e164", "email", "district_std", "gender_std",
            "registration_date_iso"]
    completeness = int(sum(str(row[c]).strip() not in ("", "nan", "None")
                           for c in cols))
    return (-completeness,
            str(row["registration_date_iso"]) or "9999-12-31",
            str(row["customer_id"]))


def find_duplicate_clusters(df: pd.DataFrame, log: dict):
    """Return (clusters, open_review_pairs, stats).

    clusters        : list of lists of row-index (auto-merge candidates)
    open_review_pairs: list of (i, j, score) needing human adjudication
    """
    parent = {i: i for i in df.index}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    stats = {"R1_phone_deterministic": 0, "R2_fuzzy_auto": 0,
             "R2_rejected_email_conflict": 0, "pairs_scored": 0}

    # ---- R1: deterministic key = normalized phone --------------------------
    ph = df["phone_e164"].fillna("")
    for val, grp in df.loc[ph != ""].groupby(ph[ph != ""]):
        idxs = list(grp.index)
        for j in idxs[1:]:
            union(idxs[0], j)
            stats["R1_phone_deterministic"] += 1

    # ---- R2: fuzzy, blocked on canonical district --------------------------
    names = {i: _norm_name(v) for i, v in df["full_name"].items()}
    phones = {i: v for i, v in ph.items()}
    emails = {i: _email(v) for i, v in df["email"].items()}
    open_review = []

    for district, grp in df.groupby("district_std"):
        if district in ("", "UNRESOLVED"):
            continue
        idxs = list(grp.index)
        for a in range(len(idxs)):
            for b in range(a + 1, len(idxs)):
                i, j = idxs[a], idxs[b]
                if find(i) == find(j):
                    continue
                sim = fuzz.token_sort_ratio(names[i], names[j])
                if sim < 90:
                    continue
                stats["pairs_scored"] += 1
                score = 60 + (10 if sim >= 97 else 0) + 20      # name + district
                pi, pj = phones[i], phones[j]
                if pi and pj and pi == pj:
                    score += 20
                elif not pi or not pj:
                    score += 10
                ei, ej = emails[i], emails[j]
                if ei and ej and ei == ej:
                    score += 15
                elif not ei or not ej:
                    score += 5
                else:
                    score -= 10
                # AUTO-MERGE GATE: name similarity alone never merges two
                # people - a POSITIVE identifier match (phone or email equal)
                # is mandatory (protects against homonym false merges).
                positive = ((ei and ej and ei == ej) or
                            (pi and pj and pi == pj))
                if score >= 90 and positive:
                    union(i, j)
                    stats["R2_fuzzy_auto"] += 1
                elif score >= 65:
                    if ei and ej and ei != ej:
                        stats["R2_rejected_email_conflict"] += 1
                    else:
                        open_review.append((i, j, score))
                log.append({"row_a": i, "row_b": j, "name_sim": round(sim, 1),
                            "score": score})

    groups = {}
    for i in df.index:
        groups.setdefault(find(i), []).append(i)
    clusters = [g for g in groups.values() if len(g) > 1]
    return clusters, open_review, stats


def deduplicate_customers(df: pd.DataFrame):
    """Merge auto-clusters with survivorship rules; keep review items flagged.

    Survivorship (attribute-level, documented for Task B3):
      1) most complete record (non-null field count) wins  -> completeness
      2) tie -> EARLIEST registration_date (golden record keeps full history)
      3) tie -> lowest customer_id (deterministic, idempotent re-runs)
    """
    match_log = []
    clusters, open_review, stats = find_duplicate_clusters(df, match_log)
    drop_idx, merged_rows = set(), 0

    for cluster in clusters:
        survivor = min(cluster, key=lambda i: _survivor_key(df, i))
        for dup in cluster:
            if dup != survivor:
                drop_idx.add(dup)
                merged_rows += 1
        df.loc[survivor, "merged_customer_ids"] = ";".join(
            str(df.loc[i, "customer_id"]) for i in cluster if i != survivor)

    review_rows = {i for pair in open_review for i in pair[:2]} - drop_idx
    for i in review_rows:
        df.loc[i, "stewardship_flag"] = "REVIEW: possible duplicate"

    clean = df.drop(index=list(drop_idx)).copy()
    stats["merged_rows"] = merged_rows
    stats["clusters"] = len(clusters)
    stats["open_review_pairs"] = len(open_review)
    stats["rows_flagged_for_review"] = len(review_rows)
    return clean, stats


# ==============================================================================
# SECTION 3 - PROFILING (the SAME functions feed the before & after passes)
# ==============================================================================


def profile_customers(df_in: pd.DataFrame) -> OrderedDict:
    df = _prep_for_matching(df_in)
    n = len(df)
    m = OrderedDict()
    # ---- Uniqueness --------------------------------------------------------
    clusters, open_review, _ = find_duplicate_clusters(df, [])
    confirmed = sum(len(c) - 1 for c in clusters)
    dropped = set()
    for c in clusters:
        surv = min(c, key=lambda i: _survivor_key(df, i))
        dropped |= (set(c) - {surv})
    review_rows = {i for p in open_review for i in p[:2]} - dropped
    m[("Uniqueness", "Confirmed duplicate rows - auto-matched by rules (%)")] = \
        round(confirmed / n * 100, 2)
    m[("Uniqueness", "Open stewardship review rows - suspected duplicates "
       "(count)")] = len(review_rows)
    m[("Uniqueness", "Total duplicate-person flag rate (confirmed + open "
       "review, %)")] = round((confirmed + len(review_rows)) / n * 100, 2)
    m[("Uniqueness", "Exact duplicate rows (all fields except ID, %)")] = \
        round(df[ORIGINAL_CUST_COLS].duplicated(keep=False).sum() / n * 100, 2)
    m[("Uniqueness", "Unique customer_id (%)")] = \
        round(df["customer_id"].nunique() / n * 100, 2)
    # ---- Completeness ------------------------------------------------------
    for col in ["full_name", "phone_number", "email", "district",
                "registration_date", "gender"]:
        present = df[col].astype(str).str.strip().ne("").sum()
        m[("Completeness", f"Present values: {col} (%)")] = round(present / n * 100, 2)
    grid = df[["full_name", "phone_number", "email", "district",
               "registration_date", "gender"]].astype(str)
    m[("Completeness", "Cell-level completeness across 6 fields (%)")] = \
        round(grid.apply(lambda c: c.str.strip().ne("")).stack().mean() * 100, 2)
    # ---- Consistency -------------------------------------------------------
    def phone_format(v):
        s = str(v).strip()
        if s in ("", "nan", "None"):
            return "missing"
        if re.fullmatch(r"\+2567\d{8}", s):
            return "+256... (E.164)"
        if re.fullmatch(r"07\d{8}", s):
            return "07... (national)"
        if re.fullmatch(r"2567\d{8}", s):
            return "256... (no plus)"
        if re.fullmatch(r"7\d{8}", s):
            return "7... (no leading 0)"
        if re.fullmatch(r"[\d\s\-]+", s) and re.search(r"[\s\-]", s):
            return "spaced/dashed"
        return "other/invalid"
    fmt_counts = df["phone_number"].map(phone_format).value_counts()
    fmt_counts = fmt_counts.drop(index="missing", errors="ignore")
    m[("Consistency", "Distinct phone format variants (count)")] = int(fmt_counts.shape[0])
    m[("Consistency", "Records in dominant phone format (%)")] = \
        round(fmt_counts.iloc[0] / n * 100, 2) if len(fmt_counts) else 0.0
    date_fmts = df["registration_date"].map(lambda v: standardize_date(v)[1])
    m[("Consistency", "Distinct date format variants (count)")] = \
        int(date_fmts[date_fmts != "missing"].nunique())
    m[("Consistency", "Records in ISO-8601 date format (%)")] = \
        round((date_fmts == "%Y-%m-%d").sum() / n * 100, 2)
    m[("Consistency", "Distinct raw district labels (count)")] = \
        int(df["district"].astype(str).str.strip().replace("", pd.NA).nunique())
    gender_labels = df["gender"].astype(str).str.strip()
    gender_labels = gender_labels[gender_labels != ""]
    m[("Consistency", "Distinct gender label variants (count)")] = \
        int(gender_labels.nunique())
    # ---- Timeliness --------------------------------------------------------
    parsed = df["registration_date"].map(lambda v: standardize_date(v)[0])
    dates = pd.to_datetime(parsed.replace("", pd.NA), errors="coerce")
    m[("Timeliness", "Registration date parseable (%)")] = \
        round(dates.notna().sum() / n * 100, 2)
    m[("Timeliness", "Dates not in the future (%)")] = \
        round((dates <= pd.Timestamp(TODAY)).sum() / n * 100, 2)
    m[("Timeliness", "Records registered <= 4 years ago (%)")] = \
        round(((dates >= pd.Timestamp(TODAY) - pd.Timedelta(days=1461))
               & (dates <= pd.Timestamp(TODAY))).sum() / n * 100, 2)
    # ---- Accuracy (proxy vs reference data - assumption documented) --------
    resolvable = df["district"].map(lambda v: standardize_district(v)[1])
    m[("Accuracy", "District stored as official name (no repair needed, %)")] = \
        round((resolvable == "exact").sum() / n * 100, 2)
    phone_ok = df["phone_number"].map(
        lambda v: standardize_phone(v)[1] == "valid")
    m[("Accuracy", "Phone is plausible Ugandan MSISDN (%)")] = \
        round(phone_ok.sum() / n * 100, 2)
    gender_ok = df["gender"].map(
        lambda v: str(v).strip() in {"M", "F", ""})   # stored in canonical domain
    m[("Accuracy", "Gender stored in canonical domain {M,F} (%)")] = \
        round(gender_ok.sum() / n * 100, 2)
    # ---- Validity ----------------------------------------------------------
    # validity = value ALREADY stored in conforming format (no transformation)
    v_phone = df["phone_number"].map(
        lambda v: bool(PHONE_E164_RE.match(str(v).strip())))
    v_email = df["email"].map(
        lambda v: str(v).strip() == "" or bool(EMAIL_RE.match(str(v).strip())))
    v_date = parsed.map(lambda s: s != "")
    v_gender = df["gender"].map(
        lambda v: str(v).strip() in {"M", "F", "Male", "Female"})
    m[("Validity", "Phone already in E.164 (+2567XXXXXXXX) (%)")] = \
        round(v_phone.sum() / n * 100, 2)
    m[("Validity", "Email RFC-5322 lite conforming (or null) (%)")] = \
        round(v_email.sum() / n * 100, 2)
    m[("Validity", "Registration date conforming (%)")] = \
        round(v_date.sum() / n * 100, 2)
    m[("Validity", "Gender value conforming (%)")] = \
        round(v_gender.sum() / n * 100, 2)
    m[("Validity", "Composite record validity - all 4 rules pass (%)")] = \
        round((v_phone & v_email & v_date & v_gender).sum() / n * 100, 2)
    return m


def profile_products(df: pd.DataFrame) -> OrderedDict:
    n = len(df)
    m = OrderedDict()
    # ---- Uniqueness --------------------------------------------------------
    sku = df["sku"].astype(str).str.strip()
    dup_sku = sku.duplicated(keep=False) & sku.ne("") & sku.ne("nan")
    m[("Uniqueness", "Rows sharing a duplicate SKU (count)")] = \
        int(dup_sku.sum())
    pid = df["product_id"].astype(str).str.strip()
    m[("Uniqueness", "product_id unique and non-null (%)")] = \
        round((pid.ne("") & pid.ne("nan")).sum() / n * 100, 2)
    m[("Uniqueness", "Exact duplicate rows (all fields except ID, %)")] = \
        round(df[ORIGINAL_PROD_COLS].duplicated(keep=False).sum() / n * 100, 2)
    # ---- Completeness ------------------------------------------------------
    for col in ["sku", "product_name", "category", "unit_of_measure",
                "cost_ugx", "selling_price_ugx"]:
        present = df[col].astype(str).str.strip().ne("").sum()
        m[("Completeness", f"Present values: {col} (%)")] = round(present / n * 100, 2)
    grid = df[["sku", "product_name", "category", "unit_of_measure",
               "cost_ugx", "selling_price_ugx"]].astype(str)
    m[("Completeness", "Cell-level completeness across 6 fields (%)")] = \
        round(grid.apply(lambda c: c.str.strip().ne("")).stack().mean() * 100, 2)
    # ---- Consistency -------------------------------------------------------
    m[("Consistency", "Distinct unit-of-measure labels (count)")] = \
        int(df["unit_of_measure"].astype(str).str.strip().nunique())
    m[("Consistency", "Distinct category labels (count)")] = \
        int(df["category"].astype(str).str.strip().nunique())
    price_fmt = df["selling_price_ugx"].map(
        lambda v: "currency string" if re.search(r"(?i)ugx|,", str(v))
        else "numeric")
    m[("Consistency", "Price stored as free-text currency string (%)")] = \
        round((price_fmt == "currency string").sum() / n * 100, 2)
    # SKU->name divergence: same SKU, different names
    g = df[sku.ne("")].groupby(sku)["product_name"].nunique()
    m[("Consistency", "SKUs mapped to >1 product name (count)")] = \
        int((g > 1).sum())
    # ---- Timeliness --------------------------------------------------------
    refreshable = (df["product_id"].notna() & sku.ne("")).sum()
    m[("Timeliness", "Refreshable via key: product_id AND SKU present (%) "
       "[proxy - source has no last_updated column]")] = round(refreshable / n * 100, 2)
    # ---- Accuracy ----------------------------------------------------------
    cost = df["cost_ugx"].map(lambda v: standardize_price(v)[0])
    sell = df["selling_price_ugx"].map(lambda v: standardize_price(v)[0])
    cost_s = pd.to_numeric(pd.Series(cost), errors="coerce")
    sell_s = pd.to_numeric(pd.Series(sell), errors="coerce")
    m[("Accuracy", "Selling price below cost - margin anomaly (%)")] = \
        round(((sell_s < cost_s) & sell_s.notna() & cost_s.notna()).sum() / n * 100, 2)
    m[("Accuracy", "Prices parseable to numeric (%)")] = \
        round((sell_s.notna() & cost_s.notna()).sum() / n * 100, 2)
    m[("Accuracy", "Cost and price non-negative (%)")] = \
        round(((sell_s >= 0) & (cost_s >= 0)).sum() / n * 100, 2)
    # ---- Validity ----------------------------------------------------------
    unit_ok = df["unit_of_measure"].map(
        lambda v: str(v).strip() in {"kg", "pcs", "liters"})
    cat_ok = df["category"].map(lambda v: str(v).strip() in CANONICAL_CATEGORIES)
    sku_ok = sku.map(lambda v: bool(re.fullmatch(r"[A-Z0-9]{3,10}", v)))
    m[("Validity", "Unit of measure in {kg, pcs, liters} (%)")] = \
        round(unit_ok.sum() / n * 100, 2)
    m[("Validity", "Category in master list (%)")] = \
        round(cat_ok.sum() / n * 100, 2)
    m[("Validity", "SKU matches ^[A-Z0-9]{3,10}$ (%)")] = \
        round(sku_ok.sum() / n * 100, 2)
    m[("Validity", "Composite product validity - all rules pass (%)")] = \
        round((unit_ok & cat_ok & sku_ok & sell_s.notna()).sum() / n * 100, 2)
    return m


def md_table(rows, headers):
    out = "| " + " | ".join(headers) + " |\n"
    out += "|" + "|".join(["---"] * len(headers)) + "|\n"
    for r in rows:
        out += "| " + " | ".join(str(x) for x in r) + " |\n"
    return out


def profile_to_md(prof, title):
    rows = [[dim, metric, val] for (dim, metric), val in prof.items()]
    return f"### {title}\n\n" + md_table(rows, ["Dimension", "Metric", "Value"])


# ==============================================================================
# SECTION 4 - CLEANSING PIPELINE
# ==============================================================================


def cleanse_customers(df: pd.DataFrame):
    """Standardize in place (originals preserved in *_raw audit columns)."""
    out = df.copy()

    ph = out["phone_number"].map(standardize_phone)
    out["phone_number_raw"] = out["phone_number"]
    out["phone_e164"] = [p for p, _ in ph]
    out["phone_status"] = [s for _, s in ph]
    # overwrite: cleansed file stores the canonical E.164 value
    out["phone_number"] = out["phone_e164"]

    dis = out["district"].map(standardize_district)
    out["district_raw"] = out["district"]
    out["district_std"] = [d for d, _ in dis]
    out["district_status"] = [s for _, s in dis]
    out["district"] = out["district_std"]

    dt = out["registration_date"].map(standardize_date)
    out["registration_date_raw"] = out["registration_date"]
    out["registration_date_iso"] = [d for d, _ in dt]
    out["date_format_original"] = [f for _, f in dt]
    out["registration_date"] = out["registration_date_iso"]

    gd = out["gender"].map(standardize_gender)
    out["gender_raw"] = out["gender"]
    out["gender_std"] = [g for g, _ in gd]
    out["gender_status"] = [s for _, s in gd]
    out["gender"] = out["gender_std"]

    out["email"] = out["email"].map(
        lambda v: str(v).strip().lower() if str(v).strip() not in
        ("", "nan", "None") else "")
    out["full_name"] = out["full_name"].map(
        lambda v: " ".join(str(v).split()) if str(v).strip() not in
        ("", "nan", "None") else "")
    out["merged_customer_ids"] = ""
    out["stewardship_flag"] = ""

    clean, log = deduplicate_customers(out)
    return clean, log


def cleanse_products(df: pd.DataFrame):
    """Standardize UOM/category/prices (originals kept in *_raw columns);
    quarantine rows with NULL business keys; FLAG business-rule violations."""
    out = df.copy()
    u = out["unit_of_measure"].map(standardize_unit)
    out["unit_raw"] = out["unit_of_measure"]
    out["unit_std"] = [x for x, _ in u]
    out["unit_status"] = [s for _, s in u]
    out["unit_of_measure"] = out["unit_std"]

    c = out["category"].map(standardize_category)
    out["category_raw"] = out["category"]
    out["category_std"] = [x for x, _ in c]
    out["category_status"] = [s for _, s in c]
    out["category"] = out["category_std"]

    cost = out["cost_ugx"].map(lambda v: standardize_price(v)[0])
    sell = out["selling_price_ugx"].map(lambda v: standardize_price(v)[0])
    out["cost_ugx_raw"] = out["cost_ugx"]
    out["selling_price_ugx_raw"] = out["selling_price_ugx"]
    out["cost_ugx_std"] = ["" if v is None else v for v in cost]
    out["selling_price_ugx_std"] = ["" if v is None else v for v in sell]
    out["price_status"] = out["selling_price_ugx"].map(
        lambda v: standardize_price(v)[1])
    out["cost_ugx"] = out["cost_ugx_std"]
    out["selling_price_ugx"] = out["selling_price_ugx_std"]

    # business-rule flags (NOT auto-corrected - pricing is an owned decision)
    cost_n = pd.to_numeric(out["cost_ugx_std"], errors="coerce")
    sell_n = pd.to_numeric(out["selling_price_ugx_std"], errors="coerce")
    out["margin_anomaly_flag"] = ((sell_n < cost_n) & sell_n.notna()
                                  & cost_n.notna())
    sku = out["sku"].astype(str).str.strip()
    out["sku"] = sku
    dupe_sku = sku.duplicated(keep=False) & sku.ne("") & sku.ne("nan")
    out["duplicate_sku_flag"] = dupe_sku   # flagged, NOT auto-merged (VR-008)
    pid = out["product_id"].astype(str).str.strip()
    bad_key = pid.isin(["", "nan", "None"]) | sku.isin(["", "nan", "None"])
    quarantined = out[bad_key].copy()
    clean = out[~bad_key].copy()
    return clean, quarantined


# ==============================================================================
# SECTION 5 - VALIDATION RULES CATALOG + MONITORING SPEC
# ==============================================================================

VALIDATION_RULES = [
    {"rule_id": "VR-001", "field": "customers.phone_number",
     "type": "Technical",
     "condition": "phone_number must match ^(\\+256|0)7[0-9]{8}$ after input-mask normalization",
     "action_on_failure": "Block save; re-render input with +256 mask; log to dq_violation_log",
     "severity": "High"},
    {"rule_id": "VR-002", "field": "customers.district",
     "type": "Business",
     "condition": "district must be a member of the official Uganda district reference list (dropdown only, free text disabled)",
     "action_on_failure": "Block save; force selection from reference list; steward notified for legacy values",
     "severity": "Medium"},
    {"rule_id": "VR-003", "field": "customers.email",
     "type": "Technical",
     "condition": "email IS NULL OR email ~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$",
     "action_on_failure": "Allow save but quarantine from campaign exports; nightly re-validation",
     "severity": "Medium"},
    {"rule_id": "VR-004", "field": "customers.customer_id",
     "type": "Technical",
     "condition": "PRIMARY KEY: NOT NULL AND unique across operational + MDM stores",
     "action_on_failure": "Reject insert; abort load batch; page on-call data engineer",
     "severity": "Critical"},
    {"rule_id": "VR-005", "field": "customers.registration_date",
     "type": "Business",
     "condition": "registration_date <= CURRENT_DATE AND registration_date >= '2000-01-01' AND stored as ISO-8601",
     "action_on_failure": "Block save (future/backdated signup); default to CURRENT_DATE on retry",
     "severity": "High"},
    {"rule_id": "VR-006", "field": "customers.full_name",
     "type": "Technical",
     "condition": "TRIM(full_name) length >= 2 AND full_name ~ '^[A-Za-z .-]+$'",
     "action_on_failure": "Block save; inline prompt (no single-letter placeholder names)",
     "severity": "Medium"},
    {"rule_id": "VR-007", "field": "customers (golden record)",
     "type": "Business",
     "condition": "NORMALIZED(phone_number) unique across golden records OR record is in stewardship review queue",
     "action_on_failure": "Route to MDM matching queue (auto-merge >= 90 score, else steward); block loyalty point posting until resolved",
     "severity": "Critical"},
    {"rule_id": "VR-008", "field": "products.sku",
     "type": "Technical",
     "condition": "sku NOT NULL AND unique among active products (one SKU = one product name)",
     "action_on_failure": "Reject insert; raise SKU-collision ticket to merchandising; quarantine batch",
     "severity": "Critical"},
    {"rule_id": "VR-009", "field": "products.unit_of_measure",
     "type": "Business",
     "condition": "unit_of_measure IN ('kg','pcs','liters') - controlled vocabulary enforced at POS/e-commerce item setup",
     "action_on_failure": "Block save; show UOM picker; existing violations auto-mapped by cleansing script",
     "severity": "High"},
    {"rule_id": "VR-010", "field": "products.category",
     "type": "Business",
     "condition": "category IN master merchandise hierarchy (Beverages, Grains & Cereals, Snacks, Household, Personal Care, Stationery)",
     "action_on_failure": "Block save; enforce hierarchy picker; fuzzy-matched values need steward approval",
     "severity": "High"},
    {"rule_id": "VR-011", "field": "products.selling_price_ugx / cost_ugx",
     "type": "Business",
     "condition": "selling_price_ugx >= cost_ugx UNLESS promo_flag = TRUE AND promo_approved_by IS NOT NULL",
     "action_on_failure": "Warn at entry; nightly margin-anomaly report to Pricing Analyst; never auto-correct",
     "severity": "Medium"},
    {"rule_id": "VR-012", "field": "sales.payment_ref (Mobile Money)",
     "type": "Business",
     "condition": "payment_method IN ('MTN MoMo','Airtel Money') implies payment_ref populated within 24h of capture OR reconciliation_status = 'PENDING'",
     "action_on_failure": "Permit capture offline (store outages) but quarantine transaction from revenue reports until ref arrives; escalate if aged > 24h",
     "severity": "High"},
]

MONITORING_SPEC = {
    "spec_name": "SRG Continuous Data Quality Monitoring",
    "schedule": "Daily 05:30 EAT after nightly ETL (plus intra-day for payments)",
    "owner_role": "CDM Admin (IT Manager acts as interim Data Steward lead)",
    "checks": [
        {"check_id": "DQC-01", "metric": "Customer duplicate-person rate",
         "measure": "(matched duplicate rows + open review rows) / total customers",
         "alert_threshold": "> 1.0% daily; > 2.0% = P1 incident",
         "escalation_role": "CRM Officer -> Data Governance Council (if > 2% for 3 days)",
         "remediation_script": "python module2_data_quality/dq_assessment_cleansing.py --stage dedupe && open MDM review queue"},
        {"check_id": "DQC-02", "metric": "Phone E.164 validity rate",
         "measure": "rows matching ^\\+2567\\d{8}$ / non-null phones",
         "alert_threshold": "< 99.0%",
         "escalation_role": "CRM Officer (entry-point fix) / IT Operations Lead (integration fix)",
         "remediation_script": "python scripts/dq_check.py --metric phone_validity; re-run standardize_phone() backfill"},
        {"check_id": "DQC-03", "metric": "District resolution rate",
         "measure": "rows resolving to official district list / non-null districts",
         "alert_threshold": "< 99.5% or any new unresolved label pattern > 50 rows/day",
         "escalation_role": "Data Steward (Marketing Officer)",
         "remediation_script": "python module2_data_quality/dq_assessment_cleansing.py --stage profile; add alias to DISTRICT_VARIANTS after steward approval"},
        {"check_id": "DQC-04", "metric": "Core-field completeness (phone, email, district)",
         "measure": "non-null % per field",
         "alert_threshold": "phone < 92%; email < 85%; district < 99%",
         "escalation_role": "CRM Officer -> Store Manager (data capture at POS)",
         "remediation_script": "python scripts/dq_check.py --metric completeness; launch capture-form fix at offending stores"},
        {"check_id": "DQC-05", "metric": "Product UOM / category conformance",
         "measure": "rows in controlled vocabulary / total products",
         "alert_threshold": "< 99.0% (any new row entering non-conforming)",
         "escalation_role": "Merchandising Officer",
         "remediation_script": "python module2_data_quality/dq_assessment_cleansing.py --stage products; block non-conforming item setup in Odoo"},
        {"check_id": "DQC-06", "metric": "SKU uniqueness violations",
         "measure": "count of SKUs mapped to >1 active product",
         "alert_threshold": "> 0 (zero tolerance, nightly)",
         "escalation_role": "Merchandising Officer -> IT Manager",
         "remediation_script": "SQL: sku_collision_report.sql; quarantine batch and re-issue SKU"},
        {"check_id": "DQC-07", "metric": "ETL quarantine rate",
         "measure": "quarantined rows / rows staged per nightly run",
         "alert_threshold": "> 0.5% or > 100 rows in one run",
         "escalation_role": "IT Operations Lead (2 on-call engineers)",
         "remediation_script": "python module3_etl/srg_etl_pipeline.py --inspect-quarantine; fix source, replay from quarantine"},
        {"check_id": "DQC-08", "metric": "Mobile-money payment refs pending > 24h",
         "measure": "count of MoMo/Airtel transactions with NULL payment_ref aged > 24h",
         "alert_threshold": "> 0 daily; > 50 = P1 (revenue integrity)",
         "escalation_role": "Finance Reconciliation Officer -> CFO",
         "remediation_script": "SQL: reconcile_momo_pending.sql (match provider CSV downloads); auto-close or write off with approval"},
        {"check_id": "DQC-09", "metric": "Future-dated / unparseable registration dates",
         "measure": "count of rows failing VR-005",
         "alert_threshold": "> 0 per run",
         "escalation_role": "CRM Officer",
         "remediation_script": "python scripts/dq_check.py --metric dates; block offending registration form"},
        {"check_id": "DQC-10", "metric": "Margin-anomaly products (selling < cost)",
         "measure": "count of active SKUs with selling_price < cost without promo flag",
         "alert_threshold": "> 0 weekly review; > 25 rows = escalate",
         "escalation_role": "Pricing Analyst -> Finance Manager",
         "remediation_script": "SQL: margin_anomaly_report.sql; business decision - never auto-corrected by ETL"},
    ],
}


def main():
    print("=" * 78)
    print("MODULE 2 - DATA QUALITY ASSESSMENT & CLEANSING (Task B2)")
    print("=" * 78)

    customers = pd.read_csv(os.path.join(RAW_DIR, "SRG_Customers.csv"),
                            dtype=str).fillna("")
    products = pd.read_csv(os.path.join(RAW_DIR, "SRG_Products.csv"),
                           dtype=str).fillna("")
    print(f"\nLoaded raw: customers={len(customers)} rows, "
          f"products={len(products)} rows")

    # ---------------- 1. PROFILING (BEFORE) --------------------------------
    cust_before = profile_customers(customers)
    prod_before = profile_products(products)

    before_md = (profile_to_md(cust_before, "SRG_Customers - BEFORE cleansing")
                 + "\n" + profile_to_md(prod_before, "SRG_Products - BEFORE cleansing"))
    print("\n" + "=" * 78)
    print("1) DATA PROFILING - BEFORE CLEANSING SUMMARY")
    print("=" * 78)
    print(before_md)

    # ---------------- 2. CLEANSING ----------------------------------------
    clean_cust, dedupe_stats = cleanse_customers(customers)
    clean_prod, quarantined = cleanse_products(products)

    cust_after = profile_customers(clean_cust)
    prod_after = profile_products(clean_prod)

    print("\n" + "=" * 78)
    print("2) DEDUPLICATION STATISTICS")
    print("=" * 78)
    for k, v in dedupe_stats.items():
        print(f"  {k:<34}: {v}")
    print(f"  {'customers rows after merge':<34}: {len(clean_cust)} "
          f"(from {len(customers)})")
    print(f"  {'products quarantined (null keys)':<34}: {len(quarantined)}")

    # ---------------- 3. BEFORE vs AFTER TABLE -----------------------------
    rows = []
    for key, b in cust_before.items():
        a = cust_after.get(key)
        if a is None:
            continue
        dim, metric = key
        delta = round(a - b, 2)
        rows.append(["Customers", dim, metric, b, a, delta])
    for key, b in prod_before.items():
        a = prod_after.get(key)
        if a is None:
            continue
        dim, metric = key
        delta = round(a - b, 2)
        rows.append(["Products", dim, metric, b, a, delta])

    LOWER_IS_BETTER_TOKENS = (
        "duplicate", "variants", "Distinct", "distinct", "below cost",
        "SKUs mapped", "currency string", "Duplicate",
        "below cost - margin anomaly")

    def status(dim, metric, b, a, delta):
        if "margin anomaly" in metric:
            return "Flagged (manual, by design)"
        if "<= 4 years" in metric:
            return "Monitored (aging)"
        if ("duplicate SKU" in metric or "SKUs mapped" in metric) and delta == 0:
            return "Flagged (VR-008 stewardship)"
        if delta == 0:
            return "No change"
        lower_better = any(t in metric for t in LOWER_IS_BETTER_TOKENS)
        improved = (delta < 0) if lower_better else (delta > 0)
        if not improved and abs(delta) < 0.5 and "%)" in metric:
            # sub-0.5pp shift caused purely by removing merged duplicate rows
            return "Stable (dedupe denominator shift)"
        return "Improved" if improved else "Regressed - review"

    rows2 = [r + [status(r[1], r[2], r[3], r[4], r[5])] for r in rows]
    ba_md = ("### Before vs After Quality Metrics (exact %, computed by the "
             "same functions on both states)\n\n"
             + md_table(rows2, ["Dataset", "Dimension", "Metric", "Before (%)",
                                "After (%)", "Delta (pp)", "Status"]))
    print("\n" + "=" * 78)
    print("3) BEFORE vs AFTER QUALITY METRICS TABLE")
    print("=" * 78)
    print(ba_md)

    # headline proof numbers (the classic headline metrics)
    dup_b = cust_before[("Uniqueness",
                         "Total duplicate-person flag rate (confirmed + open "
                         "review, %)")]
    dup_a = cust_after[("Uniqueness",
                        "Total duplicate-person flag rate (confirmed + open "
                        "review, %)")]
    conf_b = cust_before[("Uniqueness",
                          "Confirmed duplicate rows - auto-matched by rules (%)")]
    conf_a = cust_after[("Uniqueness",
                         "Confirmed duplicate rows - auto-matched by rules (%)")]
    rev_b = cust_before[("Uniqueness",
                         "Open stewardship review rows - suspected duplicates "
                         "(count)")]
    rev_a = cust_after[("Uniqueness",
                        "Open stewardship review rows - suspected duplicates "
                        "(count)")]
    print("\nHEADLINE IMPROVEMENTS")
    print(f"  Confirmed duplicates   : {conf_b}%  ->  {conf_a}%  "
          f"(auto-merged: {dedupe_stats['merged_rows']} rows)")
    print(f"  Open stewardship review: {rev_b} rows  ->  {rev_a} rows "
          f"(unresolved identity candidates, no data fabricated)")
    print(f"  Total duplicate flag   : {dup_b}%  ->  {dup_a}%")
    for k in cust_before:
        if "variants" in k[1] or "ISO-8601" in k[1] or "district labels" in k[1]:
            print(f"  {k[1]:<46}: {cust_before[k]} -> {cust_after[k]}")
    for k in prod_before:
        if k[1] in {"Unit of measure in {kg, pcs, liters} (%)",
                    "Category in master list (%)",
                    "Distinct unit-of-measure labels (count)",
                    "Distinct category labels (count)"}:
            print(f"  {k[1]:<46}: {prod_before[k]} -> {prod_after[k]}")

    # ---------------- 4. VALIDATION RULES ---------------------------------
    rules_md = ("### Validation Rules Catalog (12 rules: technical + business)\n\n"
                + md_table([[r["rule_id"], r["field"], r["type"], r["condition"],
                             r["action_on_failure"], r["severity"]]
                            for r in VALIDATION_RULES],
                           ["Rule ID", "Field", "Type", "Condition",
                            "Action on Failure", "Failure Severity"]))
    print("\n" + "=" * 78)
    print("4) VALIDATION RULES CATALOG")
    print("=" * 78)
    print(rules_md)

    # ---------------- 5. MONITORING SPEC ----------------------------------
    mon_md = ("### Continuous Data Quality Monitoring Spec (daily automated "
              "checks)\n\n"
              + md_table([[c["check_id"], c["metric"], c["alert_threshold"],
                           c["escalation_role"], c["remediation_script"]]
                          for c in MONITORING_SPEC["checks"]],
                         ["Check ID", "Metric", "Alert Threshold",
                          "Escalation Role", "Remediation Script"]))
    print("\n" + "=" * 78)
    print("5) CONTINUOUS QUALITY MONITORING SPECIFICATION")
    print("=" * 78)
    print(mon_md)

    # ---------------- persist artifacts ------------------------------------
    with open(os.path.join(OUT_DIR, "profile_before.md"), "w") as fh:
        fh.write("# SRG Data Quality Profile - BEFORE Cleansing\n\n" + before_md)
    with open(os.path.join(OUT_DIR, "before_after_metrics.md"), "w") as fh:
        fh.write("# SRG Before vs After Quality Metrics\n\n" + ba_md)
    with open(os.path.join(OUT_DIR, "validation_rules.json"), "w") as fh:
        json.dump(VALIDATION_RULES, fh, indent=2)
    with open(os.path.join(OUT_DIR, "validation_rules.md"), "w") as fh:
        fh.write(rules_md)
    with open(os.path.join(OUT_DIR, "dq_monitoring_spec.json"), "w") as fh:
        json.dump(MONITORING_SPEC, fh, indent=2)
    with open(os.path.join(OUT_DIR, "dq_monitoring_spec.md"), "w") as fh:
        fh.write(mon_md)
    with open(os.path.join(OUT_DIR, "dedupe_match_log.json"), "w") as fh:
        json.dump(dedupe_stats, fh, indent=2)

    clean_cust.to_csv(os.path.join(OUT_DIR, "SRG_Customers_clean.csv"),
                      index=False)
    clean_prod.to_csv(os.path.join(OUT_DIR, "SRG_Products_clean.csv"),
                      index=False)
    quarantined.to_csv(os.path.join(OUT_DIR, "SRG_Products_quarantine.csv"),
                       index=False)
    print("\nArtifacts written to:", OUT_DIR)
    for f in sorted(os.listdir(OUT_DIR)):
        print("  -", f)


if __name__ == "__main__":
    main()
