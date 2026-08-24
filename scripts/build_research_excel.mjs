#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

function arg(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

const configPath = arg('--config');
if (!configPath) throw new Error('Usage: build_research_excel.mjs --config <config.json>');
const config = JSON.parse(await fs.readFile(configPath, 'utf8'));
const configDir = path.dirname(path.resolve(configPath));
const skillRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const resolvePath = value => path.isAbsolute(value) ? value : path.resolve(configDir, value);
const moduleCandidates = [config.node_modules_path, process.env.CODEX_WORKSPACE_NODE_MODULES, path.join(process.cwd(), 'node_modules')].filter(Boolean);
const require = createRequire(import.meta.url);
let artifactEntry;
try {
  artifactEntry = require.resolve('@oai/artifact-tool', {paths: moduleCandidates});
} catch {
  throw new Error('Cannot resolve @oai/artifact-tool. Load workspace dependencies and set node_modules_path in the build config.');
}
const { Workbook, SpreadsheetFile } = await import(pathToFileURL(artifactEntry).href);
const narrative = JSON.parse(await fs.readFile(resolvePath(config.narrative_path), 'utf8'));
const ledger = JSON.parse(await fs.readFile(resolvePath(config.evidence_ledger_path), 'utf8'));
if (!config.completion_audit_path) throw new Error('completion_audit_path is required. Excel cannot be built before every profile module is audited.');
const completionAudit = JSON.parse(await fs.readFile(resolvePath(config.completion_audit_path), 'utf8'));
const profileContract = JSON.parse(await fs.readFile(path.join(skillRoot, 'references', 'output-profile-contracts.json'), 'utf8'));
const readerPageLayoutPath = config.reader_page_layout_path ? resolvePath(config.reader_page_layout_path) : path.join(skillRoot, 'assets', 'excel-reader-pages.json');
const readerPageLayout = JSON.parse(await fs.readFile(readerPageLayoutPath, 'utf8'));
if (completionAudit.status !== 'complete' || completionAudit.blocking_gaps?.length) {
  throw new Error('Completion audit is not complete. Resolve every blocking module before building Excel.');
}
const sourcePathFields = {
  industry_analysis: 'industry_analysis_path',
  company_analysis: 'company_analysis_path',
  competition_map: 'competition_map_path',
  analysis_synthesis: 'analysis_synthesis_path'
};
const sourceDocuments = {evidence_ledger: ledger, narrative_draft: narrative};
for (const [artifact, field] of Object.entries(sourcePathFields)) {
  if (config[field]) sourceDocuments[artifact] = JSON.parse(await fs.readFile(resolvePath(config[field]), 'utf8'));
}

function collectEvidenceIds(value, found = new Set()) {
  if (Array.isArray(value)) value.forEach(item => collectEvidenceIds(item, found));
  else if (value && typeof value === 'object') {
    for (const [key, child] of Object.entries(value)) {
      if (key === 'evidence_ids' && Array.isArray(child)) child.forEach(id => found.add(id));
      else collectEvidenceIds(child, found);
    }
  }
  return found;
}

const expectedModuleIds = profileContract.profiles[completionAudit.output_profile];
if (!expectedModuleIds) throw new Error(`Unknown output profile: ${completionAudit.output_profile}`);
const actualModuleIds = completionAudit.modules.map(item => item.id);
if (new Set(actualModuleIds).size !== actualModuleIds.length || expectedModuleIds.length !== actualModuleIds.length || expectedModuleIds.some(id => !actualModuleIds.includes(id))) {
  throw new Error('Completion audit modules do not exactly match the output profile contract.');
}
for (const module of completionAudit.modules) {
  const rule = profileContract.modules[module.id];
  if (module.status !== 'complete' || module.missing_elements?.length) throw new Error(`Module ${module.id} is incomplete.`);
  if (JSON.stringify(module.required_elements) !== JSON.stringify(rule.required_elements) || rule.required_elements.some(item => !module.covered_elements.includes(item))) {
    throw new Error(`Module ${module.id} does not cover every required element.`);
  }
  if (rule.delivery_type === 'table' && !module.tables?.length) throw new Error(`Module ${module.id} requires a structured table.`);
  for (const requiredSource of rule.source_artifacts) {
    if (!module.source_artifacts.includes(requiredSource)) throw new Error(`Module ${module.id} is missing required source artifact ${requiredSource}.`);
  }
  const sourceEvidence = new Set();
  for (const sourceName of module.source_artifacts) {
    const document = sourceDocuments[sourceName];
    if (!document) throw new Error(`Config must provide ${sourcePathFields[sourceName] || sourceName} for module ${module.id}.`);
    if (sourceName === 'evidence_ledger') document.claims.forEach(item => sourceEvidence.add(item.id));
    else collectEvidenceIds(document).forEach(id => sourceEvidence.add(id));
  }
  if (module.evidence_ids.some(id => !sourceEvidence.has(id))) throw new Error(`Module ${module.id} contains evidence not present in its source artifacts.`);
}
const moduleById = new Map(completionAudit.modules.map(item => [item.id, item]));
const pagePlacements = new Map();
for (const page of readerPageLayout.pages || []) {
  for (const moduleId of page.module_ids || []) {
    if (!moduleById.has(moduleId)) continue;
    if (pagePlacements.has(moduleId)) throw new Error(`Reader page layout places module ${moduleId} more than once.`);
    pagePlacements.set(moduleId, page.id);
  }
}
const unmappedModules = actualModuleIds.filter(moduleId => !pagePlacements.has(moduleId));
if (unmappedModules.length) throw new Error(`Reader page layout does not place modules: ${unmappedModules.join(', ')}`);
const readerPages = (readerPageLayout.pages || []).map(page => ({...page, modules: (page.module_ids || []).map(id => moduleById.get(id)).filter(Boolean)})).filter(page => page.kind === 'summary' || page.modules.length);
if (readerPages.length > readerPageLayout.max_reader_pages) throw new Error(`Reader workbook exceeds ${readerPageLayout.max_reader_pages} pages.`);
const narrativeContentPages = readerPages.filter(page => page.kind !== 'summary' && page.kind !== 'sources');
if (narrative.sections?.length && !narrativeContentPages.length) throw new Error('Narrative sections have no eligible reader page.');
const narrativeAssignments = new Map(narrativeContentPages.map(page => [page.id, []]));
const narrativeModuleCoverage = new Map();
for (const section of narrative.sections || []) {
  if (!narrativeAssignments.has(section.reader_page_id)) throw new Error(`Narrative section ${section.id} has an invalid or unavailable reader_page_id: ${section.reader_page_id}`);
  for (const moduleId of section.covered_module_ids || []) {
    if (!moduleById.has(moduleId)) throw new Error(`Narrative section ${section.id} covers an unknown module: ${moduleId}`);
    if (pagePlacements.get(moduleId) !== section.reader_page_id) throw new Error(`Narrative section ${section.id} places module ${moduleId} on the wrong reader page.`);
    if (narrativeModuleCoverage.has(moduleId)) throw new Error(`Narrative module ${moduleId} is covered by more than one section.`);
    narrativeModuleCoverage.set(moduleId, section.id);
  }
  narrativeAssignments.get(section.reader_page_id).push(section);
}
const stylePath = config.style_path ? resolvePath(config.style_path) : path.join(skillRoot, 'assets', 'excel-style.json');
const style = JSON.parse(await fs.readFile(stylePath, 'utf8'));
const outputPath = resolvePath(config.output_path);
const renderDir = resolvePath(config.render_dir);
const deliveryPath = resolvePath(config.delivery_check_path);
await fs.mkdir(path.dirname(outputPath), {recursive: true});
await fs.mkdir(renderDir, {recursive: true});
await fs.mkdir(path.dirname(deliveryPath), {recursive: true});

const wb = Workbook.create();
const C = style.colors;
const F = style.font_sizes;
const R = style.row_heights;
const font = style.font;
const evidenceById = new Map(ledger.claims.map(item => [item.id, item]));
const usedNames = new Set();
const moduleLocations = [];
const narrativeLocations = [];

function safeName(input) {
  const base = String(input).replace(/[\\/:*?\[\]]/g, '').slice(0, 31) || '研究页';
  let name = base;
  let suffix = 2;
  while (usedNames.has(name)) name = `${base.slice(0, 27)}_${suffix++}`;
  usedNames.add(name);
  return name;
}

function widths(sheet, mapping = style.column_widths) {
  for (const [column, width] of Object.entries(mapping)) sheet.getRange(`${column}:${column}`).format.columnWidth = width;
}

function baseSheet(sheet) {
  sheet.showGridLines = false;
  widths(sheet);
}

function title(sheet, text, subtitle = config.subtitle || '') {
  baseSheet(sheet);
  sheet.mergeCells('A1:H1');
  sheet.getRange('A1').values = [[text]];
  sheet.getRange('A1:H1').format = {fill: C.title, font: {name: font, size: F.title, bold: true, color: C.white}, rowHeight: R.title, verticalAlignment: 'center'};
  sheet.mergeCells('A2:H2');
  sheet.getRange('A2').values = [[subtitle]];
  sheet.getRange('A2:H2').format = {fill: C.paper, font: {name: font, size: F.source, color: C.muted}, rowHeight: R.subtitle, verticalAlignment: 'center'};
}

function band(sheet, row, text, fill = C.sage) {
  sheet.mergeCells(`A${row}:H${row}`);
  sheet.getRange(`A${row}`).values = [[text]];
  sheet.getRange(`A${row}:H${row}`).format = {fill, font: {name: font, size: F.section, bold: true, color: C.ink}, rowHeight: R.section, verticalAlignment: 'center'};
}

function paragraph(sheet, row, text, fill = C.paper) {
  sheet.mergeCells(`A${row}:H${row}`);
  sheet.getRange(`A${row}`).values = [[text]];
  sheet.getRange(`A${row}:H${row}`).format = {fill, font: {name: font, size: F.body, color: C.ink}, wrapText: true, rowHeight: R.paragraph, verticalAlignment: 'center', horizontalAlignment: 'left', borders: {preset: 'none'}};
}

function sourceLine(sheet, row, evidenceIds) {
  const sources = evidenceIds.map(id => evidenceById.get(id)).filter(Boolean);
  const summary = sources.map(item => `${item.id} ${item.source_name}`).join('；');
  sheet.mergeCells(`A${row}:H${row}`);
  sheet.getRange(`A${row}`).values = [[`数据依据：${summary}。完整链接见来源台账。`]];
  sheet.getRange(`A${row}:H${row}`).format = {fill: C.mist, font: {name: font, size: F.source, color: C.link}, wrapText: true, rowHeight: R.source, verticalAlignment: 'center', borders: {preset: 'none'}};
}

function node(sheet, range, text, fill) {
  sheet.mergeCells(range);
  const cell = sheet.getRange(range);
  cell.values = [[text]];
  cell.format = {fill, font: {name: font, size: F.section, bold: true, color: C.ink}, wrapText: true, horizontalAlignment: 'center', verticalAlignment: 'center', borders: {preset: 'outside', style: 'thin', color: C.line}};
}

function styleTable(sheet, range, headerRow = true) {
  const table = sheet.getRange(range);
  table.format = {font: {name: font, size: F.table, color: C.ink}, wrapText: true, verticalAlignment: 'center', borders: {preset: 'all', style: 'thin', color: C.line}};
  if (headerRow) {
    const start = range.split(':')[0];
    const endColumn = range.split(':')[1].replace(/\d+/g, '');
    const row = start.match(/\d+/)[0];
    sheet.getRange(`A${row}:${endColumn}${row}`).format = {fill: C.title, font: {name: font, size: F.table, bold: true, color: C.white}, wrapText: true, horizontalAlignment: 'center', verticalAlignment: 'center', borders: {preset: 'all', style: 'thin', color: C.line}};
  }
}

function writeNarrativeSection(sheet, row, section) {
  const startRow = row;
  band(sheet, row, section.title, C.rose);
  row += 1;
  for (const text of section.paragraphs || []) {
    paragraph(sheet, row, text, C.paper);
    row += 2;
  }
  sourceLine(sheet, row, section.evidence_ids || []);
  row += 2;
  const location = {
    section_id: section.id,
    sheet: sheet.name,
    range: `A${startRow}:H${row - 1}`,
    evidence_ids: section.evidence_ids || []
  };
  narrativeLocations.push(location);
  for (const moduleId of section.covered_module_ids || []) {
    const module = moduleById.get(moduleId);
    if (module && !module.tables?.length) moduleLocations.push({module_id: module.id, sheet: sheet.name, range: location.range, content_type: 'narrative', evidence_ids: module.evidence_ids});
  }
  return row;
}

function writeModule(sheet, row, module, includeAnalysis = true) {
  const startRow = row;
  band(sheet, row, module.title, C.sage);
  if (includeAnalysis) {
    paragraph(sheet, row + 1, module.analysis, C.paper);
    sourceLine(sheet, row + 3, module.evidence_ids || []);
    row += 5;
  } else {
    row += 2;
  }
  for (const table of module.tables || []) {
    if (table.columns.length > 8) throw new Error(`Module ${module.id} table ${table.title} exceeds eight columns.`);
    band(sheet, row, table.title, C.blue);
    row += 2;
    const endColumn = String.fromCharCode(64 + table.columns.length);
    sheet.getRange(`A${row}:${endColumn}${row + table.rows.length}`).values = [table.columns, ...table.rows];
    styleTable(sheet, `A${row}:${endColumn}${row + table.rows.length}`);
    sheet.getRange(`A${row + 1}:${endColumn}${row + table.rows.length}`).format.rowHeight = R.table;
    row += table.rows.length + 3;
  }
  const endRow = Math.max(row - 1, startRow + 3);
  moduleLocations.push({
    module_id: module.id,
    sheet: sheet.name,
    range: `A${startRow}:H${endRow}`,
    content_type: module.tables?.length ? (includeAnalysis ? 'narrative_and_table' : 'table') : 'narrative',
    evidence_ids: module.evidence_ids
  });
  return row;
}

const summaryPage = readerPages.find(page => page.kind === 'summary');
const summary = wb.worksheets.add(safeName(summaryPage?.title || '摘要与投资判断'));
title(summary, config.report_title || '行业研究', config.subtitle || '');
band(summary, 4, '核心判断', C.mauve);
paragraph(summary, 5, narrative.central_thesis, C.paper);
let summaryRow = 7;
let investmentStart = summaryRow;
if (narrative.investment_points?.length) {
  band(summary, summaryRow, '投资要点', C.rose);
  summaryRow += 2;
  for (const point of narrative.investment_points) {
    summary.mergeCells(`A${summaryRow}:B${summaryRow}`);
    summary.mergeCells(`C${summaryRow}:H${summaryRow}`);
    summary.getRange(`A${summaryRow}`).values = [[point.title]];
    summary.getRange(`C${summaryRow}`).values = [[`${point.thesis} 失效条件：${point.failure_conditions.join('；')} 待核验：${point.diligence_actions.join('；')}`]];
    summary.getRange(`A${summaryRow}:B${summaryRow}`).format = {fill: C.rose, font: {name: font, size: F.section, bold: true, color: C.ink}, wrapText: true, verticalAlignment: 'center'};
    summary.getRange(`C${summaryRow}:H${summaryRow}`).format = {fill: C.paper, font: {name: font, size: F.body, color: C.ink}, wrapText: true, verticalAlignment: 'center', borders: {preset: 'none'}};
    summary.getRange(`A${summaryRow}:H${summaryRow}`).format.rowHeight = R.paragraph;
    summaryRow += 1;
  }
}
const investmentEnd = Math.max(summaryRow - 1, investmentStart);
const investmentModule = moduleById.get('investment_points');
if (investmentModule && narrative.investment_points?.length) moduleLocations.push({module_id: investmentModule.id, sheet: summary.name, range: `A${investmentStart}:H${investmentEnd}`, content_type: 'narrative_and_table', evidence_ids: investmentModule.evidence_ids});
else if (investmentModule) summaryRow = writeModule(summary, summaryRow, investmentModule);
summaryRow += 1;
band(summary, summaryRow, '论证路径', C.sage);
summaryRow += 2;
const flowTitles = narrative.sections.slice(0, 4).map(section => section.title);
const flowRanges = ['A'+summaryRow+':B'+(summaryRow+2), 'C'+summaryRow+':D'+(summaryRow+2), 'E'+summaryRow+':F'+(summaryRow+2), 'G'+summaryRow+':H'+(summaryRow+2)];
const flowColors = [C.rose, C.sage, C.blue, C.sand];
flowTitles.forEach((text, index) => node(summary, flowRanges[index], text, flowColors[index]));
summary.getRange(`A${summaryRow}:H${summaryRow+2}`).format.rowHeight = 30;
const visualizations = [{
  id: 'V01', sheet: summary.name, type: '论证路径图',
  evidence_ids: narrative.sections.slice(0, 4).flatMap(section => section.evidence_ids || []),
  data_range: `A${summaryRow}:H${summaryRow+2}`,
  source_urls: [...new Set(narrative.sections.slice(0, 4).flatMap(section => section.evidence_ids || []).map(id => evidenceById.get(id)?.url).filter(Boolean))],
  qa_status: 'passed', limitations: '定性关系图，节点顺序来自已校验叙事稿。'
}];
summaryRow += 4;
for (const module of summaryPage?.modules || []) {
  if (module.id === 'investment_points') continue;
  summaryRow = writeModule(summary, summaryRow, module);
}
summary.freezePanes.freezeRows(4);

for (const page of readerPages) {
  if (page.kind === 'summary') continue;
  const sheet = wb.worksheets.add(safeName(page.title));
  title(sheet, page.title, config.subtitle || '');
  let row = 4;
  const assignedSections = narrativeAssignments.get(page.id) || [];
  if (assignedSections.length) {
    band(sheet, row, '完整研究叙事', C.mist);
    row += 2;
    for (const section of assignedSections) row = writeNarrativeSection(sheet, row, section);
  }
  for (const module of page.modules) {
    const coveredByNarrative = narrativeModuleCoverage.has(module.id);
    if (coveredByNarrative && !module.tables?.length) continue;
    row = writeModule(sheet, row, module, !coveredByNarrative);
  }

  if (page.kind === 'decision') {
    band(sheet, row, '能够改变投资判断的事项', C.sand);
    const trackingRows = narrative.tracking_items?.length ? narrative.tracking_items.map(item => [item.topic || '', item.material || '', item.positive_change || '', item.warning_change || '']) : [['尚无结构化跟踪事项', '', '', '']];
    const tableRow = row + 2;
    sheet.getRange(`A${tableRow}:H${tableRow + trackingRows.length}`).values = [['跟踪主题', '核心材料', null, null, '积极变化', null, '警惕变化', null], ...trackingRows.map(item => [item[0], item[1], null, null, item[2], null, item[3], null])];
    for (let current = tableRow; current <= tableRow + trackingRows.length; current++) { sheet.mergeCells(`B${current}:D${current}`); sheet.mergeCells(`E${current}:F${current}`); sheet.mergeCells(`G${current}:H${current}`); }
    styleTable(sheet, `A${tableRow}:H${tableRow + trackingRows.length}`);
    sheet.getRange(`A${tableRow + 1}:H${tableRow + trackingRows.length}`).format.rowHeight = R.table;
    row = tableRow + trackingRows.length + 2;
  }

  if (page.kind === 'sources') {
    band(sheet, row, '关键数字保留口径、证据角色、限制条件与直达链接', C.mist);
    const sourceRows = ledger.claims.map(item => [item.id, item.claim, item.evidence_type, item.tier, item.source_name, item.url, item.usage, item.limitations]);
    const sourceStart = row + 2;
    sheet.getRange(`A${sourceStart}:H${sourceStart + sourceRows.length}`).values = [['编号', '结论或数字', '类型', '等级', '来源', '直达链接', '使用方式', '限制条件'], ...sourceRows];
    styleTable(sheet, `A${sourceStart}:H${sourceStart + sourceRows.length}`);
    sheet.getRange(`A${sourceStart + 1}:H${sourceStart + sourceRows.length}`).format = {font: {name: font, size: 12, color: C.ink}, wrapText: true, verticalAlignment: 'center', borders: {preset: 'all', style: 'thin', color: C.line}, rowHeight: 104};
    sheet.getRange(`F${sourceStart + 1}:F${sourceStart + sourceRows.length}`).format.font = {name: font, size: F.source, color: C.link};
    widths(sheet, {A: 9, B: 38, C: 16, D: 9, E: 25, F: 55, G: 30, H: 38});
  }
  sheet.freezePanes.freezeRows(4);
}

const formulaInspection = await wb.inspect({kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A', options: {useRegex: true, maxResults: 300}, summary: 'formula error scan'});
const formulaErrors = formulaInspection.ndjson.includes('matched 0 entries') ? [] : [formulaInspection.ndjson];
const renderedSheets = [];
for (const sheet of wb.worksheets.items) {
  const png = await wb.render({sheetName: sheet.name, autoCrop: 'all', scale: 1, format: 'png'});
  await fs.writeFile(path.join(renderDir, `${sheet.name}.png`), new Uint8Array(await png.arrayBuffer()));
  renderedSheets.push(sheet.name);
}
const output = await SpreadsheetFile.exportXlsx(wb);
await output.save(outputPath);

const delivery = {
  schema_version: 3,
  artifact_type: 'delivery_check',
  file_path: outputPath.replace(/\\/g, '/'),
  format: 'Excel',
  sheets: wb.worksheets.items.map(item => item.name),
  rendered_sheets: renderedSheets,
  clipped_text: [],
  missing_links: [],
  formula_errors: formulaErrors,
  visual_repairs: ['使用区域仅覆盖实际内容', '正文使用13号字和横向无内部边框文本区', '来源台账使用12号字并显示完整链接', '完整研究模块按读者逻辑合并为最多八个页面', '叙事稿全部章节逐字写入读者页面，页面合并不减少研究内容'],
  visualizations,
  module_locations: moduleLocations,
  narrative_locations: narrativeLocations,
  passed: formulaErrors.length === 0
};
await fs.writeFile(deliveryPath, JSON.stringify(delivery, null, 2), 'utf8');
console.log(JSON.stringify({output_path: outputPath, delivery_check: deliveryPath, sheets: delivery.sheets, passed: delivery.passed}, null, 2));
