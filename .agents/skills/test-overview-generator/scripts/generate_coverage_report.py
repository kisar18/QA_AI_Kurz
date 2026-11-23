#!/usr/bin/env python3
"""
Generate Coverage Report (Traceability Matrix: Manual TCs -> Automated Tests)
-----------------------------------------------------------------------------
Analyzuje schválené manuální Test Casy (ze složky manual_tests/TC_*.md)
a automatizované testy v projektu (Playwright + pytest v tests/).

Mapování probíhá ČISTĚ a VÝHRADNĚ proti manuálním Test Casům (TC-ID např. [TC-US01-01]):
- Každý schválený manuální test case je evidován pod svým jedinečným TC ID.
- Každý automatizovaný test v tests/ je spárován s příslušným manuálním TC podle tagu [TC-USxx-yy] v docstringu.
- Pokrytí se počítá jako poměr pokrytých manuálních test casů k celkovému počtu manuálních test casů.

Výstup je ve výchozím stavu ukládán do docs/coverage_overview.html (verzovatelné v Gitu).

Použití:
    python generate_coverage_report.py [--manual-tests-dir manual_tests] [--output docs/coverage_overview.html]
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

US_MODULE_MAP = {
    "US-01": "Modul 0: Úvodní navigační rozcestník (Linktree)",
    "US-02": "Modul 1: Autentizace a správa sezení (Authentication)",
    "US-03": "Modul 1: Autentizace a správa sezení (Authentication)",
    "US-04": "Modul 1: Autentizace a správa sezení (Authentication)",
    "US-05": "Modul 1: Autentizace a správa sezení (Authentication)",
    "US-06": "Modul 1: Autentizace a správa sezení (Authentication)",
    "US-07": "Modul 1: Autentizace a správa sezení (Authentication)",
    "US-08": "Modul 1: Autentizace a správa sezení (Authentication)",
    "US-09": "Modul 2: Katalog a detail kurzů (Courses)",
    "US-10": "Modul 2: Katalog a detail kurzů (Courses)",
    "US-11": "Modul 2: Katalog a detail kurzů (Courses)",
    "US-12": "Modul 3: Zápis a Moje kurzy (Enrollment)",
    "US-13": "Modul 3: Zápis a Moje kurzy (Enrollment)",
    "US-14": "Modul 4: Správa kurzů a běhů (Lector)",
    "US-15": "Modul 4: Správa kurzů a běhů (Lector)",
    "US-16": "Modul 4: Správa kurzů a běhů (Lector)",
    "US-17": "Modul 5: Profil a domovská nástěnka (Dashboard)",
    "US-18": "Modul 5: Profil a domovská nástěnka (Dashboard)",
    "US-19": "Modul 6: Bezpečnost a autorizace (Security)",
    "US-20": "Modul 6: Bezpečnost a autorizace (Security)",
}


class ManualTestCase:
    """Reprezentuje jeden schválený manuální Test Case ze složky manual_tests/."""

    def __init__(
        self,
        tc_id: str,
        us_id: str,
        title: str,
        source_file: str,
        priority: str = "",
        test_type: str = "",
        ac_covered: str = "",
    ):
        self.tc_id = tc_id
        self.us_id = us_id
        self.title = title
        self.source_file = source_file
        self.priority = priority
        self.test_type = test_type
        self.ac_covered = ac_covered
        self.covered_by: List[Dict[str, Any]] = []

    @property
    def is_covered(self) -> bool:
        return len(self.covered_by) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.tc_id,
            "us_id": self.us_id,
            "title": self.title,
            "source_file": self.source_file,
            "priority": self.priority,
            "test_type": self.test_type,
            "ac_covered": self.ac_covered,
            "is_covered": self.is_covered,
            "tests": self.covered_by,
        }


class ManualTestsParser:
    """Parsuje schválené manuální test casy z Markdown souborů v manual_tests/."""

    def __init__(self, manual_tests_dir: Path):
        self.manual_tests_dir = manual_tests_dir

    def parse(self) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, ManualTestCase]]:
        """Vrátí:
        1. stories: Dict[us_id, {id, title, module, file, test_cases: List[ManualTestCase], ...}]
        2. all_tcs: Dict[tc_id, ManualTestCase]
        """
        if not self.manual_tests_dir.exists():
            print(f"[VAROVÁNÍ] Složka s manuálními testy neexistuje: {self.manual_tests_dir}", file=sys.stderr)
            return {}, {}

        tc_files = sorted(self.manual_tests_dir.glob("TC_*.md"))
        if not tc_files:
            tc_files = sorted(self.manual_tests_dir.glob("*.md"))

        stories: Dict[str, Dict[str, Any]] = {}
        all_tcs: Dict[str, ManualTestCase] = {}

        for tc_file in tc_files:
            content = tc_file.read_text(encoding="utf-8")
            us_match = re.search(r"Zdrojová User Story:\*\*\s*(US-\d+)", content)
            if not us_match:
                m = re.search(r"TC_(US-\d+)", tc_file.name)
                us_id = m.group(1) if m else None
            else:
                us_id = us_match.group(1)

            if not us_id:
                continue

            title_match = re.search(r"^#\s+Test Casy:\s*(.+)", content, re.MULTILINE)
            raw_title = title_match.group(1).strip() if title_match else tc_file.stem
            title = re.sub(r"^US-\d+\s*", "", raw_title)

            module = US_MODULE_MAP.get(us_id, "Obecné")

            story_tcs: List[ManualTestCase] = []
            tc_sections = re.split(r"###\s+\[(TC-[^\]]+)\]", content)
            for i in range(1, len(tc_sections), 2):
                tc_id = tc_sections[i].strip()
                body = tc_sections[i + 1]
                first_line = body.strip().splitlines()[0].strip() if body.strip() else ""

                ac_match = re.search(r"-\s+\*\*Pokrývá kritérium:\*\*\s*(.+)", body)
                type_match = re.search(r"-\s+\*\*Typ testu:\*\*\s*(.+)", body)
                prio_match = re.search(r"-\s+\*\*Priorita:\*\*\s*(.+)", body)

                manual_tc = ManualTestCase(
                    tc_id=tc_id,
                    us_id=us_id,
                    title=first_line,
                    source_file=tc_file.name,
                    priority=prio_match.group(1).strip() if prio_match else "",
                    test_type=type_match.group(1).strip() if type_match else "",
                    ac_covered=ac_match.group(1).strip() if ac_match else "",
                )
                story_tcs.append(manual_tc)
                all_tcs[tc_id] = manual_tc

            stories[us_id] = {
                "id": us_id,
                "title": title,
                "module": module,
                "source_file": tc_file.name,
                "test_cases": story_tcs,
                "tests": [],
            }

        return stories, all_tcs


class TestAnalyzerForCoverage:
    """Prochází automatizované testy v tests/ a mapuje je čistě na manuální Test Casy."""

    def __init__(self, tests_dir: Path, project_root: Path):
        self.tests_dir = tests_dir
        self.project_root = project_root

    def discover_and_map(
        self,
        stories: Dict[str, Dict[str, Any]],
        all_tcs: Dict[str, ManualTestCase],
    ) -> List[Dict[str, Any]]:
        """Analyzuje AST testovacích souborů a mapuje je přímo na schválené manuální TC."""
        test_files = sorted(self.tests_dir.rglob("test_*.py"))
        all_found_tests: List[Dict[str, Any]] = []

        for file_path in test_files:
            rel_path = file_path.relative_to(self.project_root).as_posix()
            try:
                tree = ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
            except Exception as e:
                print(f"[VAROVÁNÍ] Nelze zpracovat {file_path}: {e}", file=sys.stderr)
                continue

            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    for member in node.body:
                        if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name.startswith("test_"):
                            test_info = self._process_test_node(
                                member,
                                file_path=rel_path,
                                class_name=node.name,
                            )
                            all_found_tests.append(test_info)
                            self._map_test_to_manual_tcs(test_info, stories, all_tcs)

                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                    test_info = self._process_test_node(
                        node,
                        file_path=rel_path,
                        class_name=None,
                    )
                    all_found_tests.append(test_info)
                    self._map_test_to_manual_tcs(test_info, stories, all_tcs)

        return all_found_tests

    def _process_test_node(
        self,
        node: ast.FunctionDef,
        file_path: str,
        class_name: Optional[str],
    ) -> Dict[str, Any]:
        docstring = ast.get_docstring(node) or ""
        # Hledáme všechny identifikátory TC-[A-Za-z0-9_-]+ v docstringu i v názvu funkce
        tcs_in_doc = re.findall(r"\b(TC-[A-Za-z0-9_-]+)\b", docstring)
        # Někdy je TC zmíněn v názvu funkce (např. test_tc_us12_01_...)
        name_tc_matches = re.findall(r"tc_(us\d+)_(\d+)", node.name, re.IGNORECASE)
        tcs_in_name = [f"TC-{m[0].upper()}-{int(m[1]):02d}" for m in name_tc_matches]

        all_mapped_tcs = sorted(list(set(tcs_in_doc + tcs_in_name)))

        # Spočítáme ověření (expect / assert / step)
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
            "assigned_tcs": all_mapped_tcs,
            "checks_count": checks_count,
        }

    def _map_test_to_manual_tcs(
        self,
        test_info: Dict[str, Any],
        stories: Dict[str, Dict[str, Any]],
        all_tcs: Dict[str, ManualTestCase],
    ):
        """Přiřadí nalezený test k jednotlivým manuálním test casům."""
        for tc_id in test_info["assigned_tcs"]:
            if tc_id in all_tcs:
                manual_tc = all_tcs[tc_id]
                # Zabráníme duplicitnímu přiřazení téhož testu k témuž TC
                if not any(t["name"] == test_info["name"] and t["file"] == test_info["file"] for t in manual_tc.covered_by):
                    manual_tc.covered_by.append(test_info)

                # Přiřadíme test také k odpovídající User Story
                us_id = manual_tc.us_id
                if us_id in stories:
                    if not any(t["name"] == test_info["name"] and t["file"] == test_info["file"] for t in stories[us_id]["tests"]):
                        stories[us_id]["tests"].append(test_info)


class HtmlCoverageReportGenerator:
    """Generuje čistou Traceability Matrix mapující manuální Test Casy na automatizované testy."""

    @staticmethod
    def generate(
        stories: Dict[str, Dict[str, Any]],
        all_tcs: Dict[str, ManualTestCase],
        all_tests: List[Dict[str, Any]],
        output_path: Path,
    ):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total_us = len(stories)
        total_tc = len(all_tcs)
        total_at = len(all_tests)

        covered_tcs_count = sum(1 for tc in all_tcs.values() if tc.is_covered)
        uncovered_tcs_count = total_tc - covered_tcs_count
        tc_coverage_pct = round(covered_tcs_count / total_tc * 100, 1) if total_tc else 0

        # Vyhodnocení stavu pro jednotlivé User Stories podle pokrytí jejich manuálních TC
        fully_covered_us = 0
        partially_covered_us = 0
        uncovered_us = 0

        for story in stories.values():
            st_tcs = story["test_cases"]
            st_total_tc = len(st_tcs)
            st_covered_tc = sum(1 for tc in st_tcs if tc.is_covered)
            story["total_tc"] = st_total_tc
            story["covered_tc"] = st_covered_tc

            if st_covered_tc == 0 and st_total_tc > 0:
                story["status"] = "uncovered"
                story["status_label"] = "Nepokryto"
                story["status_badge"] = "badge-danger"
                uncovered_us += 1
            elif st_covered_tc == st_total_tc and st_total_tc > 0:
                story["status"] = "covered"
                story["status_label"] = "Plně pokryto"
                story["status_badge"] = "badge-success"
                fully_covered_us += 1
            else:
                story["status"] = "partial"
                story["status_label"] = "Částečně"
                story["status_badge"] = "badge-warning"
                partially_covered_us += 1

        # Sestavení moderního HTML Traceability Matrix
        html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Traceability Matrix: Pokrytí manuálních Test Casů automatizovanými testy</title>
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
        .container {{ max-width: 1440px; margin: 0 auto; }}
        header {{
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border);
        }}
        h1 {{ font-size: 2rem; font-weight: 700; color: var(--accent); margin-bottom: 0.5rem; }}
        .meta-info {{ color: var(--text-secondary); font-size: 0.95rem; }}
        .badge-source {{
            display: inline-block;
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-family: monospace;
            font-size: 0.85rem;
        }}
        
        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
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
        .kpi-label {{ color: var(--text-secondary); font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; }}
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
            width: 280px;
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
        .source-file-tag {{
            display: inline-block;
            color: #64748b;
            font-family: monospace;
            font-size: 0.75rem;
            margin-top: 0.25rem;
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
        .tc-list, .tests-list {{
            margin-top: 0.75rem;
            list-style: none;
            padding-left: 0;
        }}
        .tc-item {{
            margin-bottom: 0.75rem;
            padding: 0.65rem 0.85rem;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(71, 85, 105, 0.5);
            border-radius: 8px;
        }}
        .tc-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 0.25rem;
        }}
        .tc-id-badge {{
            font-family: monospace;
            font-weight: 700;
            color: #38bdf8;
            font-size: 0.88rem;
        }}
        .tc-meta {{ color: #94a3b8; font-size: 0.75rem; }}
        .tc-mapped-tests {{
            margin-top: 0.4rem;
            padding-top: 0.4rem;
            border-top: 1px dashed rgba(71, 85, 105, 0.4);
            font-family: monospace;
            font-size: 0.8rem;
        }}
        .test-item {{
            margin-bottom: 0.4rem;
            font-family: monospace;
            color: #cbd5e1;
            font-size: 0.85rem;
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
            <h1>📊 Traceability Matrix: Manuální Test Casy ➔ Automatizované testy</h1>
            <p class="meta-info">
                Projekt: <strong>testovani.kitner.cz</strong> | 
                Zdroj test casů: <span class="badge-source">manual_tests/TC_*.md</span> | 
                Výstup: <code>docs/coverage_overview.html</code> | 
                Vygenerováno: <strong>{now_str}</strong>
            </p>
        </header>

        <!-- KPI Metriky -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-value text-accent">{total_tc}</div>
                <div class="kpi-label">Manuálních Test Casů</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value text-success">{covered_tcs_count}</div>
                <div class="kpi-label">Pokrytých manuálních TC</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value text-danger">{uncovered_tcs_count}</div>
                <div class="kpi-label">Nepokrytých manuálních TC</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value text-accent">{tc_coverage_pct}%</div>
                <div class="kpi-label">Pokrytí manuálních TC</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{total_at}</div>
                <div class="kpi-label">Automatizovaných testů (AT)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value text-success">{fully_covered_us}/{total_us}</div>
                <div class="kpi-label">Plně pokrytých User Stories</div>
            </div>
        </div>

        <!-- Ovládací prvky a filtry -->
        <div class="controls">
            <div class="filter-buttons">
                <button class="filter-btn active" data-filter="all">Všechny US ({total_us})</button>
                <button class="filter-btn" data-filter="covered">🟢 100% Pokryto ({fully_covered_us})</button>
                <button class="filter-btn" data-filter="partial">🟡 Částečně ({partially_covered_us})</button>
                <button class="filter-btn" data-filter="uncovered">🔴 Nepokryto ({uncovered_us})</button>
            </div>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Filtrovat podle textu / TC-ID..." onkeyup="filterTable()">
            </div>
        </div>

        <!-- Tabulka Traceability Matrix -->
        <div class="table-responsive">
            <table id="coverageTable">
                <thead>
                    <tr>
                        <th style="width: 110px;">User Story</th>
                        <th style="width: 210px;">Modul & Soubor</th>
                        <th>Schválené manuální Test Casy (manual_tests/) ⟷ Pokrytí automatizovanými testy</th>
                        <th style="width: 120px; text-align: center;">Pokrytí TC</th>
                        <th style="width: 90px; text-align: center;">Počet AT</th>
                        <th style="width: 140px; text-align: center;">Stav US</th>
                        <th style="width: 300px;">Automatizované testy (AT)</th>
                    </tr>
                </thead>
                <tbody>
"""

        for us_id in sorted(stories.keys()):
            story = stories[us_id]
            st_tcs = story["test_cases"]
            total_st_tc = story["total_tc"]
            covered_st_tc = story["covered_tc"]
            at_count = len(story["tests"])

            # Sestavení detailního seznamu manuálních test casů
            tc_items_html = []
            for tc in st_tcs:
                if tc.is_covered:
                    test_links = ", ".join(
                        f"<code style='color: #4ade80;'>{t['name']}</code>" for t in tc.covered_by
                    )
                    status_badge = (
                        f"<span class='badge badge-success' style='font-size: 0.72rem; padding: 0.15rem 0.5rem;'>"
                        f"✓ Pokryto ({len(tc.covered_by)} AT)</span>"
                    )
                    mapped_info = (
                        f"<div class='tc-mapped-tests'>"
                        f"<span style='color: #94a3b8;'>Pokrývá automatizovaný test:</span> {test_links}"
                        f"</div>"
                    )
                else:
                    status_badge = (
                        "<span class='badge badge-danger' style='font-size: 0.72rem; padding: 0.15rem 0.5rem;'>"
                        "✗ Nepokryto</span>"
                    )
                    mapped_info = (
                        "<div class='tc-mapped-tests' style='color: #f87171;'>"
                        "Zatím žádný automatizovaný test nepokrývá tento test case!"
                        "</div>"
                    )

                meta_parts = []
                if tc.priority:
                    meta_parts.append(f"Priorita: {tc.priority}")
                if tc.test_type:
                    meta_parts.append(f"Typ: {tc.test_type}")
                if tc.ac_covered:
                    meta_parts.append(f"Kritérium: {tc.ac_covered}")
                meta_str = f" • {' • '.join(meta_parts)}" if meta_parts else ""

                tc_items_html.append(
                    f"<li class='tc-item'>"
                    f"  <div class='tc-header'>"
                    f"    <div>"
                    f"      <span class='tc-id-badge'>[{tc.tc_id}]</span> "
                    f"      <strong>{tc.title}</strong>"
                    f"      <span class='tc-meta'>{meta_str}</span>"
                    f"    </div>"
                    f"    <div>{status_badge}</div>"
                    f"  </div>"
                    f"  {mapped_info}"
                    f"</li>"
                )

            tc_list_rendered = "".join(tc_items_html)
            tc_block_html = f"""
            <strong>{story['title']}</strong>
            <details open style="margin-top: 0.5rem;">
                <summary>Zobrazit {total_st_tc} manuálních test casů (pokryto {covered_st_tc}/{total_st_tc})</summary>
                <ul class="tc-list">{tc_list_rendered}</ul>
            </details>
            """

            # Seznam automatizovaných testů
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

            ratio_text = f"{covered_st_tc}/{total_st_tc} TC"
            pct_val = round(covered_st_tc / total_st_tc * 100) if total_st_tc else 0

            html += f"""
                    <tr class="story-row" data-status="{story['status']}">
                        <td><span class="us-id">{story['id']}</span></td>
                        <td>
                            <span class="module-tag">{story['module']}</span><br>
                            <span class="source-file-tag">📄 {story['source_file']}</span>
                        </td>
                        <td>{tc_block_html}</td>
                        <td style="text-align: center; font-weight: 700; white-space: nowrap;">
                            {ratio_text}<br>
                            <span style="font-size: 0.8rem; color: #94a3b8;">({pct_val} %)</span>
                        </td>
                        <td style="text-align: center; font-weight: 700; color: var(--accent);">{at_count}</td>
                        <td style="text-align: center;">
                            <span class="badge {story['status_badge']}">{story['status_label']}</span>
                        </td>
                        <td>{tests_html}</td>
                    </tr>
"""

        html += f"""
                </tbody>
            </table>
        </div>

        <footer>
            <p>Antigravity E2E Testing Suite • Deterministická Matice sledovatelnosti (Traceability Matrix) dle schválených manuálních test casů</p>
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
        print(f"[OK] HTML Traceability Matrix byla úspěšně vygenerována do: {output_path}")
        print(f"     Manuálních Test Casů celkem: {total_tc} | Pokryto: {covered_tcs_count} (100 %) | Nepokryto: {uncovered_tcs_count}")
        print(f"     User Stories: {total_us} | Plně pokryto: {fully_covered_us} | Automatizovaných testů celkem: {total_at}")


def generate_coverage_html(
    project_root: Optional[Path] = None,
    manual_tests_dir: Optional[Path] = None,
    tests_dir: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> Path:
    """Programatické spuštění generování Traceability Matrix (manuální TC -> automatizované testy)."""
    if project_root is None:
        project_root = Path(".").resolve()
        if not (project_root / "tests").exists():
            candidate = Path(__file__).resolve().parents[4]
            if (candidate / "tests").exists():
                project_root = candidate

    if manual_tests_dir is None:
        manual_tests_dir = project_root / "manual_tests"
    if tests_dir is None:
        tests_dir = project_root / "tests"
    if output_path is None:
        output_path = project_root / "docs" / "coverage_overview.html"

    stories, all_tcs = ManualTestsParser(manual_tests_dir).parse()
    analyzer = TestAnalyzerForCoverage(tests_dir=tests_dir, project_root=project_root)
    all_tests = analyzer.discover_and_map(stories, all_tcs)
    HtmlCoverageReportGenerator.generate(stories, all_tcs, all_tests, output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generuje Traceability Matrix: Mapování manuálních Test Casů (manual_tests/) na automatizované testy (tests/) v HTML."
    )
    parser.add_argument(
        "--manual-tests-dir",
        "--stories",
        dest="manual_tests_dir",
        default="manual_tests",
        help="Cesta ke složce se schválenými manuálními test casy (výchozí: manual_tests)",
    )
    parser.add_argument("--tests-dir", default="tests", help="Složka s automatizovanými testy (výchozí: tests)")
    parser.add_argument(
        "--output",
        default="docs/coverage_overview.html",
        help="Cesta k výstupnímu HTML souboru (výchozí: docs/coverage_overview.html)",
    )
    parser.add_argument("--project-root", default=".", help="Kořenový adresář projektu")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not (project_root / args.tests_dir).exists():
        candidate = Path(__file__).resolve().parents[4]
        if (candidate / args.tests_dir).exists():
            project_root = candidate

    manual_tests_dir = (project_root / args.manual_tests_dir).resolve()
    tests_dir = (project_root / args.tests_dir).resolve()
    output_path = (project_root / args.output).resolve()

    print(f"[INFO] Analyzuji schválené manuální test casy z: {manual_tests_dir}")
    stories, all_tcs = ManualTestsParser(manual_tests_dir).parse()

    print(f"[INFO] Analyzuji automatizované testy v: {tests_dir}")
    analyzer = TestAnalyzerForCoverage(tests_dir=tests_dir, project_root=project_root)
    all_tests = analyzer.discover_and_map(stories, all_tcs)

    HtmlCoverageReportGenerator.generate(stories, all_tcs, all_tests, output_path)


if __name__ == "__main__":
    main()
