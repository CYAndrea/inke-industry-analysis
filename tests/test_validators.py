import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
spec = importlib.util.spec_from_file_location("bundle", SCRIPTS / "validate_artifact_bundle.py")
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


def profile_module_ids(profile="industry_technology"):
    return list(bundle.PROFILE_CONTRACT["profiles"][profile])


def valid_completion_audit(profile="industry_technology"):
    modules = []
    for module_id in profile_module_ids(profile):
        rule = bundle.PROFILE_CONTRACT["modules"][module_id]
        tables = []
        if rule["delivery_type"] == "table":
            tables = [{
                "title": f"{rule['title']}明细",
                "columns": ["项目", "结论"],
                "rows": [[item, "已根据现有证据完成分析"] for item in rule["required_elements"]],
                "evidence_ids": ["E01"],
            }]
        modules.append({
            "id": module_id,
            "title": rule["title"],
            "status": "complete",
            "required_elements": list(rule["required_elements"]),
            "covered_elements": list(rule["required_elements"]),
            "missing_elements": [],
            "analysis": "该模块已经根据上游阶段产物完成逐项分析，并保留证据编号、判断边界和结构化信息。测试数据用于验证完成合同能够阻止缺失模块被误标记为完成，同时检查规定要素、必要表格和最终可见位置是否能够逐项对账。",
            "evidence_ids": ["E01"],
            "source_artifacts": list(rule["source_artifacts"]),
            "tables": tables,
        })
    return {"schema_version": 3, "artifact_type": "completion_audit", "contract_version": 1, "output_profile": profile, "status": "complete", "modules": modules, "blocking_gaps": []}


def valid_brief():
    return {
        "schema_version": 3,
        "artifact_type": "brief",
        "industry_theme": "中国工业软件",
        "target_company": "",
        "deliverable": "Excel",
        "routing": {
            "research_mode": "industry_overview",
            "capital_market_stage": "not_applicable",
            "research_subject": "industry",
            "industry_orientation": "technology",
            "analysis_dimensions": ["technology"],
            "listing_status": "not_applicable",
            "listing_exchange": "",
            "ticker": "",
            "company_maturity": "不适用",
            "information_availability": "部分",
            "output_profile": "industry_technology",
            "orientation_rationale": "工业软件位于产业数字化供应侧，企业采购取决于部署、可靠性和交付能力。",
        },
        "scope": {"geography": ["中国"], "as_of": "2026-08-18", "segments": []},
        "decision_question": "该行业未来三年的主要增长机会是什么",
        "core_hypothesis": "国产化和制造业数字化共同推动需求，但客户验证与交付效率决定增长质量。",
        "mode_rationale": "当前没有指定标的公司，因此使用无标的行业研究模式。",
        "disproof_conditions": ["客户预算连续下降"],
        "must_cover_clusters": ["直接软件产品"],
        "required_sections": profile_module_ids(),
        "output_acceptance": ["关键判断可回连来源"],
    }


def valid_narrative():
    paragraph = "行业需求由政策替代和制造企业数字化共同推动，但项目制交付仍会限制规模化速度。企业需要验证标准产品收入占比、实施周期和续费情况，才能判断增长是否具有持续性。"
    return {
        "schema_version": 3,
        "artifact_type": "narrative_draft",
        "central_thesis": "行业需求保持增长，但标准化交付能力将决定企业能否把项目收入转化为持续经营优势。",
        "argument_sequence": ["需求", "竞争"],
        "investment_points": [],
        "sections": [{
            "id": "S01",
            "title": "需求增长仍需经过交付效率验证",
            "paragraphs": [paragraph, paragraph],
            "argument_chain": {
                "conclusion": "需求继续增长",
                "mechanism": "政策替代和数字化投入共同驱动",
                "evidence": "订单和客户案例提供验证",
                "investment_implication": "关注标准产品收入和实施周期",
                "boundary": "客户预算下降时判断失效",
            },
            "evidence_ids": ["E01"],
            "table_justification": "",
            "visualizations": [],
        }],
        "tracking_items": [],
        "editorial_checks": {
            "scaffolding_hidden": True,
            "paragraphs_connected": True,
            "tables_only_when_necessary": True,
            "reader_can_follow_top_to_bottom": True,
        },
    }


def valid_finding(title="需求增长仍需验证"):
    return {
        "title": title,
        "conclusion": "行业需求保持增长，但标准化交付能力仍然决定增长质量。",
        "evidence_ids": ["E01"],
        "boundary": "客户预算持续下降时判断失效。",
        "open_questions": ["标准产品收入占比仍需核验"],
    }


def valid_handoff():
    return {
        "summary": "行业需求受到政策替代与数字化投入支持，但交付效率和客户验证仍然决定商业化质量。",
        "key_evidence_ids": ["E01"],
        "unresolved_questions": ["标准产品收入占比仍需核验"],
        "completed_sections": ["供需与竞争"],
        "next_stage_focus": ["验证竞争公司的交付效率"],
    }


def valid_industry_analysis():
    return {
        "schema_version": 3,
        "artifact_type": "industry_analysis",
        "central_question": "该行业未来三年的主要增长机会是什么",
        "findings": [valid_finding()],
        "counterevidence": [valid_finding("交付约束仍可能压低增长")],
        "handoff": valid_handoff(),
        "limitations": [],
    }


def valid_synthesis():
    return {
        "schema_version": 3,
        "artifact_type": "analysis_synthesis",
        "central_thesis": "行业需求保持增长，但标准化交付能力将决定企业能否形成持续经营优势。",
        "decision_answer": "未来机会主要来自国产替代和制造业数字化，但投资判断需要继续验证交付效率。",
        "industry_conclusions": [valid_finding()],
        "company_conclusions": [],
        "conflicts": [],
        "counterevidence": [valid_finding("交付约束仍可能压低增长")],
        "disproof_conditions": ["客户预算持续下降"],
        "section_blueprint": [
            {"title": "需求基础", "purpose": "解释行业增长来源及其持续条件。", "evidence_ids": ["E01"]},
            {"title": "交付约束", "purpose": "解释交付效率如何影响增长质量。", "evidence_ids": ["E01"]},
        ],
        "handoff": valid_handoff(),
    }


class RoutingTests(unittest.TestCase):
    def test_user_examples_follow_three_level_route(self):
        self.assertEqual(bundle.derive_profile("not_applicable", "industry", "technology"), "industry_technology")
        self.assertEqual(bundle.derive_profile("secondary_market", "company", "consumer"), "secondary_consumer_company")
        self.assertEqual(bundle.derive_profile("not_applicable", "industry", "hybrid"), "industry_hybrid")
        self.assertEqual(bundle.derive_profile("secondary_market", "company", "hybrid"), "secondary_hybrid_company")

    def test_all_nine_routes_exist_in_schema(self):
        allowed = set(bundle.SCHEMA["enums"]["output_profile"])
        expected = {
            bundle.derive_profile("not_applicable", "industry", orientation)
            for orientation in bundle.SCHEMA["enums"]["industry_orientation"]
        }
        expected.update({
            bundle.derive_profile(stage, "company", orientation)
            for stage in ("primary_market", "secondary_market")
            for orientation in bundle.SCHEMA["enums"]["industry_orientation"]
        })
        self.assertEqual(len(expected), 9)
        self.assertEqual(expected, allowed)

    def test_consumer_technology_hybrid_routes(self):
        self.assertEqual(bundle.derive_profile("not_applicable", "industry", "hybrid"), "industry_hybrid")
        self.assertEqual(bundle.derive_profile("primary_market", "company", "hybrid"), "primary_hybrid_company")
        self.assertEqual(bundle.derive_profile("secondary_market", "company", "hybrid"), "secondary_hybrid_company")

    def test_industry_route_stops_before_capital_market(self):
        routing = copy.deepcopy(valid_brief()["routing"])
        routing["capital_market_stage"] = "secondary_market"
        errors = bundle.validate_routing_consistency(routing)
        self.assertTrue(any("industry routing" in error for error in errors))

    def test_listed_company_requires_exchange_and_ticker(self):
        routing = copy.deepcopy(valid_brief()["routing"])
        routing.update({
            "research_mode": "public_company",
            "research_subject": "company",
            "capital_market_stage": "secondary_market",
            "listing_status": "listed",
            "industry_orientation": "consumer",
            "analysis_dimensions": ["consumer"],
            "company_maturity": "上市运营",
            "output_profile": "secondary_consumer_company",
        })
        errors = bundle.validate_routing_consistency(routing)
        self.assertIn("listed company must record listing_exchange", errors)
        self.assertIn("listed company must record ticker", errors)

    def test_unlisted_company_routes_to_primary_market(self):
        routing = copy.deepcopy(valid_brief()["routing"])
        routing.update({
            "research_mode": "private_company",
            "research_subject": "company",
            "capital_market_stage": "primary_market",
            "listing_status": "unlisted",
            "industry_orientation": "technology",
            "company_maturity": "增长期",
            "output_profile": "primary_technology_company",
        })
        self.assertEqual(bundle.validate_routing_consistency(routing), [])


class SchemaTests(unittest.TestCase):
    def test_valid_brief_passes(self):
        self.assertEqual(bundle.validate_document(valid_brief(), "brief"), [])
        self.assertEqual(bundle.validate_brief_semantics(valid_brief()), [])

    def test_hybrid_industry_brief_passes(self):
        brief = valid_brief()
        brief["industry_theme"] = "全球消费电子"
        brief["routing"]["industry_orientation"] = "hybrid"
        brief["routing"]["analysis_dimensions"] = ["consumer", "technology", "integration"]
        brief["routing"]["output_profile"] = "industry_hybrid"
        brief["required_sections"] = profile_module_ids("industry_hybrid")
        brief["routing"]["orientation_rationale"] = "终端消费者、品牌和渠道决定需求，核心器件、工程能力和性能成本取舍同时影响购买、毛利和产品竞争。"
        self.assertEqual(bundle.validate_document(brief, "brief"), [])
        self.assertEqual(bundle.validate_brief_semantics(brief), [])

    def test_hybrid_requires_both_templates_and_integration(self):
        brief = valid_brief()
        brief["routing"]["industry_orientation"] = "hybrid"
        brief["routing"]["analysis_dimensions"] = ["consumer", "technology"]
        brief["routing"]["output_profile"] = "industry_hybrid"
        errors = bundle.validate_brief_semantics(brief)
        self.assertIn(
            "hybrid orientation must use analysis_dimensions=['consumer', 'technology', 'integration']",
            errors,
        )

    def test_unknown_field_fails(self):
        brief = valid_brief()
        brief["source"] = "unexpected synonym"
        errors = bundle.validate_document(brief, "brief")
        self.assertTrue(any("is not allowed" in error for error in errors))

    def test_only_excel_is_an_artifact_format(self):
        self.assertEqual(bundle.SCHEMA["enums"]["deliverable"], ["Excel"])
        self.assertEqual(bundle.SCHEMA["enums"]["format"], ["Excel"])

    def test_complete_excel_bundle_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            brief = valid_brief()
            ledger = {
                "schema_version": 3,
                "artifact_type": "evidence_ledger",
                "as_of": "2026-08-18",
                "claims": [{
                    "id": "E01",
                    "claim": "制造业数字化投入继续支持工业软件需求增长。",
                    "evidence_type": "fact",
                    "tier": "A",
                    "source_name": "示例监管机构",
                    "source_title": "数字化发展公告",
                    "published_at": "2026-08-18",
                    "url": "https://example.com/source",
                    "geography": "中国",
                    "period": "2026",
                    "unit": "不适用",
                    "scope": "工业软件需求",
                    "calculation": "原始披露",
                    "usage": "支持需求判断",
                    "limitations": "示例测试证据",
                    "source_role": "监管原始披露",
                    "independence": "独立来源",
                }],
                "limitations": [],
            }
            competition = {
                "schema_version": 3,
                "artifact_type": "competition_map",
                "target": "中国工业软件",
                "customer_journey": ["发现", "采购", "续约"],
                "clusters": [{
                    "name": "直接软件产品",
                    "included": [{
                        "name": "示例公司",
                        "category": "直接竞品",
                        "why_comparable": "服务相同制造企业客户并采用相近采购预算。",
                        "evidence_ids": ["E01"],
                    }],
                    "searched_but_excluded": [],
                    "search_terms": ["工业软件公司"],
                    "stop_reason": "连续两轮检索没有新增强相关项目。",
                }],
                "target_position": "行业仍由交付效率和客户验证共同决定竞争位置。",
            }
            industry_analysis = valid_industry_analysis()
            synthesis = valid_synthesis()
            narrative = valid_narrative()
            completion = valid_completion_audit()
            output = root / "report.xlsx"
            output.write_bytes(b"test")
            reader_sheets = ["摘要与投资判断", "行业研究正文", "来源与待核验事项"]
            delivery = {
                "schema_version": 3,
                "artifact_type": "delivery_check",
                "file_path": "report.xlsx",
                "format": "Excel",
                "sheets": reader_sheets,
                "rendered_sheets": reader_sheets,
                "clipped_text": [],
                "missing_links": [],
                "formula_errors": [],
                "visual_repairs": [],
                "visualizations": [],
                "module_locations": [{
                    "module_id": module["id"],
                    "sheet": "行业研究正文",
                    "range": "A1:H12",
                    "content_type": "narrative_and_table" if module["tables"] else "narrative",
                    "evidence_ids": ["E01"],
                } for index, module in enumerate(completion["modules"])],
                "narrative_locations": [{
                    "section_id": "S01",
                    "sheet": "行业研究正文",
                    "range": "A13:H20",
                    "evidence_ids": ["E01"],
                }],
                "passed": True,
            }
            names = {
                "brief.json": brief,
                "ledger.json": ledger,
                "industry.json": industry_analysis,
                "competition.json": competition,
                "synthesis.json": synthesis,
                "narrative.json": narrative,
                "completion.json": completion,
                "delivery.json": delivery,
            }
            for name, data in names.items():
                (root / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            record = {
                "schema_version": 3,
                "artifact_type": "research_record",
                "brief_file": "brief.json",
                "completed_at": "2026-08-18",
                "deliverable_path": "report.xlsx",
                "routing": copy.deepcopy(brief["routing"]),
                "key_conclusions": [{"text": "需求增长仍需经过交付效率和客户验证。", "evidence_ids": ["E01"]}],
                "coverage": {
                    "required_sections": profile_module_ids(),
                    "completed_sections": profile_module_ids(),
                    "competition_clusters": ["直接软件产品"],
                    "source_counts_by_tier": {"A": 1, "B": 0, "C": 0, "D": 0},
                },
                "stage_artifacts": {
                    "brief": "brief.json",
                    "evidence_ledger": "ledger.json",
                    "industry_analysis": "industry.json",
                    "company_analysis": "",
                    "competition_map": "competition.json",
                    "analysis_synthesis": "synthesis.json",
                    "narrative_draft": "narrative.json",
                    "completion_audit": "completion.json",
                    "delivery_check": "delivery.json",
                },
                "quality_checks": {
                    "market_scope_separated": True,
                    "investment_points_titled": True,
                    "counterevidence_present": True,
                    "primary_market_metrics_realistic": True,
                    "industry_gate_passed": True,
                    "company_gate_passed_or_not_applicable": True,
                    "synthesis_gate_passed": True,
                    "editorial_used_synthesis_only": True,
                    "narrative_contract_passed": True,
                    "content_contract_passed": True,
                    "module_completion_passed": True,
                    "artifact_reconciliation_passed": True,
                    "all_sheets_rendered": True,
                },
                "limitations": [],
            }
            record_path = root / "record.json"
            record_path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            errors, warnings = bundle.validate_bundle(record_path)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])

            incomplete = copy.deepcopy(completion)
            incomplete["modules"].pop()
            (root / "completion.json").write_text(json.dumps(incomplete, ensure_ascii=False), encoding="utf-8")
            errors, _ = bundle.validate_bundle(record_path)
            self.assertTrue(any("completion_audit modules do not match profile" in item for item in errors))
            (root / "completion.json").write_text(json.dumps(completion, ensure_ascii=False), encoding="utf-8")

            missing_table = copy.deepcopy(completion)
            table_module = next(item for item in missing_table["modules"] if item["tables"])
            table_module["tables"] = []
            (root / "completion.json").write_text(json.dumps(missing_table, ensure_ascii=False), encoding="utf-8")
            errors, _ = bundle.validate_bundle(record_path)
            self.assertTrue(any("requires a structured table" in item for item in errors))
            (root / "completion.json").write_text(json.dumps(completion, ensure_ascii=False), encoding="utf-8")

            missing_location = copy.deepcopy(delivery)
            missing_location["module_locations"].pop()
            (root / "delivery.json").write_text(json.dumps(missing_location, ensure_ascii=False), encoding="utf-8")
            errors, _ = bundle.validate_bundle(record_path)
            self.assertTrue(any("delivery module locations do not match profile" in item for item in errors))
            (root / "delivery.json").write_text(json.dumps(delivery, ensure_ascii=False), encoding="utf-8")

            missing_narrative = copy.deepcopy(delivery)
            missing_narrative["narrative_locations"][0]["section_id"] = "S02"
            (root / "delivery.json").write_text(json.dumps(missing_narrative, ensure_ascii=False), encoding="utf-8")
            errors, _ = bundle.validate_bundle(record_path)
            self.assertTrue(any("delivery narrative locations do not match narrative draft" in item for item in errors))
            (root / "delivery.json").write_text(json.dumps(delivery, ensure_ascii=False), encoding="utf-8")

            extra_claim = copy.deepcopy(ledger["claims"][0])
            extra_claim["id"] = "E02"
            extra_claim["claim"] = "新增证据只在写作阶段出现，不应绕过综合判断门禁。"
            ledger["claims"].append(extra_claim)
            narrative["sections"][0]["evidence_ids"] = ["E02"]
            record["coverage"]["source_counts_by_tier"]["A"] = 2
            (root / "ledger.json").write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
            (root / "narrative.json").write_text(json.dumps(narrative, ensure_ascii=False), encoding="utf-8")
            record_path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
            errors, _ = bundle.validate_bundle(record_path)
            self.assertIn("narrative_draft introduces evidence not approved by analysis_synthesis", errors)

    def test_stage_handoff_and_synthesis_schemas_pass(self):
        self.assertEqual(bundle.validate_document(valid_industry_analysis(), "industry_analysis"), [])
        self.assertEqual(bundle.validate_document(valid_synthesis(), "analysis_synthesis"), [])


class ContentContractTests(unittest.TestCase):
    def run_validator(self, data):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "input.json"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_content_contract.py"), "--input", str(path)],
                text=True,
                capture_output=True,
                check=False,
            )

    def test_empty_narrative_fails(self):
        narrative = valid_narrative()
        narrative["sections"] = []
        result = self.run_validator(narrative)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no sections", result.stdout)

    def test_valid_narrative_passes(self):
        result = self.run_validator(valid_narrative())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("PASS: 0", result.stdout)


class StageGateCliTests(unittest.TestCase):
    def write_json(self, root, name, data):
        path = root / name
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def test_industry_and_synthesis_gates_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ledger = {
                "schema_version": 3,
                "artifact_type": "evidence_ledger",
                "as_of": "2026-08-18",
                "claims": [{
                    "id": "E01", "claim": "制造业数字化投入继续支持工业软件需求增长。",
                    "evidence_type": "fact", "tier": "A", "source_name": "示例机构",
                    "source_title": "示例公告", "published_at": "2026-08-18",
                    "url": "https://example.com/source", "geography": "中国", "period": "2026",
                    "unit": "不适用", "scope": "工业软件需求", "calculation": "原始披露",
                    "usage": "支持需求判断", "limitations": "示例证据",
                    "source_role": "原始披露", "independence": "独立来源",
                }],
                "limitations": [],
            }
            ledger_path = self.write_json(root, "ledger.json", ledger)
            industry_path = self.write_json(root, "industry.json", valid_industry_analysis())
            synthesis_path = self.write_json(root, "synthesis.json", valid_synthesis())
            for args in (
                ["--industry-analysis", str(industry_path), "--ledger", str(ledger_path)],
                ["--synthesis", str(synthesis_path), "--industry-source", str(industry_path), "--ledger", str(ledger_path)],
            ):
                result = subprocess.run(
                    [sys.executable, str(SCRIPTS / "validate_artifact_bundle.py"), *args],
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_narrative_gate_rejects_unapproved_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ledger = {
                "schema_version": 3,
                "artifact_type": "evidence_ledger",
                "as_of": "2026-08-18",
                "claims": [],
                "limitations": [],
            }
            for evidence_id in ("E01", "E02"):
                ledger["claims"].append({
                    "id": evidence_id, "claim": "该证据用于验证阶段门禁是否阻止写作阶段新增研究内容。",
                    "evidence_type": "fact", "tier": "A", "source_name": "示例机构",
                    "source_title": "示例公告", "published_at": "2026-08-18",
                    "url": f"https://example.com/{evidence_id}", "geography": "中国", "period": "2026",
                    "unit": "不适用", "scope": "阶段门禁", "calculation": "原始披露",
                    "usage": "验证门禁", "limitations": "示例证据",
                    "source_role": "原始披露", "independence": "独立来源",
                })
            narrative = valid_narrative()
            narrative["sections"][0]["evidence_ids"] = ["E02"]
            ledger_path = self.write_json(root, "ledger.json", ledger)
            narrative_path = self.write_json(root, "narrative.json", narrative)
            synthesis_path = self.write_json(root, "synthesis.json", valid_synthesis())
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_artifact_bundle.py"),
                 "--narrative", str(narrative_path), "--synthesis-source", str(synthesis_path),
                 "--ledger", str(ledger_path)],
                text=True, capture_output=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not approved by analysis_synthesis", result.stdout)


class PortabilityTests(unittest.TestCase):
    def test_default_excel_config_has_no_style_absolute_path(self):
        config = json.loads((ROOT / "assets" / "excel-build-config.json").read_text(encoding="utf-8"))
        self.assertNotIn("style_path", config)

    def test_package_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "validate_skill_package.py"), str(ROOT)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class DeliveryRoutingTests(unittest.TestCase):
    def test_missing_format_requires_user_choice(self):
        question = "本次希望以聊天格式还是 Excel 格式输出？"
        files = [
            ROOT / "SKILL.md",
            ROOT / "references" / "execution-contracts.md",
            ROOT / "subskills" / "team-research-intake" / "SKILL.md",
        ]
        for path in files:
            text = path.read_text(encoding="utf-8-sig")
            self.assertIn(question, text)
            self.assertNotIn("默认聊天", text)

    def test_explicit_format_is_not_reasked(self):
        text = (ROOT / "references" / "team-research-log.md").read_text(encoding="utf-8-sig")
        self.assertIn("用户已经明确格式时不得重复询问", text)


if __name__ == "__main__":
    unittest.main()
