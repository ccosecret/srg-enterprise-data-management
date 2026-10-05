#!/usr/bin/env python3
"""
================================================================================
 MODULE 1 - SYNTHETIC DATASET GENERATION
 Savanna Retail Group (SRG) Capstone - Enterprise Data Management
================================================================================
 Generates three DELIBERATELY DIRTY CSV files that replicate the defect profile
 of the instructor-provided assignment files:

   1. SRG_Customers.csv  - 5,000 rows  (~23% duplicates, dirty phone/district/
                            date/gender formats, nulls)
   2. SRG_Products.csv   - 1,200 rows  (unit-of-measure inconsistencies,
                            category typos, duplicate SKUs with divergent names)
   3. SRG_Sales.csv      - 10,000 rows (negative quantities = returns, null
                            mobile-money payment refs, mixed currency strings)

 Design notes
 ------------
 * Deterministic: fixed RNG seed -> reproducible byte-identical outputs.
 * Defect injection is tracked internally (truth labels) but truth labels are
   NOT written to the CSVs, so Module 2 profiling must discover defects the
   same way a real consultant would (heuristics + reference lists).
 * Defect counters are printed as an injection report (used as ground truth in
   the Module 2 before/after proof).

 Usage:  python generate_srg_datasets.py
 Output: ./output/SRG_Customers.csv, ./output/SRG_Products.csv,
         ./output/SRG_Sales.csv, ./output/injection_report.json
================================================================================
"""

import json
import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

SEED = 20261005
random.seed(SEED)
np.random.seed(SEED)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "output")
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------------------------------------------------------------------
# Reference data: official Ugandan districts (subset covering SRG trading areas)
# plus realistic name pools
# ------------------------------------------------------------------------------
OFFICIAL_DISTRICTS = [
    "Kampala", "Wakiso", "Mukono", "Jinja", "Gulu", "Mbarara", "Mbale",
    "Lira", "Soroti", "Masaka", "Hoima", "Arua", "Kabale", "Kasese",
    "Fort Portal", "Masindi", "Luwero", "Mpigi", "Iganga", "Tororo",
    "Kumi", "Kitgum", "Nebbi", "Bushenyi", "Kabarole", "Bundibugyo",
    "Kalangala", "Mityana", "Kayunga", "Nakasongola", "Kiboga", "Sembabule",
    "Rakai", "Isingiro", "Kiruhura", "Lyantonde", "Mbarara City",
    "Gulu City", "Jinja City", "Mbale City", "Arua City", "Entebbe",
]

# Common dirty variants actually seen in Ugandan retail/CRM extracts.
# Keys are the variant, values are the canonical district.
DISTRICT_VARIANTS = {
    "kampala": "Kampala", "kla": "Kampala", "Kla": "Kampala",
    "KAMPALA": "Kampala", "Kampala City": "Kampala", "Kampala-City": "Kampala",
    "kampala district": "Kampala", "Kampala Region": "Kampala",
    "Kampala ": "Kampala", "kampala": "Kampala", "Kampala (Central)": "Kampala",
    "jinja": "Jinja", "Jinjja": "Jinja", "JINJA": "Jinja", "Jinja Town": "Jinja",
    "Jinja District": "Jinja", "jinji": "Jinja", "Jinja City": "Jinja",
    "mbarara": "Mbarara", "Mbaraa": "Mbarara", "Mbararra": "Mbarara",
    "Mbarara City": "Mbarara", "MBARARA": "Mbarara", "Mbarara Town": "Mbarara",
    "gulu": "Gulu", "Gulu City": "Gulu", "GULLU": "Gulu", "Gulu District": "Gulu",
    "Guluu": "Gulu",
    "wakiso": "Wakiso", "Wakiso District": "Wakiso", "Wakisio": "Wakiso",
    "entebbe": "Entebbe", "Enteba": "Entebbe", "Entebbe City": "Entebbe",
    "mukono": "Mukono", "Mukko": "Mukono", "Mukkono": "Mukono",
    "masaka": "Masaka", "Masacka": "Masaka",
    "mbale": "Mbale", "Mballa": "Mbale",
    "lira": "Lira", "Lira District": "Lira",
    "kabale": "Kabale", "Kabale District": "Kabale",
    "hoima": "Hoima", "Homa": "Hoima",
    "arua": "Arua", "Arua City": "Arua",
    "soroti": "Soroti", "Soroti District": "Soroti",
    "fort portal": "Fort Portal", "FortPortal": "Fort Portal",
    "Fort-Portal": "Fort Portal", "Kabarole": "Fort Portal",
    "kasese": "Kasese", "Kisese": "Kasese",
    "luwero": "Luwero", "Luweero": "Luwero", "Luwero District": "Luwero",
    "iganga": "Iganga", "Iganga Town": "Iganga",
    "tororo": "Tororo", "Torroro": "Tororo",
    "bushenyi": "Bushenyi", "Bushenyi District": "Bushenyi",
    "masindi": "Masindi", "Masindi District": "Masindi",
    "mpigi": "Mpigi", "Mpigi District": "Mpigi",
    "mityana": "Mityana", "Mityanna": "Mityana",
    "kayunga": "Kayunga", "Kalangala": "Kalangala", "Kumi": "Kumi",
    "kitgum": "Kitgum", "nebbi": "Nebbi", "isingiro": "Isingiro",
    "kiruhura": "Kiruhura", "rakai": "Rakai", "sembabule": "Sembabule",
    "nakasongola": "Nakasongola", "kiboga": "Kiboga",
    "lyantonde": "Lyantonde", "bundibugyo": "Bundibugyo",
    "kabarole district": "Fort Portal",
    # genuinely invalid / non-district place names (must be flagged)
    "Kampala CBD": None, "Central": None, "Upcountry": None, "N/A": None,
    "Unknown": None, "Kampala1": None, "  ": None, "Rural": None,
    "Somewhere": None, "Head Office": None, "NA": None, "none": None,
}

FIRST_NAMES = [
    "Mary", "John", "Grace", "Peter", "Sarah", "David", "Jane", "Brian",
    "Agnes", "Samuel", "Dorothy", "Ronald", "Catherine", "Michael", "Esther",
    "Joseph", "Rebecca", "Daniel", "Florence", "Robert", "Juliet", "Francis",
    "Naomi", "Stephen", "Ruth", "Emmanuel", "Beatrice", "Andrew", "Irene",
    "Patrick", "Joan", "Isaac", "Harriet", "Timothy", "Mercy", "Godfrey",
    "Sheila", "Collins", "Phoebe", "Alexander", "Deborah", "Henry", "Betty",
    "Christopher", "Rosemary", "Kato", "Namutebi", "Ssemakula", "Nakiganda",
    "Wasswa", "Nabirye", "Okello", "Achieng", "Mugisha", "Tumusiime",
    "Byaruhanga", "Kyomuhendo", "Kizza", "Nankya", "Ouma", "Atim",
]

LAST_NAMES = [
    "Nakato", "Mukasa", "Ssemakula", "Nakiganda", "Wasswa", "Nabirye",
    "Okello", "Achieng", "Mugisha", "Tumusiime", "Byaruhanga", "Kyomuhendo",
    "Kizza", "Nankya", "Ouma", "Atim", "Ssekandi", "Namubiru", "Kafeero",
    "Lubega", "Nabbanja", "Ssimbwa", "Wanyama", "Kyebambe", "Nakayiza",
    "Tendo", "Ssebugwawo", "Mubiru", "Kamoga", "Nalubega", "Ssempebwa",
    "Olweny", "Atukunda", "Ninsiima", "Katusiime", "Ahabwe", "Munezero",
    "Guma", "Ssentongo", "Kibirige", "Nsereko", "Butime", "Kambale",
]

MALE_NAMES = FIRST_NAMES[:20] + ["Kato", "Wasswa", "Okello", "Mugisha",
                                 "Ssemakula", "Byaruhanga", "Kizza", "Ouma",
                                 "Ssekandi", "Lubega", "Ssimbwa", "Mubiru",
                                 "Kamoga", "Ssempebwa", "Olweny", "Guma",
                                 "Ssentongo", "Kibirige", "Nsereko", "Butime"]
FEMALE_NAMES = FIRST_NAMES[20:40] + ["Nakiganda", "Nabirye", "Nakayiza",
                                     "Namubiru", "Nabbanja", "Wanyama",
                                     "Nalubega", "Ninsiima", "Katusiime",
                                     "Munezero", "Kambale", "Namutebi",
                                     "Nankya", "Atim", "Kyomuhendo"]

PRODUCT_NAMES = {
    "Beverages": ["Coca-Cola 500ml", "Pepsi 500ml", "Krest Bitter Lemon",
                  "Sprite 300ml", "Fanta Orange 500ml", "Roberts Milk 1L",
                  "Brookside Fresh Milk 500ml", "Nile Beer 500ml", "Bell Lager",
                  "Mountain Gorilla Water 1L", "Minute Maid 400ml",
                  "Array Juice 250ml", "Twins Tea 250g", "Nescafe 100g"],
    "Grains & Cereals": ["Kakira Sugar 1kg", "Maize Flour 2kg", "Rice 1kg",
                         "Wheat Flour 2kg", "Porridge Flour 500g",
                         "Sorghum 1kg", "Beans 1kg", "Maize Grains 1kg"],
    "Snacks": ["Britania Cream Cracker", "Nice Biscuits 100g",
               "Supermatch Crisps", "Kabala Groundnuts 200g",
               "Sims Chips 150g", "Marlboro Biscuits", "Tropical Heat Nuts"],
    "Household": ["Sunlight Soap 800g", "Baking Soda 500g", "Jik 1L",
                  "Kabwe Detergent 1kg", "Toilet Paper 4 Pack",
                  "Muruchu Cooking Oil 3L", "Kimbo Fat 500g",
                  "Candles 6 Pack"],
    "Personal Care": ["Colgate Toothpaste 100ml", "Imperial Leather Soap",
                      "Nice & Lovely Lotion 200ml", "Always Sanitary Pads",
                      "Head & Shoulders 400ml", "Vaseline Petroleum Jelly",
                      "Dettol Antiseptic 250ml"],
    "Stationery": ["Exercise Book 200pg", "Bic Pen Blue", "A4 Paper 500sh",
                   "Stabilo Highlighter", "Mathematical Set", "Ruler 30cm"],
}

UNIT_POOL = ["kg", "KGS", "Kilograms", "kilogram", "kgs", "g",
             "pcs", "Pieces", "piece", "pc", "PCE", "boxes",
             "liters", "Litres", "L", "ml", "bottles"]

CATEGORY_DIRTY = {
    "Beverages": ["Beverages", "Beverage", "Bvages", "Bevages", "BEVERAGES"],
    "Grains & Cereals": ["Grains & Cereals", "Grains", "Grains and Cereals",
                         "Grains&Cereals", "Grains & cereal"],
    "Snacks": ["Snacks", "Snack", "Sncks", "SNACKS"],
    "Household": ["Household", "House hold", "Household Items", "Houshold",
                  "HOUSEHOLD"],
    "Personal Care": ["Personal Care", "Percare", "PersonalCare",
                      "Personal care ", "PERSONAL CARE"],
    "Stationery": ["Stationery", "Stationary", "Statio nery", "STATIONERY"],
}

STORE_IDS = [f"ST{str(i).zfill(2)}" for i in range(1, 24)]  # 23 stores
ECOM_STORE = "ECOM01"

PAYMENT_METHODS = ["MTN MoMo", "Airtel Money", "Card", "Cash",
                   "MTN Mobile Money", "AirtelMoney", "momo", "CASH"]

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------


def dirty_phone(rng) -> str:
    """Return a phone number in one of several inconsistent formats."""
    prefix = rng.choice(["77", "70", "75", "78", "79", "71", "72", "73", "74"])
    subscriber = "".join(str(rng.randint(0, 9)) for _ in range(7))
    national = f"0{prefix}{subscriber}"          # 07XXXXXXXX (10 digits)
    e164 = f"+256{prefix}{subscriber}"           # +2567XXXXXXXX
    no_zero = f"{prefix}{subscriber}"            # 7XXXXXXXX (missing leading 0)
    fmt = rng.choices(
        ["e164", "national", "256_no_plus", "no_leading_zero", "spaced",
         "dashed", "null"],
        weights=[22, 26, 14, 12, 10, 8, 8], k=1)[0]
    if fmt == "e164":
        return e164
    if fmt == "national":
        return national
    if fmt == "256_no_plus":
        return f"256{prefix}{subscriber}"
    if fmt == "no_leading_zero":
        return no_zero
    if fmt == "spaced":
        return f"+256 {prefix} {subscriber[:3]} {subscriber[3:]}"
    if fmt == "dashed":
        return f"0{prefix}-{subscriber[:3]}-{subscriber[3:]}"
    return ""  # null


def dirty_date(rng, base: datetime) -> str:
    """Registration date in mixed formats: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY."""
    fmt = rng.choices(["iso", "slash", "dash", "null"],
                      weights=[55, 30, 10, 5], k=1)[0]
    if fmt == "iso":
        return base.strftime("%Y-%m-%d")
    if fmt == "slash":
        return base.strftime("%d/%m/%Y")
    if fmt == "dash":
        return base.strftime("%d-%m-%Y")
    return ""


def maybe_corrupt_name(name: str, rng) -> str:
    """Fuzzy variation: typos, case changes, extra spaces, initials."""
    mode = rng.choices(["keep", "typo", "case", "spaces", "initial"],
                       weights=[55, 18, 12, 9, 6], k=1)[0]
    if mode == "typo" and len(name) > 3:
        i = rng.randint(0, len(name) - 2)
        return name[:i] + rng.choice("abcdefghijklmnopqrstuvwxyz") + name[i + 1:]
    if mode == "case":
        return name.upper() if rng.random() < 0.5 else name.lower()
    if mode == "spaces":
        return "  " + name.strip() + " "
    if mode == "initial":
        parts = name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}. {parts[-1]}"
        return name
    return name


def make_full_name(gender: str, rng) -> str:
    pool = MALE_NAMES if gender == "M" else FEMALE_NAMES
    first = rng.choice(pool)
    last = rng.choice(LAST_NAMES)
    order = rng.choices(["FL", "LF", "single"], weights=[78, 16, 6], k=1)[0]
    if order == "FL":
        return f"{first} {last}"
    if order == "LF":
        return f"{last} {first}"
    return first


def make_email(name: str, rng) -> str:
    if rng.random() < 0.06:
        return ""  # missing email
    parts = [p for p in name.replace(".", "").split() if p]
    if not parts:
        parts = ["user"]
    handle = ".".join(p.lower() for p in parts[:2])
    domain = rng.choice(["gmail.com", "yahoo.com", "outlook.com",
                         "hotmail.com", "srg.co.ug", "mail.com"])
    style = rng.random()
    if style < 0.15:
        handle = handle + str(rng.randint(1, 99))
    if style < 0.22:
        handle = handle.replace(".", "")
    # occasional malformed email (missing @ / missing TLD)
    bad = rng.random()
    if bad < 0.04:
        return f"{handle}{domain}"                 # missing @
    if bad < 0.07:
        return f"{handle}@{domain.split('.')[0]}"  # missing TLD
    if bad < 0.10:
        return f" {handle}@{domain} "              # padded
    return f"{handle}@{domain}"


# ==============================================================================
# 1) SRG_Customers.csv  (5,000 rows, ~23% duplicates)
# ==============================================================================
def generate_customers(n: int = 5000) -> pd.DataFrame:
    rng = random.Random(SEED)
    n_unique = int(n * 0.77)          # 3,850 base records
    n_dupes = n - n_unique            # 1,150 duplicate rows (~23%)

    base_rows = []
    for i in range(n_unique):
        gender = rng.choices(["M", "F", ""], weights=[47, 48, 5], k=1)[0]
        gender_label = {"M": "Male", "F": "Female", "": ""}[gender]
        name = make_full_name(gender or "M", rng)
        reg = datetime(2021, 1, 1) + timedelta(days=rng.randint(0, 1750))
        district = rng.choices(
            [d for d in OFFICIAL_DISTRICTS],
            weights=([26, 14, 10, 9, 7, 7, 5, 3, 3, 3, 2, 2, 2] +
                     [1] * (len(OFFICIAL_DISTRICTS) - 13)),
            k=1)[0]
        # inject dirty district variants (~18% of records)
        if rng.random() < 0.18:
            inv = [k for k, v in DISTRICT_VARIANTS.items()
                   if v is None or v != district]
            # pick a variant OF THIS district if one exists, else any variant
            own = [k for k, v in DISTRICT_VARIANTS.items() if v == district]
            district = rng.choice(own) if (own and rng.random() < 0.7) else \
                rng.choice(inv)
        base_rows.append({
            "full_name": name,
            "phone_number": dirty_phone(rng),
            "email": make_email(name, rng),
            "district": district,
            "registration_date": dirty_date(rng, reg),
            "gender": rng.choices(
                [gender_label, gender, gender_label + " ",
                 "" if gender else ""],
                weights=[64, 20, 6, 10], k=1)[0],
        })

    rows = list(base_rows)
    # --- duplicate injection: clone a base row and fuzz it ---
    dupe_report = {"fuzzy_name_variants": 0, "phone_variants": 0,
                   "exact_copies": 0, "deleted_nulls": 0}
    for _ in range(n_dupes):
        src = dict(rng.choice(base_rows))
        fuzz = rng.random()
        if fuzz < 0.55:                      # fuzzy name (typo/case/spacing)
            src["full_name"] = maybe_corrupt_name(src["full_name"], rng)
            dupe_report["fuzzy_name_variants"] += 1
        if rng.random() < 0.70:              # re-roll phone format (same number)
            p = src["phone_number"]
            if p:
                digits = "".join(c for c in p if c.isdigit())
                if len(digits) >= 9:
                    tail = digits[-9:]        # 07XXXXXXXX or 7XXXXXXXX...
                    tail = tail[-9:]
                    sub = tail[-8:] if len(tail) == 9 else tail
                    src["phone_number"] = dirty_phone(rng)  # format churn
                    # keep same subscriber digits
                    prefix = tail[1:3] if tail.startswith("0") else tail[:2]
                    subscriber = tail[-7:]
                    alt = rng.choices(
                        ["e164", "national", "256_no_plus", "no_zero", "sp"],
                        weights=[30, 30, 20, 15, 5], k=1)[0]
                    src["phone_number"] = {
                        "e164": f"+256{prefix}{subscriber}",
                        "national": f"0{prefix}{subscriber}",
                        "256_no_plus": f"256{prefix}{subscriber}",
                        "no_zero": f"{prefix}{subscriber}",
                        "sp": f"+256 {prefix} {subscriber[:3]} {subscriber[3:]}",
                    }[alt]
                    dupe_report["phone_variants"] += 1
        else:
            dupe_report["exact_copies"] += 1
        if rng.random() < 0.10:              # duplicate loses its phone/email
            src["phone_number"] = ""
            dupe_report["deleted_nulls"] += 1
        rows.append(src)

    rng.shuffle(rows)
    df = pd.DataFrame(rows, columns=[
        "full_name", "phone_number", "email", "district",
        "registration_date", "gender"])
    df.insert(0, "customer_id",
              [f"CUST{str(100001 + i)}" for i in range(len(df))])
    return df, dupe_report


# ==============================================================================
# 2) SRG_Products.csv  (1,200 rows)
# ==============================================================================
def generate_products(n: int = 1200) -> pd.DataFrame:
    rng = random.Random(SEED + 1)
    # Final file = base products + duplicate-SKU rows + null-key staging rows
    n_null = int(n * 0.03)        # 36 null-key rows
    n_dupe_sku = int(n * 0.06)    # 72 duplicate-SKU rows
    n_base = n - n_null - n_dupe_sku   # 1,092 clean-ish base rows
    cats = list(CATEGORY_DIRTY.keys())
    rows = []
    used_names = []
    for i in range(n_base):
        cat = rng.choice(cats)
        name = rng.choice(PRODUCT_NAMES[cat])
        # occasionally reuse a product family member so names repeat naturally
        if used_names and rng.random() < 0.25:
            name = rng.choice(used_names)
        used_names.append(name)
        base_sku = (name[:3].upper().replace(" ", "") +
                    str(rng.randint(1000, 9999)))
        cost = rng.choice([500, 750, 1000, 1500, 2000, 2500, 3000, 4500,
                           5000, 7500, 10000, 15000, 20000, 35000, 50000])
        # 5% of products have selling price below cost (margin anomaly)
        sell = cost * rng.choice([1.1, 1.15, 1.2, 1.25, 1.3, 1.5, 1.8])
        if rng.random() < 0.05:
            sell = cost * rng.uniform(0.6, 0.95)
        rows.append({
            "product_id": f"PRD{str(200001 + i)}",
            "sku": base_sku,
            "product_name": name,
            "category": rng.choice(CATEGORY_DIRTY[cat]),
            "unit_of_measure": rng.choice(UNIT_POOL),
            "cost_ugx": round(cost, 2),
            "selling_price_ugx": round(sell, 2),
        })

    # --- duplicate SKUs pointing to slightly different product names (~6%) ---
    for _ in range(n_dupe_sku):
        src = rng.choice(rows)
        clone = dict(src)
        nm = src["product_name"]
        # divergent name: typo or size/variant difference
        if rng.random() < 0.5 and len(nm) > 4:
            pos = rng.randint(1, len(nm) - 2)
            clone["product_name"] = nm[:pos] + rng.choice("abcdefghijklmnopqrstuvwxyz") + nm[pos + 1:]
        else:
            clone["product_name"] = nm + rng.choice([" 500ml", " 1kg",
                                                     " (Large)", " XL"])
        clone["product_id"] = f"PRD{str(200001 + len(rows))}"
        clone["category"] = rng.choice(
            CATEGORY_DIRTY.get(
                next((c for c, v in CATEGORY_DIRTY.items()
                      if src["category"] in v), "Beverages"),
                [src["category"]]))
        clone["unit_of_measure"] = rng.choice(UNIT_POOL)
        rows.append(clone)

    # --- 3% fully null-key rows (staging defect reproduced) ---
    for _ in range(n_null):
        rows.append({
            "product_id": None,
            "sku": rng.choice(["", None, " "]),
            "product_name": rng.choice(["", None]),
            "category": rng.choice(["", None, "Unknown"]),
            "unit_of_measure": rng.choice(["", None]),
            "cost_ugx": rng.choice(["", None, "N/A"]),
            "selling_price_ugx": rng.choice(["", None, "N/A"]),
        })

    df = pd.DataFrame(rows)
    # ~4% free-text prices with currency notation inside the CSV
    for idx in df.sample(frac=0.04, random_state=SEED).index:
        v = df.at[idx, "selling_price_ugx"]
        if isinstance(v, (int, float)):
            df.at[idx, "selling_price_ugx"] = rng.choice(
                [f"UGX {v:,.0f}", f"UGX{v:.0f}", f"{v:,.0f}"])
    return df


# ==============================================================================
# 3) SRG_Sales.csv  (10,000 sample rows)
# ==============================================================================
def generate_sales(customers: pd.DataFrame, products: pd.DataFrame,
                   n: int = 10000) -> pd.DataFrame:
    rng = random.Random(SEED + 2)
    cust_ids = [c for c in customers["customer_id"].tolist() if c]
    prod = products[products["product_id"].notna()].copy()
    prod["selling_price_ugx"] = pd.to_numeric(
        prod["selling_price_ugx"].astype(str).str.replace(r"[^\d.]", "",
                                                          regex=True),
        errors="coerce").fillna(1000.0)

    start = datetime(2024, 7, 1)
    rows = []
    for i in range(n):
        ts = start + timedelta(minutes=rng.randint(0, 60 * 24 * 180))
        p = prod.iloc[rng.randint(0, len(prod) - 1)]
        qty = rng.choices([1, 2, 3, 4, 5, -1, -2],
                          weights=[45, 25, 14, 8, 3, 3, 2], k=1)[0]
        price = float(p["selling_price_ugx"])
        method = rng.choices(
            ["MTN MoMo", "Airtel Money", "Card", "Cash"],
            weights=[38, 22, 18, 22], k=1)[0]
        # null payment_ref for mobile money (~18% of the time)
        if method in ("MTN MoMo", "Airtel Money") and rng.random() < 0.18:
            ref = ""
        else:
            ref = rng.choice([
                f"MP{rng.randint(100000000, 999999999)}",
                f"AM{rng.randint(100000000, 999999999)}",
                f"AUTH{rng.randint(10000, 99999)}",
                f"CASH-{rng.randint(1000, 9999)}",
            ])
        # mixed currency strings for unit_price (~10%)
        if rng.random() < 0.10:
            unit_price = rng.choice([f"UGX {price:,.0f}", f"UGX{price:.0f}",
                                     f"{price:,.0f}", str(price)])
        else:
            unit_price = price
        rows.append({
            "transaction_id": f"TXN{str(90000001 + i)}",
            "store_id": rng.choices(STORE_IDS + [ECOM_STORE],
                                    weights=[1] * 23 + [6], k=1)[0],
            "customer_id": rng.choice(cust_ids) if rng.random() < 0.92 else "",
            "product_id": p["product_id"],
            "quantity": qty,
            "unit_price": unit_price,
            "payment_method": rng.choices(
                PAYMENT_METHODS,
                weights=[26, 16, 4, 16, 14, 10, 8, 6], k=1)[0],
            "payment_ref": ref,
            "transaction_timestamp": ts.strftime("%Y-%m-%d %H:%M:%S")
            if rng.random() < 0.85 else ts.strftime("%d/%m/%Y %H:%M"),
        })
    return pd.DataFrame(rows)


# ==============================================================================
# Main
# ==============================================================================
def main():
    print("=" * 78)
    print("MODULE 1 - SRG SYNTHETIC DIRTY DATASET GENERATION")
    print("=" * 78)

    customers, dupe_report = generate_customers()
    products = generate_products()
    sales = generate_sales(customers, products)

    customers.to_csv(os.path.join(OUT_DIR, "SRG_Customers.csv"), index=False)
    products.to_csv(os.path.join(OUT_DIR, "SRG_Products.csv"), index=False)
    sales.to_csv(os.path.join(OUT_DIR, "SRG_Sales.csv"), index=False)

    report = {
        "seed": SEED,
        "customers": {
            "rows": len(customers),
            "duplicate_rows_injected": 1150,
            "duplicate_pct": round(1150 / len(customers) * 100, 2),
            **dupe_report,
            "null_phone": int((customers["phone_number"].fillna("") == "").sum()),
            "null_email": int((customers["email"].fillna("") == "").sum()),
            "null_district": int((customers["district"].fillna("") == "").sum()),
            "null_gender": int((customers["gender"].fillna("") == "").sum()),
        },
        "products": {
            "rows": len(products),
            "null_key_rows": int(products["product_id"].isna().sum()),
            "duplicate_sku_rows": int(
                products["sku"].dropna().duplicated(keep=False).sum()),
        },
        "sales": {
            "rows": len(sales),
            "negative_qty_rows": int((sales["quantity"] < 0).sum()),
            "null_payment_ref_rows": int(
                (sales["payment_ref"].fillna("") == "").sum()),
            "currency_string_unit_price": int(
                sales["unit_price"].astype(str).str.contains("UGX|,",
                                                             regex=True).sum()),
        },
    }
    with open(os.path.join(OUT_DIR, "injection_report.json"), "w") as fh:
        json.dump(report, fh, indent=2)

    print(f"Customers  : {report['customers']['rows']:>6} rows "
          f"({report['customers']['duplicate_pct']}% duplicates injected)")
    print(f"Products   : {report['products']['rows']:>6} rows")
    print(f"Sales      : {report['sales']['rows']:>6} rows")
    print(json.dumps(report, indent=2))
    print("=" * 78)


if __name__ == "__main__":
    main()
