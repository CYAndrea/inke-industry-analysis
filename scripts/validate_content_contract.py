#!/usr/bin/env python3
"""Validate narrative content and reject empty semantic checks."""

import argparse
import json
import re
import sys
from pathlib import Path


def sentence_count(text):
    return len([item for item in re.split(r"[。！？!?；;]+", text) if item.strip()])


def looks_like_keyword_list(text):
    sentences = max(sentence_count(text), 1)
    return text.count("、") + text.count(",") + text.count("，") >= max(4, sentences * 3)


def validate_legacy_block(block):
    errors = []
    text = block.get("text", "")
    if not isinstance(text, str) or len(text.strip()) < 35:
        return ["text is too short"]
    if block.get("kind") == "engineering_bottleneck":
        if sentence_count(text) < 2:
            errors.append("engineering_bottleneck needs at least two sentences")
        if looks_like_keyword_list(text):
            errors.append("engineering_bottleneck appears to be a keyword list")
        required = block.get("required_elements", ["问题", "原因", "影响"])
        missing = [item for item in required if item not in text]
        if missing:
            errors.append("missing elements: " + ", ".join(missing))
    return errors


def validate_narrative(data):
    errors = []
    checked = 0
    sections = data.get("sections")
    if not isinstance(sections, list) or not sections:
        return ["narrative contains no sections"], checked
    technical_terms = re.compile(r"技术|工程|工艺|架构|部署|量产|瓶颈")
    for sidx, section in enumerate(sections, start=1):
        paragraphs = section.get("paragraphs")
        if not isinstance(paragraphs, list) or not paragraphs:
            errors.append(f"section[{sidx}] contains no paragraphs")
            continue
        text = "".join(str(item).strip() for item in paragraphs)
        checked += len(paragraphs)
        if len(text) < 140:
            errors.append(f"section[{sidx}] content is too short")
        if looks_like_keyword_list(text):
            errors.append(f"section[{sidx}] appears to be a keyword list")
        if technical_terms.search(str(section.get("title", "")) + text):
            if sentence_count(text) < 2:
                errors.append(f"section[{sidx}] technical analysis needs at least two sentences")
            chain = section.get("argument_chain", {})
            for field in ("mechanism", "investment_implication", "boundary"):
                if not str(chain.get(field, "")).strip():
                    errors.append(f"section[{sidx}].argument_chain.{field} is required for technical analysis")
    points = data.get("investment_points", [])
    if not isinstance(points, list):
        errors.append("investment_points must be a list")
    else:
        for pidx, point in enumerate(points, start=1):
            checked += 1
            if not str(point.get("thesis", "")).strip():
                errors.append(f"investment_points[{pidx}].thesis is required")
            for field in ("evidence_ids", "failure_conditions", "diligence_actions"):
                if not isinstance(point.get(field), list) or not point[field]:
                    errors.append(f"investment_points[{pidx}].{field} must be non-empty")
    return errors, checked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    errors = []
    checked = 0
    if isinstance(data, dict) and data.get("artifact_type") == "narrative_draft":
        errors, checked = validate_narrative(data)
    else:
        blocks = data.get("blocks") if isinstance(data, dict) else data
        if not isinstance(blocks, list) or not blocks:
            errors.append("input contains no narrative blocks")
        else:
            for index, block in enumerate(blocks, start=1):
                checked += 1
                for error in validate_legacy_block(block):
                    errors.append(f"block[{index}]: {error}")
    if checked == 0 and not errors:
        errors.append("no narrative content was validated")
    if errors:
        print("FAIL")
        print("\n".join("- " + error for error in errors))
        sys.exit(1)
    print(f"PASS: {checked} narrative items validated")


if __name__ == "__main__":
    main()
