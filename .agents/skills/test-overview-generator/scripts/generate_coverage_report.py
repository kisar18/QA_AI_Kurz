#!/usr/bin/env python3
"""
Generate Coverage Report
------------------------
Analyzuje User Stories (specifikaci požadavků a akceptační kritéria / test casy)
a automatizované testy v projektu (Playwright + pytest).
Generuje ucelený HTML přehled mapování požadavků na testy (Traceability Matrix).

Použití:
    python generate_coverage_report.py [--output reports/coverage_overview.html]
"""

import argparse
import ast
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Zajištění správného kódování výstupu na Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


class UserStoryParser:
    """Parsuje specifikaci User Stories a jejich akceptační kritéria (test casy)."""

    def __init__(self, stories_path: Path):
        self.stories_path = stories_path

    def parse(self) -> Dict[str, Dict[str, Any]]:
        """Vrátí slovník {US-ID: metadata}."""
        if not self.stories_path.exists():
            print(f"[VAROVÁNÍ] Soubor s User Stories neexistuje: {self.stories_path}", file=sys.stderr)
            return {}

        content = self.stories_path.read_text(encoding="utf-8")
        stories: Dict[str, Dict[str, Any]] = {}
        current_module = "Obecné"

        # Detekce modulů v textu
        module_positions: List[Tuple[int, str]] = []
        for match in re.finditer(r"###\s+(Modul\s+\d+:\s*[^\n]+)", content):
            module_positions.append((match.start(), match.group(1).strip()))

        # Parsování jednotlivých US
        sections = re.split(r"####\s+(US-\d+):", content)
        # sections[0] je úvod před prvním US, pak se střídají (us_id, body)
        for i in range(1, len(sections), 2):
            us_id = sections[i]
            body = sections[i + 1]
            title_line = body.strip().splitlines()[0].strip()

            # Přiřazení odpovídajícího modulu podle pozice v textu
            us_pos = content.find(f"#### {us_id}:")
            module_name = "Obecné"
            for pos, mod_title in module_positions:
                if pos < us_pos:
                    module_name = mod_title

            # Extrakce akceptačních kritérií (test casů)
            criteria: List[str] = []
            ac_match = re.search(
                r"-\s+\*\*Akceptační kritéria:\*\*(.*?)(?=\n---|\n###|\n####|\Z)",
                body,
                re.DOTALL,
            )
            if ac_match:
                for line in ac_match.group(1).splitlines():
                    stripped = line.strip()
                    if stripped.startswith("- ") or stripped.startswith("* "):
                        bullet_text = stripped[2:].strip()
                        if bullet_text:
                            criteria.append(bullet_text)

            # Extrakce rolí / cílů (Jako, Chci, Abych)
            role_match = re.search(r"-\s+\*\*Jako:\*\*\s*(.+)", body)
            want_match = re.search(r"-\s+\*\*Chci:\*\*\s*(.+)", body)
            goal_match = re.search(r"-\s+\*\*Abych:\*\*\s*(.+)", body)

            stories[us_id] = {
                "id": us_id,
                "title": title_line,
                "module": module_name,
                "role": role_match.group(1).strip() if role_match else "",
                "want": want_match.group(1).strip() if want_match else "",
                "goal": goal_match.group(1).strip() if goal_match else "",
                "criteria": criteria,
                "test_cases_count": len(criteria),
                "tests": [],
            }

        return stories


class TestAnalyzerForCoverage:
    """Prochází automatizované testy v tests/ a mapuje je na User Stories."""

    # Kontextové mapování souborů na US (pokud test nemá explicitní značku v docstringu)
    FILE_FALLBACK_MAP = {
        "test_login.py": ["US-03"],
        "test_register.py": ["US-02"],
        "test_logout.py": ["US-04"],
        "test_forgot_password.py": ["US-05"],
        "test_reset_password.py": ["US-06"],
        "test_email_verification.py": ["US-07"],
        "test_rate_limiting.py": ["US-08"],
        "test_linktree.py": ["US-01"],
        "test_home_dashboard.py": ["US-17"],
        "test_courses.py": ["US-09", "US-10", "US-11"],
        "test_course_management.py": ["US-14"],
        "test_course_iterations.py": ["US-15", "US-16"],
        "test_enrollment.py": ["US-12"],
        "test_rbac.py": ["US-19"],
        "test_csrf.py": ["US-20"],
    }

    CLASS_FALLBACK_MAP = {
        "TestUserProfile": ["US-18"],
        "TestMyCourses": ["US-13"],
        "TestDemoLogin": ["US-03"],
        "TestDemoRegister": ["US-02"],
        "TestDemoLogout": ["US-04"],
        "TestForgotPassword": ["US-05"],
        "TestResetPassword": ["US-06"],
        "TestEmailVerification": ["US-07"],
        "TestRateLimiting": ["US-08"],
        "TestPortalLinktree": ["US-01"],
        "TestHomeDashboard": ["US-17"],
        "TestCoursesCatalog": ["US-09", "US-10", "US-11"],
        "TestCourseManagement": ["US-14"],
        "TestCourseIterations": ["US-15", "US-16"],
        "TestCourseEnrollment": ["US-12"],
        "TestRoleBasedAccessControl": ["US-19"],
        "TestCsrfAndSessionIntegrity": ["US-20"],
    }

    def __init__(self, tests_dir: Path, project_root: Path):
        self.tests_dir = tests_dir
        self.project_root = project_root

    def discover_and_map(self, stories: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Projistí testy a přiřadí je do odpovídajících User Stories."""
        test_files = sorted(self.tests_dir.rglob("test_*.py"))
        all_found_tests: List[Dict[str, Any]] = []

        for file_path in test_files:
            rel_path = file_path.relative_to(self.project_root).as_posix()
            try:
                tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
            except Exception as e:
                print(f"[VAROVÁNÍ] Nelze zpracovat {file_path}: {e}", file=sys.stderr)
                continue

            file_us = self._extract_us_tags(ast.get_docstring(tree) or "")
            if not file_us and file_path.name in self.FILE_FALLBACK_MAP:
                file_us = self.FILE_FALLBACK_MAP[file_path.name]

            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    cls_doc = ast.get_docstring(node) or ""
                    cls_us = self._extract_us_tags(cls_doc)
                    if not cls_us and node.name in self.CLASS_FALLBACK_MAP:
                        cls_us = self.CLASS_FALLBACK_MAP[node.name]
                    if not cls_us:
                        cls_us = file_us

                    for member in node.body:
                        if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name.startswith("test_"):
                            test_info = self._process_test_node(
                                member,
                                file_path=rel_path,
                                class_name=node.name,
                                inherited_us=cls_us,
                            )
                            all_found_tests.append(test_info)
                            self._assign_to_stories(test_info, stories)

                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                    test_info = self._process_test_node(
                        node,
                        file_path=rel_path,
                        class_name=None,
                        inherited_us=file_us,
                    )
                    all_found_tests.append(test_info)
                    self._assign_to_stories(test_info, stories)

        return all_found_tests

    def _extract_us_tags(self, text: str) -> List[str]:
        """Extrahuje kódy US-01 až US-99 z textu."""
        matches = re.findall(r"\bUS-(\d+)\b", text, re.IGNORECASE)
        return [f"US-{int(m):02d}" for m in matches]

    def _process_test_node(
        self,
        node: ast.FunctionDef,
        file_path: str,
        class_name: Optional[str],
        inherited_us: List[str],
    ) -> Dict[str, Any]:
        docstring = ast.get_docstring(node) or ""
        explicit_us = self._extract_us_tags(docstring) + self._extract_us_tags(node.name)

        # Explicitní tag v docstringu testu má přednost; pokud není, dědí se z třídy/souboru
        assigned_us = sorted(list(set(explicit_us if explicit_us else inherited_us)))

        # Spočítáme ověření (expect / assert)
        checks_count = 0
        for sub_node in ast.walk(node):
            if isinstance(sub_node, ast.Assert):
                checks_count += 1
            elif isinstance(sub_node, ast.Expr) and isinstance(sub_node.value, ast.Call):
                code = ast.unparse(sub_node.value)
                if "expect(" in code or (isinstance(sub_node.value.func, ast.Name) and sub_node.value.func.id == "step"):
                    checks_count += 1

        return {
            "name": node.name,
            "line": node.lineno,
            "file": file_path,
            "class_name": class_name,
            "docstring": docstring.strip(),
            "assigned_us": assigned_us,
            "checks_count": checks_count,
        }

    def _assign_to_stories(self, test_info: Dict[str, Any], stories: Dict[str, Dict[str, Any]]):
        for us_id in test_info["assigned_us"]:
            if us_id in stories:
                # Zabráníme duplikaci téhož testu u US
                if not any(t["name"] == test_info["name"] and t["file"] == test_info["file"] for t in stories[us_id]["tests"]):
                    stories[us_id]["tests"].append(test_info)


class HtmlCoverageReportGenerator:
    """Generuje přehledný, moderní a interaktivní HTML report."""

    @staticmethod
    def generate(stories: Dict[str, Dict[str, Any]], all_tests: List[Dict[str, Any]], output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Výpočet celkových metrik
        total_us = len(stories)
        total_tc = sum(s["test_cases_count"] for s in stories.values())
        total_at = len(all_tests)

        covered_us = 0
        partial_us = 0
        uncovered_us = 0

        for s in stories.values():
            at_count = len(s["tests"])
            tc_count = s["test_cases_count"]
            if at_count == 0:
                s["status"] = "uncovered"
                s["status_label"] = "Nepokryto"
                s["status_badge"] = "badge-danger"
                uncovered_us += 1
            elif tc_count > 0 and at_count >= tc_count:
                s["status"] = "covered"
                s["status_label"] = "Plně pokryto"
                s["status_badge"] = "badge-success"
                covered_us += 1
            else:
                s["status"] = "partial"
                s["status_label"] = "Částečně"
                s["status_badge"] = "badge-warning"
                partial_us += 1

        coverage_pct = round((covered_us + 0.5 * partial_us) / total_us * 100, 1) if total_us else 0

        # Sestavení HTML
        html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Přehled pokrytí User Stories automatizovanými testy</title>
    <style>
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent: #38bdf8;
            --success: #22c55e;
            --warning: #f59e0b;
            --danger: #ef4444;
            --border: #475569;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            padding: 2rem;
            line-height: 1.5;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border);
        }}
        h1 {{ font-size: 2rem; font-weight: 700; color: var(--accent); margin-bottom: 0.5rem; }}
        .meta-info {{ color: var(--text-secondary); font-size: 0.95rem; }}
        
        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }}
        .kpi-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        .kpi-value {{ font-size: 2.2rem; font-weight: 800; margin-bottom: 0.25rem; }}
        .kpi-label {{ color: var(--text-secondary); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }}
        .text-accent {{ color: var(--accent); }}
        .text-success {{ color: var(--success); }}
        .text-warning {{ color: var(--warning); }}
        .text-danger {{ color: var(--danger); }}

        /* Controls */
        .controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        .filter-buttons {{ display: flex; gap: 0.5rem; }}
        .filter-btn {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.2s;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: var(--accent);
            color: #0f172a;
            border-color: var(--accent);
        }}
        .search-box input {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 0.55rem 1rem;
            border-radius: 8px;
            font-size: 0.9rem;
            width: 260px;
        }}

        /* Table */
        .table-responsive {{
            overflow-x: auto;
            border: 1px solid var(--border);
            border-radius: 12px;
            background: var(--bg-secondary);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}
        th {{
            background: #182234;
            color: var(--text-secondary);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 1rem;
            border-bottom: 1px solid var(--border);
        }}
        td {{
            padding: 1rem;
            border-bottom: 1px solid rgba(71, 85, 105, 0.4);
            font-size: 0.95rem;
            vertical-align: top;
        }}
        tr:hover td {{ background: rgba(51, 65, 85, 0.5); }}
        .us-id {{
            font-family: monospace;
            font-weight: 700;
            color: var(--accent);
            white-space: nowrap;
        }}
        .module-tag {{
            display: inline-block;
            background: rgba(56, 189, 248, 0.1);
            color: var(--accent);
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            font-size: 0.75rem;
            margin-top: 0.35rem;
        }}

        /* Badges */
        .badge {{
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 700;
            text-align: center;
            white-space: nowrap;
        }}
        .badge-success {{ background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4); }}
        .badge-warning {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }}
        .badge-danger {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }}

        /* Collapsible details */
        details summary {{
            cursor: pointer;
            color: var(--accent);
            font-size: 0.85rem;
            font-weight: 600;
            outline: none;
            margin-top: 0.4rem;
        }}
        details summary:hover {{ text-decoration: underline; }}
        .criteria-list, .tests-list {{
            margin-top: 0.5rem;
            padding-left: 1.25rem;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }}
        .criteria-list li {{ margin-bottom: 0.25rem; }}
        .test-item {{
            margin-bottom: 0.35rem;
            font-family: monospace;
            color: #cbd5e1;
        }}
        .test-meta {{ color: #64748b; font-size: 0.75rem; }}

        footer {{
            margin-top: 2rem;
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Přehled pokrytí User Stories automatizovanými testy</h1>
            <p class="meta-info">
                Projekt: <strong>testovani.kitner.cz</strong> | 
                Zdroj specifikace: <code>user stories/požadavky_ust_podle_src.md</code> | 
                Vygenerováno: <strong>{now_str}</strong> (opakovatelný běh)
            </p>
        </header>

        <!-- KPI Metriky -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-value text-accent">{total_us}</div>
                <div class="kpi-label">Celkem User Stories</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value text-success">{covered_us}</div>
                <div class="kpi-label">Plně pokryto</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value text-warning">{partial_us}</div>
                <div class="kpi-label">Částečně pokryto</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value text-danger">{uncovered_us}</div>
                <div class="kpi-label">Nepokryto</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value text-accent">{coverage_pct}%</div>
                <div class="kpi-label">Celkové pokrytí</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{total_tc}</div>
                <div class="kpi-label">Akceptačních test casů</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{total_at}</div>
                <div class="kpi-label">Automatizovaných testů (AT)</div>
            </div>
        </div>

        <!-- Ovládací prvky a filtry -->
        <div class="controls">
            <div class="filter-buttons">
                <button class="filter-btn active" data-filter="all">Všechny ({total_us})</button>
                <button class="filter-btn" data-filter="covered">🟢 Pokryto ({covered_us})</button>
                <button class="filter-btn" data-filter="partial">🟡 Částečně ({partial_us})</button>
                <button class="filter-btn" data-filter="uncovered">🔴 Nepokryto ({uncovered_us})</button>
            </div>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Filtrovat podle textu / US..." onkeyup="filterTable()">
            </div>
        </div>

        <!-- Tabulka Traceability Matrix -->
        <div class="table-responsive">
            <table id="coverageTable">
                <thead>
                    <tr>
                        <th style="width: 100px;">User Story</th>
                        <th style="width: 200px;">Modul</th>
                        <th>Název & Akceptační kritéria (Test Casy)</th>
                        <th style="width: 120px; text-align: center;">Test Casů</th>
                        <th style="width: 110px; text-align: center;">Počet AT</th>
                        <th style="width: 140px; text-align: center;">Stav pokrytí</th>
                        <th style="width: 320px;">Automatizované testy (AT)</th>
                    </tr>
                </thead>
                <tbody>
"""

        for us_id in sorted(stories.keys()):
            story = stories[us_id]
            at_count = len(story["tests"])
            tc_count = story["test_cases_count"]

            # Generování seznamu akceptačních kritérií
            criteria_html = ""
            if story["criteria"]:
                items = "".join(f"<li>{c}</li>" for c in story["criteria"])
                criteria_html = f"""
                <details>
                    <summary>Zobrazit {tc_count} akceptačních kritérií (Test Casů)</summary>
                    <ul class="criteria-list">{items}</ul>
                </details>
                """

            # Generování seznamu testů
            tests_html = ""
            if story["tests"]:
                test_items = []
                for t in story["tests"]:
                    cls_prefix = f"{t['class_name']}." if t["class_name"] else ""
                    test_items.append(
                        f"<div class='test-item'>⚙️ <strong>{cls_prefix}{t['name']}</strong>"
                        f"<div class='test-meta'>📁 {t['file']} | 🔍 {t['checks_count']} kontrol</div></div>"
                    )
                tests_html = f"""
                <details open>
                    <summary>Přiřazené testy ({at_count})</summary>
                    <div class="tests-list">{"".join(test_items)}</div>
                </details>
                """
            else:
                tests_html = "<span style='color: var(--text-secondary); font-style: italic;'>Žádný automatizovaný test zatím nepřiřazen</span>"

            ratio_text = f"{at_count}/{tc_count}" if tc_count else f"{at_count}"

            html += f"""
                    <tr class="story-row" data-status="{story['status']}">
                        <td><span class="us-id">{story['id']}</span></td>
                        <td><span class="module-tag">{story['module']}</span></td>
                        <td>
                            <strong>{story['title']}</strong>
                            {criteria_html}
                        </td>
                        <td style="text-align: center; font-weight: 700;">{tc_count}</td>
                        <td style="text-align: center; font-weight: 700; color: var(--accent);">{at_count}</td>
                        <td style="text-align: center;">
                            <span class="badge {story['status_badge']}">{story['status_label']} ({ratio_text})</span>
                        </td>
                        <td>{tests_html}</td>
                    </tr>
"""

        html += f"""
                </tbody>
            </table>
        </div>

        <footer>
            <p>Antigravity E2E Testing Suite • Automaticky generovaný a opakovatelný report pokrytí požadavků</p>
        </footer>
    </div>

    <script>
        // Filtrace podle tlačítek
        const filterButtons = document.querySelectorAll('.filter-btn');
        filterButtons.forEach(btn => {{
            btn.addEventListener('click', () => {{
                filterButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const filter = btn.getAttribute('data-filter');
                const rows = document.querySelectorAll('.story-row');
                rows.forEach(row => {{
                    if (filter === 'all' || row.getAttribute('data-status') === filter) {{
                        row.style.display = '';
                    }} else {{
                        row.style.display = 'none';
                    }}
                }});
            }});
        }});

        // Vyhledávání v tabulce
        function filterTable() {{
            const input = document.getElementById('searchInput');
            const filter = input.value.toLowerCase();
            const rows = document.querySelectorAll('.story-row');
            rows.forEach(row => {{
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            }});
        }}
    </script>
</body>
</html>
"""
        output_path.write_text(html, encoding="utf-8")
        print(f"[OK] HTML přehled pokrytí byl úspěšně vygenerován do: {output_path}")
        print(f"     User Stories celkem: {total_us} | Plně pokryto: {covered_us} | Částečně: {partial_us} | Nepokryto: {uncovered_us}")


def generate_coverage_html(
    project_root: Optional[Path] = None,
    stories_path: Optional[Path] = None,
    tests_dir: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> Path:
    """Programatické spuštění generování HTML reportu pokrytí."""
    if project_root is None:
        project_root = Path(".").resolve()
        if not (project_root / "tests").exists():
            candidate = Path(__file__).resolve().parents[4]
            if (candidate / "tests").exists():
                project_root = candidate

    if stories_path is None:
        stories_path = project_root / "user stories" / "požadavky_ust_podle_src.md"
    if tests_dir is None:
        tests_dir = project_root / "tests"
    if output_path is None:
        output_path = project_root / "reports" / "coverage_overview.html"

    stories = UserStoryParser(stories_path).parse()
    all_tests = TestAnalyzerForCoverage(tests_dir=tests_dir, project_root=project_root).discover_and_map(stories)
    HtmlCoverageReportGenerator.generate(stories, all_tests, output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generuje přehled pokrytí User Stories automatizovanými testy v HTML (Traceability Matrix)."
    )
    parser.add_argument(
        "--stories",
        default="user stories/požadavky_ust_podle_src.md",
        help="Cesta k souboru se specifikací User Stories",
    )
    parser.add_argument("--tests-dir", default="tests", help="Složka s testy")
    parser.add_argument(
        "--output",
        default="reports/coverage_overview.html",
        help="Cesta k výstupnímu HTML souboru (výchozí: reports/coverage_overview.html)",
    )
    parser.add_argument("--project-root", default=".", help="Kořenový adresář projektu")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    # Detekce kořene projektu, pokud je spuštěno z podsložky
    if not (project_root / args.tests_dir).exists():
        candidate = Path(__file__).resolve().parents[4]
        if (candidate / args.tests_dir).exists():
            project_root = candidate

    stories_path = (project_root / args.stories).resolve()
    tests_dir = (project_root / args.tests_dir).resolve()
    output_path = (project_root / args.output).resolve()

    print(f"[INFO] Analyzuji User Stories z: {stories_path}")
    stories_parser = UserStoryParser(stories_path)
    stories = stories_parser.parse()

    print(f"[INFO] Analyzuji automatizované testy v: {tests_dir}")
    test_mapper = TestAnalyzerForCoverage(tests_dir=tests_dir, project_root=project_root)
    all_tests = test_mapper.discover_and_map(stories)

    HtmlCoverageReportGenerator.generate(stories, all_tests, output_path)


if __name__ == "__main__":
    main()
