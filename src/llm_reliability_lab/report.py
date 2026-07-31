from html import escape

from .models import EvalReport


def render_html(report: EvalReport) -> str:
    rows = []
    for case in report.cases:
        status = "PASS" if case.passed else "FAIL"
        failures = ", ".join(case.failures) or "-"
        rows.append(
            "<tr>"
            f"<td>{escape(case.id)}</td><td class='{status.lower()}'>{status}</td>"
            f"<td>{case.score:.2%}</td><td>{case.citation_precision:.2%}</td>"
            f"<td>{case.citation_recall:.2%}</td><td>{case.fact_recall:.2%}</td>"
            f"<td>{escape(failures)}</td></tr>"
        )
    summary = report.summary
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{escape(report.suite)} reliability report</title>
<style>
body{{font:15px system-ui;max-width:1100px;margin:40px auto;padding:0 20px;
background:#0b1020;color:#e8edf7}}
h1{{font-size:28px}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}}
.card{{background:#151d31;border:1px solid #2a3655;border-radius:10px;padding:16px}}
.value{{font-size:24px;font-weight:700}}
table{{width:100%;border-collapse:collapse;background:#151d31}}
th,td{{padding:12px;border-bottom:1px solid #2a3655;text-align:left}}
.pass{{color:#5ee39a;font-weight:700}}
.fail{{color:#ff7f8a;font-weight:700}}
@media(max-width:720px){{.cards{{grid-template-columns:1fr 1fr}}}}
</style></head><body><h1>{escape(report.suite)}</h1>
<div class="cards">
<div class="card"><div>Pass rate</div>
<div class="value">{summary.pass_rate:.1%}</div></div>
<div class="card"><div>Mean score</div>
<div class="value">{summary.mean_score:.1%}</div></div>
<div class="card"><div>Latency SLO</div>
<div class="value">{summary.latency_slo_pass_rate:.1%}</div></div>
<div class="card"><div>Estimated cost</div>
<div class="value">${summary.total_estimated_cost_usd:.6f}</div></div></div>
<table><thead><tr><th>Case</th><th>Status</th><th>Score</th>
<th>Citation precision</th><th>Citation recall</th><th>Fact recall</th>
<th>Failures</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></body></html>"""
