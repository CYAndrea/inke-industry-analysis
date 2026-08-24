#!/usr/bin/env node
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const nodeModulesIndex = process.argv.indexOf('--node-modules');
const nodeModules = nodeModulesIndex >= 0 ? process.argv[nodeModulesIndex + 1] : process.env.CODEX_WORKSPACE_NODE_MODULES;
if (!nodeModules) throw new Error('Pass --node-modules with the bundled workspace dependency path.');

const temp = await fs.mkdtemp(path.join(os.tmpdir(), 'industry-skill-excel-'));
const contract = JSON.parse(await fs.readFile(path.join(root, 'references', 'output-profile-contracts.json'), 'utf8'));
const readerLayout = JSON.parse(await fs.readFile(path.join(root, 'assets', 'excel-reader-pages.json'), 'utf8'));
const profile = 'industry_technology';
const ledger = {
  schema_version: 3,
  artifact_type: 'evidence_ledger',
  as_of: '2026-08-20',
  claims: [{id: 'E01', claim: '测试证据用于验证模块内容能够完整写入工作簿。', evidence_type: 'fact', tier: 'A', source_name: '测试来源', source_title: '测试公告', published_at: '2026-08-20', url: 'https://example.com/source', geography: '中国', period: '2026', unit: '不适用', scope: '集成测试', calculation: '原始披露', usage: '验证生成器', limitations: '仅用于测试', source_role: '原始披露', independence: '独立来源'}],
  limitations: []
};
const profileModules = new Set(contract.profiles[profile]);
const paragraphOne = '完成合同把输出路径中的核心模块转换为机器可读清单，使行业、公司、竞争、财务和估值等研究成果能够在生成前逐项核对。每个模块需要保留规定要素、完整分析、证据编号和必要的结构化表格。';
const paragraphTwo = 'Excel 生成器直接读取已经通过审计的模块内容，把完整叙事与必要表格合并到最多八个读者页面，并为每项内容建立唯一位置记录。任何章节、模块、必要表格或可见位置缺失都会让跨产物校验失败。';
const narrativeSections = readerLayout.pages.filter(page => !['summary', 'sources'].includes(page.kind)).map(page => ({
  page,
  covered: page.module_ids.filter(id => profileModules.has(id))
})).filter(item => item.covered.length).map((item, index) => ({
  id: `S${String(index + 1).padStart(2, '0')}`,
  title: `${item.page.title}需要经过完整性门禁`,
  reader_page_id: item.page.id,
  covered_module_ids: item.covered,
  paragraphs: [paragraphOne, paragraphTwo],
  argument_chain: {conclusion: '核心模块必须全部进入成品', mechanism: '完成审计连接研究产物与Excel生成器', evidence: '集成测试验证生成结果', investment_implication: '避免简版交付掩盖后台完整研究', boundary: '测试不评价实际行业结论'},
  evidence_ids: ['E01'],
  table_justification: '',
  visualizations: []
}));
const narrative = {
  schema_version: 3,
  artifact_type: 'narrative_draft',
  central_thesis: '该测试报告用于验证完成合同中的全部核心模块都会出现在最终工作簿中，并形成能够被校验器定位的唯一可见页面。',
  argument_sequence: narrativeSections.map(section => section.title),
  investment_points: [],
  sections: narrativeSections,
  tracking_items: [],
  editorial_checks: {scaffolding_hidden: true, paragraphs_connected: true, tables_only_when_necessary: true, reader_can_follow_top_to_bottom: true}
};
const modules = contract.profiles[profile].map(id => {
  const rule = contract.modules[id];
  return {
    id,
    title: rule.title,
    status: 'complete',
    required_elements: rule.required_elements,
    covered_elements: rule.required_elements,
    missing_elements: [],
    analysis: '本模块已经完成合同规定的全部分析要素，并将结论、证据编号、判断边界和待核验事项写入可阅读正文。当前内容用于验证模块明细在工作簿中的传递和显示，不代表任何实际行业或公司的投资判断。',
    evidence_ids: ['E01'],
    source_artifacts: rule.source_artifacts,
    tables: rule.delivery_type === 'table' ? [{title: `${rule.title}明细`, columns: ['规定要素', '测试状态'], rows: rule.required_elements.map(item => [item, '已写入工作簿']), evidence_ids: ['E01']}] : []
  };
});
const audit = {schema_version: 3, artifact_type: 'completion_audit', contract_version: 1, output_profile: profile, status: 'complete', modules, blocking_gaps: []};
const industry = {artifact_type: 'industry_analysis', findings: [{evidence_ids: ['E01']}]};
const competition = {artifact_type: 'competition_map', clusters: [{included: [{evidence_ids: ['E01']}]}]};
const synthesis = {artifact_type: 'analysis_synthesis', industry_conclusions: [{evidence_ids: ['E01']}], counterevidence: [{evidence_ids: ['E01']}]};

const files = {ledger: path.join(temp, 'ledger.json'), narrative: path.join(temp, 'narrative.json'), audit: path.join(temp, 'completion.json'), industry: path.join(temp, 'industry.json'), competition: path.join(temp, 'competition.json'), synthesis: path.join(temp, 'synthesis.json')};
await fs.writeFile(files.ledger, JSON.stringify(ledger, null, 2));
await fs.writeFile(files.narrative, JSON.stringify(narrative, null, 2));
await fs.writeFile(files.audit, JSON.stringify(audit, null, 2));
await fs.writeFile(files.industry, JSON.stringify(industry, null, 2));
await fs.writeFile(files.competition, JSON.stringify(competition, null, 2));
await fs.writeFile(files.synthesis, JSON.stringify(synthesis, null, 2));
const config = {
  schema_version: 1,
  report_title: '完成合同集成测试',
  subtitle: '验证全部核心模块进入Excel',
  narrative_path: files.narrative,
  evidence_ledger_path: files.ledger,
  industry_analysis_path: files.industry,
  company_analysis_path: '',
  competition_map_path: files.competition,
  analysis_synthesis_path: files.synthesis,
  completion_audit_path: files.audit,
  output_path: path.join(temp, 'completion-contract-test.xlsx'),
  render_dir: path.join(temp, 'renders'),
  delivery_check_path: path.join(temp, 'delivery.json'),
  node_modules_path: nodeModules
};
const configPath = path.join(temp, 'config.json');
await fs.writeFile(configPath, JSON.stringify(config, null, 2));
const result = spawnSync(process.execPath, [path.join(root, 'scripts', 'build_research_excel.mjs'), '--config', configPath], {encoding: 'utf8'});
if (result.status !== 0) throw new Error(result.stdout + result.stderr);
const delivery = JSON.parse(await fs.readFile(config.delivery_check_path, 'utf8'));
if (delivery.module_locations.length !== modules.length) throw new Error('Not every completion module received a visible Excel location.');
if (!delivery.module_locations.every(item => delivery.sheets.includes(item.sheet) && delivery.rendered_sheets.includes(item.sheet))) throw new Error('A module location is missing from the sheet or render list.');
if (delivery.narrative_locations.length !== narrative.sections.length) throw new Error('Not every narrative section received a visible Excel location.');
if (!delivery.narrative_locations.every(item => delivery.sheets.includes(item.sheet) && delivery.rendered_sheets.includes(item.sheet))) throw new Error('A narrative location is missing from the sheet or render list.');
if (delivery.sheets.length > 8) throw new Error('Reader workbook exceeds eight sheets.');
if (delivery.sheets.some(name => name.startsWith('模块-'))) throw new Error('Reader workbook contains mechanical module sheets.');
const stat = await fs.stat(config.output_path);
if (stat.size < 1000) throw new Error('Generated workbook is unexpectedly small.');
console.log(JSON.stringify({status: 'PASS', workbook: config.output_path, module_count: modules.length, sheet_count: delivery.sheets.length, rendered_count: delivery.rendered_sheets.length}, null, 2));
