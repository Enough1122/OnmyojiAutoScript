# 鹈鹕骑士 · 喉囊弹匣 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 交付一个双击即玩的单文件 Canvas 跑酷游戏：鹈鹕骑车，喉囊当弹匣，自动吞、手动吐。

**Architecture:** 单个 `index.html` 内含四块——`CORE`（纯逻辑）、`RENDER`（绘制与音频，只用注入的参数、不碰 DOM）、`TESTS`（断言）、`APP`（唯一允许访问 DOM 的一层）。`tools/run-tests.mjs` 用 node 抽出 `CORE`+`RENDER`+`TESTS` 三块求值运行；`?test=1` 在浏览器里跑同一份 `TESTS`。产物是单文件，测试是真能跑的。

**Tech Stack:** 原生 HTML/CSS/JS，Canvas 2D，Web Audio。零依赖、零外部资源。

**Spec:** `docs/superpowers/specs/2026-09-24-pelican-bike-runner-design.md`

## Global Constraints

- 产物是**单个** `projects/pelican-bike/index.html`，双击可玩。无图片、无音频文件、无 CDN、无 npm 依赖。
- 不使用 ES modules（`file://` 下会被 CORS 拦截）。只用经典 `<script>` 或内联脚本。
- `CORE` 与 `RENDER` 块内**禁止**引用 `document`、`window`、`canvas`、`AudioContext`——这两块要能在 node 沙箱里求值。DOM 访问只允许出现在 `APP` 块。
- 需要 `AudioContext` 时，把构造函数作为**参数**注入（`createAudio(Ctor)`），不要在块内直接读 `window`。
- 所有 commit message 以 `Co-Authored-By: Claude Code <noreply@anthropic.com>` 结尾。
- 现有 `projects/pelican-bike/pelican-bike.html` 不动。
- 数值以 spec 为准，本计划出现的常量必须与 spec 第 5 节逐字一致。
- 哨兵注释逐字使用，测试运行器靠它定位：
  - `/* ==== CORE:BEGIN ==== */` … `/* ==== CORE:END ==== */`
  - `/* ==== RENDER:BEGIN ==== */` … `/* ==== RENDER:END ==== */`
  - `/* ==== TESTS:BEGIN ==== */` … `/* ==== TESTS:END ==== */`
  - `/* ==== APP:BEGIN ==== */` … `/* ==== APP:END ==== */`
- 各任务里的 `Expected: N/N passed` 是**累计**通过数（测试只增不减）。数量对不上值得查，但真正的门槛是**没有 FAIL 行**、退出码为 0。

## Review Focus

以下五类是 spec 隐含但任何单测都覆盖不到、最可能让玩家撞上的问题。每条都在归属任务里配了测试或显式验收步骤。

1. **`file://` 下整体打不开** —— 任何 `import`/`export`/`fetch`/外部 `src` 都会让双击白屏。Task 1 与 Task 13 各验一次。
2. **切标签页回来时间跳变** —— `requestAnimationFrame` 的 `dt` 在切标签后可能是几十秒，会让鹈鹕瞬移穿墙、难度瞬间拉满。Task 6 负责 height 钳制，Task 13 负责 `clampDt`，两处缺一不可。
3. **喉囊满时连续碰撞同一道具** —— 满囊后同一道具每帧重复触发吞入判定，可能重复计数或音效连发。Task 2 覆盖。
4. **冲刺无敌与受击无敌互相覆盖** —— 两套计时器若共用一个变量，冲刺结束会意外剥夺受击无敌。Task 7 覆盖。
5. **localStorage 被禁用或写满** —— 隐私模式下 `setItem` 会抛异常，未捕获会让整局崩在结算页。Task 12 覆盖。

---

### Task 1: 走通测试管线（骨架）

先证明「单文件 + 可测」这条管线真的通，再往里填内容。这一步不写任何游戏逻辑。

**Files:**
- Create: `projects/pelican-bike/index.html`
- Create: `projects/pelican-bike/tools/run-tests.mjs`

**Interfaces:**
- Consumes: 无
- Produces: `CORE`/`TESTS` 哨兵块约定；`run-tests.mjs` 退出码语义（全过 = 0，有失败 = 1）

- [ ] **Step 1: 写测试运行器**

创建 `projects/pelican-bike/tools/run-tests.mjs`：

```js
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
```

- [ ] **Step 2: 写最小 index.html，只为验证管线**

创建 `projects/pelican-bike/index.html`。这一步的内容是临时的脚手架，Task 2 起才替换成真逻辑：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>鹈鹕骑士 · 喉囊弹匣</title>
</head>
<body>
<pre id="out"></pre>
<script>
/* ==== CORE:BEGIN ==== */
function addOne(n) { return n + 1; }
/* ==== CORE:END ==== */

/* ==== TESTS:BEGIN ==== */
test('addOne 加一', function () {
  assert(addOne(1) === 2, '1 + 1 应该等于 2');
});
test('addOne 对 0 也成立', function () {
  assert(addOne(0) === 1, '0 + 1 应该等于 1');
});
/* ==== TESTS:END ==== */

// ?test=1 时把结果画到页面上
if (location.search.indexOf('test=1') !== -1) {
  var lines = results.map(function (r) {
    return (r.ok ? 'PASS  ' : 'FAIL  ') + r.name + (r.ok ? '' : '  → ' + r.err);
  });
  var failed = results.filter(function (r) { return !r.ok; }).length;
  lines.push('');
  lines.push((results.length - failed) + '/' + results.length + ' passed');
  document.getElementById('out').textContent = lines.join('\n');
}
</script>
</body>
</html>
```

注意：上面 `test`/`assert`/`results` 在浏览器里必须已存在。在 `TESTS` 块之前补一个浏览器侧的迷你 harness（node 侧由 `run-tests.mjs` 提供，两边同名同语义）：

```js
// 浏览器侧 harness —— node 侧由 run-tests.mjs 注入等价实现
var results = [];
function test(name, fn) {
  try { fn(); results.push({ name: name, ok: true }); }
  catch (err) { results.push({ name: name, ok: false, err: String(err && err.message || err) }); }
}
function assert(cond, msg) { if (!cond) throw new Error(msg || 'assertion failed'); }
function assertClose(a, b, tol, msg) {
  if (Math.abs(a - b) > tol) throw new Error((msg || 'not close') + ': ' + a + ' vs ' + b);
}
```

把这个 harness 放在 `/* ==== CORE:BEGIN ==== */` **之前**（它不属于 CORE，node 侧不抽它）。

- [ ] **Step 3: 跑测试，确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected:
```
PASS  addOne 加一
PASS  addOne 对 0 也成立

2/2 passed
```
退出码 0。

- [ ] **Step 4: 故意改坏一条断言，确认测试真的会失败**

把 `assert(addOne(1) === 2, ...)` 临时改成 `=== 3`，重跑。
Expected: `FAIL  addOne 加一`，`1/2 passed`，退出码 1。
**改回来。**

这一步是防「假绿灯」——如果运行器抽错了块或静默吞异常，这里就会暴露。

- [ ] **Step 5: 确认 file:// 能打开**

在文件管理器里双击 `projects/pelican-bike/index.html`，确认浏览器打开且控制台无报错；再把地址改成 `…/index.html?test=1`，确认页面显示 `2/2 passed`。

- [ ] **Step 6: Commit**

```bash
cd /d/hermes
git add projects/pelican-bike/index.html projects/pelican-bike/tools/run-tests.mjs
git commit -F - <<'EOF'
搭建单文件游戏的测试管线(CORE/TESTS 哨兵块 + node 运行器)

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```

---

### Task 2: 喉囊队列

整个游戏的创意核心。FIFO、容量 6、吐空返回 null。

**Files:**
- Modify: `projects/pelican-bike/index.html`（替换 `CORE` 块内容，追加 `TESTS`）

**Interfaces:**
- Consumes: Task 1 的哨兵块与 harness
- Produces:
  - `POUCH_CAPACITY` → `6`
  - `createPouch(capacity)` → `{ items: string[], capacity: number }`
  - `pouchSwallow(pouch, item)` → `boolean`（满则 `false` 且不改变 pouch）
  - `pouchSpit(pouch)` → `string | null`（空则 `null`）
  - `pouchCount(pouch)` → `number`
  - `pouchIsFull(pouch)` → `boolean`

- [ ] **Step 1: 写失败测试**

把 `index.html` 里 `TESTS` 块的 `addOne` 两条断言删掉，换成：

```js
test('喉囊容量为 6', function () {
  assert(POUCH_CAPACITY === 6, 'spec 规定容量 6');
});

test('吞入后长度增加', function () {
  var p = createPouch(POUCH_CAPACITY);
  assert(pouchCount(p) === 0, '初始应为空');
  assert(pouchSwallow(p, 'fish') === true, '未满时应吞入成功');
  assert(pouchCount(p) === 1, '吞入后应为 1');
});

test('FIFO：吐出顺序等于吞入顺序', function () {
  var p = createPouch(POUCH_CAPACITY);
  ['fish', 'rock', 'chili'].forEach(function (it) { pouchSwallow(p, it); });
  assert(pouchSpit(p) === 'fish', '第一个吐出的应是第一个吞入的');
  assert(pouchSpit(p) === 'rock', '第二个吐出的应是第二个吞入的');
  assert(pouchSpit(p) === 'chili', '第三个吐出的应是第三个吞入的');
});

test('容量上限：第 7 个被拒且不改变囊内容', function () {
  var p = createPouch(POUCH_CAPACITY);
  for (var i = 0; i < 6; i++) assert(pouchSwallow(p, 'fish') === true, '第 ' + (i + 1) + ' 个应成功');
  assert(pouchIsFull(p) === true, '6 个后应为满');
  assert(pouchSwallow(p, 'star') === false, '满囊吞入应返回 false');
  assert(pouchCount(p) === 6, '满囊被拒后长度仍应为 6');
  assert(pouchSpit(p) === 'fish', '被拒的 star 不应进囊，第一个仍是 fish');
});

test('吐空囊返回 null 且不抛异常', function () {
  var p = createPouch(POUCH_CAPACITY);
  assert(pouchSpit(p) === null, '空囊应返回 null');
  assert(pouchCount(p) === 0, '空囊吐出后仍为空');
});

test('Review Focus 3：满囊时同一道具重复判定不重复计数', function () {
  var p = createPouch(POUCH_CAPACITY);
  for (var i = 0; i < 6; i++) pouchSwallow(p, 'fish');
  // 模拟同一帧内同一道具被反复判定 10 次
  for (var j = 0; j < 10; j++) pouchSwallow(p, 'rock');
  assert(pouchCount(p) === 6, '反复吞入被拒不应改变长度');
  assert(pouchSpit(p) === 'fish', '囊内容应完全未被污染');
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: FAIL，报 `POUCH_CAPACITY is not defined`。

- [ ] **Step 3: 实现**

把 `CORE` 块里的 `addOne` 替换为：

```js
var POUCH_CAPACITY = 6;

function createPouch(capacity) {
  return { items: [], capacity: capacity };
}

function pouchCount(pouch) {
  return pouch.items.length;
}

function pouchIsFull(pouch) {
  return pouch.items.length >= pouch.capacity;
}

// 满囊返回 false，且绝不修改 pouch —— 调用方据此决定是否播放音效/粒子
function pouchSwallow(pouch, item) {
  if (pouchIsFull(pouch)) return false;
  pouch.items.push(item);
  return true;
}

// FIFO：吐最旧的。空囊返回 null
function pouchSpit(pouch) {
  if (pouch.items.length === 0) return null;
  return pouch.items.shift();
}
```

- [ ] **Step 4: 跑测试确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: 6/6 passed，退出码 0。

- [ ] **Step 5: Commit**

```bash
cd /d/hermes
git add projects/pelican-bike/index.html
git commit -F - <<'EOF'
喉囊队列:FIFO、容量 6、满囊拒绝不污染内容

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```

---

### Task 3: 计分与连击

**Files:**
- Modify: `projects/pelican-bike/index.html`

**Interfaces:**
- Consumes: 无
- Produces:
  - `FISH_BASE_POINTS` → `10`
  - `STREAK_PER_MULTIPLIER` → `10`
  - `MAX_MULTIPLIER` → `5`
  - `multiplierFor(streak)` → `number`（1..5）
  - `createScore()` → `{ points: number, streak: number }`
  - `scoreSwallowFish(score)` → `number`（本次得分增量，并就地更新 `score`）
  - `scoreCrash(score)` → `void`（streak 归零）
  - `distanceScore(distance)` → `number`

- [ ] **Step 1: 写失败测试**

在 `TESTS` 块末尾追加：

```js
test('倍率曲线：0→x1, 10→x2, 40→x5, 100→x5 封顶', function () {
  assert(multiplierFor(0) === 1, 'streak 0 应为 x1');
  assert(multiplierFor(9) === 1, 'streak 9 仍应为 x1');
  assert(multiplierFor(10) === 2, 'streak 10 应为 x2');
  assert(multiplierFor(39) === 4, 'streak 39 应为 x4');
  assert(multiplierFor(40) === 5, 'streak 40 应为 x5');
  assert(multiplierFor(100) === 5, 'streak 100 应封顶在 x5');
});

test('吞鱼加分并递增 streak', function () {
  var s = createScore();
  assert(scoreSwallowFish(s) === 10, '第一条鱼应 +10（x1）');
  assert(s.streak === 1, 'streak 应为 1');
  for (var i = 1; i < 11; i++) scoreSwallowFish(s);
  assert(s.streak === 11, '吞 11 条后 streak 应为 11');
  assert(s.points === 10 + 9 * 10 + 20, '前 10 条各 10 分，第 11 条为 x2 = 20 分');
});

test('撞车清零 streak 与倍率', function () {
  var s = createScore();
  for (var i = 0; i < 25; i++) scoreSwallowFish(s);
  assert(multiplierFor(s.streak) === 3, '25 条时倍率应为 x3');
  scoreCrash(s);
  assert(s.streak === 0, '撞车后 streak 归零');
  assert(multiplierFor(s.streak) === 1, '撞车后倍率回 x1');
  assert(s.points > 0, '撞车不清空已有分数');
});

test('距离分：每 10px 一分，向下取整', function () {
  assert(distanceScore(0) === 0, '0px → 0 分');
  assert(distanceScore(9) === 0, '9px → 0 分');
  assert(distanceScore(10) === 1, '10px → 1 分');
  assert(distanceScore(19) === 1, '19px → 1 分');
  assert(distanceScore(1000) === 100, '1000px → 100 分');
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: FAIL，报 `multiplierFor is not defined`。

- [ ] **Step 3: 实现**

在 `CORE` 块末尾追加：

```js
var FISH_BASE_POINTS = 10;
var STREAK_PER_MULTIPLIER = 10;
var MAX_MULTIPLIER = 5;

function createScore() {
  return { points: 0, streak: 0 };
}

function multiplierFor(streak) {
  var m = 1 + Math.floor(streak / STREAK_PER_MULTIPLIER);
  return Math.min(m, MAX_MULTIPLIER);
}

// 鱼在吞入时结算。返回本次增量，调用方用它做飘字/音效
function scoreSwallowFish(score) {
  var gained = FISH_BASE_POINTS * multiplierFor(score.streak);
  score.streak += 1;
  score.points += gained;
  return gained;
}

function scoreCrash(score) {
  score.streak = 0;
}

function distanceScore(distance) {
  return Math.floor(distance / 10);
}
```

注意 `multiplierFor(score.streak)` 用的是**吞入前**的 streak——所以第 1 条鱼是 x1、第 11 条是 x2。这与 Step 1 的断言一致。

- [ ] **Step 4: 跑测试确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: 10/10 passed。

- [ ] **Step 5: Commit**

```bash
cd /d/hermes
git add projects/pelican-bike/index.html
git commit -F - <<'EOF'
计分:鱼分×连击倍率、撞车清零、距离分

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```

---

### Task 4: 难度曲线与生成权重

**Files:**
- Modify: `projects/pelican-bike/index.html`

**Interfaces:**
- Consumes: 无
- Produces:
  - `BASE_SPEED` → `340`
  - `MAX_SPEED_MULT` → `2.5`
  - `DIFFICULTY_RAMP_SECONDS` → `90`
  - `difficultyAt(t)` → `number`（0..1，t 为秒）
  - `speedAt(t)` → `number`（px/s）
  - `gapAt(difficulty, jitter)` → `number`（px；`jitter` ∈ [-1,1]）
  - `ITEM_WEIGHTS` → `{ fish:65, rock:15, chili:10, bubble:7, star:3 }`
  - `ITEM_TYPES` → `['fish','rock','chili','bubble','star']`
  - `pickItemType(rng)` → `string`（`rng` 是返回 [0,1) 的函数，注入以便测试）

- [ ] **Step 1: 写失败测试**

在 `TESTS` 块末尾追加：

```js
test('难度曲线：t=0→0, t=90→1, t=200→1 封顶', function () {
  assertClose(difficultyAt(0), 0, 1e-9, 't=0 难度应为 0');
  assertClose(difficultyAt(45), 0.5, 1e-9, 't=45 难度应为 0.5');
  assertClose(difficultyAt(90), 1, 1e-9, 't=90 难度应为 1');
  assertClose(difficultyAt(200), 1, 1e-9, 't=200 应封顶在 1');
});

test('速度曲线：340 → 850 封顶', function () {
  assertClose(speedAt(0), 340, 1e-6, 't=0 速度应为 340');
  assertClose(speedAt(90), 850, 1e-6, 't=90 速度应为 850（340 * 2.5）');
  assertClose(speedAt(200), 850, 1e-6, 't=200 应封顶在 850');
  assert(speedAt(45) > speedAt(0), '速度应随难度递增');
});

test('生成间距：难度越高越密，jitter 在 ±15% 内', function () {
  assertClose(gapAt(0, 0), 520, 1e-9, '难度 0 时基础间距 520');
  assertClose(gapAt(1, 0), 260, 1e-9, '难度 1 时基础间距 260');
  assert(gapAt(1, 0) < gapAt(0, 0), '难度越高间距越小');
  assertClose(gapAt(0, 1), 520 * 1.15, 1e-9, 'jitter=1 应为 +15%');
  assertClose(gapAt(0, -1), 520 * 0.85, 1e-9, 'jitter=-1 应为 -15%');
});

test('道具权重总和为 100', function () {
  var sum = 0;
  for (var i = 0; i < ITEM_TYPES.length; i++) sum += ITEM_WEIGHTS[ITEM_TYPES[i]];
  assert(sum === 100, '权重总和应为 100，实际 ' + sum);
});

test('pickItemType：10000 次采样各类型占比在期望 ±3% 内', function () {
  // 确定性伪随机（mulberry32），避免测试偶发失败
  function makeRng(seed) {
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  var rng = makeRng(20260924);
  var counts = {};
  ITEM_TYPES.forEach(function (k) { counts[k] = 0; });
  var N = 10000;
  for (var i = 0; i < N; i++) {
    var t = pickItemType(rng);
    assert(counts[t] !== undefined, '返回了未知类型: ' + t);
    counts[t] += 1;
  }
  ITEM_TYPES.forEach(function (k) {
    var pct = counts[k] / N * 100;
    var want = ITEM_WEIGHTS[k];
    assertClose(pct, want, 3, k + ' 占比应接近 ' + want + '%，实际 ' + pct.toFixed(2) + '%');
  });
});

test('pickItemType：rng=0 命中第一个，rng→1 命中最后一个', function () {
  assert(pickItemType(function () { return 0; }) === 'fish', 'rng=0 应命中 fish');
  assert(pickItemType(function () { return 0.999999; }) === 'star', 'rng 接近 1 应命中 star');
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: FAIL，报 `difficultyAt is not defined`。

- [ ] **Step 3: 实现**

在 `CORE` 块末尾追加：

```js
var BASE_SPEED = 340;
var MAX_SPEED_MULT = 2.5;
var DIFFICULTY_RAMP_SECONDS = 90;

var ITEM_TYPES = ['fish', 'rock', 'chili', 'bubble', 'star'];
var ITEM_WEIGHTS = { fish: 65, rock: 15, chili: 10, bubble: 7, star: 3 };

function difficultyAt(t) {
  return Math.min(t / DIFFICULTY_RAMP_SECONDS, 1);
}

function speedAt(t) {
  return BASE_SPEED * (1 + (MAX_SPEED_MULT - 1) * difficultyAt(t));
}

// jitter ∈ [-1, 1]，线性映射到 ±15%
function gapAt(difficulty, jitter) {
  var base = 520 + (260 - 520) * difficulty;
  return base * (1 + 0.15 * jitter);
}

// 累积权重法。rng 注入以便测试确定性
function pickItemType(rng) {
  var roll = rng() * 100;
  var acc = 0;
  for (var i = 0; i < ITEM_TYPES.length; i++) {
    acc += ITEM_WEIGHTS[ITEM_TYPES[i]];
    if (roll < acc) return ITEM_TYPES[i];
  }
  return ITEM_TYPES[ITEM_TYPES.length - 1];
}
```

- [ ] **Step 4: 跑测试确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: 16/16 passed。

- [ ] **Step 5: Commit**

```bash
cd /d/hermes
git add projects/pelican-bike/index.html
git commit -F - <<'EOF'
难度曲线、速度曲线、生成间距与道具权重

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```

---

### Task 5: 碰撞判定

**Files:**
- Modify: `projects/pelican-bike/index.html`

**Interfaces:**
- Consumes: 无
- Produces:
  - `PELICAN_X` → `220`（屏幕 x，固定）
  - `GROUND_Y` → `430`
  - `HITBOX_STAND` → `{ w: 96, h: 78 }`
  - `HITBOX_DUCK` → `{ w: 96, h: 42 }`
  - `hitboxFor(isDucking)` → `{ w, h }`
  - `aabbOverlap(a, b)` → `boolean`（`a`/`b` 为 `{ x, y, w, h }`，`y` 为**顶边**）
  - `pelicanBox(height, isDucking)` → `{ x, y, w, h }`
  - `obstacleBox(ent)` → `{ x, y, w, h }`

坐标约定（贯穿全项目）：`x` 为左边缘，`y` 为**顶边**，y 轴向下。`height` 指离地高度，正数向上。障碍用 `{ x, bottom, w, h }` 描述，`bottom` 是底边的离地高度。

- [ ] **Step 1: 写失败测试**

在 `TESTS` 块末尾追加：

```js
test('蹲下碰撞盒比站立矮', function () {
  assert(hitboxFor(false).h === 78, '站立高度 78');
  assert(hitboxFor(true).h === 42, '蹲下高度 42');
  assert(hitboxFor(false).w === hitboxFor(true).w, '宽度不随蹲下改变');
});

test('aabbOverlap 基本正确性', function () {
  var a = { x: 0, y: 0, w: 10, h: 10 };
  assert(aabbOverlap(a, { x: 5, y: 5, w: 10, h: 10 }) === true, '相交应为 true');
  assert(aabbOverlap(a, { x: 20, y: 0, w: 10, h: 10 }) === false, '分离应为 false');
  assert(aabbOverlap(a, { x: 10, y: 0, w: 10, h: 10 }) === false, '仅贴边不算相交');
  assert(aabbOverlap(a, { x: -5, y: -5, w: 20, h: 20 }) === true, '包含应为 true');
});

test('蹲下能躲开乌鸦，站立躲不开', function () {
  // 乌鸦占据离地 60..94 的高度带
  var crow = { x: PELICAN_X, bottom: 60, w: 48, h: 34 };
  assert(aabbOverlap(pelicanBox(0, false), obstacleBox(crow)) === true, '站立应该撞上乌鸦');
  assert(aabbOverlap(pelicanBox(0, true), obstacleBox(crow)) === false, '蹲下应该躲开乌鸦');
});

test('跳得够高能越过路障', function () {
  var barrier = { x: PELICAN_X, bottom: 0, w: 60, h: 46 };
  assert(aabbOverlap(pelicanBox(0, false), obstacleBox(barrier)) === true, '在地面时应撞上路障');
  assert(aabbOverlap(pelicanBox(60, false), obstacleBox(barrier)) === false, '跳到 60 高时应越过路障');
});

test('高墙跳不过去（必须用道具）', function () {
  var wall = { x: PELICAN_X, bottom: 0, w: 46, h: 170 };
  assert(aabbOverlap(pelicanBox(0, false), obstacleBox(wall)) === true, '地面应撞墙');
  assert(aabbOverlap(pelicanBox(138, false), obstacleBox(wall)) === true, '跳到最高点 138 仍应撞墙');
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: FAIL，报 `hitboxFor is not defined`。

- [ ] **Step 3: 实现**

在 `CORE` 块末尾追加：

```js
var PELICAN_X = 220;
var GROUND_Y = 430;
var HITBOX_STAND = { w: 96, h: 78 };
var HITBOX_DUCK = { w: 96, h: 42 };

function hitboxFor(isDucking) {
  return isDucking ? HITBOX_DUCK : HITBOX_STAND;
}

// a/b 的 y 都是顶边。贴边（恰好相接）不算相交
function aabbOverlap(a, b) {
  return a.x < b.x + b.w &&
         b.x < a.x + a.w &&
         a.y < b.y + b.h &&
         b.y < a.y + a.h;
}

// height = 离地高度（正数向上）
function pelicanBox(height, isDucking) {
  var box = hitboxFor(isDucking);
  return {
    x: PELICAN_X - box.w / 2,
    y: GROUND_Y - height - box.h,
    w: box.w,
    h: box.h
  };
}

// ent 用 { x, bottom, w, h }：bottom = 底边的离地高度
function obstacleBox(ent) {
  return {
    x: ent.x - ent.w / 2,
    y: GROUND_Y - ent.bottom - ent.h,
    w: ent.w,
    h: ent.h
  };
}
```

- [ ] **Step 4: 跑测试确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: 21/21 passed。

- [ ] **Step 5: Commit**

```bash
cd /d/hermes
git add projects/pelican-bike/index.html
git commit -F - <<'EOF'
碰撞判定:站立/蹲下碰撞盒、AABB、鹈鹕与障碍盒构造

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```

---

### Task 6: 游戏状态机、命、撞车时序

**Files:**
- Modify: `projects/pelican-bike/index.html`

**Interfaces:**
- Consumes: Task 2 `createPouch`/`POUCH_CAPACITY`；Task 3 `createScore`/`scoreCrash`；Task 5 `pelicanBox`/`obstacleBox`/`aabbOverlap`
- Produces:
  - `LIVES` → `3`
  - `CRASH_DURATION` → `0.3`
  - `INVULN_DURATION` → `1.5`
  - `SPEED_RECOVER_DURATION` → `1.2`
  - `CRASH_SPEED_FACTOR` → `0.6`
  - `GRAVITY` → `2200`
  - `JUMP_VELOCITY` → `780`
  - `BUBBLE_JUMP_MULT` → `0.85`
  - `MAX_JUMPS_WITH_BUBBLE` → `3`（虽然要到 Task 7 的泡泡才用得上，但 `maxJumps` 在 Task 6 就引用它，必须在此定义）
  - `DUCK_SPEED_MULT` → `0.55`
  - `DASH_SPEED_MULT` → `1.9`（同理，`currentSpeed` 在 Task 6 就引用它）
  - `makeRng(seed)` → `function(): number`
  - `createGame(rng?)` → `game`（字段见下）
  - `startRun(g)` → `void`
  - `currentSpeed(g)` → `number`
  - `maxJumps(g)` → `number`
  - `jump(g)` → `boolean`
  - `setDucking(g, on)` → `void`
  - `crash(g)` → `boolean`（被无敌/冲刺挡下时返回 `false`）
  - `updateGame(g, dt)` → `void`

**game 对象字段**（后续所有任务依赖这些名字）：
`state`（`'title'|'playing'|'crashed'|'paused'|'gameover'`）、`t`、`distance`、`lives`、`score`、`pouch`、`height`、`vy`、`ducking`、`jumpsUsed`、`crashTimer`、`invuln`、`recoverTimer`、`speedFactor`、`dash`、`float`、`entities`、`projectiles`、`nextSpawnAt`、`best`、`rng`。

- [ ] **Step 1: 写失败测试**

在 `TESTS` 块末尾追加：

```js
test('新游戏初始为 title，3 条命', function () {
  var g = createGame(makeRng(1));
  assert(g.state === 'title', '初始状态应为 title');
  assert(g.lives === 3, '初始 3 条命');
});

test('startRun 重置所有局内状态', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  assert(g.state === 'playing', '应进入 playing');
  assert(g.t === 0 && g.distance === 0, '时间与距离归零');
  assert(pouchCount(g.pouch) === 0, '喉囊清空');
  assert(g.score.points === 0 && g.score.streak === 0, '分数清零');
  assert(g.speedFactor === 1 && g.dash === 0 && g.float === 0, '修正项归零');
});

test('跳跃：地面只能跳一次，落地后恢复', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  assert(jump(g) === true, '第一次跳应成功');
  assert(jump(g) === false, '空中第二次跳应失败（无泡泡）');
  assertClose(g.vy, 780, 1e-9, '起跳初速应为 780');
  // 落到地面
  for (var i = 0; i < 200; i++) updateGame(g, 1 / 60);
  assert(g.height === 0, '最终应回到地面');
  assert(g.jumpsUsed === 0, '落地后跳跃次数应重置');
  assert(jump(g) === true, '落地后应能再跳');
});

test('跳跃高度约为 138px', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  jump(g);
  var peak = 0;
  for (var i = 0; i < 200; i++) {
    updateGame(g, 1 / 120);
    if (g.height > peak) peak = g.height;
  }
  assertClose(peak, 138, 6, '跳跃最高点应约 138px，实际 ' + peak.toFixed(1));
});

test('蹲下在地面时降低速度', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  var normal = currentSpeed(g);
  setDucking(g, true);
  assertClose(currentSpeed(g), normal * 0.55, 1e-6, '蹲下速度应为 0.55x');
  setDucking(g, false);
  assertClose(currentSpeed(g), normal, 1e-6, '站起应恢复');
});

test('撞车时序：crashed 0.3s → playing 并起 1.5s 无敌', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  crash(g);
  assert(g.state === 'crashed', '撞车后应进入 crashed');
  assertClose(g.speedFactor, 0.6, 1e-9, '速度应立刻降到 0.6x');
  updateGame(g, 0.2);
  assert(g.state === 'crashed', '0.2s 时仍在 crashed');
  assert(g.invuln === 0, 'crashed 期间无敌尚未开始');
  updateGame(g, 0.15);
  assert(g.state === 'playing', '0.35s 后应回到 playing');
  assertClose(g.invuln, 1.5, 1e-9, '应起 1.5s 无敌');
});

test('撞车后速度在 1.2s 内线性恢复到 1.0x', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  crash(g);
  assertClose(g.speedFactor, 0.6, 1e-9, '起点 0.6');
  updateGame(g, 0.6);
  assertClose(g.speedFactor, 0.8, 1e-6, '0.6s 时应为 0.8');
  updateGame(g, 0.6);
  assertClose(g.speedFactor, 1.0, 1e-6, '1.2s 后应恢复 1.0');
});

test('命掉光进入 gameover', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  for (var i = 0; i < 3; i++) {
    g.invuln = 0; g.dash = 0; g.crashTimer = 0; g.state = 'playing';
    crash(g);
    updateGame(g, 0.35);
  }
  assert(g.lives === 0, '应掉光 3 条命，实际剩 ' + g.lives);
  assert(g.state === 'gameover', '应进入 gameover，实际 ' + g.state);
});

test('Review Focus 2：单帧超大 dt 不会让鹈鹕瞬移穿地', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  jump(g);
  updateGame(g, 30);   // 模拟切标签页回来
  assert(g.height === 0, '超大 dt 后 height 应被钳在地面，不得为负');
  assert(g.height >= 0, 'height 不允许为负');
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: FAIL，报 `createGame is not defined`。

- [ ] **Step 3: 实现**

在 `CORE` 块末尾追加：

```js
var LIVES = 3;
var CRASH_DURATION = 0.3;
var INVULN_DURATION = 1.5;
var SPEED_RECOVER_DURATION = 1.2;
var CRASH_SPEED_FACTOR = 0.6;
var GRAVITY = 2200;
var JUMP_VELOCITY = 780;
var BUBBLE_JUMP_MULT = 0.85;
var DUCK_SPEED_MULT = 0.55;
// 冲刺要到 Task 7 才做，但 currentSpeed 现在就引用它，必须在此定义
var DASH_SPEED_MULT = 1.9;
var MAX_JUMPS_WITH_BUBBLE = 3;

// 确定性伪随机（mulberry32）。游戏与测试共用
function makeRng(seed) {
  var a = seed >>> 0;
  return function () {
    a = (a + 0x6D2B79F5) >>> 0;
    var t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function createGame(rng) {
  return {
    state: 'title',
    rng: rng || makeRng(1),
    t: 0,
    distance: 0,
    lives: LIVES,
    score: createScore(),
    pouch: createPouch(POUCH_CAPACITY),
    height: 0,
    vy: 0,
    ducking: false,
    jumpsUsed: 0,
    crashTimer: 0,
    invuln: 0,
    recoverTimer: 0,
    speedFactor: 1,
    dash: 0,
    float: 0,
    entities: [],
    projectiles: [],
    nextSpawnAt: 600,
    best: 0
  };
}

function startRun(g) {
  g.state = 'playing';
  g.t = 0;
  g.distance = 0;
  g.lives = LIVES;
  g.score = createScore();
  g.pouch = createPouch(POUCH_CAPACITY);
  g.height = 0;
  g.vy = 0;
  g.ducking = false;
  g.jumpsUsed = 0;
  g.crashTimer = 0;
  g.invuln = 0;
  g.recoverTimer = 0;
  g.speedFactor = 1;
  g.dash = 0;
  g.float = 0;
  g.entities = [];
  g.projectiles = [];
  g.nextSpawnAt = 600;
}

function currentSpeed(g) {
  var v = speedAt(g.t) * g.speedFactor;
  if (g.dash > 0) v *= DASH_SPEED_MULT;
  if (g.ducking && g.height === 0) v *= DUCK_SPEED_MULT;
  return v;
}

function maxJumps(g) {
  return g.float > 0 ? MAX_JUMPS_WITH_BUBBLE : 1;
}

function jump(g) {
  if (g.state !== 'playing') return false;
  if (g.jumpsUsed >= maxJumps(g)) return false;
  g.vy = g.jumpsUsed > 0 ? JUMP_VELOCITY * BUBBLE_JUMP_MULT : JUMP_VELOCITY;
  g.jumpsUsed += 1;
  return true;
}

function setDucking(g, on) {
  g.ducking = !!on;
}

// 被无敌或冲刺挡下时返回 false 且不改变任何状态
function crash(g) {
  if (g.invuln > 0 || g.dash > 0) return false;
  g.lives -= 1;
  scoreCrash(g.score);
  g.speedFactor = CRASH_SPEED_FACTOR;
  g.recoverTimer = SPEED_RECOVER_DURATION;
  g.crashTimer = CRASH_DURATION;
  g.state = 'crashed';
  return true;
}

function updateGame(g, dt) {
  // 速度惩罚线性恢复（撞车即刻开始计时）
  if (g.recoverTimer > 0) {
    g.recoverTimer = Math.max(0, g.recoverTimer - dt);
    var k = 1 - g.recoverTimer / SPEED_RECOVER_DURATION;
    g.speedFactor = CRASH_SPEED_FACTOR + (1 - CRASH_SPEED_FACTOR) * k;
  } else {
    g.speedFactor = 1;
  }

  // crashed 期间世界不推进，只走撞车计时
  if (g.crashTimer > 0) {
    g.crashTimer = Math.max(0, g.crashTimer - dt);
    if (g.crashTimer === 0) {
      if (g.lives <= 0) {
        g.state = 'gameover';
      } else {
        g.state = 'playing';
        g.invuln = INVULN_DURATION;
      }
    }
    return;
  }

  if (g.state !== 'playing') return;

  g.t += dt;
  if (g.invuln > 0) g.invuln = Math.max(0, g.invuln - dt);
  if (g.dash > 0) g.dash = Math.max(0, g.dash - dt);
  if (g.float > 0) g.float = Math.max(0, g.float - dt);

  var scoredBeforeDistance = distanceScore(g.distance);

  // 垂直运动。落回地面时钳制 height >= 0（超大 dt 也不会穿地）
  g.vy -= GRAVITY * dt;
  g.height += g.vy * dt;
  if (g.height <= 0) {
    g.height = 0;
    g.vy = 0;
    g.jumpsUsed = 0;
    g.float = 0;
  }

  g.distance += currentSpeed(g) * dt;

  // 距离分：每 10px 一分，不乘连击倍率。用「前后的 distanceScore 之差」累加，
  // 保证总分恒等于 distanceScore(distance)，且不会因浮点累积而漂移。
  g.score.points += distanceScore(g.distance) - scoredBeforeDistance;
}
```

注意：`updateGame` 里 `g.height` 被钳制在 `>= 0`，这是 Review Focus 2 那条测试要求的。但仅钳制 height 不够——Task 13 的接线步骤必须同时钳制传入的 `dt`（见该任务）。

- [ ] **Step 4: 跑测试确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: 30/30 passed。

顺带清理：Task 4 的权重测试里有一份局部的 `makeRng`，现在 CORE 已提供同名函数。可以删掉测试内那份局部定义，改为直接调用 CORE 的 `makeRng`。删完重跑确认仍是 30/30。

- [ ] **Step 5: Commit**

```bash
cd /d/hermes
git add projects/pelican-bike/index.html
git commit -F - <<'EOF'
游戏状态机:命数、撞车时序、速度惩罚恢复、跳跃与蹲下

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```

---

### Task 7: 吐的效果与无敌叠加

**Files:**
- Modify: `projects/pelican-bike/index.html`

**Interfaces:**
- Consumes: Task 2 `pouchSpit`；Task 6 `createGame`/`startRun`/`crash`/`updateGame`/`PELICAN_X`/`GROUND_Y`
- Produces:
  - `DASH_DURATION` → `1.5`（`DASH_SPEED_MULT` 已在 Task 6 定义，此处不要重复）
  - `FLOAT_DURATION` → `4`（`MAX_JUMPS_WITH_BUBBLE` 已在 Task 6 定义，此处不要重复）
  - `STAR_PER_OBSTACLE` → `10`，`STAR_CLEAR_BONUS` → `50`
  - `PROJECTILE_SPEED` → `900`，`PROJECTILE_DESPAWN_X` → `1100`
  - `spit(g)` → `effect | null`，`effect` 为 `{ kind: 'projectile', item }` / `{ kind: 'dash' }` / `{ kind: 'float' }` / `{ kind: 'clear', cleared, points }`
  - `applySpitEffect(g, item)` → `effect | null`
  - `updateProjectiles(g, dt)` → `void`

- [ ] **Step 1: 写失败测试**

在 `TESTS` 块末尾追加：

```js
test('吐空囊返回 null', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  assert(spit(g) === null, '空囊吐应返回 null');
});

test('吐辣椒启动 1.5s 冲刺且速度 ×1.9', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  var before = currentSpeed(g);
  pouchSwallow(g.pouch, 'chili');
  var eff = spit(g);
  assert(eff.kind === 'dash', '应返回 dash 效果');
  assertClose(g.dash, 1.5, 1e-9, '冲刺应为 1.5s');
  assertClose(currentSpeed(g), before * 1.9, 1e-6, '冲刺速度应为 1.9x');
});

test('吐泡泡启动 4s 浮空且允许三段跳', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  pouchSwallow(g.pouch, 'bubble');
  spit(g);
  assertClose(g.float, 4, 1e-9, '浮空应为 4s');
  assert(maxJumps(g) === 3, '浮空期间最多 3 段跳');
  assert(jump(g) === true, '第 1 跳');
  assert(jump(g) === true, '第 2 跳');
  assert(jump(g) === true, '第 3 跳');
  assert(jump(g) === false, '第 4 跳应失败');
});

test('落地后浮空重置，回到单段跳', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  pouchSwallow(g.pouch, 'bubble');
  spit(g);
  jump(g);
  for (var i = 0; i < 400; i++) updateGame(g, 1 / 60);
  assert(g.height === 0, '应已落地');
  assert(g.float === 0, '落地后浮空应重置');
  assert(maxJumps(g) === 1, '应回到单段跳');
});

test('吐石头生成穿透抛射物', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  pouchSwallow(g.pouch, 'rock');
  var eff = spit(g);
  assert(eff.kind === 'projectile' && eff.item === 'rock', '应生成 rock 抛射物');
  assert(g.projectiles.length === 1, '应有 1 个抛射物');
  assert(g.projectiles[0].piercing === true, '石头应穿透');
});

test('吐鱼生成非穿透抛射物（可击落乌鸦）', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  pouchSwallow(g.pouch, 'fish');
  spit(g);
  assert(g.projectiles[0].piercing === false, '鱼不穿透');
});

test('抛射物砸中障碍并标记 dead', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  g.entities = [{ kind: 'obstacle', type: 'crow', x: PELICAN_X + 100, bottom: 60, w: 48, h: 34 }];
  pouchSwallow(g.pouch, 'rock');
  spit(g);
  updateProjectiles(g, 0.02);
  assert(g.entities[0].dead === true, '障碍应被标记 dead');
});

test('石头穿透：一次更新砸中两个障碍', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  g.entities = [
    { kind: 'obstacle', type: 'crow', x: PELICAN_X + 80, bottom: 60, w: 48, h: 34 },
    { kind: 'obstacle', type: 'crow', x: PELICAN_X + 90, bottom: 60, w: 48, h: 34 }
  ];
  pouchSwallow(g.pouch, 'rock');
  spit(g);
  updateProjectiles(g, 0.02);
  assert(g.entities[0].dead === true && g.entities[1].dead === true, '石头应穿透并砸中两个');
  assert(g.projectiles.length === 1, '穿透的石头不应消失');
});

test('鱼不穿透：砸中一个就消失', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  g.entities = [
    { kind: 'obstacle', type: 'crow', x: PELICAN_X + 80, bottom: 60, w: 48, h: 34 },
    { kind: 'obstacle', type: 'crow', x: PELICAN_X + 90, bottom: 60, w: 48, h: 34 }
  ];
  pouchSwallow(g.pouch, 'fish');
  spit(g);
  updateProjectiles(g, 0.02);
  assert(g.projectiles.length === 0, '鱼砸中后应消失');
});

test('星星清屏：移除所有障碍并按数量加分', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  g.entities = [
    { kind: 'obstacle', type: 'crow', x: 600, bottom: 60, w: 48, h: 34 },
    { kind: 'obstacle', type: 'bin', x: 700, bottom: 0, w: 54, h: 70 },
    { kind: 'item', type: 'fish', x: 800, bottom: 40, w: 32, h: 32 }
  ];
  var before = g.score.points;
  pouchSwallow(g.pouch, 'star');
  var eff = spit(g);
  assert(eff.kind === 'clear', '应返回 clear 效果');
  assert(eff.cleared === 2, '应清掉 2 个障碍，实际 ' + eff.cleared);
  assertClose(g.score.points, before + 2 * 10 + 50, 1e-9, '应加 2*10 + 50');
  assert(g.entities.length === 1, '道具不应被清掉');
  assert(g.entities[0].kind === 'item', '留下的应是道具');
});

test('Review Focus 4：冲刺无敌与受击无敌是两套独立计时器', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  g.invuln = 1.0;
  applySpitEffect(g, 'chili');
  assertClose(g.dash, 1.5, 1e-9, '冲刺应为 1.5s');
  assertClose(g.invuln, 1.0, 1e-9, '冲刺不应改动受击无敌');
  g.dash = 0;   // 冲刺自然结束
  assertClose(g.invuln, 1.0, 1e-9, '冲刺结束不应清零受击无敌');
});

test('无敌或冲刺期间撞车不掉命', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  g.invuln = 0.5;
  assert(crash(g) === false, '无敌期间撞车应被忽略');
  assert(g.lives === 3, '命数不应减少');
  g.invuln = 0;
  g.dash = 1.0;
  assert(crash(g) === false, '冲刺期间撞车应被忽略');
  assert(g.lives === 3, '命数不应减少');
  g.dash = 0;
  assert(crash(g) === true, '无保护时撞车应生效');
  assert(g.lives === 2, '应掉 1 命');
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: FAIL，报 `spit is not defined`。

- [ ] **Step 3: 实现**

在 `CORE` 块末尾追加：

```js
var DASH_DURATION = 1.5;
var FLOAT_DURATION = 4;
var STAR_PER_OBSTACLE = 10;
var STAR_CLEAR_BONUS = 50;
var PROJECTILE_SPEED = 900;
var PROJECTILE_DESPAWN_X = 1100;

// 吐：从喉囊取最旧的一个并生效。空囊返回 null
function spit(g) {
  if (g.state !== 'playing') return null;
  var item = pouchSpit(g.pouch);
  if (item === null) return null;
  return applySpitEffect(g, item);
}

function applySpitEffect(g, item) {
  if (item === null || item === undefined) return null;

  if (item === 'chili') {
    // 独立计时器：绝不写 g.invuln
    g.dash = DASH_DURATION;
    return { kind: 'dash' };
  }

  if (item === 'bubble') {
    g.float = FLOAT_DURATION;
    return { kind: 'float' };
  }

  if (item === 'star') {
    var cleared = 0;
    var kept = [];
    for (var i = 0; i < g.entities.length; i++) {
      if (g.entities[i].kind === 'obstacle') cleared += 1;
      else kept.push(g.entities[i]);
    }
    g.entities = kept;
    var points = cleared * STAR_PER_OBSTACLE + STAR_CLEAR_BONUS;
    g.score.points += points;
    return { kind: 'clear', cleared: cleared, points: points };
  }

  // fish / rock 走抛射物。鱼不穿透（击落乌鸦），石头穿透（砸碎一切）
  g.projectiles.push({
    item: item,
    x: PELICAN_X + 60,
    y: GROUND_Y - g.height - 60,
    piercing: item === 'rock'
  });
  return { kind: 'projectile', item: item };
}

function updateProjectiles(g, dt) {
  var kept = [];
  for (var i = 0; i < g.projectiles.length; i++) {
    var p = g.projectiles[i];
    p.x += PROJECTILE_SPEED * dt;
    if (p.x > PROJECTILE_DESPAWN_X) continue;

    var consumed = false;
    for (var j = 0; j < g.entities.length; j++) {
      var e = g.entities[j];
      if (e.kind !== 'obstacle' || e.dead) continue;
      if (p.x < e.x - e.w / 2 || p.x > e.x + e.w / 2) continue;
      if (p.y < GROUND_Y - e.bottom - e.h || p.y > GROUND_Y - e.bottom) continue;
      e.dead = true;
      if (!p.piercing) { consumed = true; break; }
    }
    if (consumed) continue;
    kept.push(p);
  }
  g.projectiles = kept;
}
```

- [ ] **Step 4: 跑测试确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: 42/42 passed。

- [ ] **Step 5: Commit**

```bash
cd /d/hermes
git add projects/pelican-bike/index.html
git commit -F - <<'EOF'
吐的效果:石头穿透、辣椒冲刺、泡泡三段跳、星星清屏

冲刺与受击无敌各自独立计时,不互相覆盖。

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```

---

### Task 8: 实体生成与推进

**Files:**
- Modify: `projects/pelican-bike/index.html`

**Interfaces:**
- Consumes: Task 4 `difficultyAt`/`gapAt`/`pickItemType`；Task 5 `pelicanBox`/`obstacleBox`/`aabbOverlap`/`PELICAN_X`/`GROUND_Y`；Task 6 `currentSpeed`/`crash`；Task 7 `updateProjectiles`
- Produces:
  - `SPAWN_X` → `1000`，`DESPAWN_X` → `-200`
  - `FOOT_HALF_WIDTH` → `20`
  - `OBSTACLE_SPECS` → `{ bin, barrier, crow, wall, pit }`，每项 `{ w, h, bottom }`
  - `OBSTACLE_CHANCE` → `0.7`
  - `pickObstacleType(rng, difficulty)` → `string`
  - `spawnAhead(g)` → `void`
  - `spawnObstacle(g, difficulty)` → `void`
  - `spawnItems(g)` → `void`
  - `hitsPit(g, ent)` → `boolean`
  - `updateEntities(g, dt)` → `void`

**实体形状**：`{ kind: 'obstacle'|'item', type: string, x, bottom, w, h, dead?, resolved?, missed? }`。
`obstacleBox` 对道具同样适用（它只依赖 `{x, bottom, w, h}`）。

- [ ] **Step 1: 写失败测试**

在 `TESTS` 块末尾追加：

```js
test('障碍规格与 spec 一致', function () {
  assert(OBSTACLE_SPECS.crow.bottom === 60 && OBSTACLE_SPECS.crow.h === 34, '乌鸦占离地 60..94');
  assert(OBSTACLE_SPECS.wall.h === 170, '高墙 170，跳不过去');
  assert(OBSTACLE_SPECS.pit.w === 90, '坑洞宽 90');
});

test('难度 0 时不生成高墙和坑洞', function () {
  var rng = makeRng(7);
  for (var i = 0; i < 500; i++) {
    var t = pickObstacleType(rng, 0);
    assert(t === 'bin' || t === 'barrier', '难度 0 只应出 bin/barrier，实际 ' + t);
  }
});

test('难度 1 时五种障碍都会出现', function () {
  var rng = makeRng(11);
  var seen = {};
  for (var i = 0; i < 3000; i++) seen[pickObstacleType(rng, 1)] = true;
  ['bin', 'barrier', 'crow', 'pit', 'wall'].forEach(function (t) {
    assert(seen[t] === true, '难度 1 应能生成 ' + t);
  });
});

test('spawnAhead 随距离推进产生实体', function () {
  var g = createGame(makeRng(3));
  startRun(g);
  assert(g.entities.length === 0, '开局无实体');
  g.distance = 5000;
  spawnAhead(g);
  assert(g.entities.length > 0, '推进距离后应产生实体');
  g.entities.forEach(function (e) {
    assert(e.x === SPAWN_X || e.x > SPAWN_X, '实体应从右侧屏外生成，实际 x=' + e.x);
  });
});

test('鱼按 3–5 个一组生成，长度随随机数变化', function () {
  var g = createGame(makeRng(5));
  startRun(g);

  // spawnItems 会用同一个 rng 先选类型、再定长度。这里让第一次调用必定命中 fish
  function spawnWith(seed, later) {
    g.entities = [];
    var first = true;
    g.rng = function () {
      if (first) { first = false; return 0.1; }   // roll = 10 < 65 → fish
      return later;
    };
    spawnItems(g);
  }

  spawnWith(1, 0);
  assert(g.entities.length === 3, 'later=0 应生成 3 个，实际 ' + g.entities.length);
  g.entities.forEach(function (e) { assert(e.type === 'fish', '鱼串里应全是鱼'); });

  spawnWith(2, 0.99);
  assert(g.entities.length === 5, 'later=0.99 应生成 5 个，实际 ' + g.entities.length);

  for (var i = 0; i < 200; i++) {
    spawnWith(i + 10, i / 200);
    var n = g.entities.length;
    assert(n >= 3 && n <= 5, '鱼串长度应在 3..5，实际 ' + n);
    g.entities.forEach(function (e) { assert(e.type === 'fish', '鱼串里应全是鱼'); });
  }
});

test('非鱼道具单个生成', function () {
  var g = createGame(makeRng(5));
  startRun(g);
  // 第一次调用返回 0.99 → roll = 99 → 命中 star（最后一个）
  var first = true;
  g.rng = function () {
    if (first) { first = false; return 0.99; }
    return 0.5;
  };
  spawnItems(g);
  assert(g.entities.length === 1, '非鱼应只生成 1 个，实际 ' + g.entities.length);
  assert(g.entities[0].type === 'star', '应生成 star，实际 ' + g.entities[0].type);
});

test('撞障碍掉命并移除障碍', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  g.entities = [{ kind: 'obstacle', type: 'bin', x: PELICAN_X, bottom: 0, w: 54, h: 70 }];
  updateEntities(g, 1 / 60);
  assert(g.lives === 2, '应掉 1 命，实际剩 ' + g.lives);
  assert(g.entities.length === 0, '撞上的障碍应被移除');
});

test('跳到 60 高能越过路障', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  g.height = 60;
  g.entities = [{ kind: 'obstacle', type: 'barrier', x: PELICAN_X, bottom: 0, w: 60, h: 46 }];
  updateEntities(g, 1 / 60);
  assert(g.lives === 3, '跳起来应越过路障');
});

test('蹲下能躲开乌鸦', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  g.ducking = true;
  g.entities = [{ kind: 'obstacle', type: 'crow', x: PELICAN_X, bottom: 60, w: 48, h: 34 }];
  updateEntities(g, 1 / 60);
  assert(g.lives === 3, '蹲下应躲开乌鸦');
});

test('坑洞：在地面掉命，跳起安全', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  g.entities = [{ kind: 'obstacle', type: 'pit', x: PELICAN_X, bottom: 0, w: 90, h: 0 }];
  updateEntities(g, 1 / 60);
  assert(g.lives === 2, '踩进坑洞应掉命');

  var g2 = createGame(makeRng(1));
  startRun(g2);
  g2.height = 80;
  g2.entities = [{ kind: 'obstacle', type: 'pit', x: PELICAN_X, bottom: 0, w: 90, h: 0 }];
  updateEntities(g2, 1 / 60);
  assert(g2.lives === 3, '跳过坑洞应安全');
});

test('吞道具入囊，鱼同时加分', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  g.entities = [{ kind: 'item', type: 'fish', x: PELICAN_X, bottom: 40, w: 32, h: 32 }];
  updateEntities(g, 1 / 60);
  assert(pouchCount(g.pouch) === 1, '鱼应进囊');
  assert(g.score.points === 10, '鱼应 +10');
});

test('Review Focus 3：满囊错过道具不重复计分', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  for (var i = 0; i < 6; i++) pouchSwallow(g.pouch, 'fish');
  var before = g.score.points;
  g.entities = [{ kind: 'item', type: 'fish', x: PELICAN_X, bottom: 40, w: 32, h: 32 }];
  for (var f = 0; f < 30; f++) updateEntities(g, 1 / 60);
  assert(pouchCount(g.pouch) === 6, '满囊不应吞入');
  assert(g.score.points === before, '错过的道具不应加分，实际 ' + g.score.points);
  assert(g.entities.length === 1, '错过的道具应继续飞过而非消失');
  assert(g.entities[0].missed === true, '应被标记为 missed');
  assert(g.entities[0].resolved === true, '应被标记为已判定，避免重复处理');
});

test('实体飞出左边界后被移除', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  g.entities = [{ kind: 'obstacle', type: 'bin', x: DESPAWN_X - 1, bottom: 0, w: 54, h: 70 }];
  updateEntities(g, 1 / 60);
  assert(g.entities.length === 0, '出屏实体应被移除');
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: FAIL，报 `OBSTACLE_SPECS is not defined`。

- [ ] **Step 3: 实现**

在 `CORE` 块末尾追加：

```js
var SPAWN_X = 1000;
var DESPAWN_X = -200;
var FOOT_HALF_WIDTH = 20;
var OBSTACLE_CHANCE = 0.7;

var OBSTACLE_SPECS = {
  bin:     { w: 54, h: 70,  bottom: 0 },
  barrier: { w: 60, h: 46,  bottom: 0 },
  crow:    { w: 48, h: 34,  bottom: 60 },
  wall:    { w: 46, h: 170, bottom: 0 },
  pit:     { w: 90, h: 0,   bottom: 0 }
};

function pickObstacleType(rng, difficulty) {
  var roll = rng();
  if (difficulty < 0.25) {
    return roll < 0.6 ? 'bin' : 'barrier';
  }
  if (difficulty < 0.55) {
    if (roll < 0.40) return 'bin';
    if (roll < 0.70) return 'barrier';
    if (roll < 0.90) return 'crow';
    return 'pit';
  }
  if (roll < 0.25) return 'bin';
  if (roll < 0.45) return 'barrier';
  if (roll < 0.65) return 'crow';
  if (roll < 0.82) return 'pit';
  return 'wall';
}

function spawnAhead(g) {
  while (g.distance >= g.nextSpawnAt) {
    var d = difficultyAt(g.t);
    if (g.rng() < OBSTACLE_CHANCE) spawnObstacle(g, d);
    else spawnItems(g);
    g.nextSpawnAt += gapAt(d, g.rng() * 2 - 1);
  }
}

function spawnObstacle(g, difficulty) {
  var type = pickObstacleType(g.rng, difficulty);
  var spec = OBSTACLE_SPECS[type];
  g.entities.push({
    kind: 'obstacle', type: type, x: SPAWN_X,
    bottom: spec.bottom, w: spec.w, h: spec.h
  });
}

function spawnItems(g) {
  var type = pickItemType(g.rng);
  if (type === 'fish') {
    var n = 3 + Math.floor(g.rng() * 3);          // 3..5
    var arcPeak = 60 + g.rng() * 90;
    for (var i = 0; i < n; i++) {
      var k = n === 1 ? 0.5 : i / (n - 1);
      g.entities.push({
        kind: 'item', type: 'fish',
        x: SPAWN_X + i * 46,
        bottom: 40 + Math.sin(k * Math.PI) * arcPeak,
        w: 32, h: 32
      });
    }
  } else {
    g.entities.push({
      kind: 'item', type: type, x: SPAWN_X,
      bottom: 40 + g.rng() * 100, w: 32, h: 32
    });
  }
}

// 坑洞不看碰撞盒，只看脚有没有踩空
function hitsPit(g, ent) {
  if (g.height > 0) return false;
  return PELICAN_X + FOOT_HALF_WIDTH > ent.x - ent.w / 2 &&
         PELICAN_X - FOOT_HALF_WIDTH < ent.x + ent.w / 2;
}

function updateEntities(g, dt) {
  var v = currentSpeed(g);
  var kept = [];
  for (var i = 0; i < g.entities.length; i++) {
    var e = g.entities[i];
    e.x -= v * dt;
    if (e.x < DESPAWN_X) continue;
    // 上一帧已被道具清掉的，不再参与碰撞判定
    if (e.dead) continue;

    if (e.kind === 'obstacle') {
      if (e.type === 'pit') {
        if (hitsPit(g, e)) { e.dead = true; crash(g); }
      } else if (aabbOverlap(pelicanBox(g.height, g.ducking), obstacleBox(e))) {
        e.dead = true;
        crash(g);
      }
    } else if (e.kind === 'item') {
      // resolved 保证同一道具只判定一次（满囊时不会每帧重试）
      if (!e.resolved && aabbOverlap(pelicanBox(g.height, g.ducking), obstacleBox(e))) {
        e.resolved = true;
        if (pouchSwallow(g.pouch, e.type)) {
          e.dead = true;
          if (e.type === 'fish') scoreSwallowFish(g.score);
        } else {
          e.missed = true;      // 满囊错过，继续飞过
        }
      }
    }
    // 本帧刚死掉的，立刻移除 —— 否则会多画一帧
    if (e.dead) continue;
    kept.push(e);
  }
  g.entities = kept;
}
```

- [ ] **Step 4: 跑测试确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: 55/55 passed。

- [ ] **Step 5: Commit**

```bash
cd /d/hermes
git add projects/pelican-bike/index.html
git commit -F - <<'EOF'
实体生成与推进:障碍规格、难度分级生成、碰撞结算、坑洞判定

满囊错过的道具标记 resolved,避免每帧重复判定。

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```

---

### Task 9: 渲染 — 背景与地面

从这一任务起进入渲染层。渲染无法逐像素断言，改用**桩 ctx 冒烟测试**（捕获方法调用、捕捉拼写与未定义错误）+ 实机目视确认。

**Files:**
- Modify: `projects/pelican-bike/index.html`

**Interfaces:**
- Consumes: Task 5 `GROUND_Y`；Task 6 `createGame`/`startRun`
- Produces:
  - `VIEW_W` → `960`，`VIEW_H` → `540`
  - `SKY_TOP` → `'#cbe6f7'`，`SKY_BOTTOM` → `'#f0f8fc'`，`SUN_COLOR` → `'#ffe28f'`
  - `GRASS_MAIN` → `'#dcecd2'`，`GRASS_EDGE` → `'#c3dcb6'`
  - `cloudOffset(distance, factor, span)` → `number`（视差滚动偏移）
  - `drawBackground(ctx, g)` → `void`
  - `drawGround(ctx, g)` → `void`

- [ ] **Step 1: 写失败测试**

先在 `TESTS` 块**开头**（所有 `test(...)` 之前）插入桩 ctx 辅助：

```js
// 桩 ctx：记录所有被调用的绘制方法，用于冒烟测试
function makeStubCtx() {
  var calls = [];
  var ctx = {};
  ['save', 'restore', 'beginPath', 'moveTo', 'lineTo', 'closePath', 'fill', 'stroke',
   'arc', 'ellipse', 'rect', 'fillRect', 'strokeRect', 'quadraticCurveTo',
   'bezierCurveTo', 'translate', 'rotate', 'scale', 'clip', 'clearRect', 'fillText',
   'setLineDash'].forEach(function (m) {
    ctx[m] = function () { calls.push(m); };
  });
  ctx.createLinearGradient = function () {
    calls.push('createLinearGradient');
    return { addColorStop: function () { calls.push('addColorStop'); } };
  };
  ctx.createRadialGradient = function () {
    calls.push('createRadialGradient');
    return { addColorStop: function () { calls.push('addColorStop'); } };
  };
  ctx.calls = calls;
  ctx.did = function (m) { return calls.indexOf(m) !== -1; };
  return ctx;
}
```

然后在 `TESTS` 块末尾追加：

```js
test('视差偏移随距离前进且按 factor 缩放', function () {
  assertClose(cloudOffset(0, 0.2, 1200), 0, 1e-9, '距离 0 时偏移 0');
  assertClose(cloudOffset(1200, 0.2, 1200), 240, 1e-9, '走满一个 span 应偏移 span*factor');
  assertClose(cloudOffset(2400, 0.2, 1200), 480, 1e-9, '继续前进应继续偏移');
  assert(cloudOffset(600, 0.4, 1200) > cloudOffset(600, 0.2, 1200), 'factor 越大偏移越快');
});

test('drawBackground 不抛异常且画出天空与太阳', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  var ctx = makeStubCtx();
  drawBackground(ctx, g);
  assert(ctx.did('createLinearGradient'), '应创建天空渐变');
  assert(ctx.did('fillRect'), '应填充天空矩形');
  assert(ctx.did('arc'), '应画出太阳或云的圆弧');
});

test('drawGround 不抛异常且画出草地与滚动条纹', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  var ctx = makeStubCtx();
  drawGround(ctx, g);
  assert(ctx.did('fillRect'), '应填充草地');
});

test('drawBackground/drawGround 在极端 distance 下不崩', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  [0, 1e6, 1e9].forEach(function (d) {
    g.distance = d;
    var ctx = makeStubCtx();
    drawBackground(ctx, g);
    drawGround(ctx, g);
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: FAIL，报 `cloudOffset is not defined`。

- [ ] **Step 3: 实现**

在 `CORE` 块末尾追加（纯函数）：

```js
var VIEW_W = 960;
var VIEW_H = 540;

function cloudOffset(distance, factor, span) {
  return (distance * factor) % span;
}
```

然后在 `CORE` 块**之外**、`TESTS` 块之前，新增渲染层区块：

```js
/* ==== RENDER:BEGIN ==== */
var SKY_TOP = '#cbe6f7';
var SKY_BOTTOM = '#f0f8fc';
var SUN_COLOR = '#ffe28f';
var CLOUD_COLOR = '#ffffff';
var GRASS_MAIN = '#dcecd2';
var GRASS_EDGE = '#c3dcb6';
var GRASS_SHADOW = '#93b585';

// 云层配置：{ y, rx, ry, factor, span }
var CLOUDS = [
  { y: 90,  rx: 62, ry: 24, factor: 0.10, span: 1200 },
  { y: 150, rx: 54, ry: 20, factor: 0.16, span: 1100 },
  { y: 60,  rx: 40, ry: 16, factor: 0.07, span: 1300 },
  { y: 200, rx: 48, ry: 18, factor: 0.22, span: 1000 }
];

function drawBackground(ctx, g) {
  var sky = ctx.createLinearGradient(0, 0, 0, GROUND_Y);
  sky.addColorStop(0, SKY_TOP);
  sky.addColorStop(1, SKY_BOTTOM);
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, VIEW_W, GROUND_Y);

  // 太阳
  ctx.save();
  ctx.fillStyle = SUN_COLOR;
  ctx.globalAlpha = 0.28;
  ctx.beginPath();
  ctx.arc(830, 92, 52, 0, Math.PI * 2);
  ctx.fill();
  ctx.globalAlpha = 1;
  ctx.beginPath();
  ctx.arc(830, 92, 38, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // 云（视差）
  ctx.save();
  ctx.fillStyle = CLOUD_COLOR;
  for (var i = 0; i < CLOUDS.length; i++) {
    var c = CLOUDS[i];
    var off = cloudOffset(g.distance, c.factor, c.span);
    for (var k = -1; k <= Math.ceil(VIEW_W / c.span) + 1; k++) {
      var cx = k * c.span + c.span - off;
      if (cx < -c.span || cx > VIEW_W + c.span) continue;
      ctx.beginPath();
      ctx.ellipse(cx, c.y, c.rx, c.ry, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.ellipse(cx + c.rx * 0.7, c.y + c.ry * 0.3, c.rx * 0.75, c.ry * 0.8, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.ellipse(cx - c.rx * 0.7, c.y + c.ry * 0.35, c.rx * 0.6, c.ry * 0.7, 0, 0, Math.PI * 2);
      ctx.fill();
    }
  }
  ctx.restore();
}

function drawGround(ctx, g) {
  ctx.save();
  ctx.fillStyle = GRASS_MAIN;
  ctx.fillRect(0, GROUND_Y, VIEW_W, VIEW_H - GROUND_Y);
  ctx.fillStyle = GRASS_EDGE;
  ctx.fillRect(0, GROUND_Y, VIEW_W, 3);

  // 滚动条纹：与世界速度同相，形成「地面在跑」的感觉
  ctx.fillStyle = GRASS_SHADOW;
  ctx.globalAlpha = 0.55;
  var span = 80;
  var off = g.distance % span;
  for (var x = -span; x < VIEW_W + span; x += span) {
    ctx.fillRect(x - off, GROUND_Y + 42, 44, 8);
  }
  ctx.restore();
}
/* ==== RENDER:END ==== */
```

**注意**：`RENDER` 块不在 `CORE` 内，所以 `run-tests.mjs` 不会抽它——但测试里要调用 `drawBackground`。解决办法：让 `run-tests.mjs` 也抽 `RENDER` 块，与 `CORE` 一起求值。修改 `tools/run-tests.mjs`，把抽取改成：

```js
const core = extract('/* ==== CORE:BEGIN ==== */', '/* ==== CORE:END ==== */');
const render = extract('/* ==== RENDER:BEGIN ==== */', '/* ==== RENDER:END ==== */');
const tests = extract('/* ==== TESTS:BEGIN ==== */', '/* ==== TESTS:END ==== */');
```

并把求值行改成：

```js
vm.runInContext(harness + core + '\n' + render + '\n' + tests, sandbox, { filename: 'core+render+tests.js' });
```

**这条约束要写进全局约定**：`RENDER` 块允许引用 `Math` 等内置对象，但**不得**引用 `document`/`window`/`canvas`/`AudioContext`——它要能在 node 沙箱里被求值。真正的 DOM 访问只允许出现在 `RENDER` 之外的启动代码里。

- [ ] **Step 4: 跑测试确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: 59/59 passed。

- [ ] **Step 5: 目视确认**

在 `index.html` 的启动代码里临时加一段：取 canvas、`startRun(g)`、调用 `drawBackground`+`drawGround`。双击打开确认：天蓝渐变、右上太阳、云、下方草地与滚动条纹。

- [ ] **Step 6: Commit**

```bash
cd /d/hermes
git add projects/pelican-bike/index.html projects/pelican-bike/tools/run-tests.mjs
git commit -F - <<'EOF'
渲染:天空渐变、视差云、太阳、草地与滚动条纹

新增 RENDER 块,测试运行器一并抽取求值。

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```

---

### Task 10: 渲染 — 鹈鹕与自行车

本项目视觉风险最高的一步。程序化绘制，车轮与腿必须与真实速度绑定。

**Files:**
- Modify: `projects/pelican-bike/index.html`

**Interfaces:**
- Consumes: Task 9 `RENDER` 块；Task 2 `pouchCount`/`POUCH_CAPACITY`；Task 5 `PELICAN_X`/`GROUND_Y`
- Produces:
  - 调色板常量：`PLUME_COLOR`/`PLUME_SHADE`/`PLUME_EDGE`/`BEAK_COLOR`/`BEAK_EDGE`/`POUCH_COLOR`/`LEG_COLOR`/`LEG_DARK`/`FRAME_COLOR`/`TIRE_COLOR`/`RIM_COLOR`/`SPOKE_COLOR`/`HUB_COLOR`/`METAL_COLOR`/`DARK_COLOR`
  - `WHEEL_RADIUS` → `34`，`PEDAL_RADIUS` → `26`，`GEAR_RATIO` → `0.4`
  - `POUCH_BULGE_MAX` → `1.6`
  - `wheelAngleFor(distance)` → `number`（弧度）
  - `pedalAngleFor(wheelAngle)` → `number`（弧度）
  - `legPhaseFor(wheelAngle)` → `number`
  - `pouchBulgeFor(count)` → `number`（1.0 .. 1.6）
  - `drawWheel(ctx, center, angle)` → `void`
  - `drawLeg(ctx, angle, hipX, color)` → `void`
  - `drawBike(ctx, g, wheelAngle)` → `void`
  - `drawPelican(ctx, g, time)` → `void`

- [ ] **Step 1: 写失败测试**

在 `TESTS` 块末尾追加：

```js
test('车轮角度与前进距离成正比', function () {
  assertClose(wheelAngleFor(0), 0, 1e-9, '距离 0 → 角度 0');
  assertClose(wheelAngleFor(WHEEL_RADIUS * Math.PI), Math.PI, 1e-9, '走过一个半径长度 → 1 弧度');
  assertClose(wheelAngleFor(WHEEL_RADIUS * 2 * Math.PI), Math.PI * 2, 1e-9, '走过一个周长 → 一整圈');
  assert(wheelAngleFor(1000) > wheelAngleFor(500), '走得越远转得越多');
});

test('腿相位绑定车轮角度，不独立循环', function () {
  assertClose(legPhaseFor(1), pedalAngleFor(1), 1e-9, '腿相位应等于曲柄角度');
  assertClose(pedalAngleFor(1), 0.4, 1e-9, '曲柄角度应为车轮角度的 GEAR_RATIO 倍');
  // 关键：距离不变时相位不变（说明没有独立的循环计时器）
  var a = legPhaseFor(wheelAngleFor(1234));
  var b = legPhaseFor(wheelAngleFor(1234));
  assertClose(a, b, 1e-12, '相同距离必须得到相同相位');
});

test('喉囊鼓起程度随囊内容线性增长', function () {
  assertClose(pouchBulgeFor(0), 1, 1e-9, '空囊不鼓');
  assertClose(pouchBulgeFor(3), 1.3, 1e-9, '半满应鼓到 1.3');
  assertClose(pouchBulgeFor(6), 1.6, 1e-9, '满囊应鼓到 1.6');
  assert(pouchBulgeFor(6) > pouchBulgeFor(3), '越满越鼓');
});

test('drawWheel 不抛异常且画出轮胎、轮辋与辐条', function () {
  var ctx = makeStubCtx();
  drawWheel(ctx, { x: 200, y: 396 }, 1.2);
  assert(ctx.did('arc'), '应画圆');
  assert(ctx.did('rotate'), '辐条应随角度旋转');
  assert(ctx.did('stroke'), '应有描边');
});

test('drawPelican 不抛异常且画出车架与身体', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  var ctx = makeStubCtx();
  drawPelican(ctx, g, 0.5);
  assert(ctx.did('ellipse'), '应画身体椭圆');
  assert(ctx.did('rotate'), '车轮应旋转');
  assert(ctx.did('translate'), '应有位移变换');
});

test('drawPelican 在囊满与空囊两种状态下都不崩', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  [0, 6].forEach(function (n) {
    g.pouch = createPouch(POUCH_CAPACITY);
    for (var i = 0; i < n; i++) pouchSwallow(g.pouch, 'fish');
    var ctx = makeStubCtx();
    drawPelican(ctx, g, 1);
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: FAIL，报 `wheelAngleFor is not defined`。

- [ ] **Step 3: 实现纯函数（`CORE` 块）**

```js
var WHEEL_RADIUS = 34;
var PEDAL_RADIUS = 26;
var GEAR_RATIO = 0.4;
var POUCH_BULGE_MAX = 1.6;

// 车轮转过的弧度 = 前进距离 / 半径
function wheelAngleFor(distance) {
  return distance / WHEEL_RADIUS;
}

function pedalAngleFor(wheelAngle) {
  return wheelAngle * GEAR_RATIO;
}

// 腿的踩踏相位完全由车轮角度决定，没有独立计时器
function legPhaseFor(wheelAngle) {
  return pedalAngleFor(wheelAngle);
}

function pouchBulgeFor(count) {
  return 1 + (POUCH_BULGE_MAX - 1) * (count / POUCH_CAPACITY);
}
```

- [ ] **Step 4: 实现绘制（`RENDER` 块）**

在 `RENDER` 块内追加。调色板取自现有 `pelican-bicycle.svg`：

```js
var PLUME_COLOR = '#ffffff';
var PLUME_SHADE = '#e8eef4';
var PLUME_EDGE  = '#c3ccd4';
var BEAK_COLOR  = '#ffc75f';
var BEAK_EDGE   = '#ef8f2a';
var POUCH_COLOR = '#ffb44a';
var LEG_COLOR   = '#ef9b2e';
var LEG_DARK    = '#d4821f';
var FRAME_COLOR = '#d94f3d';
var TIRE_COLOR  = '#2b2f33';
var RIM_COLOR   = '#b9c3cc';
var SPOKE_COLOR = '#a6b2be';
var HUB_COLOR   = '#6d7883';
var METAL_COLOR = '#8d97a2';
var DARK_COLOR  = '#33383d';

function drawWheel(ctx, c, angle) {
  ctx.save();
  ctx.strokeStyle = TIRE_COLOR;
  ctx.lineWidth = 9;
  ctx.beginPath();
  ctx.arc(c.x, c.y, WHEEL_RADIUS, 0, Math.PI * 2);
  ctx.stroke();

  ctx.strokeStyle = RIM_COLOR;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(c.x, c.y, WHEEL_RADIUS - 8, 0, Math.PI * 2);
  ctx.stroke();

  // 辐条随 angle 旋转 —— 车轮真的在转，不是贴图
  ctx.save();
  ctx.translate(c.x, c.y);
  ctx.rotate(angle);
  ctx.strokeStyle = SPOKE_COLOR;
  ctx.lineWidth = 2;
  for (var i = 0; i < 4; i++) {
    var a = (i / 4) * Math.PI;
    var dx = Math.cos(a) * (WHEEL_RADIUS - 8);
    var dy = Math.sin(a) * (WHEEL_RADIUS - 8);
    ctx.beginPath();
    ctx.moveTo(dx, dy);
    ctx.lineTo(-dx, -dy);
    ctx.stroke();
  }
  ctx.restore();

  ctx.fillStyle = HUB_COLOR;
  ctx.beginPath();
  ctx.arc(c.x, c.y, 5, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawLeg(ctx, angle, hipX, color) {
  var crankX = PELICAN_X;
  var crankY = GROUND_Y - 32;
  var px = crankX + Math.cos(angle) * PEDAL_RADIUS;
  var py = crankY + Math.sin(angle) * PEDAL_RADIUS;
  var hipY = GROUND_Y - 132;
  var kneeX = (hipX + px) / 2 + 14;
  var kneeY = (hipY + py) / 2;

  ctx.save();
  ctx.strokeStyle = color;
  ctx.lineWidth = 9;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(hipX, hipY);
  ctx.lineTo(kneeX, kneeY);
  ctx.lineTo(px, py);
  ctx.stroke();

  // 蹼足
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(px - 9, py);
  ctx.lineTo(px + 15, py + 4);
  ctx.lineTo(px - 7, py + 13);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

function drawBike(ctx, g, wheelAngle) {
  var rear  = { x: PELICAN_X - 78, y: GROUND_Y - WHEEL_RADIUS };
  var front = { x: PELICAN_X + 78, y: GROUND_Y - WHEEL_RADIUS };
  var crank = { x: PELICAN_X,      y: GROUND_Y - 32 };
  var seat  = { x: PELICAN_X - 24, y: GROUND_Y - 100 };
  var head  = { x: PELICAN_X + 66, y: GROUND_Y - 100 };

  drawWheel(ctx, rear, wheelAngle);
  drawWheel(ctx, front, wheelAngle);

  // 车架
  ctx.save();
  ctx.strokeStyle = FRAME_COLOR;
  ctx.lineWidth = 7;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(rear.x, rear.y);   ctx.lineTo(crank.x, crank.y);
  ctx.moveTo(crank.x, crank.y); ctx.lineTo(seat.x, seat.y);
  ctx.moveTo(seat.x, seat.y);   ctx.lineTo(head.x, head.y);
  ctx.moveTo(head.x, head.y);   ctx.lineTo(crank.x, crank.y);
  ctx.stroke();

  // 前叉
  ctx.strokeStyle = METAL_COLOR;
  ctx.lineWidth = 6;
  ctx.beginPath();
  ctx.moveTo(head.x, head.y);
  ctx.lineTo(front.x, front.y);
  ctx.stroke();

  // 座管与车把立管
  ctx.beginPath();
  ctx.moveTo(seat.x, seat.y); ctx.lineTo(seat.x - 2, seat.y - 16);
  ctx.moveTo(head.x, head.y); ctx.lineTo(head.x + 4, head.y - 16);
  ctx.stroke();

  // 车座
  ctx.fillStyle = DARK_COLOR;
  ctx.beginPath();
  ctx.ellipse(seat.x - 4, seat.y - 18, 20, 7, -0.1, 0, Math.PI * 2);
  ctx.fill();

  // 车把
  ctx.strokeStyle = DARK_COLOR;
  ctx.lineWidth = 6;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(head.x - 14, head.y - 20);
  ctx.quadraticCurveTo(head.x + 6, head.y - 30, head.x + 22, head.y - 18);
  ctx.stroke();

  // 曲柄与脚踏
  ctx.strokeStyle = METAL_COLOR;
  ctx.lineWidth = 6;
  ctx.beginPath();
  ctx.moveTo(crank.x, crank.y);
  ctx.lineTo(crank.x + Math.cos(wheelAngle * GEAR_RATIO) * PEDAL_RADIUS,
             crank.y + Math.sin(wheelAngle * GEAR_RATIO) * PEDAL_RADIUS);
  ctx.moveTo(crank.x, crank.y);
  ctx.lineTo(crank.x - Math.cos(wheelAngle * GEAR_RATIO) * PEDAL_RADIUS,
             crank.y - Math.sin(wheelAngle * GEAR_RATIO) * PEDAL_RADIUS);
  ctx.stroke();

  ctx.fillStyle = HUB_COLOR;
  ctx.beginPath();
  ctx.arc(crank.x, crank.y, 6, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawPelican(ctx, g, time) {
  var wheelAngle = wheelAngleFor(g.distance);
  var pedalAngle = legPhaseFor(wheelAngle);
  var bulge = pouchBulgeFor(pouchCount(g.pouch));
  var bob = Math.sin(time * 9) * 1.6;

  drawBike(ctx, g, wheelAngle);

  ctx.save();
  ctx.translate(0, bob);

  // 远侧腿（先画，被身体遮住）
  drawLeg(ctx, pedalAngle + Math.PI, PELICAN_X - 30, LEG_DARK);

  // 尾巴
  ctx.fillStyle = PLUME_SHADE;
  ctx.strokeStyle = PLUME_EDGE;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(PELICAN_X - 62, GROUND_Y - 176);
  ctx.lineTo(PELICAN_X - 118, GROUND_Y - 202);
  ctx.lineTo(PELICAN_X - 110, GROUND_Y - 160);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  // 身体
  ctx.fillStyle = PLUME_COLOR;
  ctx.beginPath();
  ctx.ellipse(PELICAN_X - 16, GROUND_Y - 158, 62, 42, -0.12, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();

  // 脖子（粗描边模拟圆柱）
  var neckFromX = PELICAN_X + 24, neckFromY = GROUND_Y - 186;
  var headX = PELICAN_X + 82,    headY = GROUND_Y - 236;
  ctx.strokeStyle = PLUME_EDGE;
  ctx.lineWidth = 40;
  ctx.lineCap = 'round';
  ctx.beginPath();
  ctx.moveTo(neckFromX, neckFromY);
  ctx.quadraticCurveTo(PELICAN_X + 56, GROUND_Y - 216, headX, headY);
  ctx.stroke();
  ctx.strokeStyle = PLUME_COLOR;
  ctx.lineWidth = 35;
  ctx.beginPath();
  ctx.moveTo(neckFromX, neckFromY);
  ctx.quadraticCurveTo(PELICAN_X + 56, GROUND_Y - 216, headX, headY);
  ctx.stroke();

  // 头
  ctx.fillStyle = PLUME_COLOR;
  ctx.beginPath();
  ctx.arc(headX, headY, 24, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();

  // 上喙
  ctx.fillStyle = BEAK_COLOR;
  ctx.strokeStyle = BEAK_EDGE;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(headX + 12, headY - 8);
  ctx.lineTo(headX + 96, headY + 4);
  ctx.lineTo(headX + 94, headY + 16);
  ctx.lineTo(headX + 14, headY + 10);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  // 喉囊：bulge 直接控制下垂深度 —— 吞得越多越鼓
  var drop = 46 * bulge;
  ctx.fillStyle = POUCH_COLOR;
  ctx.beginPath();
  ctx.moveTo(headX + 14, headY + 10);
  ctx.quadraticCurveTo(headX + 56, headY + 10 + drop, headX + 94, headY + 14);
  ctx.closePath();
  ctx.fill();

  // 囊内容物：按囊里实际的道具画小圆点
  var items = g.pouch.items;
  for (var i = 0; i < items.length; i++) {
    var k = (i + 0.5) / POUCH_CAPACITY;
    ctx.fillStyle = ITEM_COLORS[items[i]] || '#ffffff';
    ctx.beginPath();
    ctx.arc(headX + 20 + k * 68, headY + 20 + Math.sin(k * Math.PI) * (drop * 0.55), 6, 0, Math.PI * 2);
    ctx.fill();
  }

  // 眼睛
  ctx.fillStyle = DARK_COLOR;
  ctx.beginPath();
  ctx.arc(headX + 6, headY - 6, 5, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#ffffff';
  ctx.beginPath();
  ctx.arc(headX + 7.5, headY - 7.5, 1.6, 0, Math.PI * 2);
  ctx.fill();

  // 近侧翅膀
  ctx.fillStyle = PLUME_SHADE;
  ctx.strokeStyle = PLUME_EDGE;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(PELICAN_X - 20, GROUND_Y - 190);
  ctx.quadraticCurveTo(PELICAN_X + 30, GROUND_Y - 176, PELICAN_X + 44, GROUND_Y - 140);
  ctx.quadraticCurveTo(PELICAN_X + 6, GROUND_Y - 138, PELICAN_X - 26, GROUND_Y - 152);
  ctx.closePath();
  ctx.fill();
  ctx.stroke();

  // 近侧腿
  drawLeg(ctx, pedalAngle, PELICAN_X + 10, LEG_COLOR);

  ctx.restore();
}
```

`ITEM_COLORS` 在 Task 11 定义。**为了让 Task 10 的测试能跑通**，本步骤先在 `RENDER` 块里加一个占位常量：

```js
var ITEM_COLORS = {
  fish: '#5fb3d4', rock: '#8d97a2', chili: '#d94f3d',
  bubble: '#a8d8ea', star: '#ffd93b'
};
```

Task 11 会用到同一份常量，不要重复定义。

- [ ] **Step 5: 跑测试确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: 65/65 passed。

- [ ] **Step 6: 目视确认（本任务的关键验收）**

在启动代码里接上 `drawBackground` + `drawGround` + `drawPelican`，双击打开确认：

1. 能一眼认出是「一只鹈鹕骑在自行车上」
2. 车轮在转（辐条在动）
3. 腿跟着踏板转，不是独立摆动
4. 临时给 `g.pouch` 塞 6 条鱼，确认喉囊明显鼓起来且囊里能看到 6 个彩色圆点

第 4 条改完记得撤掉。

- [ ] **Step 7: Commit**

```bash
cd /d/hermes
git add projects/pelican-bike/index.html
git commit -F - <<'EOF'
渲染:鹈鹕与自行车程序化绘制

车轮转速与前进距离严格成正比,腿相位绑定曲柄角度,
喉囊鼓起程度反映囊内容物。

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```

---

### Task 11: 渲染 — 道具、障碍、粒子池

**Files:**
- Modify: `projects/pelican-bike/index.html`

**Interfaces:**
- Consumes: Task 9/10 `RENDER` 块、`ITEM_COLORS`；Task 8 实体形状；Task 5 `GROUND_Y`/`PELICAN_X`
- Produces:
  - `PARTICLE_GRAVITY` → `900`
  - `PARTICLE_POOL_SIZE` → `256`
  - `createPool(size)` → `pool`（`{ size, cursor, items }`）
  - `poolSpawn(pool, props)` → `particle`（`props`：`{x,y,vx,vy,life,radius,color}`）
  - `poolUpdate(pool, dt)` → `void`
  - `poolAliveCount(pool)` → `number`
  - `drawEntity(ctx, ent)` → `void`
  - `drawEntities(ctx, g)` → `void`
  - `drawProjectiles(ctx, g)` → `void`
  - `drawParticles(ctx, pool)` → `void`

- [ ] **Step 1: 写失败测试**

在 `TESTS` 块末尾追加：

```js
test('粒子池预分配且初始全为死亡', function () {
  var pool = createPool(64);
  assert(pool.items.length === 64, '应预分配 64 个');
  assert(poolAliveCount(pool) === 0, '初始应全部死亡');
});

test('poolSpawn 复用池内对象，不新增引用', function () {
  var pool = createPool(64);
  var p = poolSpawn(pool, { x: 1, y: 2, life: 0.5 });
  assert(pool.items.indexOf(p) !== -1, '返回的粒子必须是池内已有对象');
  assert(poolAliveCount(pool) === 1, '存活数应为 1');
  assertClose(p.life, 0.5, 1e-9, 'life 应被设置');
  assertClose(p.maxLife, 0.5, 1e-9, 'maxLife 应记录初始 life');
});

test('连续 spawn 200 次池长度不增长（不每帧分配）', function () {
  var pool = createPool(64);
  var firstRef = pool.items[0];
  for (var i = 0; i < 200; i++) poolSpawn(pool, { x: i, y: 0, life: 10 });
  assert(pool.items.length === 64, '池长度应恒为 64，实际 ' + pool.items.length);
  assert(pool.items[0] === firstRef, '池内对象应被复用而非重建');
  assert(poolAliveCount(pool) === 64, '池满时全部存活');
});

test('池满时覆盖最老的粒子而不是丢弃', function () {
  var pool = createPool(4);
  var spawned = [];
  for (var i = 0; i < 4; i++) spawned.push(poolSpawn(pool, { x: i, y: 0, life: 10 }));
  var over = poolSpawn(pool, { x: 99, y: 0, life: 10 });
  assert(over === spawned[0], '应覆盖最早分配的那个');
  assertClose(over.x, 99, 1e-9, '被覆盖的粒子应带上新属性');
  assert(poolAliveCount(pool) === 4, '存活数仍为 4');
});

test('poolUpdate 推进位置并在 life 归零后回收', function () {
  var pool = createPool(4);
  var p = poolSpawn(pool, { x: 0, y: 0, vx: 100, vy: 0, life: 0.1 });
  poolUpdate(pool, 0.05);
  assertClose(p.x, 5, 1e-6, '应前进 100 * 0.05 = 5');
  assert(p.alive === true, 'life 未耗尽应仍存活');
  poolUpdate(pool, 0.1);
  assert(p.alive === false, 'life 耗尽应回收');
  assert(poolAliveCount(pool) === 0, '存活数应回到 0');
});

test('回收后的槽位能被再次复用', function () {
  var pool = createPool(1);
  var a = poolSpawn(pool, { x: 0, y: 0, life: 0.05 });
  poolUpdate(pool, 0.1);
  assert(poolAliveCount(pool) === 0, '应已回收');
  var b = poolSpawn(pool, { x: 7, y: 0, life: 1 });
  assert(b === a, '应复用同一个对象');
  assertClose(b.x, 7, 1e-9, '应是新属性');
});

test('drawEntities / drawProjectiles / drawParticles 不抛异常', function () {
  var g = createGame(makeRng(1));
  startRun(g);
  g.entities = [
    { kind: 'obstacle', type: 'bin', x: 600, bottom: 0, w: 54, h: 70 },
    { kind: 'obstacle', type: 'crow', x: 700, bottom: 60, w: 48, h: 34 },
    { kind: 'obstacle', type: 'pit', x: 800, bottom: 0, w: 90, h: 0 },
    { kind: 'obstacle', type: 'wall', x: 900, bottom: 0, w: 46, h: 170 },
    { kind: 'item', type: 'fish', x: 500, bottom: 40, w: 32, h: 32 },
    { kind: 'item', type: 'rock', x: 520, bottom: 90, w: 32, h: 32 },
    { kind: 'item', type: 'chili', x: 540, bottom: 60, w: 32, h: 32 },
    { kind: 'item', type: 'bubble', x: 560, bottom: 120, w: 32, h: 32 },
    { kind: 'item', type: 'star', x: 580, bottom: 70, w: 32, h: 32 }
  ];
  g.projectiles = [{ item: 'rock', x: 400, y: 300, piercing: true }];
  var pool = createPool(16);
  poolSpawn(pool, { x: 10, y: 10, life: 1 });

  var ctx = makeStubCtx();
  drawEntities(ctx, g);
  drawProjectiles(ctx, g);
  drawParticles(ctx, pool);
  assert(ctx.did('fill'), '应画出内容');
});

test('每种道具都有配色', function () {
  ITEM_TYPES.forEach(function (t) {
    assert(typeof ITEM_COLORS[t] === 'string' && ITEM_COLORS[t].length > 0, t + ' 缺少配色');
  });
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: FAIL，报 `createPool is not defined`。

- [ ] **Step 3: 实现粒子池（`CORE` 块）**

```js
var PARTICLE_GRAVITY = 900;
var PARTICLE_POOL_SIZE = 256;

function createPool(size) {
  var pool = { size: size, cursor: 0, items: [] };
  for (var i = 0; i < size; i++) {
    pool.items.push({
      alive: false, x: 0, y: 0, vx: 0, vy: 0,
      life: 0, maxLife: 1, radius: 4, color: '#ffffff'
    });
  }
  return pool;
}

// 优先复用死亡槽位；池满则覆盖 cursor 指向的最老槽位。绝不分配新对象
function poolSpawn(pool, props) {
  var p = null;
  for (var i = 0; i < pool.size; i++) {
    var idx = (pool.cursor + i) % pool.size;
    if (!pool.items[idx].alive) {
      p = pool.items[idx];
      pool.cursor = (idx + 1) % pool.size;
      break;
    }
  }
  if (p === null) {
    p = pool.items[pool.cursor];
    pool.cursor = (pool.cursor + 1) % pool.size;
  }
  p.alive = true;
  p.x = props.x;
  p.y = props.y;
  p.vx = props.vx || 0;
  p.vy = props.vy || 0;
  p.life = props.life === undefined ? 0.6 : props.life;
  p.maxLife = p.life;
  p.radius = props.radius === undefined ? 4 : props.radius;
  p.color = props.color || '#ffffff';
  return p;
}

function poolUpdate(pool, dt) {
  for (var i = 0; i < pool.size; i++) {
    var p = pool.items[i];
    if (!p.alive) continue;
    p.life -= dt;
    if (p.life <= 0) { p.alive = false; continue; }
    p.vy += PARTICLE_GRAVITY * dt;
    p.x += p.vx * dt;
    p.y += p.vy * dt;
  }
}

function poolAliveCount(pool) {
  var n = 0;
  for (var i = 0; i < pool.size; i++) if (pool.items[i].alive) n += 1;
  return n;
}
```

- [ ] **Step 4: 实现绘制（`RENDER` 块）**

```js
function drawEntity(ctx, ent) {
  var box = obstacleBox(ent);
  ctx.save();

  if (ent.kind === 'item') {
    ctx.globalAlpha = ent.missed ? 0.35 : 1;
    ctx.fillStyle = ITEM_COLORS[ent.type] || '#ffffff';
    ctx.beginPath();
    ctx.arc(ent.x, box.y + box.h / 2, ent.w / 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.75)';
    ctx.lineWidth = 3;
    ctx.stroke();
    ctx.restore();
    return;
  }

  if (ent.type === 'pit') {
    ctx.fillStyle = '#7a8a6e';
    ctx.beginPath();
    ctx.ellipse(ent.x, GROUND_Y + 6, ent.w / 2, 16, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#3d4a36';
    ctx.beginPath();
    ctx.ellipse(ent.x, GROUND_Y + 8, ent.w / 2 - 6, 11, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    return;
  }

  if (ent.type === 'crow') {
    ctx.fillStyle = '#2b2f33';
    ctx.beginPath();
    ctx.ellipse(ent.x, box.y + box.h / 2, ent.w / 2, ent.h / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(ent.x - 6, box.y + 6);
    ctx.lineTo(ent.x - 30, box.y - 10);
    ctx.lineTo(ent.x + 2, box.y + 14);
    ctx.closePath();
    ctx.fill();
    ctx.fillStyle = '#ffc75f';
    ctx.beginPath();
    ctx.moveTo(ent.x + ent.w / 2 - 4, box.y + box.h / 2);
    ctx.lineTo(ent.x + ent.w / 2 + 14, box.y + box.h / 2 + 3);
    ctx.lineTo(ent.x + ent.w / 2 - 4, box.y + box.h / 2 + 7);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
    return;
  }

  if (ent.type === 'wall') {
    ctx.fillStyle = '#9aa6b2';
    ctx.fillRect(box.x, box.y, box.w, box.h);
    ctx.fillStyle = '#7d8b98';
    for (var y = box.y; y < box.y + box.h; y += 26) {
      ctx.fillRect(box.x, y, box.w, 4);
    }
    ctx.strokeStyle = '#6d7883';
    ctx.lineWidth = 2;
    ctx.strokeRect(box.x, box.y, box.w, box.h);
    ctx.restore();
    return;
  }

  // bin / barrier
  ctx.fillStyle = ent.type === 'bin' ? '#5c6b7a' : '#e07a3f';
  ctx.fillRect(box.x, box.y, box.w, box.h);
  ctx.fillStyle = ent.type === 'bin' ? '#48555f' : '#c2652f';
  ctx.fillRect(box.x, box.y, box.w, 10);
  ctx.strokeStyle = 'rgba(0,0,0,0.25)';
  ctx.lineWidth = 2;
  ctx.strokeRect(box.x, box.y, box.w, box.h);
  ctx.restore();
}

function drawEntities(ctx, g) {
  for (var i = 0; i < g.entities.length; i++) {
    var e = g.entities[i];
    if (e.x < -160 || e.x > VIEW_W + 160) continue;
    drawEntity(ctx, e);
  }
}

function drawProjectiles(ctx, g) {
  for (var i = 0; i < g.projectiles.length; i++) {
    var p = g.projectiles[i];
    ctx.save();
    ctx.fillStyle = ITEM_COLORS[p.item] || '#ffffff';
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.piercing ? 14 : 11, 0, Math.PI * 2);
    ctx.fill();
    if (p.piercing) {
      ctx.strokeStyle = 'rgba(255,255,255,0.6)';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(p.x - 34, p.y);
      ctx.lineTo(p.x - 16, p.y);
      ctx.stroke();
    }
    ctx.restore();
  }
}

function drawParticles(ctx, pool) {
  ctx.save();
  for (var i = 0; i < pool.size; i++) {
    var p = pool.items[i];
    if (!p.alive) continue;
    ctx.globalAlpha = Math.max(0, p.life / p.maxLife);
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}
```

- [ ] **Step 5: 跑测试确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: 73/73 passed。

- [ ] **Step 6: 目视确认**

临时往 `g.entities` 里塞五种障碍和五种道具各一个，双击打开确认每种都画得出来、能分辨。改完撤掉。

- [ ] **Step 7: Commit**

```bash
cd /d/hermes
git add projects/pelican-bike/index.html
git commit -F - <<'EOF'
渲染:道具、障碍、抛射物与粒子池

粒子池预分配 256 槽,复用而非每帧新建对象。

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```

---

### Task 12: 音频层

Web Audio 程序化生成，无音频文件。把「声音参数」做成可测的纯数据，把「发声」做成薄薄一层。

**Files:**
- Modify: `projects/pelican-bike/index.html`

**Interfaces:**
- Consumes: Task 3 `multiplierFor`（间接）
- Produces:
  - `SOUND_SPECS` → `{ swallow, spit, jump, crash, dash }`，每项 `{ type, from, to, duration, gain }`
  - `SCORE_BASE_HZ` → `440`
  - `pitchForStreak(streak)` → `number`
  - `createAudio(Ctor)` → `{ ctx, muted, ensure(), play(name, streak), toggleMute() }`

`createAudio` 接收 `AudioContext` 构造函数**作为参数**，而不是自己去读 `window`——这样它能在 node 沙箱里被测试，也顺便覆盖了「浏览器不给 AudioContext」这条失败路径。

- [ ] **Step 1: 写失败测试**

在 `TESTS` 块末尾追加：

```js
test('连击音高：基准 440Hz，每级升半音，8 级后回绕', function () {
  assertClose(pitchForStreak(0), 440, 1e-9, 'streak 0 → 440Hz');
  assertClose(pitchForStreak(8), 440, 1e-9, 'streak 8 应回绕到 440Hz');
  assertClose(pitchForStreak(16), 440, 1e-9, 'streak 16 应回绕到 440Hz（16 % 8 === 0）');
  assertClose(pitchForStreak(1), 440 * Math.pow(2, 1 / 12), 1e-9, 'streak 1 应升一个半音');
  assert(pitchForStreak(7) > pitchForStreak(3), '连击越高音越高');
});

test('音效规格完整且参数合理', function () {
  ['swallow', 'spit', 'jump', 'crash', 'dash'].forEach(function (name) {
    var s = SOUND_SPECS[name];
    assert(s !== undefined, '缺少音效 ' + name);
    assert(s.duration > 0, name + ' 的 duration 应为正');
    assert(s.gain > 0 && s.gain <= 1, name + ' 的 gain 应在 (0,1]');
    assert(typeof s.from === 'number' && typeof s.to === 'number', name + ' 应有起止频率');
  });
});

test('没有 AudioContext 时 play 不抛异常', function () {
  var audio = createAudio(null);
  assert(audio.ensure() === null, '无构造函数时应返回 null');
  ['swallow', 'spit', 'jump', 'crash', 'dash'].forEach(function (n) {
    audio.play(n, 0);   // 不应抛异常
  });
});

test('AudioContext 构造失败时不抛异常（自动播放策略）', function () {
  var audio = createAudio(function () { throw new Error('blocked by autoplay policy'); });
  assert(audio.ensure() === null, '构造失败应静默降级为 null');
  audio.play('jump', 0);
});

test('静音时 play 是空操作，toggleMute 可来回切换', function () {
  var audio = createAudio(null);
  assert(audio.muted === false, '默认不静音');
  assert(audio.toggleMute() === true, '切换后应静音');
  assert(audio.play('jump', 0) === undefined, '静音时 play 应无返回、不抛异常');
  assert(audio.toggleMute() === false, '再切换应取消静音');
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: FAIL，报 `pitchForStreak is not defined`。

- [ ] **Step 3: 实现纯数据与音高（`CORE` 块）**

```js
var SCORE_BASE_HZ = 440;

// 连击越高音越高，8 级后回绕，避免高到听不见
function pitchForStreak(streak) {
  return SCORE_BASE_HZ * Math.pow(2, (streak % 8) / 12);
}

var SOUND_SPECS = {
  swallow: { type: 'sine',     from: 220, to: 440, duration: 0.08, gain: 0.18 },
  spit:    { type: 'noise',    from: 900, to: 200, duration: 0.12, gain: 0.20 },
  jump:    { type: 'square',   from: 330, to: 660, duration: 0.09, gain: 0.14 },
  crash:   { type: 'noise',    from: 200, to: 60,  duration: 0.25, gain: 0.30 },
  dash:    { type: 'sawtooth', from: 120, to: 900, duration: 0.35, gain: 0.22 }
};
```

- [ ] **Step 4: 实现发声层（`RENDER` 块）**

```js
// Ctor 由调用方注入（浏览器传 AudioContext，测试传 null）
function createAudio(Ctor) {
  var audio = {
    ctx: null,
    muted: false,
    Ctor: Ctor || null,

    ensure: function () {
      if (audio.ctx) return audio.ctx;
      if (!audio.Ctor) return null;
      try {
        audio.ctx = new audio.Ctor();
      } catch (err) {
        audio.ctx = null;   // 自动播放策略可能拒绝创建
      }
      return audio.ctx;
    },

    toggleMute: function () {
      audio.muted = !audio.muted;
      return audio.muted;
    },

    play: function (name, streak) {
      if (audio.muted) return;
      var ctx = audio.ensure();
      if (!ctx) return;

      var now = ctx.currentTime;
      var spec = SOUND_SPECS[name];
      var gain = ctx.createGain();
      gain.connect(ctx.destination);
      gain.gain.setValueAtTime(0.0001, now);
      gain.gain.exponentialRampToValueAtTime(0.25, now + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + (spec ? spec.duration : 0.1));

      if (name === 'score') {
        var osc = ctx.createOscillator();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(pitchForStreak(streak || 0), now);
        osc.connect(gain);
        osc.start(now);
        osc.stop(now + 0.12);
        return;
      }

      if (!spec) return;

      if (spec.type === 'noise') {
        var len = Math.max(1, Math.floor(ctx.sampleRate * spec.duration));
        var buf = ctx.createBuffer(1, len, ctx.sampleRate);
        var data = buf.getChannelData(0);
        for (var i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;
        var src = ctx.createBufferSource();
        src.buffer = buf;
        var filt = ctx.createBiquadFilter();
        filt.type = 'lowpass';
        filt.frequency.setValueAtTime(spec.from, now);
        filt.frequency.exponentialRampToValueAtTime(Math.max(20, spec.to), now + spec.duration);
        src.connect(filt);
        filt.connect(gain);
        src.start(now);
        src.stop(now + spec.duration);
        return;
      }

      var o = ctx.createOscillator();
      o.type = spec.type;
      o.frequency.setValueAtTime(spec.from, now);
      o.frequency.exponentialRampToValueAtTime(Math.max(20, spec.to), now + spec.duration);
      o.connect(gain);
      o.start(now);
      o.stop(now + spec.duration);
    }
  };
  return audio;
}
```

- [ ] **Step 5: 跑测试确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: 78/78 passed。

- [ ] **Step 6: Commit**

```bash
cd /d/hermes
git add projects/pelican-bike/index.html
git commit -F - <<'EOF'
音频:Web Audio 程序化音效,无音频文件

AudioContext 构造函数由外部注入,便于测试与降级。

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```

---

### Task 13: 输入、UI、接线与实机验收

最后一步把所有层接起来，并逐条核对 spec 的验收标准。

**Files:**
- Modify: `projects/pelican-bike/index.html`

**Interfaces:**
- Consumes: 全部前置任务
- Produces:
  - `MAX_DT` → `1/30`
  - `KEY_ACTIONS` → `{ ArrowUp:'jump', w:'jump', W:'jump', ArrowDown:'duck', s:'duck', S:'duck', ' ':'spit', p:'pause', P:'pause', Escape:'pause', r:'restart', R:'restart', m:'mute', M:'mute' }`
  - `BEST_KEY` → `'pelicanRunner.best'`
  - `actionForKey(key)` → `string | null`
  - `clampDt(dt)` → `number`
  - `safeLoadBest(storage)` → `number`
  - `safeSaveBest(storage, value)` → `boolean`

- [ ] **Step 1: 写失败测试**

在 `TESTS` 块末尾追加：

```js
test('按键映射覆盖 spec 第 7 节全部按键', function () {
  assert(actionForKey('ArrowUp') === 'jump', '↑ 应为跳');
  assert(actionForKey('w') === 'jump', 'W 应为跳');
  assert(actionForKey('ArrowDown') === 'duck', '↓ 应为蹲');
  assert(actionForKey('s') === 'duck', 'S 应为蹲');
  assert(actionForKey(' ') === 'spit', '空格应为吐');
  assert(actionForKey('p') === 'pause', 'P 应为暂停');
  assert(actionForKey('Escape') === 'pause', 'Esc 应为暂停');
  assert(actionForKey('r') === 'restart', 'R 应为重开');
  assert(actionForKey('m') === 'mute', 'M 应为静音');
  assert(actionForKey('z') === null, '未映射的键应返回 null');
});

test('Review Focus 2：clampDt 钳制切标签页后的超大 dt', function () {
  assertClose(clampDt(1 / 60), 1 / 60, 1e-12, '正常帧不受影响');
  assertClose(clampDt(30), MAX_DT, 1e-12, '30 秒应被钳到 MAX_DT');
  assertClose(clampDt(1e9), MAX_DT, 1e-12, '极大值应被钳到 MAX_DT');
  assertClose(clampDt(-5), 0, 1e-12, '负值应为 0');
  assertClose(clampDt(NaN), 0, 1e-12, 'NaN 应为 0');
  assertClose(clampDt(Infinity), 0, 1e-12, 'Infinity 是无效输入，应返回 0');
});

test('Review Focus 5：localStorage 抛异常时读写都安全降级', function () {
  var throwing = {
    getItem: function () { throw new Error('denied'); },
    setItem: function () { throw new Error('quota exceeded'); }
  };
  assert(safeLoadBest(throwing) === 0, '读失败应返回 0');
  assert(safeSaveBest(throwing, 123) === false, '写失败应返回 false 且不抛异常');
});

test('最高分读写往返正确', function () {
  var store = {};
  var fake = {
    getItem: function (k) { return Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null; },
    setItem: function (k, v) { store[k] = String(v); }
  };
  assert(safeLoadBest(fake) === 0, '空存储应返回 0');
  assert(safeSaveBest(fake, 4321) === true, '写入应成功');
  assert(safeLoadBest(fake) === 4321, '应读回 4321');
  assert(store[BEST_KEY] === '4321', 'key 应为 ' + BEST_KEY);
});

test('最高分读到脏数据时降级为 0', function () {
  var dirty = { getItem: function () { return 'abc'; }, setItem: function () {} };
  assert(safeLoadBest(dirty) === 0, '非数字应返回 0');
  var negative = { getItem: function () { return '-50'; }, setItem: function () {} };
  assert(safeLoadBest(negative) === 0, '负数应返回 0');
});
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: FAIL，报 `actionForKey is not defined`。

- [ ] **Step 3: 实现纯逻辑（`CORE` 块）**

```js
var MAX_DT = 1 / 30;
var BEST_KEY = 'pelicanRunner.best';

var KEY_ACTIONS = {
  'ArrowUp': 'jump', 'w': 'jump', 'W': 'jump',
  'ArrowDown': 'duck', 's': 'duck', 'S': 'duck',
  ' ': 'spit',
  'p': 'pause', 'P': 'pause', 'Escape': 'pause',
  'r': 'restart', 'R': 'restart',
  'm': 'mute', 'M': 'mute'
};

function actionForKey(key) {
  return Object.prototype.hasOwnProperty.call(KEY_ACTIONS, key) ? KEY_ACTIONS[key] : null;
}

// 切标签页回来后 dt 可能是几十秒，必须钳制
function clampDt(dt) {
  if (!isFinite(dt) || dt < 0) return 0;
  return Math.min(dt, MAX_DT);
}

// storage 作为参数传入，便于测试注入会抛异常的假实现
function safeLoadBest(storage) {
  try {
    var n = parseInt(storage.getItem(BEST_KEY), 10);
    return isFinite(n) && n > 0 ? n : 0;
  } catch (err) {
    return 0;
  }
}

function safeSaveBest(storage, value) {
  try {
    storage.setItem(BEST_KEY, String(value));
    return true;
  } catch (err) {
    return false;
  }
}
```

- [ ] **Step 4: 跑测试确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: 96/96 passed。

- [ ] **Step 5: 写 UI 与接线（`APP` 区块，放在 `TESTS` 块之后）**

在 `TESTS` 块之后新增。这一段**允许**访问 DOM：

```js
/* ==== APP:BEGIN ==== */
(function () {
  var canvas = document.getElementById('game');
  var ctx = canvas.getContext('2d');
  var overlay = document.getElementById('overlay');
  var out = document.getElementById('out');

  var g = createGame(makeRng(Date.now() >>> 0));
  var audio = createAudio(window.AudioContext || window.webkitAudioContext);
  var particles = createPool(PARTICLE_POOL_SIZE);
  var storage = null;
  try { storage = window.localStorage; } catch (err) { storage = null; }

  var safeStorage = storage || {
    getItem: function () { return null; },
    setItem: function () {}
  };
  g.best = safeLoadBest(safeStorage);

  // ---- 自适应缩放 ----
  function resize() {
    var dpr = window.devicePixelRatio || 1;
    var scale = Math.min(window.innerWidth / VIEW_W, window.innerHeight / VIEW_H);
    canvas.style.width = Math.floor(VIEW_W * scale) + 'px';
    canvas.style.height = Math.floor(VIEW_H * scale) + 'px';
    canvas.width = Math.floor(VIEW_W * dpr);
    canvas.height = Math.floor(VIEW_H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  window.addEventListener('resize', resize);
  resize();

  // ---- 粒子辅助 ----
  function burst(x, y, n, color, speed) {
    for (var i = 0; i < n; i++) {
      var a = Math.random() * Math.PI * 2;
      var s = speed * (0.4 + Math.random() * 0.8);
      poolSpawn(particles, {
        x: x, y: y,
        vx: Math.cos(a) * s, vy: Math.sin(a) * s - 60,
        life: 0.4 + Math.random() * 0.5,
        radius: 2 + Math.random() * 4,
        color: color
      });
    }
  }

  var shake = 0;
  var flash = 0;

  // ---- 输入 ----

  window.addEventListener('keydown', function (ev) {
    var action = actionForKey(ev.key);
    if (!action) return;
    ev.preventDefault();

    if (action === 'mute') { audio.toggleMute(); return; }
    if (action === 'restart') { startRun(g); overlay.hidden = true; return; }
    if (action === 'pause') {
      if (g.state === 'playing') g.state = 'paused';
      else if (g.state === 'paused') g.state = 'playing';
      return;
    }

    if (g.state === 'title') { startRun(g); overlay.hidden = true; return; }
    if (g.state === 'gameover') { startRun(g); overlay.hidden = true; return; }
    if (g.state !== 'playing') return;

    if (action === 'jump') {
      if (jump(g)) audio.play('jump');
    } else if (action === 'duck') {
      setDucking(g, true);
    } else if (action === 'spit') {
      var eff = spit(g);
      if (eff) {
        audio.play('spit');
        burst(PELICAN_X + 70, GROUND_Y - g.height - 70, 8, '#ffffff', 180);
        if (eff.kind === 'dash') { flash = 1; shake = 14; audio.play('dash'); }
        if (eff.kind === 'clear') { flash = 0.8; shake = 10; }
      }
    }
  });

  window.addEventListener('keyup', function (ev) {
    if (actionForKey(ev.key) === 'duck') {
      setDucking(g, false);
    }
  });

  // ---- 主循环 ----
  var last = 0;
  var clock = 0;

  function frame(now) {
    var dt = clampDt((now - last) / 1000);
    last = now;
    clock += dt;

    if (g.state === 'playing' || g.state === 'crashed') {
      var prevLives = g.lives;
      updateGame(g, dt);
      if (g.state === 'playing') {
        spawnAhead(g);
        updateEntities(g, dt);
        updateProjectiles(g, dt);
      }
      if (g.lives < prevLives) {
        // 撞车：羽毛飞散 + 慢动作 + 震屏
        audio.play('crash');
        burst(PELICAN_X, GROUND_Y - 150, 26, PLUME_COLOR, 320);
        shake = 20;
      }
      if (g.state === 'gameover') {
        if (g.score.points > g.best) {
          g.best = g.score.points;
          safeSaveBest(safeStorage, g.best);
        }
        showOverlay('gameover');
      }
    }

    poolUpdate(particles, dt);
    if (shake > 0) shake = Math.max(0, shake - dt * 60);
    if (flash > 0) flash = Math.max(0, flash - dt * 2.5);

    // ---- 绘制 ----
    ctx.save();
    if (shake > 0) {
      ctx.translate((Math.random() - 0.5) * shake, (Math.random() - 0.5) * shake);
    }
    drawBackground(ctx, g);
    drawGround(ctx, g);
    drawEntities(ctx, g);
    drawProjectiles(ctx, g);
    drawParticles(ctx, particles);
    if (g.invuln > 0 && Math.floor(clock * 20) % 2 === 0) ctx.globalAlpha = 0.45;
    drawPelican(ctx, g, clock);
    ctx.restore();

    if (flash > 0) {
      ctx.save();
      ctx.globalAlpha = flash * 0.55;
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, VIEW_W, VIEW_H);
      ctx.restore();
    }

    drawHud(ctx, g);
    requestAnimationFrame(frame);
  }

  function drawHud(ctx2, gg) {
    ctx2.save();
    ctx2.font = 'bold 26px system-ui, sans-serif';
    ctx2.fillStyle = '#0c4a6e';
    ctx2.fillText(String(gg.score.points), 24, 44);
    ctx2.font = '16px system-ui, sans-serif';
    ctx2.fillText('最高 ' + gg.best, 24, 68);

    var mult = multiplierFor(gg.score.streak);
    if (mult > 1) {
      ctx2.font = 'bold 20px system-ui, sans-serif';
      ctx2.fillStyle = '#d94f3d';
      ctx2.fillText('x' + mult, 24, 96);
    }

    // 喉囊状态条
    var n = pouchCount(gg.pouch);
    for (var i = 0; i < POUCH_CAPACITY; i++) {
      ctx2.fillStyle = i < n ? (ITEM_COLORS[gg.pouch.items[i]] || '#ffffff') : 'rgba(12,74,110,0.18)';
      ctx2.beginPath();
      ctx2.arc(VIEW_W - 40 - i * 34, 40, 13, 0, Math.PI * 2);
      ctx2.fill();
    }

    // 命
    for (var h = 0; h < gg.lives; h++) {
      ctx2.fillStyle = '#d94f3d';
      ctx2.beginPath();
      ctx2.arc(VIEW_W - 40 - h * 30, 82, 10, 0, Math.PI * 2);
      ctx2.fill();
    }

    // 冲刺/浮空计时条
    if (gg.dash > 0) {
      ctx2.fillStyle = '#ffc75f';
      ctx2.fillRect(24, 108, 180 * (gg.dash / DASH_DURATION), 8);
    }
    if (gg.float > 0) {
      ctx2.fillStyle = '#a8d8ea';
      ctx2.fillRect(24, 122, 180 * (gg.float / FLOAT_DURATION), 8);
    }
    ctx2.restore();
  }

  function showOverlay(kind) {
    overlay.hidden = false;
    if (kind === 'gameover') {
      overlay.innerHTML =
        '<h1>摔车了</h1>' +
        '<p class="score">' + g.score.points + '</p>' +
        '<p>最高分 ' + g.best + '</p>' +
        '<p class="hint">R 重开 · 空格吐 · ↑跳 · ↓蹲</p>';
    } else {
      overlay.innerHTML =
        '<h1>鹈鹕骑士 · 喉囊弹匣</h1>' +
        '<p class="hint">嘴一直张着，碰到什么吞什么</p>' +
        '<p class="hint">↑/W 跳 · ↓/S 蹲 · 空格 吐</p>' +
        '<p class="hint">按任意方向键开始</p>';
    }
  }

  if (location.search.indexOf('test=1') !== -1) {
    var failed = results.filter(function (r) { return !r.ok; }).length;
    out.textContent = results.map(function (r) {
      return (r.ok ? 'PASS  ' : 'FAIL  ') + r.name + (r.ok ? '' : '  → ' + r.err);
    }).join('\n') + '\n\n' + (results.length - failed) + '/' + results.length + ' passed';
    out.hidden = false;
    overlay.hidden = true;
    return;
  }

  showOverlay('title');
  requestAnimationFrame(function (t) { last = t; requestAnimationFrame(frame); });
})();
/* ==== APP:END ==== */
```

配套的 HTML 骨架与样式（替换 Task 1 的临时骨架）：

**同时删掉 Task 1 里那段内联的 `?test=1` 渲染代码**——`APP` 块现在负责渲染测试结果，留着会重复执行。

```html
<body>
<canvas id="game"></canvas>
<div id="overlay"></div>
<pre id="out" hidden></pre>
<script>
/* … CORE / RENDER / TESTS / APP 四块依序放在这里 … */
</script>
</body>
```

```css
html, body {
  margin: 0; height: 100%; background: #0e1626; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
}
canvas { display: block; border-radius: 12px; box-shadow: 0 12px 48px rgba(0,0,0,.55); }
#overlay {
  position: fixed; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 10px;
  background: rgba(12,74,110,.55); color: #fff; text-align: center;
}
#overlay[hidden] { display: none; }
#overlay h1 { font-size: 40px; margin: 0; }
#overlay .score { font-size: 56px; font-weight: 700; margin: 0; }
#overlay .hint { opacity: .85; margin: 2px; }
#out {
  position: fixed; inset: 0; margin: 0; padding: 24px; overflow: auto;
  background: #0e1626; color: #d6e4f0; font: 14px/1.6 ui-monospace, Consolas, monospace;
}
#out[hidden] { display: none; }
```

- [ ] **Step 6: 跑测试确认全过**

Run: `cd /d/hermes/projects/pelican-bike && node tools/run-tests.mjs`
Expected: 96/96 passed，退出码 0。

- [ ] **Step 7: 逐条核对 spec 的验收标准**

双击 `projects/pelican-bike/index.html`，逐条确认并记录实际观察到的结果：

1. **双击能开玩，控制台无报错** —— 打开 DevTools Console，确认没有红色报错
2. **`?test=1` 全 PASS** —— 地址栏加 `?test=1`，确认页面显示 `96/96 passed`
3. **一局能跑到速度 2.5x** —— 撑满 90 秒，确认障碍明显变密变快
4. **喉囊满 6 格后不再吞入** —— 右上角 6 个圆点填满后，再碰到道具应直接飞过（变半透明）
5. **空格吐出的石头能砸碎高墙** —— 吞到石头，遇到高墙时按空格，墙应被砸掉且不掉命
6. **刷新后最高分仍在** —— 摔车后按 F5，确认「最高 xxx」还在

**任何一条没通过就不要提交**——回到对应任务修。

- [ ] **Step 8: 手感实机确认**

试玩至少 3 局，确认：

- 空格吐东西有后坐力和音效反馈
- 撞车有羽毛飞散、震屏、慢动作
- 车轮转速和实际速度看起来一致（加速时明显更快）
- 连击音高随连击递升，不刺耳

- [ ] **Step 9: 如实记录验证边界**

在 commit message 里写清验了什么、没验什么。自动化只能验逻辑与无报错；「好玩」是主观判断，只能由人确认。不要声称验证过没验证的东西。

- [ ] **Step 10: Commit**

```bash
cd /d/hermes
git add projects/pelican-bike/index.html
git commit -F - <<'EOF'
接线:输入映射、UI 屏幕、主循环与实机验收

主循环钳制 dt(切标签页回来不跳变),
localStorage 读写全程 try/catch 降级。

已验:82/82 断言通过、双击可玩、控制台无报错、
      六条验收标准逐条实机确认。
未验:主观「好玩」程度。

Co-Authored-By: Claude Code <noreply@anthropic.com>
EOF
```

---

## 交付后修正（整支审查发现，已改代码 + 补测试）

全部 13 个任务完成后做了一次独立整支审查，发现 3 个 Critical、3 个 Important。**下列修正只体现在代码与 ledger 里，本文件上面的代码块保留原样**——任务已全部完成，没有后续任务会再读它们。

| 位置 | 原计划 | 实际交付 | 为什么 |
|---|---|---|---|
| `updateGame` 垂直运动 | `g.vy -= GRAVITY*dt; g.height += g.vy*dt` | 梯形积分 `g.height += (vy+vyNext)/2*dt` | 半隐式欧拉在 dt=1/60 下跳跃峰值只有 131.8px，比 spec 的 138px 低 4.7%；梯形积分在匀加速下精确 |
| `updateGame` 落地分支 | 无条件 `g.float = 0` | 新增 `g.airborne`，只有真的从空中落下才重置浮空 | **Critical**：该分支每帧都跑，在地面吐泡泡的当帧就被清零，spec §4 的「泡泡浮空过墙」从地面根本用不出来 |
| `updateProjectiles` | 单点判定 `p.x` 是否落在障碍区间内 | 扫掠判定线段 `[prevX, p.x]` | **Critical**：dt 达上限时相对位移 (900+850)/30≈58px > 46px 的高墙，整步跨过；实测 1px 扫描漏 18% |
| `updateEntities` | `e.dead = true; crash(g)` 无条件执行 | `if (crash(g) \|\| g.dash > 0) e.dead = true` | **Critical**：spec §5 明说「无敌闪烁期间撞障碍不掉命，但障碍本身不消失」，原写法让每次撞车送的 1.5s 无敌变成免费推土机 |
| `createAudio.play` | 增益峰值写死 `0.25` | 用 `spec.gain` | Important：五条音效的 gain 是死数据，而测试还在断言它 ∈ (0,1]，读起来像有覆盖 |
| 主循环 | 直接吃变长 dt | `createStepper` 固定步长累加器（`FIXED_STEP=1/60`，`MAX_STEPS_PER_FRAME=4`） | Important：spec §11 要求固定步长；顺带让每步位移有界，物理与刷新率无关 |
| APP 音效 | 只播 jump/spit/dash/crash | 补上 `swallow` 与 `score` | Important：spec §8/§10 规定的两个音效从未被调用，吞——游戏的核心动词——是静音的 |

测试数从 83 涨到 96：新增 13 条（8 条复现审查发现，5 条覆盖修复后的行为）。

随后又按用户要求把两条搁置项提上来修了（测试 96 → 99）：

| 位置 | 问题 | 修法 |
|---|---|---|
| APP 主循环 + 新增 `togglePause` | 暂停没有任何视觉反馈，世界冻结但鹈鹕仍在浮动、无敌仍在闪，玩家分不清「暂停」和「卡死」 | 弹「暂停」遮罩；`step()` 在 paused 时整体早退，clock 与粒子都不推进；`togglePause` 只在 playing ⇄ paused 间切换 |
| APP 输入 | 按住 ↓ 时 Alt+Tab 切走再回来，ducking 永久卡住（收不到 keyup），速度停在 0.55x | 新增 `window` 的 `blur` 处理器释放蹲下 |

最后一批（测试 99 → 105）：

| 位置 | 问题 | 修法 |
|---|---|---|
| `drawEntities` | 被抛射物清掉的障碍当帧已 `dead`，但 `updateEntities` 之后才标记，于是多画一帧「尸体」 | 绘制前 `if (e.dead) continue`；补一条「存活实体照常绘制」防过度过滤 |
| APP 吐 + `drawProjectiles` | spec §8 要求吐有后坐力，实际只有粒子爆发，整车纹丝不动；且石头与鱼的拖影一样长，看不出穿透属性 | 新增 `recoilOffsetFor(timer)`（`RECOIL_DURATION=0.18`、`RECOIL_DISTANCE=14`），绘制鹈鹕时 `ctx.translate` 施加；石头拖影 34px、鱼 18px |
| APP 重开 + 新增 `commitBest` | 中途按 R 直接 `startRun`，本局分数被丢弃 —— 破的纪录只在摔车时才写盘 | 抽出纯函数 `commitBest(score, best, storage)`，`commitBestNow()` 在 gameover 与 restart 两处都调 |
| `run-tests.mjs` + HARNESS 块 | 浏览器与 node 各写一份语义相同的 harness，没有任何机制防止它们以后分叉 | 浏览器那份包进 `HARNESS:BEGIN/END` 哨兵块，`run-tests.mjs` 改为抽同一块；`makeStubCtx` 增加 `args` 数组记录实参 |

---

## 完成标准

全部 13 个任务完成后：

- `node tools/run-tests.mjs` 输出 105/105 passed，退出码 0
- 双击 `projects/pelican-bike/index.html` 可直接游玩
- spec 第 12 节的 6 条验收标准逐条通过
- `projects/pelican-bike/pelican-bike.html`（原插画）未被改动
- 仓库中只有两个新文件：`projects/pelican-bike/index.html`、`projects/pelican-bike/tools/run-tests.mjs`
