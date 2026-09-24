// 从 index.html 抽出 CORE 与 TESTS 两块，在 node 里跑断言。
// 零依赖：只用 node 内置模块。
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

const core = extract('/* ==== CORE:BEGIN ==== */', '/* ==== CORE:END ==== */');
const tests = extract('/* ==== TESTS:BEGIN ==== */', '/* ==== TESTS:END ==== */');

// 用 vm 沙箱跑，防止 CORE 里误用 DOM 全局时静默通过。
const sandbox = { console, results: null };
vm.createContext(sandbox);

const harness = `
  globalThis.__results = [];
  globalThis.test = function (name, fn) {
    try { fn(); globalThis.__results.push({ name, ok: true }); }
    catch (err) { globalThis.__results.push({ name, ok: false, err: String(err && err.message || err) }); }
  };
  globalThis.assert = function (cond, msg) {
    if (!cond) throw new Error(msg || 'assertion failed');
  };
  globalThis.assertClose = function (a, b, tol, msg) {
    if (Math.abs(a - b) > tol) throw new Error((msg || 'not close') + ': ' + a + ' vs ' + b);
  };
`;

vm.runInContext(harness + core + '\n' + tests, sandbox, { filename: 'core+tests.js' });

const results = sandbox.__results;
const failed = results.filter((r) => !r.ok);
for (const r of results) {
  console.log(`${r.ok ? 'PASS' : 'FAIL'}  ${r.name}${r.ok ? '' : '  → ' + r.err}`);
}
console.log(`\n${results.length - failed.length}/${results.length} passed`);
process.exit(failed.length === 0 ? 0 : 1);
