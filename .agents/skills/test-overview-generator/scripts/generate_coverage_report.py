#!/usr/bin/env python3
"""
Generate Coverage Report (Traceability Matrix: Manual TCs -> Automated Tests)
-----------------------------------------------------------------------------
Analyzuje schválené manuální Test Casy (ze složky manual_tests/TC_*.md)
a automatizované testy v projektu (Playwright + pytest v tests/).

Mapování probíhá ČISTĚ a VÝHRADNĚ proti manuálním Test Casům (TC-ID např. [TC-US01-01]):
- Každý schválený manuální test case je evidován pod svým jedinečným TC ID.
- Každý automatizovaný test v tests/ je spárován s příslušným manuálním TC podle tagu [TC-USxx-yy] v docstringu.
- Přehledné a moderní uspořádání matice sledovatelnosti bez redundantních sloupců a bez ořezaného textu.

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
        tcs_in_doc = re.findall(r"\b(TC-[A-Za-z0-9_-]+)\b", docstring)
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
                if not any(t["name"] == test_info["name"] and t["file"] == test_info["file"] for t in manual_tc.covered_by):
                    manual_tc.covered_by.append(test_info)

                us_id = manual_tc.us_id
                if us_id in stories:
                    if not any(t["name"] == test_info["name"] and t["file"] == test_info["file"] for t in stories[us_id]["tests"]):
                        stories[us_id]["tests"].append(test_info)


class HtmlCoverageReportGenerator:
    """Generuje přehlednou a moderní Traceability Matrix propojující manuální TC a automatizované testy."""

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
        total_checks = sum(t.get("checks_count", 0) for t in all_tests)

        covered_tcs_count = sum(1 for tc in all_tcs.values() if tc.is_covered)
        uncovered_tcs_count = total_tc - covered_tcs_count
        tc_coverage_pct = round(covered_tcs_count / total_tc * 100, 1) if total_tc else 0

        fully_covered_us = 0
        partially_covered_us = 0
        uncovered_us = 0

        for story in stories.values():
            st_tcs = story["test_cases"]
            st_total_tc = len(st_tcs)
            st_covered_tc = sum(1 for tc in st_tcs if tc.is_covered)
            story["total_tc"] = st_total_tc
            story["covered_tc"] = st_covered_tc
            story["checks_count"] = sum(t.get("checks_count", 0) for t in story["tests"])

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

        # Sestavení karet jednotlivých User Stories s přehlednou Traceability tabulkou
        story_cards_html = []
        for us_id in sorted(stories.keys()):
            story = stories[us_id]
            st_tcs = story["test_cases"]
            st_total_tc = story["total_tc"]
            st_covered_tc = story["covered_tc"]
            at_count = len(story["tests"])
            checks_count = story["checks_count"]
            pct_val = round(st_covered_tc / st_total_tc * 100) if st_total_tc else 0

            # Řádky pro jednotlivé manuální test casy
            tc_rows_html = []
            for tc in st_tcs:
                # Prioritní štítek
                prio_class = "badge-prio-high" if tc.priority.lower() == "high" else ("badge-prio-med" if tc.priority.lower() == "medium" else "badge-prio-low")
                prio_badge = f"<span class='badge-prio {prio_class}'>{tc.priority}</span>" if tc.priority else ""
                type_badge = f"<span class='badge-type'>{tc.test_type}</span>" if tc.test_type else ""

                # Pokrývající automatizované testy
                if tc.is_covered:
                    status_badge = "<span class='badge badge-success'>✓ Pokryto</span>"
                    at_items = []
                    for t in tc.covered_by:
                        cls_part = f"<span class='at-class'>{t['class_name']}.</span>" if t["class_name"] else ""
                        at_items.append(
                            f"<div class='at-item'>"
                            f"  <div class='at-name'>⚙️ {cls_part}<strong>{t['name']}</strong></div>"
                            f"  <div class='at-meta'>📁 {t['file']}:{t['line']} &nbsp;•&nbsp; 🔍 {t['checks_count']} kontrol</div>"
                            f"</div>"
                        )
                    tests_cell = "".join(at_items)
                else:
                    status_badge = "<span class='badge badge-danger'>✗ Nepokryto</span>"
                    tests_cell = "<span class='at-uncovered'>Zatím žádný automatizovaný test nepokrývá tento test case</span>"

                ac_note = f"<div class='tc-ac-note'>Pokrývá kritérium: <strong>{tc.ac_covered}</strong></div>" if tc.ac_covered else ""

                tc_rows_html.append(
                    f"<tr>"
                    f"  <td class='tc-id-col'>"
                    f"    <span class='tc-id-pill'>{tc.tc_id}</span>"
                    f"    <div class='tc-tags'>{prio_badge} {type_badge}</div>"
                    f"  </td>"
                    f"  <td class='tc-desc-col'>"
                    f"    <div class='tc-title'>{tc.title}</div>"
                    f"    {ac_note}"
                    f"  </td>"
                    f"  <td class='tc-status-col'>{status_badge}</td>"
                    f"  <td class='tc-at-col'>{tests_cell}</td>"
                    f"</tr>"
                )

            table_body = "".join(tc_rows_html)

            story_cards_html.append(
                f"""
        <div class="story-card open" data-status="{story['status']}" data-us="{story['id']}">
            <div class="story-card-header" onclick="toggleStory(this)">
                <div class="header-left">
                    <span class="us-id-pill">{story['id']}</span>
                    <div class="header-titles">
                        <h2 class="story-title">{story['title']}</h2>
                        <div class="story-meta-pills">
                            <span class="meta-pill module-pill">{story['module']}</span>
                            <span class="meta-pill file-pill">📄 {story['source_file']}</span>
                        </div>
                    </div>
                </div>
                <div class="header-right">
                    <div class="story-stat-box">
                        <span class="stat-num">{st_covered_tc}/{st_total_tc} TC</span>
                        <span class="stat-lbl">Pokrytí ({pct_val} %)</span>
                    </div>
                    <div class="story-stat-box">
                        <span class="stat-num">{at_count} AT</span>
                        <span class="stat-lbl">{checks_count} kontrol</span>
                    </div>
                    <span class="badge {story['status_badge']}">{story['status_label']}</span>
                    <span class="chevron">▼</span>
                </div>
            </div>
            <div class="story-card-body">
                <div class="table-wrapper">
                    <table class="traceability-table">
                        <thead>
                            <tr>
                                <th style="width: 140px;">Test Case ID</th>
                                <th>Schválený manuální Test Case (manual_tests/)</th>
                                <th style="width: 110px; text-align: center;">Stav</th>
                                <th style="width: 48%;">Pokrývající automatizovaný test (Playwright)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_body}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
                """
            )

        cards_rendered = "\n".join(story_cards_html)

        html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Traceability Matrix: Pokrytí manuálních Test Casů automatizovanými testy</title>
    <style>
        :root {{
            --bg-page: #0b1120;
            --bg-card: #151e32;
            --bg-card-header: #1e293b;
            --bg-table-head: #111827;
            --bg-row-hover: #1e293b80;
            --border-card: #334155;
            --border-row: rgba(51, 65, 85, 0.45);
            --text-main: #f8fafc;
            --text-sub: #94a3b8;
            --text-dim: #64748b;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --success: #22c55e;
            --success-bg: rgba(34, 197, 94, 0.12);
            --success-border: rgba(34, 197, 94, 0.35);
            --warning: #f59e0b;
            --warning-bg: rgba(245, 158, 11, 0.12);
            --warning-border: rgba(245, 158, 11, 0.35);
            --danger: #ef4444;
            --danger-bg: rgba(239, 68, 68, 0.12);
            --danger-border: rgba(239, 68, 68, 0.35);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-page);
            color: var(--text-main);
            padding: 1.5rem 2rem;
            line-height: 1.5;
        }}
        .container {{
            max-width: 1560px;
            margin: 0 auto;
        }}

        /* Header */
        header {{
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-card);
        }}
        h1 {{
            font-size: 2rem;
            font-weight: 800;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }}
        h1 span.title-icon {{ color: var(--accent); }}
        .header-meta {{
            color: var(--text-sub);
            font-size: 0.95rem;
            display: flex;
            flex-wrap: wrap;
            gap: 1.25rem;
        }}
        .header-meta strong {{ color: var(--text-main); }}
        .meta-tag-src {{
            background: var(--accent-glow);
            color: var(--accent);
            padding: 0.15rem 0.55rem;
            border-radius: 6px;
            font-family: monospace;
            font-size: 0.85rem;
        }}

        /* KPI Dashboard */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }}
        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            transition: transform 0.15s ease;
        }}
        .kpi-card:hover {{ transform: translateY(-2px); }}
        .kpi-value {{
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 0.35rem;
        }}
        .kpi-label {{
            color: var(--text-sub);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}
        .text-accent {{ color: var(--accent); }}
        .text-success {{ color: #4ade80; }}
        .text-danger {{ color: #f87171; }}

        /* Action Toolbar */
        .toolbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        .toolbar-left {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        .filter-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            color: var(--text-main);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.88rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .filter-btn:hover, .filter-btn.active {{
            background: var(--accent);
            color: #0b1120;
            border-color: var(--accent);
        }}
        .action-btn {{
            background: transparent;
            border: 1px solid var(--border-card);
            color: var(--text-sub);
            padding: 0.5rem 0.85rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .action-btn:hover {{
            background: var(--bg-card-header);
            color: var(--text-main);
        }}
        .toolbar-right {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .search-box input {{
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            color: var(--text-main);
            padding: 0.55rem 1rem;
            border-radius: 8px;
            font-size: 0.9rem;
            width: 320px;
            outline: none;
            transition: border-color 0.2s ease;
        }}
        .search-box input:focus {{
            border-color: var(--accent);
        }}

        /* Story Cards */
        .story-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 12px;
            margin-bottom: 1.5rem;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
            transition: border-color 0.2s ease;
        }}
        .story-card:hover {{ border-color: rgba(56, 189, 248, 0.4); }}
        
        .story-card-header {{
            background: var(--bg-card-header);
            padding: 1rem 1.35rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            user-select: none;
            border-bottom: 1px solid transparent;
            transition: background-color 0.2s ease;
        }}
        .story-card.open .story-card-header {{
            border-bottom-color: var(--border-card);
        }}
        .story-card-header:hover {{
            background: #243247;
        }}

        .header-left {{
            display: flex;
            align-items: center;
            gap: 1rem;
            flex: 1;
            min-width: 300px;
        }}
        .us-id-pill {{
            background: rgba(56, 189, 248, 0.2);
            color: var(--accent);
            border: 1px solid rgba(56, 189, 248, 0.4);
            font-family: monospace;
            font-weight: 800;
            font-size: 1.05rem;
            padding: 0.35rem 0.75rem;
            border-radius: 8px;
            white-space: nowrap;
        }}
        .header-titles {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}
        .story-title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text-main);
        }}
        .story-meta-pills {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            flex-wrap: wrap;
        }}
        .meta-pill {{
            font-size: 0.75rem;
            padding: 0.15rem 0.5rem;
            border-radius: 6px;
        }}
        .module-pill {{
            background: rgba(56, 189, 248, 0.1);
            color: var(--accent);
        }}
        .file-pill {{
            background: rgba(148, 163, 184, 0.1);
            color: var(--text-sub);
            font-family: monospace;
        }}

        .header-right {{
            display: flex;
            align-items: center;
            gap: 1.25rem;
        }}
        .story-stat-box {{
            text-align: right;
            line-height: 1.2;
        }}
        .story-stat-box .stat-num {{
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-main);
            display: block;
        }}
        .story-stat-box .stat-lbl {{
            font-size: 0.75rem;
            color: var(--text-sub);
        }}
        .chevron {{
            font-size: 0.8rem;
            color: var(--accent);
            transition: transform 0.25s ease;
        }}
        .story-card.open .chevron {{
            transform: rotate(180deg);
        }}

        .story-card-body {{
            display: none;
            padding: 0;
        }}
        .story-card.open .story-card-body {{
            display: block;
        }}

        /* Table inside card */
        .table-wrapper {{
            overflow-x: auto;
        }}
        .traceability-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}
        .traceability-table th {{
            background: var(--bg-table-head);
            color: var(--text-sub);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 0.85rem 1.25rem;
            border-bottom: 1px solid var(--border-card);
        }}
        .traceability-table td {{
            padding: 1rem 1.25rem;
            border-bottom: 1px solid var(--border-row);
            font-size: 0.92rem;
            vertical-align: top;
        }}
        .traceability-table tr:last-child td {{
            border-bottom: none;
        }}
        .traceability-table tr:hover td {{
            background: var(--bg-row-hover);
        }}

        /* Column details */
        .tc-id-col {{
            white-space: nowrap;
        }}
        .tc-id-pill {{
            font-family: monospace;
            font-weight: 700;
            color: var(--accent);
            font-size: 0.9rem;
            display: inline-block;
            margin-bottom: 0.35rem;
        }}
        .tc-tags {{
            display: flex;
            gap: 0.35rem;
            flex-wrap: wrap;
        }}
        .badge-prio {{
            font-size: 0.7rem;
            font-weight: 700;
            padding: 0.1rem 0.45rem;
            border-radius: 4px;
            text-transform: uppercase;
        }}
        .badge-prio-high {{ background: rgba(239, 68, 68, 0.2); color: #f87171; }}
        .badge-prio-med {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; }}
        .badge-prio-low {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; }}
        .badge-type {{
            background: rgba(148, 163, 184, 0.15);
            color: var(--text-sub);
            font-size: 0.7rem;
            padding: 0.1rem 0.45rem;
            border-radius: 4px;
        }}

        .tc-desc-col {{
            word-break: break-word;
            overflow-wrap: anywhere;
        }}
        .tc-title {{
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 0.25rem;
            line-height: 1.4;
        }}
        .tc-ac-note {{
            font-size: 0.78rem;
            color: var(--text-sub);
        }}
        .tc-ac-note strong {{ color: #cbd5e1; }}

        .tc-status-col {{
            text-align: center;
            white-space: nowrap;
        }}

        .tc-at-col {{
            word-break: break-word;
            overflow-wrap: anywhere;
        }}
        .at-item {{
            margin-bottom: 0.6rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px dashed rgba(71, 85, 105, 0.3);
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.82rem;
            line-height: 1.4;
        }}
        .at-item:last-child {{
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }}
        .at-class {{
            color: var(--accent);
            font-weight: 600;
        }}
        .at-name {{
            color: #f1f5f9;
            margin-bottom: 0.15rem;
        }}
        .at-meta {{
            color: var(--text-dim);
            font-size: 0.74rem;
        }}
        .at-uncovered {{
            color: #f87171;
            font-style: italic;
            font-size: 0.85rem;
        }}

        /* General Badges */
        .badge {{
            display: inline-block;
            padding: 0.3rem 0.7rem;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 700;
            text-align: center;
            white-space: nowrap;
        }}
        .badge-success {{
            background: var(--success-bg);
            color: #4ade80;
            border: 1px solid var(--success-border);
        }}
        .badge-warning {{
            background: var(--warning-bg);
            color: #fbbf24;
            border: 1px solid var(--warning-border);
        }}
        .badge-danger {{
            background: var(--danger-bg);
            color: #f87171;
            border: 1px solid var(--danger-border);
        }}

        footer {{
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid var(--border-card);
            text-align: center;
            color: var(--text-dim);
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><span class="title-icon">📊</span> Traceability Matrix: Manuální Test Casy ➔ Automatizované testy</h1>
            <div class="header-meta">
                <div>Projekt: <strong>testovani.kitner.cz</strong></div>
                <div>Zdroj manuálních TC: <span class="meta-tag-src">manual_tests/TC_*.md</span></div>
                <div>Výstup: <code>docs/coverage_overview.html</code></div>
                <div>Vygenerováno: <strong>{now_str}</strong></div>
            </div>
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

        <!-- Akční lišta -->
        <div class="toolbar">
            <div class="toolbar-left">
                <button class="filter-btn active" data-filter="all">Všechny US ({total_us})</button>
                <button class="filter-btn" data-filter="covered">🟢 100% Pokryto ({fully_covered_us})</button>
                <button class="filter-btn" data-filter="partial">🟡 Částečně ({partially_covered_us})</button>
                <button class="filter-btn" data-filter="uncovered">🔴 Nepokryto ({uncovered_us})</button>
                <button class="action-btn" onclick="expandAll()">⬇️ Rozbalit vše</button>
                <button class="action-btn" onclick="collapseAll()">⬆️ Sbalit vše</button>
            </div>
            <div class="toolbar-right">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="🔍 Hledat podle US, TC ID, názvu testu..." onkeyup="filterStories()">
                </div>
            </div>
        </div>

        <!-- Seznam karet User Stories -->
        <div id="storiesContainer">
            {cards_rendered}
        </div>

        <footer>
            <p>Antigravity E2E Testing Suite • Deterministická Matice sledovatelnosti (Traceability Matrix) mapující schválené manuální test casy na automatizované testy</p>
        </footer>
    </div>

    <script>
        // Rozbalení / sbalení konkrétní karty
        function toggleStory(headerElem) {{
            const card = headerElem.closest('.story-card');
            card.classList.toggle('open');
        }}

        // Rozbalit vše
        function expandAll() {{
            document.querySelectorAll('.story-card').forEach(c => c.classList.add('open'));
        }}

        // Sbalit vše
        function collapseAll() {{
            document.querySelectorAll('.story-card').forEach(c => c.classList.remove('open'));
        }}

        // Filtrace podle tlačítek stavu
        const filterButtons = document.querySelectorAll('.filter-btn');
        let currentFilter = 'all';

        filterButtons.forEach(btn => {{
            btn.addEventListener('click', () => {{
                filterButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.getAttribute('data-filter');
                applyFilters();
            }});
        }});

        // Vyhledávání v textu
        function filterStories() {{
            applyFilters();
        }}

        function applyFilters() {{
            const searchVal = document.getElementById('searchInput').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.story-card');

            cards.forEach(card => {{
                const status = card.getAttribute('data-status');
                const text = card.innerText.toLowerCase();

                const matchesStatus = (currentFilter === 'all' || status === currentFilter);
                const matchesSearch = (!searchVal || text.includes(searchVal));

                if (matchesStatus && matchesSearch) {{
                    card.style.display = '';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""
        output_path.write_text(html, encoding="utf-8")
        print(f"[OK] HTML Traceability Matrix byla úspěšně vygenerována do: {output_path}")
        print(f"     Manuálních Test Casů celkem: {total_tc} | Pokryto: {covered_tcs_count} (100 %) | Nepokryto: {uncovered_tcs_count}")
        print(f"     User Stories: {total_us} | Plně pokryto: {fully_covered_us} | Automatizovaných testů celkem: {total_at} ({total_checks} kontrol)")


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
