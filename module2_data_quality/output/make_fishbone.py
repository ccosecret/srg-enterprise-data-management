#!/usr/bin/env python3
"""
Generate the Ishikawa (fishbone) root-cause diagram for the 8.4% book-vs-physical
stock variance (Task B2.4). Emits SVG so the diagram is reproducible from source;
the portfolio build converts this to PNG (see portfolio/build_portfolio.py).

Colour legend distinguishes SYSTEMIC causes (process/design defects that recur by
design) from POINT-OF-ENTRY causes (defects introduced at the moment of capture).
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "stock_variance_fishbone.svg"

SPINE_Y = 430
X0, X1 = 40, 1400          # spine extent
HEAD_X = 1400              # problem box starts here
SYS = "#b3261e"            # systemic  (red)
POE = "#1a56a8"            # point-of-entry (blue)
INK = "#1f2933"
BONE = "#4b5563"

# category label, anchor x on spine, side (-1 above / +1 below), causes[(text, kind)]
CATEGORIES = [
    ("PEOPLE", 330, -1, [
        ("Cashiers edit stock counts by hand", "POE"),
        ("No adjustment approval authority", "SYS"),
        ("Transfers not posted by store teams", "POE"),
    ]),
    ("METHOD", 700, -1, [
        ("No cycle-count calendar", "SYS"),
        ("Returns processed offline, keyed later", "SYS"),
        ("Shrink never audited (theft unlogged)", "SYS"),
    ]),
    ("MEASUREMENT", 1070, -1, [
        ("5 competing product identifiers", "SYS"),
        ("UOM kg / KGS / Kilograms (15.33% non-conformance)", "POE"),
        ("Hand-written count sheets", "POE"),
    ]),
    ("SYSTEMS", 330, 1, [
        ("23 MySQL silos, no stock ledger", "SYS"),
        ("Offline POS sales sync when connectivity returns", "SYS"),
        ("No audit trail on quantity changes", "SYS"),
    ]),
    ("DATA", 700, 1, [
        ("Duplicate SKUs across POS / e-comm / supplier files", "SYS"),
        ("Category typos break like-for-like counts", "POE"),
        ("Supplier Excel variants of same product", "SYS"),
    ]),
    ("ENVIRONMENT", 1070, 1, [
        ("Connectivity loss hours daily", "SYS"),
        ("Power outages — UPS-only tills", "SYS"),
        ("Shop-floor piloting at busy stores", "POE"),
    ]),
]

BONE_LEN_X, BONE_LEN_Y = 130, 260   # bone reaches up/down and back (tail-ward)
TICK_DX, TICK_GAP = 46, 62           # sub-cause ticks branch toward the head


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build() -> str:
    w, h = 1640, 880
    p: list[str] = []
    a = p.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
      f'viewBox="0 0 {w} {h}" font-family="DejaVu Sans, Liberation Sans, Arial, sans-serif">')
    a(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')

    # ---- spine + head ----
    a(f'<defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" '
      f'orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="{INK}"/></marker></defs>')
    a(f'<line x1="{X0}" y1="{SPINE_Y}" x2="{X1}" y2="{SPINE_Y}" stroke="{INK}" '
      f'stroke-width="5" marker-end="url(#arrow)"/>')

    # problem (fish head)
    a(f'<g><rect x="{HEAD_X + 12}" y="{SPINE_Y - 78}" width="216" height="156" rx="14" '
      f'fill="#fdecea" stroke="{SYS}" stroke-width="4"/>')
    a(f'<text x="{HEAD_X + 120}" y="{SPINE_Y - 40}" text-anchor="middle" font-size="26" '
      f'font-weight="bold" fill="{SYS}">PROBLEM</text>')
    for i, line in enumerate(["8.4% book-vs-", "physical stock", "variance", "(unexplained)"]):
        a(f'<text x="{HEAD_X + 120}" y="{SPINE_Y - 4 + i * 30}" text-anchor="middle" '
          f'font-size="23" fill="{INK}">{esc(line)}</text>')
    a('</g>')

    # ---- bones + causes ----
    for name, anchor, side, causes in CATEGORIES:
        bx = anchor                      # where the bone meets the spine
        tip_x = bx - BONE_LEN_X          # tail-ward end of the bone
        tip_y = SPINE_Y + side * BONE_LEN_Y
        a(f'<line x1="{bx}" y1="{SPINE_Y}" x2="{tip_x}" y2="{tip_y}" stroke="{BONE}" '
          f'stroke-width="3.5"/>')
        # category label at the bone tip
        a(f'<rect x="{tip_x - 118}" y="{tip_y - (46 if side < 0 else 6)}" width="236" height="40" '
          f'rx="8" fill="#eef2f7" stroke="{BONE}" stroke-width="2"/>')
        a(f'<text x="{tip_x}" y="{tip_y + (20 if side < 0 else 21) - (14 if side < 0 else 0)}" '
          f'text-anchor="middle" font-size="21" font-weight="bold" fill="{INK}">{name}</text>')
        # sub-cause ticks climbing the bone (parallel text)
        for j, (text, kind) in enumerate(causes):
            frac = (j + 1) / (len(causes) + 1)
            cx = bx + (tip_x - bx) * frac          # point on the bone
            cy = SPINE_Y + (tip_y - SPINE_Y) * frac
            ex, ey = cx + TICK_DX, cy - side * (TICK_GAP - 10)
            colour = SYS if kind == "SYS" else POE
            a(f'<line x1="{cx:.0f}" y1="{cy:.0f}" x2="{ex:.0f}" y2="{ey:.0f}" '
              f'stroke="{colour}" stroke-width="2.5"/>')
            a(f'<text x="{ex + 6}" y="{ey + 5}" font-size="17.5" fill="{INK}">'
              f'{esc(text)}</text>')

    # ---- legend ----
    ly = h - 44
    a(f'<rect x="380" y="{ly - 22}" width="900" height="44" rx="8" fill="#f7f9fb" '
      f'stroke="#cbd5e1"/>')
    a(f'<line x1="404" y1="{ly}" x2="452" y2="{ly}" stroke="{SYS}" stroke-width="4"/>')
    a(f'<text x="462" y="{ly + 6}" font-size="19" fill="{INK}">'
      f'SYSTEMIC — recurring by design (fix the process)</text>')
    a(f'<line x1="852" y1="{ly}" x2="900" y2="{ly}" stroke="{POE}" stroke-width="4"/>')
    a(f'<text x="910" y="{ly + 6}" font-size="19" fill="{INK}">'
      f'POINT-OF-ENTRY — introduced at capture (validate input)</text>')

    a('</svg>')
    return "\n".join(p)


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
