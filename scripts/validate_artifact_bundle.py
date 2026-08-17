#!/usr/bin/env python3
"""Validate schema-v3 research artifacts and reconcile evidence references."""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "references" / "research-artifact-schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8-sig"))


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def resolve_ref(ref):
    node = SCHEMA
    for part in ref.removeprefix("#/").split("/"):
        node = node[part]
    return node


def type_matches(value, expected):
    mapping = {
        "object": dict,
        "array": list,
        "string": str,
        "boolean": bool,
        "integer": int,
        "number": (int, float),
    }
    return isinstance(value, mapping[expected]) and not (expected in {"integer", "number"} and isinstance(value, bool))


def validate_node(value, rule, path="$"):
    errors = []
    if "$ref" in rule:
        return validate_node(value, resolve_ref(rule["$ref"]), path)
    if "enum_ref" in rule:
        allowed = SCHEMA["enums"][rule["enum_ref"]]
        if value not in allowed:
            errors.append(f"{path} must be one of {allowed}")
        return errors
    if "const" in rule and value != rule["const"]:
        errors.append(f"{path} must equal {rule['const']!r}")
    if "enum" in rule and value not in rule["enum"]:
        errors.append(f"{path} must be one of {rule['enum']}")
    expected = rule.get("type")
    if expected and not type_matches(value, expected):
        errors.append(f"{path} must be {expected}")
        return errors
    if isinstance(value, str):
        if len(value.strip()) < rule.get("minLength", 0):
            errors.append(f"{path} is too short")
        if rule.get("pattern") and not re.search(rule["pattern"], value):
            errors.append(f"{path} does not match {rule['pattern']}")
    if isinstance(value, list):
        if len(value) < rule.get("minItems", 0):
            errors.append(f"{path} needs at least {rule['minItems']} items")
        if "items" in rule:
            for index, item in enumerate(value):
                errors.extend(validate_node(item, rule["items"], f"{path}[{index}]"))
    if isinstance(value, dict):
        for key in rule.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key} is required")
        for key, child_rule in rule.get("properties", {}).items():
            if key in value:
                errors.extend(validate_node(value[key], child_rule, f"{path}.{key}"))
    return errors


def validate_document(data, artifact_type):
    return validate_node(data, SCHEMA["$defs"][artifact_type])


def derive_profile(stage, archetype, technology):
    core = technology == "核心护城河"
    if stage == "not_applicable":
        if archetype == "大消费品":
            return "industry_consumer_core_tech" if core else "industry_consumer"
        if archetype == "软件平台":
            return "industry_software_core_tech" if core else "industry_software_service"
        if archetype == "服务与医疗" and not core:
            return "industry_software_service"
        return "industry_core_tech" if core else "industry_consumer"
    prefix = "primary" if stage == "primary_market" else "secondary"
    if archetype == "大消费品":
        return f"{prefix}_consumer_core_tech" if core else f"{prefix}_consumer"
    if archetype == "软件平台":
        return f"{prefix}_software_core_tech" if core else f"{prefix}_software_service"
    if archetype == "服务与医疗" and not core:
        return f"{prefix}_software_service"
    return f"{prefix}_core_tech" if core else f"{prefix}_consumer"


def evidence_refs(data):
    refs = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "evidence_ids" and isinstance(value, list):
                refs.extend(value)
            else:
                refs.extend(evidence_refs(value))
    elif isinstance(data, list):
        for item in data:
            refs.extend(evidence_refs(item))
    return refs


def same_path(a, b):
    try:
        return Path(a).resolve() == Path(b).resolve()
    except OSError:
        return str(a) == str(b)


def validate_bundle(record_path):
    errors = []
    record_path = Path(record_path).resolve()
    record_dir = record_path.parent
    record = load(record_path)
    errors.extend(validate_document(record, "research_record"))
    artifacts = record.get("stage_artifacts", {})
    names = {
        "brief": "brief",
        "evidence_ledger": "evidence_ledger",
        "competition_map": "competition_map",
        "narrative_draft": "narrative_draft",
        "delivery_check": "delivery_check",
    }
    docs = {}
    for key, artifact_type in names.items():
        path = artifacts.get(key)
        artifact_path = Path(path) if path else None
        if artifact_path and not artifact_path.is_absolute():
            artifact_path = record_dir / artifact_path
        if not artifact_path or not artifact_path.exists():
            errors.append(f"stage_artifacts.{key} is missing")
            continue
        artifacts[key] = str(artifact_path.resolve())
        docs[key] = load(artifact_path)
        errors.extend(validate_document(docs[key], artifact_type))
    if errors or set(docs) != set(names):
        return errors, []

    brief = docs["brief"]
    ledger = docs["evidence_ledger"]
    competition = docs["competition_map"]
    narrative = docs["narrative_draft"]
    delivery = docs["delivery_check"]

    routing = brief["routing"]
    if routing != record["routing"]:
        errors.append("record.routing must exactly match brief.routing")
    expected = derive_profile(routing["capital_market_stage"], routing["research_archetype"], routing["technology_materiality"])
    if routing["output_profile"] != expected:
        errors.append(f"routing.output_profile must be {expected}")
    brief_file = Path(record["brief_file"])
    if not brief_file.is_absolute():
        brief_file = record_dir / brief_file
    if not same_path(brief_file, artifacts["brief"]):
        errors.append("record.brief_file must match stage_artifacts.brief")
    deliverable_path = Path(record["deliverable_path"])
    if not deliverable_path.is_absolute():
        deliverable_path = record_dir / deliverable_path
    delivery_file = Path(delivery["file_path"])
    if not delivery_file.is_absolute():
        delivery_file = record_dir / delivery_file
    if not same_path(deliverable_path, delivery_file):
        errors.append("record.deliverable_path must match delivery_check.file_path")
    if brief["deliverable"] != delivery["format"]:
        errors.append("brief.deliverable must match delivery_check.format")
    if not delivery_file.exists():
        errors.append("delivery_check.file_path does not exist")

    evidence_ids = [item["id"] for item in ledger["claims"]]
    duplicates = [key for key, count in Counter(evidence_ids).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate evidence ids: {duplicates}")
    valid_ids = set(evidence_ids)
    referenced = set(evidence_refs(narrative) + evidence_refs(competition) + evidence_refs(delivery) + evidence_refs(record))
    unknown = sorted(referenced - valid_ids)
    if unknown:
        errors.append(f"unknown evidence ids: {unknown}")

    counts = Counter(item["tier"] for item in ledger["claims"])
    recorded_counts = record["coverage"]["source_counts_by_tier"]
    expected_counts = {tier: counts.get(tier, 0) for tier in "ABCD"}
    if recorded_counts != expected_counts:
        errors.append(f"coverage.source_counts_by_tier must equal {expected_counts}")
    if set(brief["required_sections"]) - set(record["coverage"]["completed_sections"]):
        errors.append("completed_sections does not cover brief.required_sections")
    if set(brief["required_sections"]) != set(record["coverage"]["required_sections"]):
        errors.append("record required_sections must match brief required_sections")
    cluster_names = [item["name"] for item in competition["clusters"]]
    if set(cluster_names) != set(record["coverage"]["competition_clusters"]):
        errors.append("record competition_clusters must match competition_map clusters")
    if set(delivery["sheets"]) != set(delivery["rendered_sheets"]):
        errors.append("all sheets must be rendered")
    for key, value in record["quality_checks"].items():
        if value is not True:
            errors.append(f"quality_checks.{key} must be true")
    for key in ("clipped_text", "missing_links", "formula_errors"):
        if delivery[key]:
            errors.append(f"delivery_check.{key} must be empty")

    evidence_url = {item["id"]: item["url"] for item in ledger["claims"]}
    for index, visual in enumerate(delivery["visualizations"]):
        required_urls = {evidence_url[item] for item in visual["evidence_ids"] if item in evidence_url}
        if not required_urls.issubset(set(visual["source_urls"])):
            errors.append(f"delivery visualization[{index}] source_urls does not cover evidence sources")
        if visual["sheet"] not in delivery["sheets"]:
            errors.append(f"delivery visualization[{index}] refers to an unknown sheet")

    warnings = []
    unused = sorted(valid_ids - referenced)
    if unused:
        warnings.append(f"unused evidence ids: {unused}")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--record")
    group.add_argument("--brief")
    args = parser.parse_args()
    if args.brief:
        errors = validate_document(load(args.brief), "brief")
        warnings = []
    else:
        errors, warnings = validate_bundle(args.record)
    if errors:
        print("FAIL")
        for item in errors:
            print("- " + item)
        sys.exit(1)
    print("PASS: schema and artifact reconciliation validated")
    for item in warnings:
        print("WARN: " + item)


if __name__ == "__main__":
    main()
