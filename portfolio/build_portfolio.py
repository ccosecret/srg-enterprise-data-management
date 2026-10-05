#!/usr/bin/env python3
"""
Build the single written-portfolio PDF for Project Savanna.

    portfolio/build_portfolio.py [--keep-tex]

Pipeline:
  1. assemble body  = cover + contents + executive summary + Parts A–D
  2. assemble appendices A–AA from the full artifacts (headings demoted,
     mermaid blocks replaced with the rendered figures)
  3. pandoc (markdown -> latex, lualatex) with header.tex styling
  4. two extra lualatex passes (TOC / LastPage stability)
  5. audit: find the APPENDICES divider page -> body page count must be <= 40
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PORT = REPO / "portfolio"
BUILD = PORT / "build"
BUILD.mkdir(exist_ok=True)

FIG = PORT / "figures"
BODY = PORT / "body"

# ---------------------------------------------------------------- appendix map
APPENDICES: list[tuple[str, str, list[str]]] = [
    ("A", "Assumptions Register",
     ["docs/A0_assumptions_register.md"]),
    ("B", "EDM Diagnostic — Executive Briefing Memo to the Board",
     ["docs/A1_edm_diagnostic_memo.md"]),
    ("C", "Customer Data Lifecycle Map & DAMA-DMBOK Gap Analysis",
     ["docs/A1_data_lifecycle_map.md"]),
    ("D", "Data Governance Charter, Operating Structure & RACI Matrix",
     ["docs/A2_governance_charter.md"]),
    ("E", "Three Enforceable Data Policies (Access & Classification, Quality, Retention)",
     ["docs/A2_policies.md"]),
    ("F", "Compliance Obligations & Gap Register (DPPA 2019 / GDPR / CCPA)",
     ["docs/A2_compliance_register.md"]),
    ("G", "CFO Rebuttal Memo — The Cost of Inaction",
     ["docs/A2_cfo_memo.md"]),
    ("H", "Architecture Selection — Weighted Trade-Off Decision",
     ["docs/B1_architecture_decision.md"]),
    ("I", "ER Model & Normalization (1NF → 2NF → 3NF)",
     ["docs/B1_er_model.md", "docs/B1_normalization.md"]),
    ("J", "Data Quality Evidence — Profiling, Before/After Metrics, Validation Rules, Monitoring & Root Cause",
     ["docs/B2_stock_variance_root_cause.md",
      "module2_data_quality/output/profile_before.md",
      "module2_data_quality/output/before_after_metrics.md",
      "module2_data_quality/output/validation_rules.md",
      "module2_data_quality/output/dq_monitoring_spec.md"]),
    ("K", "Customer Master Data Management Design",
     ["docs/B3_mdm_design.md"]),
    ("L", "ETL Workflow, Job Diagnosis & ETL vs ELT Decision",
     ["docs/B4_etl_workflow.md", "docs/B4_etl_vs_elt.md", "module3_etl/etl_diagnosis.md"]),
    ("M", "Real-Time Integration Architecture (Footfall & Mobile-Money Streams)",
     ["docs/B4_realtime_architecture.md"]),
    ("N", "Warehouse Data Dictionary (25 Classified Attributes)",
     ["module5_warehouse/data_dictionary.md"]),
    ("O", "KPI Lineage (Monthly Active Customers) & Address-Schema Impact Analysis",
     ["docs/C1_lineage_kpi.md", "docs/C1_impact_analysis.md"]),
    ("P", "Data Catalog Taxonomy & Metadata Tool Evaluation",
     ["docs/C1_catalog_tools.md"]),
    ("Q", "Threat Model & Enterprise Risk Register",
     ["docs/C2_threat_model_risk_register.md"]),
    ("R", "RBAC Matrix, GRANT/REVOKE Test Evidence & Masking Specification",
     ["docs/C2_encryption_masking_spec.md",
      "module4_security/rbac_test_expected_output.md",
      "module4_security/output/masking_demo_output.txt"]),
    ("S", "Data Protection Impact Assessment & Breach Response Plan",
     ["docs/C2_dpia_loyalty_app.md", "docs/C2_breach_response_plan.md"]),
    ("T", "Compliance Audit Checklist & Prioritised Remediation Plan",
     ["docs/C2_compliance_audit_checklist.md"]),
    ("U", "Five Strategic Business Questions & Analytics Workflow",
     ["docs/C3_business_questions.md"]),
    ("V", "Dashboard Specification, Interaction Map & Published Screenshots",
     ["docs/C3_dashboard.md"]),
    ("W", "Executive Insight Brief (Three Findings, Three Actions)",
     ["docs/C3_executive_insight_brief.md"]),
    ("X", "Emerging Technology Evaluation & Analytics Maturity Path",
     ["docs/C3_emerging_tech.md", "docs/C3_analytics_maturity.md"]),
    ("Y", "Integrated 18-Month EDM Strategy Roadmap (Full Plan)",
     ["docs/D1_roadmap_18months.md"]),
    ("Z", "Decision Log (26 Entries)",
     ["docs/D2_decision_log.md"]),
    ("AA", "Red-Team Critique — Full Dossier (15 Findings)",
     ["docs/D2_red_team.md"]),
]

# figure overrides: (file stem, mermaid index) -> png name
FIG_OVERRIDE = {
    ("C1_lineage_kpi", 1): "C1_lineage_kpi_print.png",
    ("B4_realtime_architecture", 1): "B4_realtime_architecture_print.png",
}


def demote_headings(text: str) -> str:
    """Demote ATX headings by two levels (cap 5), fence-aware."""
    out, in_fence, fence_marker = [], False, None
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        m = re.match(r"^(#{1,6})\s", stripped)
        if stripped.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if m and not in_fence:
            lvl = len(m.group(1))
            new = min(lvl + 2, 5)
            out.append("#" * new + stripped[lvl:] + "\n")
        else:
            out.append(line)
    return "".join(out)


def replace_mermaid(stem: str, text: str, seen: dict) -> str:
    """Replace each ```mermaid block with its rendered PNG figure."""
    def sub(m: re.Match) -> str:
        seen[stem] = seen.get(stem, 0) + 1
        idx = seen[stem]
        name = FIG_OVERRIDE.get((stem, idx), f"{stem}_{idx}.png")
        png = FIG / name
        if not png.exists():
            raise SystemExit(f"MISSING FIGURE: {name} (from {stem}.md block {idx})")
        pretty = stem.replace("_", " ")
        return f"\n![The {pretty} diagram ({idx}).](figures/{name})\n"
    return re.sub(r"^```mermaid\n(.*?)^```[ \t]*$", sub, text, flags=re.M | re.S)


def load_md(path: Path, stem_fallback: str, mermaid_seen: dict) -> str:
    raw = path.read_text(encoding="utf-8")
    if path.suffix == ".txt":
        return "```text\n" + raw.rstrip() + "\n```\n"
    stem = path.stem
    raw = replace_mermaid(stem, raw, mermaid_seen) if re.search(r"^```mermaid", raw, re.M) else raw
    return demote_headings(raw)


def assemble() -> Path:
    parts: list[str] = []

    # ---- cover -----------------------------------------------------
    parts.append((BODY / "00_cover.md").read_text(encoding="utf-8"))

    # ---- contents --------------------------------------------------
    parts.append("```{=latex}\n\\tableofcontents\n\\clearpage\n```\n")

    # ---- executive summary (unnumbered section, still in the TOC) ---
    ex = (BODY / "01_executive_summary.md").read_text(encoding="utf-8")
    ex = ex.replace("# Executive Summary", "# Executive Summary {.unnumbered}", 1)
    parts.append(ex)

    # ---- body parts A–D -------------------------------------------
    for p in ("part_A.md", "part_B.md", "part_C.md", "part_D.md"):
        f = BODY / p
        if not f.exists():
            raise SystemExit(f"MISSING BODY FILE: {f}")
        parts.append("\n\\clearpage\n\n" + f.read_text(encoding="utf-8"))

    # ---- appendix divider -----------------------------------------
    parts.append("""```{=latex}
\\clearpage
\\appendix
\\makeatletter
% standard \\appendix letters stop at Z; we have 27 units -> allow AA
\\renewcommand{\\thesection}{\\ifnum\\c@section=27 AA\\else\\@Alph\\c@section\\fi}
\\makeatother
\\thispagestyle{empty}
\\begin{center}
\\vspace*{4.2cm}
{\\sffamily\\bfseries\\fontsize{40}{46}\\selectfont\\color{edmnvy} APPENDICES}\\\\[1.0cm]
{\\color{edmacc}\\rule{0.5\\textwidth}{1.2mm}}\\\\[1.2cm]
{\\sffamily\\Large\\color{edmgray} Appendices A--AA}\\\\[0.7cm]
{\\sffamily\\normalsize\\color{edmgray}
Full registers, policies, matrices, specifications and execution evidence.\\\\[3pt]
Excluded from the 40-page body limit under the submission requirements.}
\\end{center}
\\clearpage
```
""")

    # ---- appendices ------------------------------------------------
    mermaid_seen: dict = {}
    for letter, title, files in APPENDICES:
        # unnumbered: the letter is already in the title ("Appendix A — ...")
        parts.append(f"\n# Appendix {letter} — {title} {{.unnumbered}}\n")
        for rel in files:
            path = REPO / rel
            if not path.exists():
                raise SystemExit(f"MISSING APPENDIX FILE: {rel}")
            parts.append(f"\n\n{load_md(path, path.stem, mermaid_seen)}")

    out = BUILD / "portfolio_all.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"assembled {out} ({out.stat().st_size:,} bytes)")
    return out


def build(all_md: Path) -> Path:
    tex = BUILD / "portfolio.tex"
    pdf = BUILD / "portfolio.pdf"
    cmd = [
        "pandoc", str(all_md),
        "-s", "-f", "markdown", "-t", "latex",
        "--pdf-engine=lualatex",          # sets lualatex template vars (fontspec etc.)
        "-H", str(PORT / "header.tex"),
        "--number-sections",
        "-V", "secnumdepth=2",
        "-V", "documentclass=article",
        "-V", "fontsize=10pt",
        "-V", "mainfont=Liberation Serif",
        "-V", "sansfont=Liberation Sans",
        "-V", "monofont=DejaVu Sans Mono",
        "-V", "geometry=a4paper,top=2.55cm,bottom=2.35cm,left=2.2cm,right=2.2cm,headheight=15pt,headsep=0.55cm,footskip=1.15cm",
        "-V", "colorlinks=true",
        "-V", "linkcolor=edmnvy",
        "-V", "urlcolor=edmacc",
        "-V", "toccolor=edmnvy",
        "-o", str(tex),
    ]
    print("running pandoc ...")
    r = subprocess.run(cmd, cwd=PORT, capture_output=True, text=True)
    if r.returncode != 0 or not tex.exists():
        print(r.stdout[-6000:])
        print(r.stderr[-6000:])
        raise SystemExit("PANDOC FAILED")

    # unicode-math drags in lualatex-math (not installed) and this document has
    # no math — plain fontspec is all we need.
    src = tex.read_text(encoding="utf-8")
    src = src.replace(
        "\\usepackage{unicode-math} % this also loads fontspec",
        "\\usepackage{fontspec}",
    )
    # selnolig (ligature suppression) is not installed; ligatures are fine.
    src = src.replace("  \\usepackage{selnolig}  % disable illegal ligatures", "")
    tex.write_text(src, encoding="utf-8")

    # three lualatex passes (body, TOC, LastPage stability)
    for i in (1, 2, 3):
        r = subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory=build", str(tex)],
            cwd=PORT, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-7000:], r.stderr[-7000:])
            raise SystemExit(f"LUALATEX PASS {i} FAILED")
    print(f"built {pdf} ({pdf.stat().st_size:,} bytes)")
    return pdf


def audit(pdf: Path) -> None:
    r = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True)
    pages = r.stdout.split("\f")
    divider = next((i + 1 for i, pg in enumerate(pages) if re.search(r"\bAPPENDICES\b", pg)), None)
    total = len(pages) - (1 if pages and not pages[-1].strip() else 0)
    print(f"total pages: {total}")
    if divider is None:
        print("AUDIT WARNING: APPENDICES divider not found")
        return
    body_pages = divider - 1
    status = "OK" if body_pages <= 40 else "OVER LIMIT"
    print(f"APPENDICES divider on page {divider}  ->  BODY = {body_pages} pages  [{status}]")
    # spot checks
    checks = {
        "cover registration no.": "2024-08-32939",
        "exec summary": "Executive Summary",
        "dashboard link": "ccosecret.github.io",
        "essay": "reflective essay",
        "budget total": "480,000,000",
        "control total": "252,382,814",
    }
    all_text = "\n".join(pages)
    for label, needle in checks.items():
        print(f"  {'+' if needle in all_text else '-'} {label}")


def main() -> None:
    all_md = assemble()
    pdf = build(all_md)
    audit(pdf)
    if "--keep-tex" not in sys.argv:
        pass  # .tex is kept anyway via --keep-tex (useful for debugging)


if __name__ == "__main__":
    main()
