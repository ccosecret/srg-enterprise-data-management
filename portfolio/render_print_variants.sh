#!/usr/bin/env bash
# Render vertical ("print") variants of ultra-wide diagrams for PDF embedding,
# and re-render C1_catalog at natural size (it was clipped).
set -u
R=/home/cc_osecret/Documents/repo_clone
F=$R/portfolio/figures
T=/tmp/opencode/figs
mkdir -p "$T"
cd /tmp/opencode/pptr

for stem in C1_lineage_kpi C2_threat_model_risk_register C3_analytics_maturity B4_realtime_architecture B4_etl_vs_elt; do
  sed -n '/^```mermaid$/,/^```$/p' "$R/docs/$stem.md" | sed '1d;$d' \
    | sed -E 's/^(flowchart|graph) LR/\1 TB/; s/^(flowchart|graph) RL/\1 TB/' > "$T/${stem}_print.mmd"
  node shots.js mmd "$T/${stem}_print.mmd" "$F/${stem}_print.png" 1100
done

# C1_catalog: quadrant chart — render at natural dimensions
sed -n '/^```mermaid$/,/^```$/p' "$R/docs/C1_catalog_tools.md" | sed '1d;$d' > "$T/C1_catalog_tools_1.mmd"
node shots.js mmd "$T/C1_catalog_tools_1.mmd" "$F/C1_catalog_tools_1.png" 900

echo "=== variants ==="
file "$F"/*_print.png "$F/C1_catalog_tools_1.png" | sed -E 's/.*PNG image data, //;s/8-bit.*//'
