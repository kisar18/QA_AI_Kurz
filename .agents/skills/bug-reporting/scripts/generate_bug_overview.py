"""Generátor přehledného HTML reportu nalezených chyb z testů.

Čte data z reports/bug_reports.json a reports/test_run_data.json
a generuje moderní interaktivní HTML soubor reports/bug_overview.html.
"""

import base64
import html
import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
REPORTS_DIR = PROJECT_ROOT / "reports"
DOCS_DIR = PROJECT_ROOT / "docs"
RUN_DATA_FILE = REPORTS_DIR / "test_run_data.json"
BUG_REPORTS_FILE = REPORTS_DIR / "bug_reports.json"
HTML_OUTPUT_FILE = DOCS_DIR / "bug_overview.html"


def generate_html(output_file: Path = HTML_OUTPUT_FILE) -> int:
    """Sestaví HTML soubor na základě dat o běhu a nahlášených chybách."""
    if not RUN_DATA_FILE.exists():
        print(f"[Chyba] Chybí soubor s daty testovacího běhu: {RUN_DATA_FILE}")
        return 1

    try:
        run_data = json.loads(RUN_DATA_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[Chyba] Nelze načíst data běhu: {e}")
        return 1

    bug_reports = []
    if BUG_REPORTS_FILE.exists():
        try:
            bug_reports = json.loads(BUG_REPORTS_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[Varování] Nelze načíst bug reporty: {e}")

    env = run_data.get("environment", {})
    total = run_data.get("total", 0)
    passed = run_data.get("passed", 0)
    failed = run_data.get("failed", 0)
    skipped = run_data.get("skipped", 0)
    total_defects = len(bug_reports)
    run_date = env.get("run_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Generování karet jednotlivých chyb
    bug_cards_html = []
    for bug in bug_reports:
        bug_id = html.escape(str(bug.get("id", "BUG-N/A")))
        title = html.escape(str(bug.get("title", bug.get("test_name", "Nespecifikovaná chyba"))))
        test_name = html.escape(str(bug.get("test_name", "")))
        test_file = html.escape(str(bug.get("test_file", "")))
        expected = html.escape(str(bug.get("expected_result", "")))
        actual = html.escape(str(bug.get("actual_result", "")))
        environment_str = html.escape(str(bug.get("environment", "")))
        status = str(bug.get("status", "FAILED")).upper()
        evidence = str(bug.get("evidence", "")).replace("\\", "/")

        is_xfail = (status == "XFAIL")
        status_data = "xfail" if is_xfail else "failed"
        badge_cls = "badge-xfail" if is_xfail else "badge-bug"
        status_badge = (
            '<span class="badge badge-type badge-type-xfail">⚠️ Očekávané selhání (XFAIL)</span>'
            if is_xfail
            else '<span class="badge badge-type badge-type-failed">🔴 Selhání testu</span>'
        )

        # Kroky k reprodukci
        steps_raw = bug.get("steps_to_reproduce", [])
        if isinstance(steps_raw, list):
            steps_items = "".join(f"<li>{html.escape(str(s))}</li>" for s in steps_raw)
            steps_html = f"<ol class='steps-list'>{steps_items}</ol>"
        else:
            steps_html = f"<p class='steps-text'>{html.escape(str(steps_raw))}</p>"

        # Odkaz / náhled důkazu
        evidence_html = ""
        evidence_path = PROJECT_ROOT / evidence if evidence else None
        if evidence and evidence_path and evidence_path.exists():
            rel_evidence = os.path.relpath(evidence_path, output_file.parent).replace("\\", "/")
            if evidence.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                try:
                    img_bytes = evidence_path.read_bytes()
                    b64_data = base64.b64encode(img_bytes).decode("ascii")
                    ext = evidence.lower().rsplit(".", 1)[-1]
                    mime = f"image/{ext}" if ext in ("png", "jpeg", "webp") else "image/png"
                    img_src = f"data:{mime};base64,{b64_data}"
                except Exception:
                    img_src = rel_evidence

                evidence_html = f"""
                <div class="evidence-box">
                    <div class="evidence-header">
                        <span class="field-label">📸 Snímek z prohlížeče v momentu selhání:</span>
                        <a href="{img_src}" target="_blank" class="btn-zoom">🔍 Otevřít screenshot v plné velikosti ↗</a>
                    </div>
                    <div class="browser-mockup">
                        <div class="browser-bar">
                            <span class="browser-dot dot-red"></span>
                            <span class="browser-dot dot-yellow"></span>
                            <span class="browser-dot dot-green"></span>
                            <span class="browser-address-bar">http://testovani.kitner.cz/</span>
                        </div>
                        <div class="browser-canvas">
                            <a href="{img_src}" target="_blank">
                                <img src="{img_src}" alt="Důkaz {bug_id}" class="evidence-thumbnail" />
                            </a>
                        </div>
                    </div>
                    <span class="evidence-path">{html.escape(evidence)}</span>
                </div>
                """
            else:
                evidence_html = f"""
                <div class="evidence-box">
                    <span class="field-label">📁 Důkaz (Trace / Log):</span>
                    <a href="{html.escape(rel_evidence)}" download class="evidence-link btn-download">Stáhnout důkaz ({html.escape(evidence)})</a>
                </div>
                """
        else:
            evidence_html = f"""
            <div class="evidence-box warning">
                <span class="field-label">⚠️ Důkaz:</span>
                <span class="missing-evidence">Soubor důkazu '{html.escape(evidence)}' nebyl na disku nalezen nebo chybí.</span>
            </div>
            """

        stacktrace_html = ""
        if bug.get("stacktrace"):
            stacktrace_html = f"""
            <details class="stacktrace-details">
                <summary>Zobrazit detail stacktrace / chybový výpis</summary>
                <pre class="stacktrace-code">{html.escape(str(bug['stacktrace']))}</pre>
            </details>
            """

        card = f"""
        <article class="bug-card bug-card-{status_data}" id="{bug_id}" data-status="{status_data}">
            <header class="bug-card-header">
                <div class="bug-title-group">
                    <span class="badge {badge_cls}">{bug_id}</span>
                    {status_badge}
                    <h3 class="bug-title">{title}</h3>
                </div>
                <div class="bug-meta">
                    <span class="test-meta-file">📄 {test_file}</span>
                    <span class="test-meta-func">⚙️ <code>{test_name}</code></span>
                </div>
            </header>
            
            <div class="bug-card-body">
                <section class="bug-section">
                    <h4 class="section-title">🐾 Kroky k reprodukci</h4>
                    {steps_html}
                </section>
                
                <div class="comparison-grid">
                    <section class="bug-section result-box expected-box">
                        <h4 class="section-title">✅ Očekávaný výsledek</h4>
                        <div class="result-content">{expected}</div>
                    </section>
                    
                    <section class="bug-section result-box actual-box">
                        <h4 class="section-title">❌ Skutečný výsledek</h4>
                        <div class="result-content">{actual}</div>
                    </section>
                </div>
                
                <section class="bug-section env-section">
                    <h4 class="section-title">🖥️ Prostředí</h4>
                    <p class="env-text">{environment_str}</p>
                </section>
                
                <section class="bug-section evidence-section">
                    {evidence_html}
                </section>
                
                {stacktrace_html}
            </div>
        </article>
        """
        bug_cards_html.append(card)

    cards_content = "\n".join(bug_cards_html) if bug_cards_html else """
    <div class="all-passed-card">
        <div class="success-icon">🎉</div>
        <h2>Všechny testy prošly úspěšně!</h2>
        <p>V aktuálním běhu testovací sady nebyly zjištěny žádné padající testy ani chyby.</p>
    </div>
    """

    # Vložení surových JSON metadat pro deterministickou validaci v hooku
    metadata_json = json.dumps({
        "generated_at": datetime.now().isoformat(),
        "run_data": run_data,
        "bug_reports": bug_reports,
    }, ensure_ascii=False)

    html_template = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Přehled chyb z automatizovaných testů</title>
    <style>
        :root {{
            --bg-primary: #f8fafc;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --danger-bg: #fef2f2;
            --danger-border: #fca5a5;
            --danger-text: #991b1b;
            --success-bg: #f0fdf4;
            --success-border: #86efac;
            --success-text: #166534;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --radius: 10px;
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-main);
            line-height: 1.6;
            padding: 2rem 1rem;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header.dashboard-header {{
            background: var(--bg-card);
            border-radius: var(--radius);
            padding: 1.5rem 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid var(--border-color);
        }}
        
        .dashboard-header h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.5rem;
        }}
        
        .dashboard-subtitle {{
            color: var(--text-muted);
            font-size: 0.95rem;
        }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }}
        
        .kpi-card {{
            background: #f1f5f9;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }}
        
        .kpi-card.failed {{ background: var(--danger-bg); border: 1px solid var(--danger-border); }}
        .kpi-card.passed {{ background: var(--success-bg); border: 1px solid var(--success-border); }}
        .kpi-card.xfail {{ background: #fffbeb; border: 1px solid #fde68a; }}
        .kpi-card.total-bugs {{ background: #eff6ff; border: 1px solid #bfdbfe; }}
        
        .kpi-value {{
            font-size: 2rem;
            font-weight: 700;
            display: block;
        }}
        .kpi-card.failed .kpi-value {{ color: var(--danger-text); }}
        .kpi-card.passed .kpi-value {{ color: var(--success-text); }}
        .kpi-card.xfail .kpi-value {{ color: #b45309; }}
        .kpi-card.total-bugs .kpi-value {{ color: #1d4ed8; }}
        
        .kpi-label {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
        }}
        
        .bug-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            margin-bottom: 1.5rem;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }}
        
        .bug-card-header {{
            padding: 1.25rem 1.5rem;
            background: #f8fafc;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .bug-title-group {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .badge {{
            padding: 0.35rem 0.65rem;
            font-size: 0.8rem;
            font-weight: 700;
            border-radius: 6px;
        }}
        
        .badge-bug {{
            background: #ef4444;
            color: #ffffff;
        }}
        
        .badge-xfail {{
            background: #d97706;
            color: #ffffff;
        }}
        
        .badge-type {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.55rem;
            border-radius: 4px;
        }}
        
        .badge-type-failed {{
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fca5a5;
        }}
        
        .badge-type-xfail {{
            background: #fef3c7;
            color: #92400e;
            border: 1px solid #fcd34d;
        }}
        
        .bug-card-xfail {{
            border-left: 4px solid #f59e0b;
        }}
        
        .bug-card-failed {{
            border-left: 4px solid #ef4444;
        }}
        
        .filter-bar {{
            display: flex;
            gap: 0.6rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 0.5rem 1.1rem;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background: var(--bg-card);
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--text-main);
            transition: all 0.2s ease;
        }}
        
        .filter-btn:hover {{
            background: #f1f5f9;
        }}
        
        .filter-btn.active {{
            background: var(--primary);
            color: #ffffff;
            border-color: var(--primary);
        }}
        
        .bug-title {{
            font-size: 1.15rem;
            font-weight: 600;
            color: #1e293b;
        }}
        
        .bug-meta {{
            font-size: 0.85rem;
            color: var(--text-muted);
            display: flex;
            gap: 1rem;
        }}
        
        .bug-card-body {{
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }}
        
        .section-title {{
            font-size: 0.95rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #475569;
            margin-bottom: 0.5rem;
        }}
        
        .steps-list {{
            padding-left: 1.5rem;
            color: #334155;
        }}
        
        .steps-list li {{
            margin-bottom: 0.25rem;
        }}
        
        .comparison-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }}
        
        @media (max-width: 768px) {{
            .comparison-grid {{ grid-template-columns: 1fr; }}
        }}
        
        .result-box {{
            padding: 1rem;
            border-radius: 8px;
        }}
        
        .expected-box {{
            background: var(--success-bg);
            border: 1px solid var(--success-border);
            color: var(--success-text);
        }}
        
        .actual-box {{
            background: var(--danger-bg);
            border: 1px solid var(--danger-border);
            color: var(--danger-text);
        }}
        
        .result-content {{
            font-weight: 500;
            font-size: 0.95rem;
        }}
        
        .env-text {{
            font-family: monospace;
            background: #f1f5f9;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            font-size: 0.9rem;
            color: #334155;
        }}
        
        .evidence-box {{
            background: #f8fafc;
            border: 1px dashed var(--border-color);
            border-radius: 8px;
            padding: 1rem;
        }}
        
        .evidence-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .btn-zoom {{
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            font-size: 0.8rem;
            padding: 0.35rem 0.75rem;
            background: var(--primary);
            color: #ffffff;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            transition: background 0.15s ease;
        }}
        .btn-zoom:hover {{
            background: var(--primary-hover);
        }}
        
        .browser-mockup {{
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #334155;
            background: #0f172a;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
            margin: 0.5rem 0;
        }}
        
        .browser-bar {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 0.5rem 0.75rem;
            background: #1e293b;
            border-bottom: 1px solid #334155;
        }}
        
        .browser-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }}
        .dot-red {{ background: #ef4444; }}
        .dot-yellow {{ background: #f59e0b; }}
        .dot-green {{ background: #10b981; }}
        
        .browser-address-bar {{
            margin-left: 0.5rem;
            font-family: monospace;
            font-size: 0.8rem;
            color: #94a3b8;
            background: #0f172a;
            padding: 0.2rem 0.7rem;
            border-radius: 4px;
            flex-grow: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .browser-canvas {{
            background: #0f172a;
            padding: 0.75rem;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .evidence-box.warning {{
            background: #fffbeb;
            border-color: #fde68a;
            color: #92400e;
        }}
        
        .evidence-thumbnail {{
            display: block;
            max-width: 100%;
            max-height: 480px;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
            cursor: pointer;
            transition: transform 0.2s ease;
        }}
        
        .evidence-thumbnail:hover {{
            transform: scale(1.005);
        }}
        
        .evidence-path {{
            display: block;
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 0.5rem;
            font-family: monospace;
        }}
        
        .all-passed-card {{
            background: var(--bg-card);
            border: 2px solid var(--success-border);
            border-radius: var(--radius);
            padding: 3rem;
            text-align: center;
        }}
        
        .success-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        
        .stacktrace-details {{
            background: #0f172a;
            color: #f8fafc;
            border-radius: 8px;
            padding: 0.75rem 1rem;
        }}
        
        .stacktrace-details summary {{
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        
        .stacktrace-code {{
            margin-top: 0.75rem;
            font-family: monospace;
            font-size: 0.8rem;
            white-space: pre-wrap;
            overflow-x: auto;
            color: #fca5a5;
        }}
        
        .field-label {{
            font-weight: 600;
            font-size: 0.9rem;
        }}
        
        .btn-download {{
            display: inline-block;
            margin-top: 0.5rem;
            padding: 0.5rem 1rem;
            background: var(--primary);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.9rem;
        }}
        .btn-download:hover {{ background: var(--primary-hover); }}
    </style>
</head>
<body>
    <div class="container">
        <header class="dashboard-header">
            <h1>🐛 Souhrnný přehled nalezených chyb</h1>
            <p class="dashboard-subtitle">Datum a čas běhu: <strong>{run_date}</strong> | Testovací URL: <strong>{env.get('base_url', 'N/A')}</strong></p>
            
            <div class="kpi-grid">
                <div class="kpi-card">
                    <span class="kpi-value">{total}</span>
                    <span class="kpi-label">Celkem testů</span>
                </div>
                <div class="kpi-card passed">
                    <span class="kpi-value">{passed}</span>
                    <span class="kpi-label">Úspěšné testy</span>
                </div>
                <div class="kpi-card failed">
                    <span class="kpi-value">{failed}</span>
                    <span class="kpi-label">Selhání testů (Failed)</span>
                </div>
                <div class="kpi-card xfail">
                    <span class="kpi-value">{skipped}</span>
                    <span class="kpi-label">Očekávaná selhání (XFail)</span>
                </div>
                <div class="kpi-card total-bugs">
                    <span class="kpi-value">{total_defects}</span>
                    <span class="kpi-label">Celkem defektů</span>
                </div>
            </div>
        </header>
        
        <div class="filter-bar">
            <button class="filter-btn active" onclick="filterBugs('all', this)">Všechny defekty ({total_defects})</button>
            <button class="filter-btn" onclick="filterBugs('failed', this)">🔴 Pouze selhání testů ({failed})</button>
            <button class="filter-btn" onclick="filterBugs('xfail', this)">⚠️ Pouze očekávaná selhání / XFAIL ({skipped})</button>
        </div>
        
        <main class="bug-list">
            {cards_content}
        </main>
    </div>

    <!-- Strojově čitelná metadata pro Stop hook a validační nástroje -->
    <script type="application/json" id="bug-reports-metadata">
{metadata_json}
    </script>

    <script>
        function filterBugs(type, btn) {{
            document.querySelectorAll('.filter-btn').forEach(function(b) {{
                b.classList.remove('active');
            }});
            btn.classList.add('active');
            document.querySelectorAll('.bug-card').forEach(function(card) {{
                if (type === 'all' || card.getAttribute('data-status') === type) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""

    output_file.write_text(html_template, encoding="utf-8")
    print(f"[BugReporter] HTML přehled chyb úspěšně vygenerován: {output_file}")
    return 0


if __name__ == "__main__":
    out_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else HTML_OUTPUT_FILE
    sys.exit(generate_html(out_arg))
