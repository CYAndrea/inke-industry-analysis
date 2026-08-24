#!/usr/bin/env python3
import argparse, json, re, sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
args = parser.parse_args()
data = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
errors = []
if data.get("schema_version") != 3 or data.get("artifact_type") != "narrative_draft":
    errors.append("narrative must use schema_version 3 and artifact_type narrative_draft")
if not isinstance(data.get("central_thesis"), str) or len(data["central_thesis"].strip()) < 30:
    errors.append("central_thesis is missing or too short")
sections = data.get("sections")
allowed_pages = {"industry", "product", "competition", "company", "financials", "decision"}
if not isinstance(sections, list) or not sections:
    errors.append("sections must be non-empty")
else:
    banned_titles = {"洞察", "驱动因素", "建议", "优势", "风险", "投资含义", "证据", "结论"}
    for idx, section in enumerate(sections, 1):
        title = str(section.get("title", "")).strip()
        if len(title) < 8:
            errors.append(f"section[{idx}].title must express a full assertion")
        if title in banned_titles:
            errors.append(f"section[{idx}].title exposes analysis scaffolding")
        if section.get("reader_page_id") not in allowed_pages:
            errors.append(f"section[{idx}].reader_page_id is invalid")
        covered_modules = section.get("covered_module_ids")
        if not isinstance(covered_modules, list) or not covered_modules:
            errors.append(f"section[{idx}].covered_module_ids must be non-empty")
        elif len(covered_modules) != len(set(covered_modules)):
            errors.append(f"section[{idx}].covered_module_ids must be unique")
        paragraphs = section.get("paragraphs")
        if not isinstance(paragraphs, list) or len(paragraphs) < 2:
            errors.append(f"section[{idx}] needs at least two connected paragraphs")
        else:
            for pidx, paragraph in enumerate(paragraphs, 1):
                text = str(paragraph).strip()
                if len(text) < 70:
                    errors.append(f"section[{idx}].paragraph[{pidx}] is too short")
                if re.match(r"^[\-•·*]\s*", text) or text.count("\n-") > 0:
                    errors.append(f"section[{idx}].paragraph[{pidx}] uses bullets for main narrative")
        chain = section.get("argument_chain", {})
        for field in ("conclusion", "mechanism", "evidence", "investment_implication", "boundary"):
            if not isinstance(chain.get(field), str) or not chain[field].strip():
                errors.append(f"section[{idx}].argument_chain.{field} is required")
        evidence_ids = section.get("evidence_ids")
        if not isinstance(evidence_ids, list) or not evidence_ids:
            errors.append(f"section[{idx}].evidence_ids must be non-empty")
points = data.get("investment_points", [])
if not isinstance(points, list):
    errors.append("investment_points must be a list")
else:
    for idx, point in enumerate(points, 1):
        for field in ("title", "thesis"):
            if not isinstance(point.get(field), str) or not point[field].strip():
                errors.append(f"investment_points[{idx}].{field} is required")
        for field in ("evidence_ids", "failure_conditions", "diligence_actions"):
            if not isinstance(point.get(field), list) or not point[field]:
                errors.append(f"investment_points[{idx}].{field} must be non-empty")
checks = data.get("editorial_checks", {})
for field in ("scaffolding_hidden", "paragraphs_connected", "tables_only_when_necessary", "reader_can_follow_top_to_bottom"):
    if checks.get(field) is not True:
        errors.append(f"editorial_checks.{field} must be true")
if errors:
    print("FAIL")
    print("\n".join("- " + item for item in errors))
    sys.exit(1)
print(f"PASS: {len(sections)} narrative sections validated")
