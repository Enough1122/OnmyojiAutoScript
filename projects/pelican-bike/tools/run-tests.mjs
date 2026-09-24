// 从 index.html 抽出 HARNESS / CORE / RENDER / TESTS 四块，在 node 里跑断言。
// 零依赖：只用 node 内置模块。
//
// HARNESS 块就是浏览器里跑的那一段 —— 只有一份实现，两边不可能分叉。
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';

const here = dirname(fileURLToPath(import.meta.url));
const htmlPath = join(here, '..', 'index.html');
const html = readFileSync(htmlPath, 'utf8');

function extract(begin, end) {
  const b = html.indexOf(begin);
  const e = html.indexOf(end);
  if (b === -1 || e === -1) {
    throw new Error(`找不到哨兵块 ${begin} / ${end}`);
  }
  return html.slice(b + begin.length, e);
}

const harness = extract('/* ==== HARNESS:BEGIN ==== */', '/* ==== HARNESS:END ==== */');
const core = extract('/* ==== CORE:BEGIN ==== */', '/* ==== CORE:END ==== */');
const render = extract('/* ==== RENDER:BEGIN ==== */', '/* ==== RENDER:END ==== */');
const tests = extract('/* ==== TESTS:BEGIN ==== */', '/* ==== TESTS:END ==== */');

// 用 vm 沙箱跑，防止 CORE/RENDER 里误用 DOM 全局时静默通过。
// 沙箱的全局里只有 console —— document/window 一律不存在。
const sandbox = { console };
vm.createContext(sandbox);

vm.runInContext(
  harness + '\n' + core + '\n' + render + '\n' + tests,
  sandbox,
  { filename: 'harness+core+render+tests.js' }
);

const results = sandbox.results;
if (!Array.isArray(results)) {
  throw new Error('HARNESS 块没有产出 results 数组');
}
const failed = results.filter((r) => !r.ok);
for (const r of results) {
  console.log(`${r.ok ? 'PASS' : 'FAIL'}  ${r.name}${r.ok ? '' : '  → ' + r.err}`);
}
console.log(`\n${results.length - failed.length}/${results.length} passed`);
process.exit(failed.length === 0 ? 0 : 1);
