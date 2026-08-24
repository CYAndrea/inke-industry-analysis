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
PROFILE_CONTRACT_PATH = ROOT / "references" / "output-profile-contracts.json"
PROFILE_CONTRACT = json.loads(PROFILE_CONTRACT_PATH.read_text(encoding="utf-8-sig"))
READER_PAGE_LAYOUT_PATH = ROOT / "assets" / "excel-reader-pages.json"
READER_PAGE_LAYOUT = json.loads(READER_PAGE_LAYOUT_PATH.read_text(encoding="utf-8-sig"))
READER_PAGE_TITLES = {page["id"]: page["title"] for page in READER_PAGE_LAYOUT["pages"]}
MODULE_PAGE_IDS = {module_id: page["id"] for page in READER_PAGE_LAYOUT["pages"] for module_id in page.get("module_ids", [])}


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
        properties = rule.get("properties", {})
        if SCHEMA.get("closed_objects") and properties:
            unexpected = sorted(set(value) - set(properties))
            for key in unexpected:
                errors.append(f"{path}.{key} is not allowed")
        for key in rule.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key} is required")
        for key, child_rule in properties.items():
            if key in value:
                errors.extend(validate_node(value[key], child_rule, f"{path}.{key}"))
    return errors


def validate_document(data, artifact_type):
    return validate_node(data, SCHEMA["$defs"][artifact_type])


def derive_profile(stage, subject, orientation):
    if orientation not in {"consumer", "technology", "hybrid"}:
        raise ValueError(f"unsupported industry_orientation: {orientation}")
    if subject == "industry":
        if stage != "not_applicable":
            raise ValueError("industry research must use capital_market_stage=not_applicable")
        return f"industry_{orientation}"
    if subject == "company":
        prefixes = {
            "primary_market": "primary",
            "secondary_market": "secondary",
        }
        if stage not in prefixes:
            raise ValueError("company research must use primary_market or secondary_market")
        return f"{prefixes[stage]}_{orientation}_company"
    raise ValueError(f"unsupported research_subject: {subject}")


def validate_routing_consistency(routing):
    errors = []
    subject = routing.get("research_subject")
    stage = routing.get("capital_market_stage")
    listing = routing.get("listing_status")
    exchange = routing.get("listing_exchange", "").strip()
    ticker = routing.get("ticker", "").strip()
    mode = routing.get("research_mode")
    maturity = routing.get("company_maturity")
    orientation = routing.get("industry_orientation")
    dimensions = routing.get("analysis_dimensions", [])

    expected_dimensions = {
        "consumer": ["consumer"],
        "technology": ["technology"],
        "hybrid": ["consumer", "technology", "integration"],
    }.get(orientation)
    if expected_dimensions is not None and dimensions != expected_dimensions:
        errors.append(f"{orientation} orientation must use analysis_dimensions={expected_dimensions}")

    if subject == "industry":
        if stage != "not_applicable":
            errors.append("industry routing must use capital_market_stage=not_applicable")
        if listing != "not_applicable":
            errors.append("industry routing must use listing_status=not_applicable")
        if exchange or ticker:
            errors.append("industry routing must leave listing_exchange and ticker empty")
        if mode not in {"industry_overview", "competitive_scan"}:
            errors.append("industry routing must use industry_overview or competitive_scan")
        if maturity != "不适用":
            errors.append("industry routing must use company_maturity=不适用")
    elif subject == "company":
        if listing == "listed":
            if stage != "secondary_market":
                errors.append("listed company must use capital_market_stage=secondary_market")
            if not exchange:
                errors.append("listed company must record listing_exchange")
            if not ticker:
                errors.append("listed company must record ticker")
            if mode not in {"public_company", "competitive_scan"}:
                errors.append("listed company must use public_company or competitive_scan")
            if maturity != "上市运营":
                errors.append("listed company must use company_maturity=上市运营")
        elif listing == "unlisted":
            if stage != "primary_market":
                errors.append("unlisted company must use capital_market_stage=primary_market")
            if exchange or ticker:
                errors.append("unlisted company must leave listing_exchange and ticker empty")
            if mode not in {"private_company", "competitive_scan"}:
                errors.append("unlisted company must use private_company or competitive_scan")
            if maturity in {"上市运营", "不适用"}:
                errors.append("unlisted company must record a non-listed company maturity")
        elif listing == "not_applicable":
            errors.append("company routing must record listed or unlisted status")

    try:
        expected = derive_profile(stage, subject, orientation)
    except ValueError as exc:
        errors.append(str(exc))
    else:
        if routing.get("output_profile") != expected:
            errors.append(f"routing.output_profile must be {expected}")
    return errors


def validate_brief_semantics(brief):
    errors = validate_routing_consistency(brief.get("routing", {}))
    profile = brief.get("routing", {}).get("output_profile")
    expected_sections = PROFILE_CONTRACT["profiles"].get(profile)
    if expected_sections is None:
        errors.append(f"no output profile completion contract found for {profile}")
    elif set(brief.get("required_sections", [])) != set(expected_sections):
        errors.append("brief.required_sections must exactly match the output profile contract")
    subject = brief.get("routing", {}).get("research_subject")
    target = brief.get("target_company", "").strip()
    if subject == "company" and not target:
        errors.append("company research must record target_company")
    if subject == "industry" and target:
        errors.append("industry research must leave target_company empty")
    return errors


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


def validate_stage_evidence(data, ledger, label):
    errors = []
    valid_ids = {item["id"] for item in ledger.get("claims", [])}
    unknown = sorted(set(evidence_refs(data)) - valid_ids)
    if unknown:
        errors.append(f"{label} contains unknown evidence ids: {unknown}")
    return errors


def validate_synthesis_sources(synthesis, industry, company=None):
    errors = []
    industry_refs = set(evidence_refs(industry))
    synthesis_industry_refs = set(evidence_refs(synthesis.get("industry_conclusions", [])))
    if not synthesis_industry_refs.issubset(industry_refs):
        errors.append("analysis_synthesis industry conclusions must come from industry_analysis")
    if company is None:
        if synthesis.get("company_conclusions"):
            errors.append("industry research synthesis must leave company_conclusions empty")
    else:
        if not synthesis.get("company_conclusions"):
            errors.append("company research synthesis must include company_conclusions")
        company_refs = set(evidence_refs(company))
        synthesis_company_refs = set(evidence_refs(synthesis.get("company_conclusions", [])))
        if not synthesis_company_refs.issubset(company_refs):
            errors.append("analysis_synthesis company conclusions must come from company_analysis")
    covered_modules = [module_id for section in synthesis.get("section_blueprint", []) for module_id in section.get("covered_module_ids", [])]
    duplicate_modules = sorted(key for key, count in Counter(covered_modules).items() if count > 1)
    if duplicate_modules:
        errors.append(f"analysis_synthesis section_blueprint assigns modules more than once: {duplicate_modules}")
    for index, section in enumerate(synthesis.get("section_blueprint", []), 1):
        page_id = section.get("reader_page_id")
        for module_id in section.get("covered_module_ids", []):
            if module_id not in MODULE_PAGE_IDS:
                errors.append(f"analysis_synthesis section {index} covers unknown module {module_id}")
            elif MODULE_PAGE_IDS[module_id] != page_id:
                errors.append(f"analysis_synthesis section {index} places module {module_id} on the wrong reader page")
    return errors


def validate_narrative_source(narrative, synthesis):
    errors = []
    narrative_refs = set(evidence_refs(narrative))
    synthesis_refs = set(evidence_refs(synthesis))
    if not narrative_refs.issubset(synthesis_refs):
        errors.append("narrative_draft introduces evidence not approved by analysis_synthesis")
    blueprint = synthesis.get("section_blueprint", [])
    sections = narrative.get("sections", [])
    if len(blueprint) != len(sections):
        errors.append("narrative_draft sections must exactly match analysis_synthesis.section_blueprint")
        return errors
    for index, (planned, written) in enumerate(zip(blueprint, sections), 1):
        if written.get("title") != planned.get("title"):
            errors.append(f"narrative section {index} must preserve the blueprint title")
        if written.get("reader_page_id") != planned.get("reader_page_id"):
            errors.append(f"narrative section {index} must preserve reader_page_id from the blueprint")
        if written.get("covered_module_ids") != planned.get("covered_module_ids"):
            errors.append(f"narrative section {index} must preserve covered_module_ids from the blueprint")
        if set(written.get("evidence_ids", [])) != set(planned.get("evidence_ids", [])):
            errors.append(f"narrative section {index} must preserve evidence_ids from the blueprint")
    return errors


def artifact_evidence_ids(name, document):
    if name == "evidence_ledger":
        return {item["id"] for item in document.get("claims", [])}
    return set(evidence_refs(document))


def validate_completion_audit(audit, profile, docs, delivery):
    errors = []
    profile_modules = PROFILE_CONTRACT["profiles"].get(profile)
    if not profile_modules:
        return [f"no completion contract found for output_profile={profile}"]
    definitions = PROFILE_CONTRACT["modules"]
    modules = audit.get("modules", [])
    module_ids = [item.get("id") for item in modules]
    duplicates = [key for key, count in Counter(module_ids).items() if count > 1]
    if duplicates:
        errors.append(f"completion_audit has duplicate modules: {duplicates}")
    if set(module_ids) != set(profile_modules):
        missing = sorted(set(profile_modules) - set(module_ids))
        extra = sorted(set(module_ids) - set(profile_modules))
        errors.append(f"completion_audit modules do not match profile; missing={missing}, extra={extra}")
    if audit.get("output_profile") != profile:
        errors.append("completion_audit.output_profile must match routing.output_profile")
    if audit.get("status") != "complete":
        errors.append("completion_audit.status must be complete")
    if audit.get("blocking_gaps"):
        errors.append("completion_audit.blocking_gaps must be empty")

    module_by_id = {item.get("id"): item for item in modules}
    narrative = docs.get("narrative_draft", {})
    narrative_coverage = [module_id for section in narrative.get("sections", []) for module_id in section.get("covered_module_ids", [])]
    narrative_exempt = {"investment_points", "industry_outlook", "sources_limitations"}
    expected_narrative_modules = set(profile_modules) - narrative_exempt
    unknown_coverage = sorted(set(narrative_coverage) - set(profile_modules))
    missing_coverage = sorted(expected_narrative_modules - set(narrative_coverage))
    duplicate_coverage = sorted(key for key, count in Counter(narrative_coverage).items() if count > 1)
    if unknown_coverage:
        errors.append(f"narrative covers modules outside the output profile: {unknown_coverage}")
    if missing_coverage:
        errors.append(f"narrative does not cover required modules: {missing_coverage}")
    if duplicate_coverage:
        errors.append(f"narrative covers modules more than once: {duplicate_coverage}")
    for module_id in profile_modules:
        module = module_by_id.get(module_id)
        if not module:
            continue
        rule = definitions[module_id]
        if module.get("title") != rule["title"]:
            errors.append(f"completion_audit.{module_id}.title must match the profile contract")
        if module.get("required_elements") != rule["required_elements"]:
            errors.append(f"completion_audit.{module_id}.required_elements must match the profile contract")
        missing_elements = sorted(set(rule["required_elements"]) - set(module.get("covered_elements", [])))
        if module.get("status") != "complete" or module.get("missing_elements") or missing_elements:
            errors.append(f"completion_audit.{module_id} is incomplete; missing={missing_elements or module.get('missing_elements', [])}")
        required_sources = set(rule["source_artifacts"])
        recorded_sources = set(module.get("source_artifacts", []))
        if not required_sources.issubset(recorded_sources):
            errors.append(f"completion_audit.{module_id}.source_artifacts must include {sorted(required_sources)}")
        available_refs = set()
        for source_name in recorded_sources:
            source = docs.get(source_name)
            if source is None:
                errors.append(f"completion_audit.{module_id} refers to unavailable artifact {source_name}")
            else:
                available_refs.update(artifact_evidence_ids(source_name, source))
        module_refs = set(module.get("evidence_ids", []))
        if not module_refs.issubset(available_refs):
            errors.append(f"completion_audit.{module_id} uses evidence not present in its source artifacts")
        tables = module.get("tables", [])
        if rule["delivery_type"] == "table" and not tables:
            errors.append(f"completion_audit.{module_id} requires a structured table")
        for index, table in enumerate(tables):
            columns = table.get("columns", [])
            if len(columns) > 8:
                errors.append(f"completion_audit.{module_id}.tables[{index}] exceeds eight Excel columns")
            for row_index, row in enumerate(table.get("rows", [])):
                if len(row) != len(columns):
                    errors.append(f"completion_audit.{module_id}.tables[{index}].rows[{row_index}] column count mismatch")
            if not set(table.get("evidence_ids", [])).issubset(module_refs):
                errors.append(f"completion_audit.{module_id}.tables[{index}] evidence must be included in module evidence_ids")

    locations = delivery.get("module_locations", [])
    sheets = delivery.get("sheets", [])
    if len(sheets) > 8:
        errors.append(f"Excel reader workbook must contain at most eight visible sheets; found={len(sheets)}")
    mechanical_module_sheets = [name for name in sheets if str(name).startswith("模块-")]
    if mechanical_module_sheets:
        errors.append(f"Excel reader workbook must merge audit modules into reader pages; mechanical sheets={mechanical_module_sheets}")
    location_ids = [item.get("module_id") for item in locations]
    location_counts = Counter(location_ids)
    if set(location_ids) != set(profile_modules):
        missing = sorted(set(profile_modules) - set(location_ids))
        extra = sorted(set(location_ids) - set(profile_modules))
        errors.append(f"delivery module locations do not match profile; missing={missing}, extra={extra}")
    repeated = sorted(key for key, count in location_counts.items() if count != 1)
    if repeated:
        errors.append(f"delivery module locations must contain one visible location per module: {repeated}")
    for location in locations:
        module_id = location.get("module_id")
        if location.get("sheet") not in delivery.get("sheets", []):
            errors.append(f"delivery module {module_id} refers to an unknown sheet")
        module = module_by_id.get(module_id, {})
        if not set(location.get("evidence_ids", [])).issubset(set(module.get("evidence_ids", []))):
            errors.append(f"delivery module {module_id} evidence must come from completion_audit")

    narrative = docs.get("narrative_draft", {})
    narrative_sections = narrative.get("sections", [])
    narrative_by_id = {item.get("id"): item for item in narrative_sections}
    narrative_locations = delivery.get("narrative_locations", [])
    narrative_location_ids = [item.get("section_id") for item in narrative_locations]
    narrative_location_counts = Counter(narrative_location_ids)
    if set(narrative_location_ids) != set(narrative_by_id):
        missing = sorted(set(narrative_by_id) - set(narrative_location_ids))
        extra = sorted(set(narrative_location_ids) - set(narrative_by_id))
        errors.append(f"delivery narrative locations do not match narrative draft; missing={missing}, extra={extra}")
    repeated_narratives = sorted(key for key, count in narrative_location_counts.items() if count != 1)
    if repeated_narratives:
        errors.append(f"delivery narrative locations must contain one visible location per section: {repeated_narratives}")
    for location in narrative_locations:
        section_id = location.get("section_id")
        if location.get("sheet") not in sheets:
            errors.append(f"delivery narrative section {section_id} refers to an unknown sheet")
        section = narrative_by_id.get(section_id, {})
        expected_sheet = READER_PAGE_TITLES.get(section.get("reader_page_id"))
        if expected_sheet and location.get("sheet") != expected_sheet:
            errors.append(f"delivery narrative section {section_id} is not written to its assigned reader page")
        if set(location.get("evidence_ids", [])) != set(section.get("evidence_ids", [])):
            errors.append(f"delivery narrative section {section_id} must preserve all evidence ids from narrative_draft")
    return errors


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
        "industry_analysis": "industry_analysis",
        "competition_map": "competition_map",
        "analysis_synthesis": "analysis_synthesis",
        "narrative_draft": "narrative_draft",
        "completion_audit": "completion_audit",
        "delivery_check": "delivery_check",
    }
    subject = record.get("routing", {}).get("research_subject")
    if subject == "company":
        names["company_analysis"] = "company_analysis"
    elif artifacts.get("company_analysis"):
        errors.append("industry research must leave stage_artifacts.company_analysis empty")
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
    industry = docs["industry_analysis"]
    company = docs.get("company_analysis")
    competition = docs["competition_map"]
    synthesis = docs["analysis_synthesis"]
    narrative = docs["narrative_draft"]
    completion = docs["completion_audit"]
    delivery = docs["delivery_check"]

    routing = brief["routing"]
    if routing != record["routing"]:
        errors.append("record.routing must exactly match brief.routing")
    errors.extend(validate_brief_semantics(brief))
    errors.extend(validate_synthesis_sources(synthesis, industry, company))
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
    referenced = set(
        evidence_refs(industry)
        + evidence_refs(company or {})
        + evidence_refs(competition)
        + evidence_refs(synthesis)
        + evidence_refs(narrative)
        + evidence_refs(completion)
        + evidence_refs(delivery)
        + evidence_refs(record)
    )
    unknown = sorted(referenced - valid_ids)
    if unknown:
        errors.append(f"unknown evidence ids: {unknown}")

    synthesis_refs = set(evidence_refs(synthesis))
    errors.extend(validate_narrative_source(narrative, synthesis))
    errors.extend(validate_completion_audit(completion, routing["output_profile"], docs, delivery))
    record_refs = set(evidence_refs(record.get("key_conclusions", [])))
    if not record_refs.issubset(synthesis_refs):
        errors.append("research_record key conclusions introduce evidence not approved by analysis_synthesis")

    counts = Counter(item["tier"] for item in ledger["claims"])
    recorded_counts = record["coverage"]["source_counts_by_tier"]
    expected_counts = {tier: counts.get(tier, 0) for tier in "ABCD"}
    if recorded_counts != expected_counts:
        errors.append(f"coverage.source_counts_by_tier must equal {expected_counts}")
    contract_sections = PROFILE_CONTRACT["profiles"][routing["output_profile"]]
    if set(brief["required_sections"]) != set(contract_sections):
        errors.append("brief.required_sections must exactly match the output profile contract")
    if set(record["coverage"]["required_sections"]) != set(contract_sections):
        errors.append("record required_sections must exactly match the output profile contract")
    if set(record["coverage"]["completed_sections"]) != set(contract_sections):
        errors.append("record completed_sections must be derived from all completed contract modules")
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
    group.add_argument("--industry-analysis")
    group.add_argument("--company-analysis")
    group.add_argument("--synthesis")
    group.add_argument("--narrative")
    parser.add_argument("--ledger")
    parser.add_argument("--industry-source")
    parser.add_argument("--company-source")
    parser.add_argument("--synthesis-source")
    args = parser.parse_args()
    if args.brief:
        brief = load(args.brief)
        errors = validate_document(brief, "brief")
        if not errors:
            errors.extend(validate_brief_semantics(brief))
        warnings = []
    elif args.record:
        errors, warnings = validate_bundle(args.record)
    else:
        errors = []
        warnings = []
        if not args.ledger:
            errors.append("stage gate validation requires --ledger")
        else:
            ledger = load(args.ledger)
            errors.extend(validate_document(ledger, "evidence_ledger"))
            if args.industry_analysis:
                data = load(args.industry_analysis)
                errors.extend(validate_document(data, "industry_analysis"))
                errors.extend(validate_stage_evidence(data, ledger, "industry_analysis"))
            elif args.company_analysis:
                data = load(args.company_analysis)
                errors.extend(validate_document(data, "company_analysis"))
                errors.extend(validate_stage_evidence(data, ledger, "company_analysis"))
            elif args.synthesis:
                data = load(args.synthesis)
                errors.extend(validate_document(data, "analysis_synthesis"))
                errors.extend(validate_stage_evidence(data, ledger, "analysis_synthesis"))
                if not args.industry_source:
                    errors.append("synthesis gate validation requires --industry-source")
                else:
                    industry = load(args.industry_source)
                    errors.extend(validate_document(industry, "industry_analysis"))
                    company = load(args.company_source) if args.company_source else None
                    if company is not None:
                        errors.extend(validate_document(company, "company_analysis"))
                    errors.extend(validate_synthesis_sources(data, industry, company))
            elif args.narrative:
                data = load(args.narrative)
                errors.extend(validate_document(data, "narrative_draft"))
                errors.extend(validate_stage_evidence(data, ledger, "narrative_draft"))
                if not args.synthesis_source:
                    errors.append("narrative gate validation requires --synthesis-source")
                else:
                    synthesis = load(args.synthesis_source)
                    errors.extend(validate_document(synthesis, "analysis_synthesis"))
                    errors.extend(validate_narrative_source(data, synthesis))
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
