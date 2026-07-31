"""Dashboard package for SentinelGraph AI risk and DataHub views."""

from __future__ import annotations

import html
import json


def build_dashboard(data: dict) -> str:
    """Build a lightweight HTML dashboard for the analysis results."""
    dataset = data.get("dataset")
    findings = data.get("findings", [])
    risk = data.get("risk")
    impact = data.get("impact")
    recommendations = data.get("recommendations", [])
    lineage = data.get("lineage")
    ai_summary = data.get("ai_summary", "")
    analyst_answers = data.get("analyst_answers", {})
    finding_rows = "".join(
        f"<tr><td>{html.escape(f.category)}</td><td>{html.escape(f.severity)}</td><td>{html.escape(f.description)}</td></tr>"
        for f in findings
    )
    recommendation_items = "".join(f"<li>{html.escape(rec.technical_summary)}</li>" for rec in recommendations)
    downstream_assets = []
    if impact:
        downstream_assets = getattr(impact, "affected_downstream_assets", []) or getattr(impact, "affected_datasets", [])
    lineage_edges = getattr(lineage, "edges", []) if lineage else []
    chat_payload = json.dumps(analyst_answers).replace("</", "<\\/")
    downstream_pills = "".join(f'<span class="pill">{html.escape(asset)}</span>' for asset in downstream_assets) or "No downstream assets found."

    return f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>SentinelGraph AI Agent Dashboard</title>
<style>
body {{ margin: 0; font-family: Arial, sans-serif; color: #17202a; background: #f6f8fa; }}
header {{ background: #16213e; color: white; padding: 28px 36px; }}
main {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }}
.card {{ background: white; border: 1px solid #d8dee4; border-radius: 8px; padding: 18px; }}
.metric {{ font-size: 34px; font-weight: 700; }}
.label {{ color: #57606a; font-size: 13px; text-transform: uppercase; }}
.bar {{ height: 14px; background: #d0d7de; border-radius: 999px; overflow: hidden; }}
.bar span {{ display: block; height: 100%; background: #cf222e; width: {risk.overall_score if risk else 0}%; }}
table {{ width: 100%; border-collapse: collapse; }}
td, th {{ border-bottom: 1px solid #d8dee4; padding: 10px; text-align: left; vertical-align: top; }}
.pill {{ display: inline-block; background: #fff8c5; border: 1px solid #d4a72c; border-radius: 999px; padding: 4px 10px; margin: 3px; }}
button {{ border: 1px solid #0969da; background: #0969da; color: white; border-radius: 6px; padding: 9px 12px; cursor: pointer; margin: 4px 4px 4px 0; }}
#answer {{ min-height: 72px; background: #f6f8fa; border-radius: 6px; padding: 12px; }}
</style>
</head>
<body>
  <header>
    <h1>SentinelGraph: An Autonomous Data Security Agent for DataHub</h1>
    <p>SentinelGraph reads DataHub metadata, reasons about lineage and risk, and writes actionable findings back to DataHub.</p>
  </header>
  <main>
    <section class=\"grid\">
      <div class=\"card\"><div class=\"label\">Dataset</div><div class=\"metric\">{html.escape(dataset.name if dataset else 'n/a')}</div></div>
      <div class=\"card\"><div class=\"label\">Risk Score</div><div class=\"metric\">{risk.overall_score if risk else 'n/a'}</div><div class=\"bar\"><span></span></div></div>
      <div class=\"card\"><div class=\"label\">Threat Level</div><div class=\"metric\">{html.escape(risk.threat_level if risk else 'n/a')}</div></div>
      <div class=\"card\"><div class=\"label\">Blast Radius</div><div class=\"metric\">{impact.blast_radius if impact else 0}</div></div>
    </section>
    <section class=\"card\">
      <h2>AI Analyst Summary</h2>
      <p>{html.escape(ai_summary)}</p>
    </section>
    <section class=\"grid\">
      <div class=\"card\">
        <h2>Findings</h2>
        <table><thead><tr><th>Category</th><th>Severity</th><th>Description</th></tr></thead><tbody>{finding_rows}</tbody></table>
      </div>
      <div class=\"card\">
        <h2>Lineage Blast Radius</h2>
        <p>{len(lineage_edges)} lineage edge(s) analyzed.</p>
        <p>{downstream_pills}</p>
      </div>
    </section>
    <section class=\"card\">
      <h2>Recommendations</h2>
      <ul>{recommendation_items}</ul>
    </section>
    <section class=\"card\">
      <h2>Ask the AI Analyst</h2>
      <button data-key=\"riskiest_dataset\">Riskiest finance dataset</button>
      <button data-key=\"pii_exposure\">Datasets with PII exposure</button>
      <button data-key=\"lineage_blast_radius\">Lineage blast radius</button>
      <div id=\"answer\">Choose a question.</div>
    </section>
  </main>
  <script>
  const answers = {chat_payload};
  document.querySelectorAll("button[data-key]").forEach((button) => {{
    button.addEventListener("click", () => {{
      document.getElementById("answer").textContent = answers[button.dataset.key] || "No answer generated for this prompt.";
    }});
  }});
  </script>
</body>
</html>"""
