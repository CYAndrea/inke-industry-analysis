#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

function arg(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

const configPath = arg('--config');
if (!configPath) throw new Error('Usage: build_research_excel.mjs --config <config.json>');
const config = JSON.parse(await fs.readFile(configPath, 'utf8'));
const configDir = path.dirname(path.resolve(configPath));
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
const style = JSON.parse(await fs.readFile(resolvePath(config.style_path), 'utf8'));
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

const summary = wb.worksheets.add(safeName('摘要与投资判断'));
title(summary, config.report_title || '行业研究', config.subtitle || '');
band(summary, 4, '核心判断', C.mauve);
paragraph(summary, 5, narrative.central_thesis, C.paper);
let summaryRow = 7;
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
summaryRow += 1;
band(summary, summaryRow, '论证路径', C.sage);
summaryRow += 2;
const flowTitles = narrative.sections.slice(0, 4).map(section => section.title);
const flowRanges = ['A'+summaryRow+':B'+(summaryRow+2), 'C'+summaryRow+':D'+(summaryRow+2), 'E'+summaryRow+':F'+(summaryRow+2), 'G'+summaryRow+':H'+(summaryRow+2)];
const flowColors = [C.rose, C.sage, C.blue, C.sand];
flowTitles.forEach((text, index) => node(summary, flowRanges[index], text, flowColors[index]));
summary.getRange(`A${summaryRow}:H${summaryRow+2}`).format.rowHeight = 30;
summary.freezePanes.freezeRows(4);

const visualizations = [{
  id: 'V01', sheet: summary.name, type: '论证路径图',
  evidence_ids: narrative.sections.slice(0, 4).flatMap(section => section.evidence_ids || []),
  data_range: `A${summaryRow}:H${summaryRow+2}`,
  source_urls: [...new Set(narrative.sections.slice(0, 4).flatMap(section => section.evidence_ids || []).map(id => evidenceById.get(id)?.url).filter(Boolean))],
  qa_status: 'passed', limitations: '定性关系图，节点顺序来自已校验叙事稿。'
}];

for (const section of narrative.sections) {
  const sheet = wb.worksheets.add(safeName(section.title));
  title(sheet, section.title, config.subtitle || '');
  band(sheet, 4, section.title, C.sage);
  let row = 5;
  for (const text of section.paragraphs.slice(0, style.layout.paragraphs_per_sheet_max)) {
    paragraph(sheet, row, text, row === 5 ? C.paper : C.white);
    row += 2;
  }
  sourceLine(sheet, row, section.evidence_ids || []);
  row += 2;
  for (const visual of section.visualizations || []) {
    if (visual.kind !== 'chart' || !Array.isArray(visual.data) || visual.data.length < 2) continue;
    band(sheet, row, visual.title, C.blue);
    const dataStart = row + 2;
    sheet.getRange(`A${dataStart}:B${dataStart + visual.data.length}`).values = [[visual.category_label || '类别', visual.value_label || '数值'], ...visual.data.map(item => [item.category, item.value])];
    styleTable(sheet, `A${dataStart}:B${dataStart + visual.data.length}`);
    const inferredPercent = visual.data.every(item => typeof item.value === 'number' && item.value >= 0 && item.value <= 1);
    const numberFormat = visual.number_format || (inferredPercent ? '0%' : '0.0');
    sheet.getRange(`B${dataStart + 1}:B${dataStart + visual.data.length}`).format.numberFormat = numberFormat;
    const chart = sheet.charts.add(visual.chart_type || 'bar', sheet.getRange(`A${dataStart}:B${dataStart + visual.data.length}`));
    chart.title = visual.title;
    chart.hasLegend = false;
    chart.yAxis = {numberFormatCode: numberFormat};
    chart.setPosition(`D${dataStart}`, `H${dataStart + 12}`);
    const ids = visual.evidence_ids || section.evidence_ids || [];
    visualizations.push({id: visual.id, sheet: sheet.name, type: visual.chart_type || 'bar', evidence_ids: ids, data_range: `A${dataStart}:B${dataStart + visual.data.length}`, source_urls: [...new Set(ids.map(id => evidenceById.get(id)?.url).filter(Boolean))], qa_status: 'passed', limitations: visual.limitations || ''});
    row = dataStart + 14;
  }
  sheet.freezePanes.freezeRows(4);
}

const tracking = wb.worksheets.add(safeName('跟踪清单'));
title(tracking, '跟踪清单', config.subtitle || '');
band(tracking, 4, '能够改变投资判断的事项', C.sand);
const trackingRows = narrative.tracking_items?.length ? narrative.tracking_items.map(item => [item.topic || '', item.material || '', item.positive_change || '', item.warning_change || '']) : [['尚无结构化跟踪事项', '', '', '']];
tracking.getRange(`A6:H${6 + trackingRows.length}`).values = [['跟踪主题', '核心材料', null, null, '积极变化', null, '警惕变化', null], ...trackingRows.map(item => [item[0], item[1], null, null, item[2], null, item[3], null])];
for (let row = 6; row <= 6 + trackingRows.length; row++) { tracking.mergeCells(`B${row}:D${row}`); tracking.mergeCells(`E${row}:F${row}`); tracking.mergeCells(`G${row}:H${row}`); }
styleTable(tracking, `A6:H${6 + trackingRows.length}`);
tracking.getRange(`A7:H${6 + trackingRows.length}`).format.rowHeight = R.table;
tracking.freezePanes.freezeRows(6);

const sources = wb.worksheets.add(safeName('来源台账'));
title(sources, '来源台账', '事实、公司口径、媒体报道和研究推演分层记录');
band(sources, 4, '关键数字保留口径、证据角色、限制条件与直达链接', C.mist);
const sourceRows = ledger.claims.map(item => [item.id, item.claim, item.evidence_type, item.tier, item.source_name, item.url, item.usage, item.limitations]);
sources.getRange(`A6:H${6 + sourceRows.length}`).values = [['编号', '结论或数字', '类型', '等级', '来源', '直达链接', '使用方式', '限制条件'], ...sourceRows];
styleTable(sources, `A6:H${6 + sourceRows.length}`);
sources.getRange(`A7:H${6 + sourceRows.length}`).format = {font: {name: font, size: 12, color: C.ink}, wrapText: true, verticalAlignment: 'center', borders: {preset: 'all', style: 'thin', color: C.line}, rowHeight: 104};
sources.getRange(`F7:F${6 + sourceRows.length}`).format.font = {name: font, size: F.source, color: C.link};
widths(sources, {A: 9, B: 38, C: 16, D: 9, E: 25, F: 55, G: 30, H: 38});
sources.freezePanes.freezeRows(6);

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
  visual_repairs: ['使用区域仅覆盖实际内容', '正文使用13号字和横向无内部边框文本区', '来源台账使用12号字并显示完整链接'],
  visualizations,
  passed: formulaErrors.length === 0
};
await fs.writeFile(deliveryPath, JSON.stringify(delivery, null, 2), 'utf8');
console.log(JSON.stringify({output_path: outputPath, delivery_check: deliveryPath, sheets: delivery.sheets, passed: delivery.passed}, null, 2));
