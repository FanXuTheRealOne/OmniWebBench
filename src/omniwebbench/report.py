"""Portable result report generation."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from omniwebbench.scoring import aggregate


def write_json_report(results: list[dict[str, Any]], output: str | Path) -> Path:
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "schema_version": "omniwebbench.report.v1",
                "summary": aggregate(results),
                "results": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return target


def write_html_report(results: list[dict[str, Any]], output: str | Path) -> Path:
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    summary = aggregate(results)
    rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(str(item['task_id']))}</code></td>"
        f"<td>{html.escape(str(item.get('verdict') or item.get('reason')))}</td>"
        f"<td>{html.escape(str(item.get('score')))}</td>"
        f"<td><pre>{html.escape(json.dumps(item.get('dimensions') or {}, indent=2))}</pre></td>"
        "</tr>"
        for item in results
    )
    document = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'><title>OmniWebBench report</title>
<style>body{{font:15px/1.5 system-ui;margin:0;background:#f5f7f8;color:#111}}main{{max-width:1100px;margin:auto;padding:48px 24px}}
h1{{font-size:48px;letter-spacing:-.04em}}.metrics{{display:flex;gap:12px;flex-wrap:wrap}}.metric{{background:white;border:1px solid #dde3e6;border-radius:14px;padding:18px;min-width:150px}}
.metric b{{display:block;font-size:30px}}table{{width:100%;border-collapse:collapse;background:white;margin-top:24px}}th,td{{padding:12px;border-bottom:1px solid #e7ebed;text-align:left;vertical-align:top}}pre{{margin:0;font-size:11px}}</style></head>
<body><main><p>OMNIWEBBENCH · EVIDENCE-GROUNDED REPORT</p><h1>Evaluation report</h1><div class='metrics'>
<div class='metric'><b>{summary["runs"]}</b>runs</div><div class='metric'><b>{summary["scored_runs"]}</b>scored</div>
<div class='metric'><b>{summary["task_success_rate"]}</b>success rate</div><div class='metric'><b>{summary["mean_score"]}</b>mean score</div></div>
<table><thead><tr><th>Task</th><th>Verdict</th><th>Score</th><th>Dimensions</th></tr></thead><tbody>{rows}</tbody></table></main></body></html>"""
    target.write_text(document, encoding="utf-8")
    return target
