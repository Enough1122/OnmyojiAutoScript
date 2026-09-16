// ============================================================
// 减重时间线 · 前端逻辑 (与 index.html / weight_data.js 分离)
// 数据流: 健康/体重记录.csv → sync_visualization.py → weight_data.js
// ============================================================

// ===== 错误边界:weight_data.js 加载失败时显示提示,避免白屏 =====
if (typeof RAW === 'undefined' || typeof META === 'undefined') {
  var _errEl = document.getElementById('header-sub');
  if (_errEl) {
    _errEl.innerHTML = '⚠ 数据文件缺失或版本过旧 (weight_data.js)。请运行 sync_visualization.py 重新生成后刷新。';
  }
  throw new Error('weight_data.js 未加载或缺少 META,页面渲染中止');
}

// ===== 全局配置 (集中管理 magic numbers) =====
// 业务目标参数 (target160/145、milestone200/188、targetDate) 由
// weight_data.js 的 META 提供 (sync 脚本生成),下方 initConfig 覆盖默认值,
// 避免 index.html 与数据文件双份硬编码导致过期不同步。
var CONFIG = {
  startWeight: 244.0,        // 起点:历史最高 (4/17)
  startDate: '2026-04-17',
  targetDate: '2026-11-22',  // 预测目标日
  target160: 160.0,          // 过渡目标
  target145: 145.0,          // 终极目标
  milestone200: 200.2,       // 超越 2022-10-20
  milestone188: 188.0,       // 历史最低
  milestone175: 175.0,       // 中段关口 (188 → 160 之间补点)
  milestone150: 150.0,       // 准正常线 (75kg, BMI≈24.8;160 → 145 之间补点)
  heightM: 1.74,             // 身高 (米)
  ringCircumference: 314,    // 进度环周长 (2πr, r=50)
  injectionIntervalDays: 6,  // 替尔泊肽固定间隔 (天)
  strictWeekly: 4.0,         // 严格执行目标: -4 斤/周 (预测卡片执行率用)
  weeklyTarget: 4.0,         // 每周累计图的目标线 (斤/周);与 strictWeekly 统一口径 (-4 斤/周 = -0.57 斤/天)
  sprintDate: '2026-09-27',  // 160 冲刺 deadline (里程碑行 label 口径)
  bmiBands: [                // [下限, 分类],从上往下匹配
    [35, 'II级肥胖'], [30, 'I级肥胖'], [27, '超重'], [24, '偏胖'], [18.5, '正常'], [0, '偏瘦']
  ]
};
(function initConfig() {
  var map = {
    startWeight: 'startWeight', startDate: 'startDate', targetDate: 'targetDate',
    target160: 'target160', target145: 'target145',
    milestone200: 'milestone200', milestone188: 'milestone188',
    milestone175: 'milestone175', milestone150: 'milestone150'
  };
  Object.keys(map).forEach(function(k) {
    var v = META[map[k]];
    if (v !== undefined && v !== null && v !== '') CONFIG[k] = v;
  });
})();
// 注射间隔:从实际注射记录反推 (原硬编码 6 天,而文案里又写死"5 天节奏",
// 两处不一致且都会随用户调整节奏过期)。取最近 3 次间隔的中位数。
(function initInjectionInterval() {
  var inj = (typeof INJECTIONS_DATA !== 'undefined') ? INJECTIONS_DATA : [];
  if (inj.length < 3) return;
  var gaps = [];
  for (var i = Math.max(1, inj.length - 3); i < inj.length; i++) {
    gaps.push(Math.round((parseLocalDate(inj[i].date) - parseLocalDate(inj[i - 1].date)) / 86400000));
  }
  gaps.sort(function(a, b){ return a - b; });
  var med = gaps[Math.floor(gaps.length / 2)];
  if (med >= 3 && med <= 14) CONFIG.injectionIntervalDays = med;
})();

// 本地时区日期字符串 YYYY-MM-DD (toISOString 是 UTC,北京时间 0-8 点会差一天)
// 注:new Date('YYYY-MM-DD') 按 UTC 午夜解析,加 'T00:00:00' 强制本地解析
function parseLocalDate(s) { return new Date(s + 'T00:00:00'); }
function fmtLocalDate(d) {
  return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
}

// ===== 数据缓存:实测点只过滤一次,各图表/统计共用 (原代码过滤 8+ 次) =====
// 真实晨重点:排除 [插值]/[起点](非实测);REAL_NO_NOISE 额外排除 [噪音]
function isRealPoint(d, excludeNoise) {
  if (!d || d.morning === null) return false;
  var note = d.note || '';
  if (note.indexOf('[插值') !== -1 || note.indexOf('[起点') !== -1) return false;
  if (excludeNoise && note.indexOf('[噪音]') !== -1) return false;
  return true;
}
var REAL_POINTS = RAW.filter(function(d){ return isRealPoint(d, false); });
var REAL_NO_NOISE = RAW.filter(function(d){ return isRealPoint(d, true); });
// 注射序列:必须在这里就绪 —— 下方激励/下一关/反弹卡都要用,
// 原来声明在文件靠后处 (var 提升为 undefined),提前引用会抛 TypeError 被 try/catch 吞掉
var INJECTIONS = (typeof INJECTIONS_DATA !== 'undefined') ? INJECTIONS_DATA : [];

// 首次达到某体重的日期 (里程碑/徽章共用,保证各处口径一致)
// 起点行带 [起点] 标记被 REAL_POINTS 排除,但"达到起点体重"的日期就是起点日本身,
// 否则 244 徽章会显示成第一条实测日 (5/13),与 startDate 自相矛盾
function firstBreakDate(weight) {
  if (weight >= CONFIG.startWeight) return CONFIG.startDate;
  for (var i = 0; i < REAL_POINTS.length; i++) {
    if (REAL_POINTS[i].morning <= weight) return REAL_POINTS[i].date;
  }
  return null;
}

// canvas tooltip 不会自动换行 (Chart.js 只按 '\n' 拆行,单行原样绘制),
// 备注最长 300+ 字 → 单行宽 3000px+ 溢出画布。按 ' · ' 自然分段后再硬折行。
function wrapNoteLines(text, perLine, maxLines) {
  perLine = perLine || 26;
  maxLines = maxLines || 10;
  var out = [];
  String(text).split(' · ').forEach(function(seg) {
    seg = seg.trim();
    if (!seg) return;
    for (var i = 0; i < seg.length; i += perLine) out.push(seg.slice(i, i + perLine));
  });
  if (out.length > maxLines) { out = out.slice(0, maxLines); out[maxLines - 1] += '…'; }
  return out;
}

// ===== 备注文本渲染 =====
// CSV 备注含 markdown **加粗** 标记;表格是 HTML 可渲染,canvas tooltip 不行
function noteToHtml(note) {
  if (!note) return '';
  return String(note)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
}
function noteToText(note) {
  return note ? String(note).replace(/\*\*/g, '').replace(/\*([^*]+)\*/g, '$1') : '';
}

// MA7 (7 日均) 计算:按自然日窗口 (最新 7 个自然日内实测点平均)
// 输入为已过滤的实测点数组 → [{x: date, y: avg}]
function computeMA7(real) {
  var pts = [];
  for (var i = 0; i < real.length; i++) {
    var d = parseLocalDate(real[i].date);
    var win = [];
    for (var j = i; j >= 0; j--) {
      if ((d - parseLocalDate(real[j].date)) / 86400000 > 6) break;
      win.unshift(real[j].morning);
    }
    var avg = win.reduce(function(s, v){ return s + v; }, 0) / win.length;
    pts.push({x: real[i].date, y: parseFloat(avg.toFixed(2))});
  }
  return pts;
}

// ===== 标题日期范围动态化 (原来写死 '2026.4 → 2026.7',月份推进后会过期) =====
(function() {
  function monthLabel(d) { return d.slice(0, 7).replace('-', '.'); }
  var h1 = document.querySelector('header h1');
  if (h1 && RAW.length) {
    h1.textContent = '减重时间线 · ' + monthLabel(RAW[0].date) + ' → ' + monthLabel(RAW[RAW.length - 1].date);
    document.title = h1.textContent;
  }
  // 预测卡片标题 + 旅程尺标题:目标值/日期从 CONFIG 动态化 (原硬编码 '11/22'/'244 → 145')
  var md = CONFIG.targetDate.slice(5).replace('-', '/');
  document.querySelectorAll('#pred-cards-grid .card').forEach(function(c) {
    var id = c.getAttribute('data-card-id');
    if (id === 'pred-1122') {
      var lbl = c.querySelector('.label');
      if (lbl) lbl.textContent = '预测 ' + md;
    }
  });
  var rulerTitle = document.querySelector('.mile-ruler-title');
  if (rulerTitle) {
    rulerTitle.childNodes[0].textContent =
      '旅程刻度 · ' + CONFIG.startWeight.toFixed(0) + ' → ' + CONFIG.target145.toFixed(0) + ' · ';
  }
})();

// ===== 折叠/展开 (稳定 key 持久化:用 data-section-id,不用动态标题) =====
// 展开 section 时点亮其中的 .reveal 元素 (防 IO 失效时展开区空白)
function revealSection(section) {
  section.querySelectorAll('.reveal').forEach(function(t) { t.classList.add('in'); });
}
function toggleSection(header) {
  var section = header.parentElement;
  section.classList.toggle('collapsed');
  animateSectionBody(section);
  setAriaExpanded(section);
  saveCollapsedState();
  // 展开后该 section 内的图表兜底补建 + reveal 点亮 (图表渲染需可见高度,等动画结束)
  if (!section.classList.contains('collapsed')) {
    setTimeout(function() { revealSection(section); ensureCharts(section); }, 400);
  }
}

function setAriaExpanded(section) {
  var h = section.querySelector('.section-header');
  if (h) h.setAttribute('aria-expanded', section.classList.contains('collapsed') ? 'false' : 'true');
}

// 折叠/展开动画:先量实际高度再过渡,展开动画结束后解除 max-height 限制
function animateSectionBody(section) {
  var body = section.querySelector('.section-body');
  if (!body) return;
  var collapsed = section.classList.contains('collapsed');
  if (collapsed) {
    body.style.maxHeight = body.scrollHeight + 'px';  // 动画起点 = 当前实际高度
    requestAnimationFrame(function() {
      body.style.maxHeight = '0';
      body.style.opacity = '0';
    });
  } else {
    body.style.maxHeight = body.scrollHeight + 'px';  // 从 0 → 实际高度
    body.style.opacity = '1';
    setTimeout(function() {
      if (!section.classList.contains('collapsed')) body.style.maxHeight = 'none';  // 长内容不被裁切
    }, 350);
  }
}

// === 折叠状态持久化 (key = data-section-id,稳定不随数据变化) ===
var COLLAPSED_KEY = 'weightViz_collapsed_v2';
function sectionKey(s) {
  return s.getAttribute('data-section-id') || ('section-' + Array.prototype.indexOf.call(document.querySelectorAll('section'), s));
}
function saveCollapsedState() {
  try {
    var states = {};
    document.querySelectorAll('section').forEach(function(s) {
      states[sectionKey(s)] = s.classList.contains('collapsed');
    });
    localStorage.setItem(COLLAPSED_KEY, JSON.stringify(states));
  } catch(e) { /* localStorage 可能被禁用 */ }
}
function restoreCollapsedState() {
  try {
    var raw = localStorage.getItem(COLLAPSED_KEY);
    if (!raw) return false;
    var states = JSON.parse(raw);
    var applied = 0;
    document.querySelectorAll('section').forEach(function(s) {
      var k = sectionKey(s);
      if (states[k] === undefined) return;
      var body = s.querySelector('.section-body');
      if (states[k]) {
        s.classList.add('collapsed');
        if (body) { body.style.maxHeight = '0'; body.style.opacity = '0'; }
      } else {
        s.classList.remove('collapsed');
        if (body) { body.style.maxHeight = 'none'; body.style.opacity = '1'; }
      }
      setAriaExpanded(s);
      applied++;
    });
    return applied > 0;
  } catch(e) { return false; }
}

var allExpanded = false;
function toggleAllSections() {
  allExpanded = !allExpanded;
  document.querySelectorAll('section').forEach(function(s) {
    if (allExpanded) {
      s.classList.remove('collapsed');
      animateSectionBody(s);
    } else {
      s.classList.add('collapsed');
      animateSectionBody(s);
    }
    setAriaExpanded(s);
  });
  document.getElementById('expandAll').textContent = allExpanded ? '折叠全部' : '展开全部';
  saveCollapsedState();
  // 展开全部后:所有图表兜底补建 + 全部 reveal 点亮 (等展开动画结束,canvas 有实际高度)
  if (allExpanded) {
    setTimeout(function() {
      document.querySelectorAll('section').forEach(function(s) { revealSection(s); ensureCharts(s); });
    }, 400);
  }
}

// ===== 事件绑定 (替代原 inline onclick) =====
(function bindEvents() {
  document.querySelectorAll('.section-header').forEach(function(h) {
    h.addEventListener('click', function() { toggleSection(h); });
    h.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleSection(h); }
    });
  });
  document.getElementById('expandAll').addEventListener('click', toggleAllSections);
  // 恢复默认:统计卡 + 预测卡两个网格都清 (原来只清 summary,预测卡也能拖但无入口复位)
  document.getElementById('resetOrderBtn').addEventListener('click', function() { resetCardOrder('all'); });

  // 刷新数据:fetch 对比同步时间戳,只有数据真变了才整页刷新
  // (原 document.write cache busting 每次加载都强制重拉,且阻塞解析)
  var refreshBtn = document.getElementById('refreshBtn');
  refreshBtn.addEventListener('click', function() {
    var btn = this;
    btn.disabled = true;
    var sub = document.getElementById('header-sub');
    var subHtml = sub.innerHTML;  // 提示是临时的,不能把 W/日期/徽章整段吃掉
    fetch('weight_data.js?v=' + Date.now(), { cache: 'no-store' })
      .then(function(res) { return res.text(); })
      .then(function(text) {
        var m = text.match(/__SYNC_TIME__\s*=\s*'([^']+)'/);
        var newSync = m ? m[1] : '';
        if (newSync && newSync !== (window.__SYNC_TIME__ || '')) {
          // 带时间戳跳转:连 HTML/脚本缓存一起绕过 (location.reload 可能命中脚本缓存)
          location.href = location.pathname + '?v=' + Date.now();
          return;
        }
        sub.innerHTML = subHtml + ' <span class="badge badge-ok">✓ 已是最新</span>';
        setTimeout(function() { sub.innerHTML = subHtml; btn.disabled = false; }, 2000);
      })
      .catch(function() {
        location.href = location.pathname + '?v=' + Date.now();  // file:// 等 fetch 受限场景退回整页刷新
      });
  });
})();

// ===== 图表构建:加载即建 + 展开 section 时兜底 ensureCharts =====
// (历史:懒加载 IO 在折叠/后台场景白屏,8/17、8/22 两次实测踩坑;
//  数据量仅 ~110 点,构建开销可忽略,故放弃 IO 懒加载,改为统一立即构建)
var _chartJobs = {};
var _chartBuilt = {};
function lazyChart(id, builder) {
  _chartJobs[id] = builder;
  buildChart(id);
}
function buildChart(id) {
  if (!_chartJobs[id] || _chartBuilt[id]) return;
  var fn = _chartJobs[id];
  _chartJobs[id] = null;
  // 失败时不置 built,并把 job 放回去 —— 原实现先置 built 再执行,
  // 一次异常后 ensureCharts 永远跳过,该图表永久空白
  try {
    fn();
    _chartBuilt[id] = true;
  } catch (err) {
    console.error('[CHART_FAIL]', id, err && (err.stack || err.message || err));
    _chartJobs[id] = fn;
  }
}
// 展开 section 时兜底:若图表未建成(异常/新增场景)则补建;已建则跳过
function ensureCharts(section) {
  section.querySelectorAll('canvas[id]').forEach(function(c) { buildChart(c.id); });
}

// ===== 统计卡片 =====
(function computeStats() {
  var m = META;
  var today = fmtLocalDate(new Date());
  var isToday = m.currentDate === today;
  // 近 14 天实测窗口的起止日期
  function drop14Range(realArr) {
    var win = realArr.slice(-14);
    if (win.length < 2) return '';
    function md(s) { return parseInt(s.slice(5,7),10) + '/' + parseInt(s.slice(8,10),10); }
    return md(win[0].date) + ' → ' + md(win[win.length-1].date);
  }
  var dataBadge = isToday
    ? '<span class="badge badge-ok">✓ 当日数据</span>'
    : '<span class="badge badge-warn">⚠ 最新 ' + m.currentDate + ' (今天 ' + today + ')</span>';
  var syncTime = window.__SYNC_TIME__ || 'unknown';
  var syncBadge = '<span class="badge badge-muted">同步 ' + syncTime.slice(11) + '</span>';
  document.getElementById('header-sub').innerHTML =
    'Hermes Agent · W' + (weeklyData.length > 0 ? weeklyData[weeklyData.length-1].week.replace('W','') : '?') +
    ' · ' + m.currentDate + ' · ' + REAL_POINTS.length + ' 条实测晨重 / ' + RAW.length +
    ' 天记录 · ' + dataBadge + ' ' + syncBadge;

  document.getElementById('stat-current').innerHTML =
    (+m.currentWeight).toFixed(1) + ' <span class="unit">斤</span>';
  // 较前日 (META 主路径)
  if (REAL_POINTS.length >= 2) {
    var curP = REAL_POINTS[REAL_POINTS.length - 1];
    var prevP = REAL_POINTS[REAL_POINTS.length - 2];
    var dd = curP.morning - prevP.morning;
    var deltaEl = document.getElementById('stat-current-delta');
    deltaEl.textContent = '较 ' + prevP.date + ' ' + (dd > 0 ? '+' : '') + dd.toFixed(1) + ' 斤';
    deltaEl.className = dd > 0 ? 'delta neg' : dd < 0 ? 'delta' : 'delta muted';
    // hero 数字涨跌动效 (下降=绿,反弹=红,持平=中性)
    var heroVal = document.getElementById('stat-current');
    heroVal.classList.remove('down', 'up', 'flat');
    heroVal.classList.add(dd > 0 ? 'up' : dd < 0 ? 'down' : 'flat');
  }
  document.getElementById('stat-total').innerHTML =
    '-' + (+m.totalDelta).toFixed(1) + ' <span class="unit">斤</span>';
  document.getElementById('stat-total-meta').textContent =
    '较 ' + m.startDate + ' ' + (+m.startWeight).toFixed(1) + ' · ' + m.days + ' 天 · 平均 ' + m.avgWeekly + ' 斤/周';

  if (weeklyData.length) {
    var wk = weeklyData[weeklyData.length - 1];
    document.getElementById('stat-week-num').textContent = wk.week.replace('W', '');
    // 涨跌着色 (规则:掉秤=冷色 lime,反弹/周涨=暖色玫红)
    var wkColor = wk.delta < 0 ? 'var(--accent)' : wk.delta > 0 ? 'var(--up)' : 'var(--muted)';
    document.getElementById('stat-week').innerHTML =
      '<span style="color:' + wkColor + '">' + (wk.delta > 0 ? '+' : '') + wk.delta.toFixed(1) +
      '</span> <span class="unit">斤</span>' + (wk.inProgress ? ' ⏳' : '');
    document.getElementById('stat-week-meta').textContent =
      wk.label + (wk.inProgress ? ' · 进行中' : '');

    // 距本周目标
    if (wk.target != null) {
      var remain = m.currentWeight - wk.target;
      document.getElementById('stat-week-target').innerHTML = remain > 0
        ? remain.toFixed(1) + ' <span class="unit">斤</span>'
        : '✓ 超 ' + Math.abs(remain).toFixed(1) + ' <span class="unit">斤</span>';
      document.getElementById('stat-week-target-meta').textContent =
        'W' + wk.week.replace('W', '') + ' 目标 ' + wk.target.toFixed(1) + ' 斤';
      document.getElementById('stat-week-target-card').style.display = '';
    } else {
      document.getElementById('stat-week-target-card').style.display = 'none';
    }
  }

  if (m.ma7 != null) {
    document.getElementById('stat-ma7').innerHTML =
      (+m.ma7).toFixed(1) + ' <span class="unit">斤</span>';
    // 晨重 vs MA7 偏离:判断当天是虚高还是真新低 (超均线 = 水分概率大)
    var ma7Dev = m.currentWeight - m.ma7;
    var ma7Meta = ma7Dev >= 0.4 ? '晨重超均线 +' + ma7Dev.toFixed(1) + ' · 虚高,回落概率大'
      : ma7Dev <= -0.4 ? '晨重低均线 ' + ma7Dev.toFixed(1) + ' · 真新低成色足'
      : '晨重贴均线 (' + (ma7Dev >= 0 ? '+' : '') + ma7Dev.toFixed(1) + ') · 趋势内';
    document.getElementById('stat-ma7-meta').textContent = ma7Meta;
  } else {
    // 无 null 门时 (+null).toFixed(1) 渲染 "0.0 斤"、偏离算出 +194.1 (2026-09-16 修)
    document.getElementById('stat-ma7').textContent = '数据不足';
    document.getElementById('stat-ma7-meta').textContent = '需要 ≥7 天实测';
  }

  if (m.dailyDrop14d != null) {
    var d14 = m.dailyDrop14d;
    var sign14 = d14 > 0 ? '-' : d14 < 0 ? '+' : '±';
    var color14 = d14 > 0 ? 'var(--accent)' : d14 < 0 ? 'var(--up)' : 'var(--muted)';
    document.getElementById('stat-drop14').innerHTML =
      '<span style="color:' + color14 + '">' + sign14 + Math.abs(d14).toFixed(2) +
      '</span> <span class="unit">斤/天</span>';
    // meta:MA14 + 窗口 + 晚晨差 (晚-晨 = 当天食物水钠的镜子)
    var gapSum = 0, gapN = 0;
    REAL_POINTS.slice(-14).forEach(function(d) {
      if (d.evening !== null && d.morning !== null) { gapSum += d.evening - d.morning; gapN++; }
    });
    var gapTxt = gapN > 0 ? ' 斤 · 晚晨差' + (gapSum / gapN >= 0 ? '+' : '') + (gapSum / gapN).toFixed(1) : ' 斤';
    document.getElementById('stat-drop14-meta').textContent =
      'MA14 ' + (+m.ma14).toFixed(1) + gapTxt + ' · ' + drop14Range(REAL_POINTS);
  } else {
    document.getElementById('stat-drop14').textContent = '数据不足';
    document.getElementById('stat-drop14-meta').textContent = '需要 ≥14 天实测';
  }

  // streak=0 时不该用 🔥 (火焰=连胜势头),换成中性图标
  document.getElementById('stat-streak').innerHTML = (m.streak > 0 ? '🔥 ' : '⏸ ') + m.streak;
  document.getElementById('stat-streak-meta').textContent =
    m.streak >= 3 ? '势头不错' : m.streak >= 1 ? '微跌' : '持平 / 反弹';

  var targets = [{id:'stat-160',target:CONFIG.target160}, {id:'stat-145',target:CONFIG.target145}];
  targets.forEach(function(t) {
    var remain = m.currentWeight - t.target;
    // 达成后原来显示 "✓ 2.0 斤",读起来像"还差 2 斤" → 明确写成"已超"
    document.getElementById(t.id).innerHTML = remain > 0
      ? remain.toFixed(1) + ' <span class="unit">斤</span>'
      : '✓ 超 ' + Math.abs(remain).toFixed(1) + ' <span class="unit">斤</span>';
  });

  // BMI (+ 距超重线 28 还差几斤:84.8kg = 169.7 斤,比 175 更早能摘掉的医学帽子)
  // 分级着色 (规则:达标=冷,需改善=暖):<24 lime → 24-27 偏胖黄 → 27-30 橙 → ≥30 肥胖玫红
  var height = CONFIG.heightM;
  var weightKg = m.currentWeight / 2;
  var bmi = (weightKg / (height * height)).toFixed(1);
  var bmiColor = bmi >= 30 ? 'var(--up)' : bmi >= 27 ? '#fb923c' : bmi >= 24 ? '#fbbf24' : bmi >= 18.5 ? 'var(--accent)' : 'var(--info)';
  document.getElementById('stat-bmi').innerHTML =
    '<span style="color:' + bmiColor + '">' + bmi + '</span>';
  var bmiCat = '—';
  for (var bi = 0; bi < CONFIG.bmiBands.length; bi++) {
    if (bmi >= CONFIG.bmiBands[bi][0]) { bmiCat = CONFIG.bmiBands[bi][1]; break; }
  }
  var jinTo28 = (weightKg - 28 * height * height) * 2;
  document.getElementById('stat-bmi-category').textContent =
    jinTo28 > 0 ? bmiCat + ' · 距超重线28还差 ' + jinTo28.toFixed(1) + ' 斤'
                : bmiCat + ' · 已入超重以内 ✓';

  // ===== 6 张新卡片 =====

  // 距下次注射: 以真实今天为准，已过期则不展示静态“5天间隔”避免误导
  var injData = (typeof INJECTIONS_DATA !== 'undefined') ? INJECTIONS_DATA : [];
  var lastInj = injData.length ? injData[injData.length - 1] : null;
  if (lastInj) {
    var injDate = parseLocalDate(lastInj.date);
    var nextInj = new Date(injDate.getTime() + CONFIG.injectionIntervalDays * 86400000);
    // 用真实今天而非 META.currentDate，避免数据晚一天时显示滞后
    var todayD = parseLocalDate(fmtLocalDate(new Date()));
    var daysLeft = Math.round((nextInj - todayD) / 86400000);
    var sinceLast = Math.round((todayD - injDate) / 86400000);
    var injColor = daysLeft <= 0 ? 'var(--up)' : daysLeft <= 1 ? '#fbbf24' : 'var(--accent)';
    var title;
    if (daysLeft < 0) title = '已过期 ' + Math.abs(daysLeft) + '天';
    else if (daysLeft === 0) title = '今天';
    else if (daysLeft === 1) title = '明天';
    else title = daysLeft + '天后';
    document.getElementById('stat-next-injection').innerHTML =
      '<span style="color:' + injColor + '">' + title + '</span>';
    var nextDateStr = fmtLocalDate(nextInj);
    var meta = lastInj.dose + 'mg · 上次 ' + lastInj.date + ' (' + sinceLast + '天前) · 下次 ' + nextDateStr;
    if (daysLeft < 0) meta += ' · 已过' + Math.abs(daysLeft) + '天';
    document.getElementById('stat-next-injection-meta').textContent = meta;
  } else {
    // 无注射记录时原来两行都停在 '—',卡片像加载失败
    document.getElementById('stat-next-injection').textContent = '无记录';
    document.getElementById('stat-next-injection-meta').textContent = '未解析到注射记录 (替尔泊肽-注射记录.md)';
  }

  // 总进度%: (起点 - 当前) / (起点 - 终极目标) × 100
  var totalProgress = ((CONFIG.startWeight - m.currentWeight) / (CONFIG.startWeight - CONFIG.target145) * 100);
  var progClamped = Math.max(0, Math.min(100, totalProgress));
  var progColor = progClamped >= 50 ? 'var(--ok)' : progClamped >= 25 ? '#fbbf24' : '#fb7185';
  document.getElementById('stat-progress').innerHTML =
    '<span style="color:' + progColor + '">' + progClamped.toFixed(1) + '</span>' +
    ' <span class="unit">%</span>';
  document.getElementById('stat-progress-meta').textContent =
    CONFIG.startWeight + ' → ' + CONFIG.target145 + ' · 已减 ' + (CONFIG.startWeight - m.currentWeight).toFixed(1) +
    ' / ' + (CONFIG.startWeight - CONFIG.target145) + ' 斤';

  // 本月减重
  if (m.monthlyDelta != null) {
    var mDelta = m.monthlyDelta;
    var mColor = mDelta > 0 ? 'var(--accent)' : mDelta < 0 ? 'var(--up)' : 'var(--muted)';
    var mSign = mDelta > 0 ? '-' : mDelta < 0 ? '+' : '±';
    document.getElementById('stat-monthly').innerHTML =
      '<span style="color:' + mColor + '">' + mSign + Math.abs(mDelta).toFixed(1) +
      '</span> <span class="unit">斤</span>';
    document.getElementById('stat-monthly-meta').textContent =
      m.currentDate.slice(0, 7) + ' 月内';
  } else {
    document.getElementById('stat-monthly').textContent = '—';
    document.getElementById('stat-monthly-meta').textContent = '数据不足';
  }

  // 最佳单周
  if (m.bestWeekDelta != null) {
    var bwColor = m.bestWeekDelta < 0 ? 'var(--ok)' : 'var(--up)';
    document.getElementById('stat-best-week').innerHTML =
      '<span style="color:' + bwColor + '">' + m.bestWeekDelta.toFixed(1) +
      '</span> <span class="unit">斤</span>';
    document.getElementById('stat-best-week-meta').textContent =
      m.bestWeekLabel + ' · 纪录';
  }

  // 反弹恢复力
  if (m.recoveryMedian != null) {
    document.getElementById('stat-recovery').innerHTML =
      m.recoveryMedian + ' <span class="unit">天</span>';
    document.getElementById('stat-recovery-meta').textContent =
      m.recoveryCount + ' 次反弹后重回新低' + (m.reboundTotal ? ' / 共 ' + m.reboundTotal + ' 次反弹' : '') + ' · 中位天数';
  } else {
    document.getElementById('stat-recovery').textContent = '—';
    document.getElementById('stat-recovery-meta').textContent = '数据不足';
  }

  // 进度环 (追踪未完成里程碑; ring-200 已于 8/9 破 200 后退役,
  // 成就在里程碑行/徽章墙保留)
  var peakH = m.peakWeightHistorical || m.peakWeight;
  setRing('ring-188', CONFIG.milestone188, m.currentWeight, peakH);
  setRing('ring-175', CONFIG.milestone175, m.currentWeight, peakH);
  setRing('ring-160', CONFIG.target160, m.currentWeight, peakH);
  setRing('ring-150', CONFIG.milestone150, m.currentWeight, peakH);
  setRing('ring-145', CONFIG.target145, m.currentWeight, peakH);

  // 里程碑进度条
  setMileBar('mile-200', CONFIG.milestone200, m.currentWeight, peakH);
  setMileBar('mile-188', CONFIG.milestone188, m.currentWeight, peakH);
  setMileBar('mile-175', CONFIG.milestone175, m.currentWeight, peakH);
  setMileBar('mile-160', CONFIG.target160, m.currentWeight, peakH);
  setMileBar('mile-150', CONFIG.milestone150, m.currentWeight, peakH);
  setMileBar('mile-145', CONFIG.target145, m.currentWeight, peakH);

  // 里程碑行状态 (dot/status) 随数据动态化
  updateMilestoneRows(m.currentWeight);

  var avgWk = m.avgWeekly;                                // 整体均速 (斤/周,自 4/17 起)
  var paceWk = (parseFloat(m.dailyDrop14d) || 0) * 7;     // 近 14 天节奏 (斤/周)
  // 里程碑详情:达到目标后不再显示"还差 X 斤"
  // ⚠️ 原文案写"按当前节奏",用的却是整体均速 2.38 斤/周;近 14 天实际只有 0.56 斤/周,
  //    距 188 会给出"约 5 周"而真实节奏要 19 周 —— 两个口径都给出来,不再混淆
  var mileText = function(goal) {
    var diff = m.currentWeight - goal;
    if (diff <= 0) return '✅ 已达成 · 低于 ' + goal.toFixed(1) + ' 斤';
    var txt = '距今 ' + diff.toFixed(1) + ' 斤 · 按均速 ' + avgWk + ' 斤/周 ≈ ' + Math.ceil(diff / avgWk) + ' 周';
    if (paceWk > 0.05) txt += ' · 按近14天 ' + paceWk.toFixed(1) + ' 斤/周 ≈ ' + Math.ceil(diff / paceWk) + ' 周';
    return txt;
  };
  document.getElementById('mile-200-detail').textContent = mileText(CONFIG.milestone200);
  document.getElementById('mile-188-detail').textContent = mileText(CONFIG.milestone188);
  document.getElementById('mile-175-detail').textContent = mileText(CONFIG.milestone175);
  document.getElementById('mile-160-detail').textContent = mileText(CONFIG.target160);
  document.getElementById('mile-150-detail').textContent = mileText(CONFIG.milestone150);
  document.getElementById('mile-145-detail').textContent = mileText(CONFIG.target145);
  // 早期已破里程碑:首破日由数据算,不再硬编码 (原 HTML 写死 "7/13 破 226",
  // 实测首次 ≤226.1 是 6/8 的 225.0,与徽章墙显示的日期互相矛盾)
  [[226.1, 'mile-226-detail'], [212.5, 'mile-212-detail'], [210.0, 'mile-210-detail']].forEach(function(p) {
    var el = document.getElementById(p[1]);
    if (!el) return;
    var d = firstBreakDate(p[0]);
    if (!d) { el.textContent = '待突破'; return; }
    var rec = null;
    for (var i = 0; i < REAL_POINTS.length; i++) if (REAL_POINTS[i].date === d) { rec = REAL_POINTS[i]; break; }
    el.textContent = '✅ 已突破 · ' + d.slice(5).replace('-', '/') + (rec ? ' (' + rec.morning.toFixed(1) + ')' : '');
  });

  // ===== 预测卡片 (实时按近 14 天日均减重推算) =====
  // dailyDrop14d 在实测 <14 条时为 null → parseFloat(null)=NaN 会显示 "NaN 斤",|| 0 兜底
  // (computePrediction 内 dailyDrop<=0 分支会显示"无法达成",语义衔接)
  computePrediction(parseFloat(m.currentWeight), parseFloat(m.dailyDrop14d) || 0);
})();

// ===== 激励升级 · 每日激励/英雄/等效/下一关/成就墙/特效 =====
// 打字机:激励主文案逐字入场 (仅纯文本元素可用;reduced-motion/移动端直接写入)
function typewriter(el, text) {
  if (!el) return;
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var narrow = window.matchMedia && window.matchMedia('(max-width: 768px)').matches;
  if (reduced || narrow) { el.textContent = text; return; }
  el.textContent = '';
  el.classList.add('typing');
  var i = 0;
  var timer = setInterval(function() {
    i++;
    el.textContent = text.slice(0, i);
    if (i >= text.length) {
      clearInterval(timer);
      setTimeout(function() { el.classList.remove('typing'); }, 1500);  // 光标停留 1.5s 再隐去
    }
  }, 26);
}
(function upgradeMotivation(){
  // --- helpers ---
  var BOOST_TTL = 15000;  // 每次打开展示 15s 后自动收起
  // 关闭每日激励条:manual=true 由 × 触发,3 天内不再出现 (key 存时间戳);
  // 自动收起只针对当前视图 —— 消息生命周期 3 天,期间每次打开都会展示 15s
  function hideBoost(manual) {
    var el = document.getElementById('daily-boost');
    if (!el || el.style.display === 'none') return;
    if (el._autoHide) { clearTimeout(el._autoHide); el._autoHide = null; }
    var finish = function() {
      el.style.display = 'none';
      el.classList.remove('closing');
      el.classList.remove('entering');
      if (manual) { try { localStorage.setItem('weightViz_boost_hidden_until', String(Date.now() + 3 * 86400000)); } catch(e) {} }
    };
    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) { finish(); return; }
    el.classList.add('closing');
    setTimeout(finish, 320);
  }
  // 15s 倒计时:底部进度线走到头自动收起;hover 暂停 (时间按 Date 差值计,恢复时从定格处继续)
  function boostCountdown(el) {
    var bar = el.querySelector('.boost-ttl');
    function arm(ms, fresh) {
      clearTimeout(el._autoHide);
      el._boostDur = ms;
      el._boostStart = Date.now();
      el._autoHide = setTimeout(function() { hideBoost(false); }, ms);
      if (bar) {
        if (fresh) {
          bar.style.transition = 'none';
          bar.style.transform = 'scaleX(1)';
          void bar.offsetWidth;  // 重置到满格
        }
        bar.style.transition = 'transform ' + ms + 'ms linear';
        bar.style.transform = 'scaleX(0)';
      }
    }
    el._boostPause = function() {
      if (!el._autoHide) return;
      el._boostRemain = Math.max(0, el._boostDur - (Date.now() - el._boostStart));
      clearTimeout(el._autoHide); el._autoHide = null;
      if (bar) {
        var tf = getComputedStyle(bar).transform;
        if (tf && tf !== 'none') { bar.style.transition = 'none'; bar.style.transform = tf; }  // 定格进度
      }
    };
    el._boostResume = function() {
      if (el._autoHide || el._boostRemain == null) return;
      var remain = el._boostRemain; el._boostRemain = null;
      arm(remain, false);  // 从定格处走完剩余
    };
    arm(BOOST_TTL, true);
  }
  // <200 连胜双口径:days=日历天(缺秤日不缩水,"守住 N 天"文案用);
  // recs=当前 <200 段的实测条数(破关庆祝"第 N 天"与 ≤7/≤14 闸门用,
  // 断秤后首条实测=第 1 条,庆祝不因断秤跳票 —— 庆祝这件事上旧记录数口径才是对的)
  // 走 REAL_NO_NOISE:[噪音] 误读 ≥200 不该清零连胜 (recentRate 同口径)
  function below200Stats(){
    var pts = REAL_NO_NOISE;
    var n = pts.length;
    if (!n) return { days: 0, recs: 0 };
    var last = pts[n - 1], anchor = null, recs = 0;
    for (var i = n - 1; i >= 0; i--) {
      if (pts[i].morning >= 200) { anchor = pts[i]; break; }
      recs++;
    }
    // 兜底:整段数据都在 <200 (起点行被剔除) → 锚第一条实测,而非 244 的起点日
    var base = anchor ? anchor.date : pts[0].date;
    return { days: Math.max(0, Math.round((parseLocalDate(last.date) - parseLocalDate(base)) / 86400000)), recs: recs };
  }
  var curW = parseFloat(META.currentWeight);
  var prevW = REAL_POINTS.length>=2 ? REAL_POINTS[REAL_POINTS.length-2].morning : null;
  var delta = (prevW!==null) ? parseFloat((curW - prevW).toFixed(1)) : 0;
  var streak = META.streak;
  var dailyDrop = parseFloat(META.dailyDrop14d) || 0;
  var _b200 = below200Stats();
  var belowDays = _b200.days;   // 日历天:"守住/已守住 N 天"文案
  var belowRecs = _b200.recs;   // 记录条数:庆祝"第 N 天"与庆祝闸门
  var isBelow200 = curW < 200;

  // --- 1. 每日激励条 ---
  try{
    var boostEl = document.getElementById('daily-boost');
    var mainEl = document.getElementById('boost-main');
    var subEl = document.getElementById('boost-sub');
    var iconEl = document.getElementById('boost-icon');
    var flameEl = document.getElementById('boost-flame');
    if(boostEl && mainEl){
      var main='', sub='', icon='💪', cls='';
      if(delta < 0){
        var abs = Math.abs(delta).toFixed(1);
        if(delta <= -1.0){
          main = '大胜！-'+abs+'斤，今天的你超厉害 🔥';
          // 无注射记录时不吹"N 天节奏"(CONFIG 里那是默认值,不是真实节律)
          sub = (INJECTIONS.length>=2 ? CONFIG.injectionIntervalDays+' 天节奏' : '节奏稳住')
              + (belowDays>1?' · 已守住<200 '+belowDays+'天':'')+' · 明天继续稳住';
          icon='🔥'; cls='boost-down';
        } else {
          main = '稳步下降 -'+abs+'斤，节奏很稳';
          sub = 'MA7 '+(META.ma7!=null?META.ma7.toFixed(1)+'斤':'数据不足')+(isBelow200?' · <200 区间保持':'')+' · 继续加油';
          icon='🍃'; cls='';
        }
        if(flameEl){ flameEl.textContent='🔥'; flameEl.className='boost-flame on'; }
      } else if(delta > 0){
        if(isBelow200){
          main = '稳住就是胜利！+'+delta.toFixed(1)+'只是水分/未排空';
          sub = '仍在 <200 区间 · 已守住 '+belowDays+'天 · 多喝水+排空明天就回落 💧';
          icon='🛡️'; cls='boost-flat';
          if(flameEl){ flameEl.textContent='🛡️'; flameEl.className='boost-flame'; }
        } else if(delta <= 0.5){
          main = '小幅波动 +'+delta.toFixed(1)+'斤，别慌';
          sub = '距 200 仅 '+ (curW-200).toFixed(1)+'斤 · 水分/钠/睡眠影响，明天验证';
          icon='🌊'; cls='boost-flat';
        } else {
          main = '反弹 +'+delta.toFixed(1)+'斤？别焦虑，是身体在调水';
          sub = '回顾 '+(META.bestWeekLabel||'最佳周')+' 曾 '+(META.bestWeekDelta!=null?Number(META.bestWeekDelta).toFixed(1):'-4.6')+'斤/周，反弹后必有连跌 · 今天多喝水、早点睡';
          icon='💧'; cls='boost-up';
        }
      } else {
        main = '持平的一天，也是胜利的一天';
        sub = (isBelow200?'稳居 <200 · 守住 '+belowDays+'天':'距 200 仅 '+(curW-200).toFixed(1)+'斤')+' · 节奏 '+dailyDrop.toFixed(2)+'斤/天';
        icon='⚖️'; cls='boost-flat';
      }
      // 特殊：<200 区间初期 · 状态播报(用户指示:破200已是旧闻,不再用庆祝口吻)
      if(isBelow200 && belowRecs>=1 && belowRecs<=7){
        main = '💪 '+curW.toFixed(1)+' 斤 · 稳居 <200 第 '+belowRecs+' 天';
        // 已入 195 内时 (curW<195) 原文案会渲染 "距 195 还差 -0.9 斤" (2026-09-16 修)
        var d195 = curW - 195;
        sub = '累计 -'+META.totalDelta.toFixed(1)+' 斤 · '+(d195 > 0 ? '距 195 还差 '+d195.toFixed(1)+' 斤' : '✓ 已破 195 关口');
        icon='💪'; cls='';
        if(flameEl){ flameEl.textContent='✨'; flameEl.className='boost-flame on'; }
      }
      // 展示策略:消息挂 3 天,期间每次打开 15s 自动收起;× 主动关闭 → 3 天内不再出现;
      // 数据超过 3 天没更新 (META.currentDate 距今 >3 天) → 消息过期退役,不展示旧文案
      var hiddenUntil = 0;
      try { hiddenUntil = parseInt(localStorage.getItem('weightViz_boost_hidden_until') || '0', 10) || 0; } catch(e) {}
      var msgAgeDays = Math.round((parseLocalDate(fmtLocalDate(new Date())) - parseLocalDate(META.currentDate)) / 86400000);
      if (hiddenUntil > Date.now() || msgAgeDays > 3) {
        boostEl.style.display = 'none';
      } else {
        typewriter(mainEl, main);  // 主文案打字机入场 (sub 直接写入,避免双动画抢戏)
        subEl.textContent = sub;
        iconEl.textContent = icon;
        boostEl.className = 'daily-boost ' + cls;
        boostEl.style.display = '';
        // 表现增强:入场动画 + 15s 倒计时进度条 (hover 暂停,离开继续)
        var reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        if (!reducedMotion) {
          boostEl.classList.add('entering');
          setTimeout(function() { boostEl.classList.remove('entering'); }, 500);
        }
        boostCountdown(boostEl);
        boostEl.addEventListener('mouseenter', function() { boostEl._boostPause && boostEl._boostPause(); });
        boostEl.addEventListener('mouseleave', function() { boostEl._boostResume && boostEl._boostResume(); });
        var closeBtn = document.getElementById('boost-close');
        if (closeBtn) closeBtn.addEventListener('click', function() { hideBoost(true); });
      }
    }
  }catch(e){ console.warn('boost',e); }

  // --- 2. 英雄庆祝横幅 ---
  try{
    var hero = document.getElementById('hero-milestone');
    var heroBadge = document.getElementById('hero-badge');
    var heroTitle = document.getElementById('hero-title');
    var heroSub = document.getElementById('hero-sub');
    var heroStats = document.getElementById('hero-stats');
    var heroFill = document.getElementById('hero-progress-fill');
    var heroLabel = document.getElementById('hero-progress-label');
    if(hero && isBelow200 && belowRecs>=1 && belowRecs<=14){
      var breakDate = firstBreakDate(200.2) || firstBreakDate(200);
      var span = CONFIG.startWeight - CONFIG.target145;
      var pct = ((CONFIG.startWeight - curW)/span*100);
      heroBadge.textContent = '🎉 破 200 大关 · '+(breakDate?breakDate.slice(5).replace('-','/')+' 突破':'已达成');
      heroTitle.innerHTML = curW.toFixed(1)+' <span class="unit">斤</span> · 稳居 <200 第 '+belowRecs+' 天';
      heroSub.textContent = '超越 2022-10-20 的 200.2 · 3 年来最轻 · 累计 -'+META.totalDelta.toFixed(1)+'斤';
      heroStats.innerHTML = '<span class="hero-stat">已走 <b>'+pct.toFixed(1)+'%</b> 旅程</span><span class="hero-stat">平均 <b>'+META.avgWeekly+'斤/周</b></span><span class="hero-stat">最佳周 <b>'+(META.bestWeekDelta!=null?Number(META.bestWeekDelta).toFixed(1):'—')+'斤</b>('+(META.bestWeekLabel||'—')+')</span>';
      heroLabel.textContent = '244 → 145 全程已走 '+pct.toFixed(1)+'% · 距 160 还有 '+(curW-160).toFixed(1)+'斤';
      setTimeout(function(){ if(heroFill) heroFill.style.width = Math.min(100,pct).toFixed(1)+'%'; }, 200);
      hero.style.display = '';
      // confetti canvas
      (function(){
        var c = document.getElementById('hero-confetti');
        if(!c || !c.getContext) return;
        var ctx=c.getContext('2d'), W,H, parts=[];
        function resize(){ W=c.width=c.offsetWidth*2; H=c.height=c.offsetHeight*2; }
        resize(); window.addEventListener('resize', resize);
        var colors=['#fbbf24','#a3e635','#7dd3fc','#c4b5fd','#f472b6','#fde68a'];
        for(var i=0;i<42;i++){
          parts.push({x:Math.random()*W, y:Math.random()*H*0.6 - H*0.3, vx:(Math.random()-0.5)*3, vy:Math.random()*2+1.2, r:2+Math.random()*3.5, c:colors[i%colors.length], rot:Math.random()*360, vr:(Math.random()-0.5)*6});
        }
        var t=0, running=true;
        function frame(){
          if(!running || !document.body.contains(c)) return;
          t++;
          ctx.clearRect(0,0,W,H);
          parts.forEach(function(p){
            p.x+=p.vx; p.y+=p.vy; p.vy+=0.04; p.rot+=p.vr;
            if(p.y>H+20){ p.y=-10; p.x=Math.random()*W; p.vy=Math.random()*2+1.2; }
            ctx.save(); ctx.translate(p.x,p.y); ctx.rotate(p.rot*Math.PI/180);
            ctx.fillStyle=p.c; ctx.globalAlpha=0.9;
            ctx.fillRect(-p.r,-p.r/2,p.r*2,p.r);
            ctx.restore();
          });
          if(t< 420) requestAnimationFrame(frame); else running=false;
        }
        if(!window.matchMedia || !window.matchMedia('(prefers-reduced-motion: reduce)').matches) requestAnimationFrame(frame);
      })();
      var closeBtn=document.getElementById('hero-close');
      if(closeBtn) closeBtn.addEventListener('click', function(){ hero.style.display='none'; try{localStorage.setItem('hero200_dismissed', META.currentDate);}catch(e){} });
      try{ if(localStorage.getItem('hero200_dismissed')===META.currentDate) hero.style.display='none'; }catch(e){}
    }
  }catch(e){ console.warn('hero',e); }

  // --- 3. 等效成就条 ---
  try{
    var eqTrack=document.getElementById('eq-track');
    if(eqTrack){
      var totalJin = META.totalDelta;
      var kg = totalJin / 2;
      // ⚠️ 7700 kcal/kg 是**纯脂肪**系数,而 totalDelta 是总减重(含水分/瘦体重),
      //    所以这里算出来的是缺口**上限**,文案必须说清,不能写成"纯脂肪已甩掉"
      var kcal = kg * 7700;
      var riceBowls = Math.round(kcal / 200);               // 一碗白饭 ≈ 200 kcal
      var cokeCans = Math.round(kcal / 139);                // 330ml 可乐 ≈ 139 kcal
      // 慢跑 ≈ 7 METs,消耗随体重走:原来写死 300 kcal/h(约等于走路),小时数虚高 2 倍多
      var kcalPerHour = 7 * (parseFloat(META.currentWeight) / 2);
      var runHours = Math.round(kcal / kcalPerHour);
      var eggs = Math.round(kcal / 70);                     // 一枚鸡蛋 ≈ 70 kcal (原写 140,枚数少算一半)
      // label 只说明口径,不复读数值 (原来 "989 碗"+"约 989 碗米饭" 数字重复两遍)
      var equ=[
        {icon:'⚖️', val:totalJin.toFixed(1)+' 斤', label:'总减重 (含水分)'},
        {icon:'🔥', val:(kcal/10000).toFixed(1)+'万 kcal', label:'热量缺口 (纯脂肪上限)'},
        {icon:'🍚', val:riceBowls+' 碗', label:'一碗 200kcal 白饭 · 上限折算'},
        {icon:'🥤', val:cokeCans+' 罐', label:'一罐 139kcal 可乐 · 上限折算'},
        {icon:'🏃', val:runHours+' h', label:'7METs·'+Math.round(kcalPerHour)+'kcal/h 慢跑 · 上限折算'},
        {icon:'🥚', val:eggs+' 枚', label:'一枚 70kcal 鸡蛋 · 上限折算'},
        {icon:'🧳', val:totalJin.toFixed(1)+'斤×'+META.days+'天', label:'负重行走等价'}
      ];
      eqTrack.innerHTML = equ.map(function(e){
        return '<div class="eq-item"><div class="eq-icon">'+e.icon+'</div><div class="eq-text"><div class="eq-val">'+e.val+'</div><div class="eq-label">'+e.label+'</div></div></div>';
      }).join('');
    }
  }catch(e){ console.warn('eq',e); }

  // --- 4. 下一关焦点 ---
  try{
    var nextTitle=document.getElementById('next-focus-title');
    var nextBig=document.getElementById('next-focus-big');
    var nextMeta=document.getElementById('next-focus-meta');
    var nextFill=document.getElementById('next-focus-fill');
    var nextEst=document.getElementById('next-focus-est');
    var nextDateEl=document.getElementById('next-focus-date');
    var nextMotiv=document.getElementById('next-focus-motiv');
    if(nextBig){
      var rateLbl=document.getElementById('next-focus-rate');
      if(rateLbl) rateLbl.textContent='按 '+dailyDrop.toFixed(2)+' 斤/天 · 预计达成';
      // 关口梯子:已破 + 未破共用一条,区间起点 = 梯子上"刚好高于当前体重"的那一档
      // (原来 candidates/prevMils 是两条独立硬编码梯子,prevMils 只到 200.2 →
      //  破 195 后区间会错算成 200.2→190,进度百分比失真)
      var ladder=[CONFIG.startWeight,226.1,212.5,210,CONFIG.milestone200,195,190,
                  CONFIG.milestone188,185,180,CONFIG.milestone175,170,
                  CONFIG.target160,CONFIG.milestone150,CONFIG.target145];
      var next=null, prevAchieved=CONFIG.startWeight;
      for(var i=0;i<ladder.length;i++){
        if(curW > ladder[i]){
          next=ladder[i];
          prevAchieved = i>0 ? ladder[i-1] : CONFIG.startWeight;
          break;
        }
      }
      if(next===null){ next=CONFIG.target145; prevAchieved=CONFIG.milestone150; }
      var remain = curW - next;
      var segment = prevAchieved - next;
      var prog = segment > 0 ? Math.max(0, Math.min(100, (prevAchieved - curW)/segment*100)) : 100;
      // 终极目标已达成:梯子走完,remain 会是负数 → 原实现会显示"距 145 还有 -2.0斤",
      // 且 days 为负,把过去的日期当成"预计达成日"
      if(remain <= 0){
        if(nextTitle) nextTitle.textContent = '全部关口已达成 🎉';
        nextBig.innerHTML = '已达 <b>'+curW.toFixed(1)+'</b> <span class="unit">斤</span> · 低于终极目标 '+next;
        nextMeta.textContent = '较终极目标 '+next+' 再低 '+Math.abs(remain).toFixed(1)+' 斤 · 进入维持期';
        nextEst.textContent = '区间进度 · 100% · 较昨日 '+(delta>0?'+':'')+delta.toFixed(1)+'斤';
        if(nextFill) nextFill.style.width = '100%';
        if(nextDateEl) nextDateEl.textContent = '✅';
        if(nextMotiv) nextMotiv.textContent = '目标全部拿下,接下来是体重维持:关注 MA7 波动区间,别让水债变脂肪债。';
        if(rateLbl) rateLbl.textContent = '已达成 · 转入维持';
      } else {
      var days = dailyDrop>0 ? Math.ceil(remain/dailyDrop) : null;
      var estDate = days ? new Date(parseLocalDate(META.currentDate).getTime()+days*86400000) : null;
      var estStr = days ? fmtLocalDate(estDate) : '—';
      if(nextTitle) nextTitle.textContent = '距 '+next+' 还有 '+remain.toFixed(1)+'斤';
      nextBig.innerHTML = '还差 <b>'+remain.toFixed(1)+'</b> <span class="unit">斤</span> 到 '+next;
      nextMeta.textContent = prevAchieved.toFixed(1)+' → '+next+' 区间已走 '+prog.toFixed(1)+'% · 当前 '+curW.toFixed(1)+'斤';
      nextEst.textContent = '区间进度 · '+prog.toFixed(1)+'% · 较昨日 '+(delta>0?'+':'')+delta.toFixed(1)+'斤';
      if(nextFill) setTimeout(function(){ nextFill.style.width = prog.toFixed(1)+'%'; }, 250);
      if(nextDateEl) nextDateEl.textContent = estStr;
      var motiv='';
      if(dailyDrop<=0) motiv='当前节奏持平/反弹，先稳住水分，明天排空即回归下降通道。';
      else if(days<=7) motiv='按 '+dailyDrop.toFixed(2)+'斤/天，<b>一周内</b>就能摸到 '+next+'！冲刺一下，连胜回来 🔥';
      else if(days<=21) motiv='不到三周就能破 '+next+'，'+(META.bestWeekLabel||'最佳周')+' 曾一周 '+(META.bestWeekDelta!=null?Number(META.bestWeekDelta).toFixed(1):'-4.6')+'斤，你完全有爆发力。';
      else if(INJECTIONS.length>=2) motiv='稳步推进，每 '+CONFIG.injectionIntervalDays+' 天一针的节奏正在起效，保持 400kcal+高蛋白即可。';
      else motiv='稳步推进，保持 400kcal 缺口 + 高蛋白即可。';
      if(nextMotiv) nextMotiv.innerHTML = motiv;
      }
    }
  }catch(e){ console.warn('next',e); }

  // --- 5. 成就墙 ---
  try{
    var grid=document.getElementById('badges-grid');
    var countEl=document.getElementById('badges-count');
    if(grid){
      var badges=[
        {w:244, label:'起点', sub:'2026-04-17', icon:'🏁'},
        {w:226.1, label:'超越 2025 最高', sub:'2025峰值', icon:'⛰️'},
        {w:212.5, label:'超越 2024-11-28', sub:'2024低点', icon:'🌊'},
        {w:210, label:'破 210 大关', sub:'2026-07-19', icon:'💎'},
        {w:200.2, label:'超越 2022 纪录', sub:'2022-10-20', icon:'🏆'},
        {w:188, label:'历史最低', sub:'2021-12', icon:'👑'},
        {w:175, label:'中段关口', sub:'188→160 半程支点', icon:'⚡'},
        {w:CONFIG.target160, label:'过渡目标', sub:CONFIG.sprintDate.slice(5).replace('-','/')+' 冲刺', icon:'🎯'},
        {w:150, label:'准正常线', sub:'BMI ≈ 24.8', icon:'🩺'},
        {w:145, label:'终极目标', sub:'BMI 24', icon:'🌟'}
      ];
      var unlocked=0;
      var html = badges.map(function(b){
        var d = firstBreakDate(b.w);
        var done = d!==null;
        if(done) unlocked++;
        return {b:b, d:d, done:done, isNext:false};
      });
      // 下一关:首个未解锁徽章
      var firstLocked = html.find(function(x){ return !x.done; });
      if (firstLocked) firstLocked.isNext = true;
      grid.innerHTML = html.map(function(x){
        var b=x.b, cls=x.done?'unlocked': x.isNext?'next':'locked';
        var dateTxt = x.done ? '✅ '+x.d.slice(5).replace('-','/') : x.isNext ? 'NEXT · 距 '+(curW-b.w).toFixed(1)+'斤' : '🔒 待解锁';
        var dateCls = x.done?'done': x.isNext?'next':'locked';
        return '<div class="badge-card '+cls+'" data-weight="'+b.w+'" title="'+b.label+' · '+b.sub+'" tabindex="0"><div class="badge-icon">'+b.icon+'</div><div class="badge-weight">'+b.w.toFixed(1)+'斤</div><div class="badge-label">'+b.label+'</div><div class="badge-date '+dateCls+'">'+dateTxt+'</div></div>';
      }).join('');
      if(countEl) countEl.textContent = unlocked+'/'+badges.length+' 已解锁';
      grid.querySelectorAll('.badge-card').forEach(function(c){
        var jump = function(){
          var w=c.getAttribute('data-weight');
          // 起点 244 没有对应里程碑行 → 退回滚到里程碑区块,不做静默无响应
          var t=document.querySelector('.milestone[data-goal="'+w+'"]') || document.querySelector('.milestones');
          if(t){ t.scrollIntoView({behavior:'smooth', block:'center'}); t.style.outline='2px solid #fbbf24'; setTimeout(function(){t.style.outline='';}, 1600); }
        };
        c.addEventListener('click', jump);
        c.addEventListener('keydown', function(e){ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); jump(); } });
      });
    }
  }catch(e){ console.warn('badges',e); }

  // --- 6. Streak 重构 ---
  try{
    var streakEl=document.getElementById('stat-streak');
    var streakMeta=document.getElementById('stat-streak-meta');
    if(streakEl && streakMeta){
      if(streak===0 && isBelow200 && belowDays>0){
        streakEl.innerHTML='🛡️ '+belowDays;
        streakMeta.textContent='守住<200 '+belowDays+'天 · 稳居区间';
        streakEl.style.color='#7dd3fc';
      } else if(streak===0){
        streakMeta.textContent='持平/反弹 · 明天排空即回落';
      }
    }
  }catch(e){}

})();

// ===== 视觉特效 · 进度环发光 =====
// (2026-08-26 Midnight Lime 重构:3D tilt / 粒子连线 / 扫光条已退役,
//  卡片 hover 效果移交纯 CSS,JS 不再写 inline transform)
(function visualPolish(){
  // 进度环下一关高亮 (ring-200 已退役;按当前体重找最近未破关口点亮)
  try{
    var cur=parseFloat(META.currentWeight);
    var nextRing=null;
    if(cur>188) nextRing='ring-188';
    else if(cur>175) nextRing='ring-175';
    else if(cur>160) nextRing='ring-160';
    else if(cur>150) nextRing='ring-150';
    else if(cur>145) nextRing='ring-145';
    if(nextRing){
      var el=document.getElementById(nextRing);
      if(el){ var card=el.closest('.ring-card'); if(card) card.classList.add('next-target'); }
    }
  }catch(e){}
})();

// ===== 数值滚动动画 (卡片数字从 0 滚到最终值,保留前后缀与内联 HTML) =====
// 覆盖:统计卡 / 进度环 / 等效成就条 / 平台期统计 (这些区块渲染晚于 stats,统一在文件末尾触发)
// 只在标签外的**正文**里找第一个数字:原实现直接对 innerHTML 跑正则,
// 会抓到 style="color:#fbbf24" 里的 24 / #fb923c 里的 923 → 动画期间把颜色值滚成
// #fbbf12 之类,真正的数值反而不动 (2026-08-29 实测:总进度卡、BMI<30 时的 BMI 卡)
function findFirstTextNumber(html) {
  var inTag = false;
  for (var i = 0; i < html.length; i++) {
    var ch = html.charAt(i);
    if (ch === '<') { inTag = true; continue; }
    if (ch === '>') { inTag = false; continue; }
    if (inTag) continue;
    if (ch >= '0' && ch <= '9') {
      var start = (i > 0 && html.charAt(i - 1) === '-') ? i - 1 : i;
      var j = i;
      while (j < html.length && ((html.charAt(j) >= '0' && html.charAt(j) <= '9') || html.charAt(j) === '.')) j++;
      var raw = html.slice(start, j).replace(/\.$/, '');
      return { raw: raw, index: start };
    }
  }
  return null;
}
function animateCountUp() {
  // 尊重系统"减弱动态效果"
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var els = document.querySelectorAll('.card .value, .ring-card .ring-value, .eq-val, .plateau-stat .ps-val');
  els.forEach(function(el) {
    // data-noroll:数字嵌在词里 (如 "Day4+ 47%"),滚动会滚成 Day0+/Day2+
    if (el.hasAttribute('data-noroll')) return;
    var html = el.innerHTML;
    // 日期型值 (YYYY-MM-DD) 不参与数字滚动,否则会滚成假日期
    if (/^\s*\d{4}-\d{2}-\d{2}/.test(html)) return;
    if (html === '—' || html.indexOf('数据不足') !== -1 || html.indexOf('无法达成') !== -1) return;
    var m = findFirstTextNumber(html);
    if (!m) return;
    var target = parseFloat(m.raw);
    if (!isFinite(target)) return;
    var prefix = html.slice(0, m.index);
    var suffix = html.slice(m.index + m.raw.length);
    var decimals = m.raw.indexOf('.') !== -1 ? m.raw.split('.')[1].length : 0;
    var dur = 700, t0 = null;
    function step(ts) {
      if (!t0) t0 = ts;
      var p = Math.min(1, (ts - t0) / dur);
      var eased = 1 - Math.pow(1 - p, 3);  // easeOutCubic
      var val = (target * eased).toFixed(decimals);
      el.innerHTML = prefix + val + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  });
}

// ===== 里程碑旅程尺生成 (244 → 145 横向刻度,当前位置发光脉冲) =====
(function buildRuler() {
  var ruler = document.getElementById('mile-ruler');
  if (!ruler) return;
  var span = CONFIG.startWeight - CONFIG.target145;  // 99 斤全程
  // ⚠️ 方向:左端=起点 244,右端=终点 145,与标题「244 → 145」一致,
  //    fill 宽度 = 已走比例 (原式 (w-145)/span 把 145 放在左端,刻度顺序与标题相反,
  //    且绿条填的是"剩余路程",导致条 54% 配文案「已走 46%」)
  function pos(w) { return Math.max(0, Math.min(100, (CONFIG.startWeight - w) / span * 100)); }
  var cur = META.currentWeight != null ? META.currentWeight
    : (REAL_POINTS.length ? REAL_POINTS[REAL_POINTS.length - 1].morning : null);
  if (cur == null) return;
  // 刻度:起点 + 关键里程碑 + 终点
  var ticks = [
    [CONFIG.startWeight, CONFIG.startWeight.toFixed(0)],
    [210.0, '210'],
    [CONFIG.milestone200, CONFIG.milestone200.toFixed(1)],
    [CONFIG.milestone188, CONFIG.milestone188.toFixed(0)],
    [CONFIG.milestone175, CONFIG.milestone175.toFixed(0)],
    [CONFIG.target160, CONFIG.target160.toFixed(0)],
    [CONFIG.milestone150, CONFIG.milestone150.toFixed(0)],
    [CONFIG.target145, CONFIG.target145.toFixed(0)]
  ];
  var ticksEl = document.getElementById('ruler-ticks');
  var labelsEl = document.getElementById('ruler-labels');
  ticks.forEach(function(t) {
    var left = pos(t[0]).toFixed(1) + '%';
    var tk = document.createElement('div');
    tk.className = 'mile-ruler-tick';
    tk.style.left = left;
    ticksEl.appendChild(tk);
    var lb = document.createElement('div');
    lb.className = 'mile-ruler-tick-label';
    lb.style.left = left;
    lb.textContent = t[1];
    labelsEl.appendChild(lb);
  });
  // 当前位置:标记点 + 旗标 + 已走亮带 + 百分比 (统一保留 1 位小数,避免 style 里写出 45.9595...%)
  var p = +pos(cur).toFixed(1);
  var markerEl = document.getElementById('ruler-marker');
  var flagEl = document.getElementById('ruler-flag');
  var fillEl = document.getElementById('ruler-fill');
  var pctEl = document.getElementById('ruler-pct');
  if (markerEl) markerEl.style.left = p + '%';
  if (flagEl) flagEl.textContent = cur.toFixed(1) + ' 斤';
  if (fillEl) fillEl.style.width = p + '%';
  if (pctEl) pctEl.textContent = p.toFixed(1) + '%';  // 与 fill 同一个值,不再两套算法
})();

// 里程碑目标值从 CONFIG 联动到静态标签 (ring 标题/里程碑行 weight 文本)
(function syncGoalLabels() {
  var ringLabels = {
    'ring-188': CONFIG.milestone188.toFixed(1) + ' · 历史最低',
    'ring-175': '破 ' + CONFIG.milestone175.toFixed(0) + ' · 中段关口',
    'ring-160': '破 ' + CONFIG.target160.toFixed(1) + ' · 过渡目标',
    'ring-150': '破 ' + CONFIG.milestone150.toFixed(0) + ' · 准正常线',
    'ring-145': '破 ' + CONFIG.target145.toFixed(1) + ' · 终极目标'
  };
  Object.keys(ringLabels).forEach(function(ringId) {
    var c = document.getElementById(ringId);
    if (c) {
      var card = c.closest('.ring-card');
      var lbl = card && card.querySelector('.ring-label');
      if (lbl) lbl.textContent = ringLabels[ringId];
    }
  });
  // 里程碑行的 weight 文本与 data-goal 同步 CONFIG 值 (目标调整时自动联动)
  document.querySelectorAll('.milestone[data-goal]').forEach(function(row) {
    var wEl = row.querySelector('.weight');
    if (!wEl) return;
    var goal = parseFloat(row.getAttribute('data-goal'));
    var replacement = null;
    if (goal === 200.2) replacement = CONFIG.milestone200;
    else if (goal === 188) replacement = CONFIG.milestone188;
    else if (goal === 175) replacement = CONFIG.milestone175;
    else if (goal === 160) replacement = CONFIG.target160;
    else if (goal === 150) replacement = CONFIG.milestone150;
    else if (goal === 145) replacement = CONFIG.target145;
    if (replacement !== null && Math.abs(replacement - goal) > 0.0001) {
      wEl.textContent = wEl.textContent.replace(new RegExp('\\b' + goal.toFixed(1) + '\\b'), replacement.toFixed(1));
      row.setAttribute('data-goal', String(replacement));
    }
  });
  // 160 行的「(9/27 冲刺)」原为静态文本,CONFIG.sprintDate 改了不联动
  var row160 = document.querySelector('.milestone[data-goal="' + CONFIG.target160 + '"]')
    || document.querySelector('.milestone[data-goal="160"]');
  if (row160) {
    var w160 = row160.querySelector('.weight');
    if (w160) w160.textContent = CONFIG.target160.toFixed(1) + ' 斤 · 过渡目标 (' +
      CONFIG.sprintDate.slice(5).replace('-', '/') + ' 冲刺)';
  }
})();

function setRing(id, target, current, peak) {
  var progress = Math.max(0, Math.min(1, (peak - current) / (peak - target)));
  var offset = CONFIG.ringCircumference * (1 - progress);
  var el = document.getElementById(id);
  if (el) el.style.strokeDashoffset = offset;
  var valEl = document.getElementById(id + '-val');
  if (valEl) valEl.innerHTML = (progress * 100).toFixed(0) + '<span class="unit">%</span>';
  var detailEl = document.getElementById(id + '-detail');
  if (detailEl) {
    detailEl.textContent = progress >= 1
      ? '✅ 已达成 · 目标 ' + target.toFixed(1) + ' 斤'
      : '还差 ' + (current - target).toFixed(1) + ' 斤';
  }
}

function setMileBar(prefix, target, current, peak) {
  var progress = Math.max(0, Math.min(100, (peak - current) / (peak - target) * 100));
  var bar = document.getElementById(prefix + '-bar');
  if (bar) {
    bar.style.width = progress.toFixed(0) + '%';
    // 渐变填充 (按里程碑颜色,静态 DONE 条保持原 inline 色)
    var colors = { 'mile-200': '#fbbf24', 'mile-188': '#fbbf24', 'mile-175': '#34d399', 'mile-160': '#7dd3fc', 'mile-150': '#f472b6', 'mile-145': '#c4b5fd' };
    var bc = colors[prefix] || '#fbbf24';
    bar.style.background = 'linear-gradient(90deg, ' + bc + '77, ' + bc + ')';
  }
}

// ===== 里程碑行状态动态化 (dot/status 原来 HTML 写死,破关后与数据不自洽) =====
function updateMilestoneRows(currentWeight) {
  var done = 0, total = 0;
  document.querySelectorAll('.milestones .milestone').forEach(function(row) {
    total++;
    var goalAttr = row.getAttribute('data-goal');
    var dot = row.querySelector('.dot');
    var status = row.querySelector('.status');
    if (goalAttr !== null) {
      var goal = parseFloat(goalAttr);
      if (currentWeight <= goal) {
        done++;
        if (dot) { dot.classList.remove('next'); dot.classList.add('done'); }
        if (status) { status.textContent = 'DONE'; status.classList.add('done'); }
      } else {
        var pending = row.getAttribute('data-pending') || 'NEXT';
        if (dot) { dot.classList.remove('done'); dot.classList.add('next'); }
        if (status) { status.textContent = pending; status.classList.remove('done'); }
      }
    } else if (status && status.textContent === 'DONE') {
      done++;  // 兜底:无 data-goal 的历史里程碑行 (现全部已补 data-goal)
    }
  });
  var countEl = document.getElementById('mile-progress-count');
  if (countEl) countEl.textContent = done + '/' + total;
}

// ===== 预测函数 (实时推算;2026-08-26 起斜率为 sync 侧 OLS 回归值) =====
// 情景辅助:近 7 天回归 (dailyDrop7d) / 近 14 天回归 (dailyDrop14d) / 最佳周节奏 参照
function scenarioRate() {
  return {
    r7: parseFloat(META.dailyDrop7d) || 0,
    r14: parseFloat(META.dailyDrop14d) || 0,
    rBest: Math.abs(parseFloat(META.bestWeekDelta) || 0) / 7
  };
}
function reachBy(cur, w, r, from) {
  if (r <= 0 || cur <= w) return null;
  var days = Math.ceil((cur - w) / r);
  return { days: days, date: new Date(from.getTime() + days * 86400000) };
}
function computePrediction(currentWeight, dailyDrop) {
  // 目标日 (由 weight_data.js 的 META.targetDate 提供,不再硬编码)
  var targetDate = parseLocalDate(CONFIG.targetDate);
  var today = parseLocalDate(META.currentDate);
  var rawDays = Math.round((targetDate - today) / 86400000);
  var expired = rawDays < 0;                 // 目标日已过
  var daysToTarget = Math.max(0, rawDays);
  var md = CONFIG.targetDate.slice(5, 7) + '/' + CONFIG.targetDate.slice(8, 10);
  // 目标日已过时,"到目标日还能减多少"没有意义 → 不再拼 "→X 斤" 的假预测
  var targetTail = expired ? ' · ' + md + ' 已过' : ' · ' + md + '→';

  // 1) 当前节奏卡片 (pred-rate) 已并入 stat-drop14「近 14 天日均减重」,不再重复展示

  // 2) 预测目标日体重 (基准=近14天回归;meta 给三档落点:近7天慢速情景 / 近14天基准 / 最佳周爆发情景)
  var pred1122 = currentWeight - dailyDrop * daysToTarget;
  if (expired) {
    // 已到期:改报目标日当天实测 (有的话),避免"预测 11/22 = 今天体重"的假象
    var tRec = null;
    for (var ti = 0; ti < RAW.length; ti++) {
      if (RAW[ti].date === CONFIG.targetDate && RAW[ti].morning !== null) { tRec = RAW[ti]; break; }
    }
    document.getElementById('pred-1122').innerHTML = tRec
      ? tRec.morning.toFixed(1) + ' <span class="unit">斤</span>'
      : '已到期';
    document.getElementById('pred-1122-meta').textContent = tRec
      ? CONFIG.targetDate + ' 当日实测 · 目标日已过,预测口径失效'
      : CONFIG.targetDate + ' 目标日已过且无当日实测 · 请更新 targetDate';
  } else {
    document.getElementById('pred-1122').innerHTML =
      pred1122.toFixed(1) + ' <span class="unit">斤</span>';
    var diff160 = pred1122 - CONFIG.target160;
    var diff145 = pred1122 - CONFIG.target145;
    var meta1122 = '';
    var t160 = CONFIG.target160, t145 = CONFIG.target145;
    if (pred1122 < t160) meta1122 = '✅ 突破 ' + t160 + ' · ' + Math.abs(diff160).toFixed(1) + ' 斤到 ' + t160;
    else if (pred1122 < t160 + 5) meta1122 = '距 ' + t160 + ' 还 ' + diff160.toFixed(1) + ' 斤';
    else meta1122 = '距 ' + t160 + ' 还 ' + diff160.toFixed(1) + ' 斤 · 距 ' + t145 + ' 还 ' + diff145.toFixed(1) + ' 斤';
    var sc = scenarioRate();
    // ⚠️ 近 7 天斜率为负 (反弹中) 时不做线性外推:-0.4 斤/天 × 85 天会算出"11/22 涨到 233 斤"
    var sSlow = sc.r7 > 0 ? (currentWeight - sc.r7 * daysToTarget).toFixed(0) : null;
    var sBest = (currentWeight - sc.rBest * daysToTarget).toFixed(0);
    document.getElementById('pred-1122-meta').textContent =
      meta1122 + ' | 三档: 近7天 ' + sc.r7.toFixed(2) +
      (sSlow !== null ? '→' + sSlow : '(反弹中·不外推)') +
      ' · 近14天→' + pred1122.toFixed(0) +
      ' · ' + (META.bestWeekLabel || '最佳周') + '节奏→' + sBest;
  }

  // 3) 预测 160 达成日 (meta 加近 7 天情景对照:慢速/基准两端)
  if (dailyDrop <= 0) {
    document.getElementById('pred-160-date').textContent = '无法达成';
    document.getElementById('pred-160-meta').textContent = '当前为反弹/持平节奏';
  } else {
    var daysTo160 = Math.ceil((currentWeight - CONFIG.target160) / dailyDrop);
    var reach160 = new Date(today.getTime() + daysTo160 * 86400000);
    document.getElementById('pred-160-date').textContent = fmtLocalDate(reach160);
    var dist160 = Math.round((reach160 - today) / 86400000);
    var alt160 = reachBy(currentWeight, CONFIG.target160, scenarioRate().r7, today);
    // 跨年带年份 (近7天慢速情景下 160 达成日常跨年)
    var alt160Txt = alt160 ? ' · 近7天→' + (alt160.date.getFullYear() !== today.getFullYear() ? alt160.date.getFullYear() + '/' : '') + fmtLocalDate(alt160.date).slice(5).replace('-', '/') : '';
    document.getElementById('pred-160-meta').textContent =
      dist160 + ' 天后 · ' + (currentWeight - CONFIG.target160).toFixed(1) + ' 斤到目标' + alt160Txt;
  }

  // 4) 预测 145 达成日 (meta 加近 7 天情景对照)
  if (dailyDrop <= 0) {
    document.getElementById('pred-145-date').textContent = '无法达成';
    document.getElementById('pred-145-meta').textContent = '当前为反弹/持平节奏';
  } else {
    var daysTo145 = Math.ceil((currentWeight - CONFIG.target145) / dailyDrop);
    var reach145 = new Date(today.getTime() + daysTo145 * 86400000);
    document.getElementById('pred-145-date').textContent = fmtLocalDate(reach145);
    var dist145 = Math.round((reach145 - today) / 86400000);
    var alt145 = reachBy(currentWeight, CONFIG.target145, scenarioRate().r7, today);
    var alt145Txt = alt145 ? ' · 近7天→' + (alt145.date.getFullYear() !== today.getFullYear() ? alt145.date.getFullYear() + '/' : '') + fmtLocalDate(alt145.date).slice(5).replace('-', '/') : '';
    document.getElementById('pred-145-meta').textContent =
      dist145 + ' 天后 · ' + (currentWeight - CONFIG.target145).toFixed(1) + ' 斤到终极目标' + alt145Txt;
  }

  // 5) 严格执行 -4 斤/周: 执行率卡片 (本周实际 vs 目标)
  var strictDrop = CONFIG.strictWeekly / 7.0;
  var strict1122 = currentWeight - strictDrop * daysToTarget;

  // 取本周实际 delta
  var wk = weeklyData.length ? weeklyData[weeklyData.length - 1] : null;
  var actualDrop = wk ? -wk.delta : 0;  // 正=掉秤, 负=反弹
  var target = CONFIG.strictWeekly;
  var deviation = target - actualDrop;  // 0=达标, 正=落后, 负=超标

  // 颜色: 偏差 0 → 绿; 偏差越大 → 越深红
  var card = document.getElementById('strict-exec-card');
  var valEl = document.getElementById('pred-strict-1122');
  var metaEl = document.getElementById('pred-strict-meta');
  var weekLabel = document.getElementById('strict-exec-week');

  if (wk) {
    weekLabel.textContent = wk.week;

    if (wk.inProgress) {
      // 进行中周:周未走完,反弹多为水债(非脂肪),不判达标/未达标
      var pSign = wk.delta > 0 ? '+' : '';
      card.style.background = 'rgba(148,163,184,0.10)';
      valEl.innerHTML =
        '<span style="color:var(--slate)">' + pSign + wk.delta.toFixed(1) +
        '</span> <span class="unit">斤/周</span>';
      metaEl.innerHTML =
        '⏳ 进行中 · ' + wk.label + ' · 周目标 -' + CONFIG.strictWeekly.toFixed(1) +
        targetTail + (expired ? '' : strict1122.toFixed(1) + ' 斤');
    } else {
      // 执行率百分比 (卡片 label 写的就是"执行率",原来算出来却没用上 → 补进 meta)
      var rate = (actualDrop / target * 100);

      // 颜色计算
      var bg, fg, bar;
      if (deviation <= 0) {
        // 达标/超标: 绿色, 偏差越负越深
        var gIntensity = Math.min(Math.abs(deviation) / 4, 1);  // 0~1
        bg = 'rgba(163,230,53,' + (0.08 + gIntensity * 0.20) + ')';
        fg = 'var(--ok)';
        bar = '✅ 达标 ' + Math.round(rate) + '%';
      } else {
        // 未达标: 红色, 偏差越大越深
        var rIntensity = Math.min(deviation / 8, 1);  // 0~1, 8 斤差=最深
        bg = 'rgba(232,65,66,' + (0.08 + rIntensity * 0.25) + ')';
        fg = 'var(--bad)';
        bar = '执行 ' + Math.round(rate) + '% · 差 ' + deviation.toFixed(1) + ' 斤';
      }
      card.style.background = bg;

      // 主数值: 本周实际 delta (带方向)
      var deltaSign = wk.delta > 0 ? '+' : '';
      valEl.innerHTML =
        '<span style="color:' + fg + '">' + deltaSign + wk.delta.toFixed(1) +
        '</span> <span class="unit">斤/周</span>';

      // meta: 执行率 + 偏差 + 目标日严格预测
      metaEl.innerHTML =
        '<span style="color:' + fg + '">' + bar + '</span>' +
        ' · 目标 -' + CONFIG.strictWeekly.toFixed(1) +
        targetTail + (expired ? '' : strict1122.toFixed(1) + ' 斤');
    }
  } else {
    valEl.innerHTML = strict1122.toFixed(1) + ' <span class="unit">斤</span>';
    metaEl.textContent = '需 -' + CONFIG.strictWeekly.toFixed(1) + ' 斤/周 × ' + Math.ceil(daysToTarget / 7) + ' 周';
  }
}

// ===== 静态数据 =====
// 跨图共用系列色 (单一来源:同一实体在两张图必须同色,防手写漂移 —— MA7 曾一图天蓝一图琥珀)
var COLOR_MA7 = '#7dd3fc';
var COLOR_INTERP = '#8b5cf6';  // 插值线深紫:原 #c4b5fd 与 MA7 天蓝在色觉障碍下 ΔE 1.7 (验证器实测),几乎同色
// timeline 里程碑水平参考线 (weight/color 由 milestoneLinesPlugin 与 tlYMin 读取;
// label 字段已随参考线 dataset 移除,语义移入行尾注释)
var MILESTONES = [
  {weight: CONFIG.startWeight, color: '#fb7185'},   // 历史最高 (4/17)
  {weight: 226.1, color: '#c4b5fd'},                // 超越 2025 最高
  {weight: 212.5, color: '#c4b5fd'},                // 超越 2024-11-28
  {weight: 210.0, color: '#a3e635'},                // 破 210 大关 (7/19)
  {weight: CONFIG.milestone200, color: '#fbbf24'},  // 超越 2022-10-20
  {weight: CONFIG.milestone188, color: '#fbbf24'},  // 历史最低 (2021-12)
  {weight: CONFIG.milestone175, color: '#34d399'},  // 破 175 · 中段关口
  {weight: CONFIG.target160, color: '#7dd3fc'},     // 过渡目标 (9/27 冲刺)
  {weight: CONFIG.milestone150, color: '#f472b6'},  // 破 150 · 准正常线
  {weight: CONFIG.target145, color: '#7dd3fc'}      // 终极目标
];

// (INJECTIONS 已提前到文件头 REAL_POINTS 旁声明,供激励/下一关/反弹卡使用)

// ===== Chart.js 默认 =====
Chart.defaults.color = '#9aa6b4';
Chart.defaults.borderColor = 'rgba(255,255,255,0.07)';
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif';
// 全局动画:更丝滑的入场 (所有图表统一)
// ⚠️ 必须 Object.assign 合并!整体替换 `Chart.defaults.animation = {...}` 会破坏 Chart.js
// 内部 animations(colors/numbers)集合的默认解析(动画配置丢失 type → 插值器 _fn=undefined),
// hover 触发属性动画时抛 "this._fn is not a function",全部图表 tooltip 失效 (2026-08-22 实测根因)
Object.assign(Chart.defaults.animation, {
  duration: 950,
  easing: 'easeOutQuart'
});
// 尊重系统"减弱动态效果":图表入场动画直接跳过
// (animation:false 是 Chart.js 官方支持的关闭方式,内部有专门分支,可安全整体赋值)
if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  Chart.defaults.animation = false;
}
Chart.defaults.elements.line.tension = 0.15;
Chart.defaults.elements.point.hoverRadius = 6;
// 悬停容差(全局): 不要求精确压中数据点——沿x轴就近吸附即出tooltip。
// 默认 intersect:true 时必须命中点本体(半径约3px),稀疏点图(如近14天)人手极难瞄准,
// 表现为"悬停无详情"。axis:'x' 让纵向任意高度都能命中最近的数据点 (2026-08-22)
Object.assign(Chart.defaults.interaction, { mode: 'nearest', intersect: false, axis: 'x' });
Chart.defaults.elements.point.hitRadius = 12;
// 玻璃 tooltip + 图例点样式 (全图统一)
// ⚠️ 必须 Object.assign 合并!整体替换 `Chart.defaults.plugins.tooltip = {...}`
// 会把 enabled/mode/callbacks 等默认值全丢掉 → tooltip 被禁用 (2026-08-01 实测根因)
Object.assign(Chart.defaults.plugins.tooltip, {
  backgroundColor: 'rgba(13,17,23,0.94)',
  borderColor: 'rgba(255,255,255,0.09)',
  borderWidth: 1,
  padding: 10,
  cornerRadius: 8,
  titleColor: '#e6e9ef',
  bodyColor: '#aab3c2',
  titleFont: { weight: '600' },
  boxPadding: 4,
  usePointStyle: true,
  caretSize: 6
});
Chart.defaults.plugins.legend.labels = Object.assign({}, Chart.defaults.plugins.legend.labels, {
  usePointStyle: true, boxWidth: 8, boxHeight: 8
});

// ===== 时间线周带背景:按周范围画交替色带 (一眼看出每周节奏,数据在色带之上) =====
var weekBands = [];
(function() {
  if (typeof weeklyData === 'undefined') return;
  // 年份推断:label 只有 MM/DD-MM/DD,从 RAW 数据范围推实际年份 (原硬编码 2026,跨年后会画错位置)
  var y0 = parseLocalDate(RAW[0].date).getFullYear();
  var y1 = parseLocalDate(RAW[RAW.length - 1].date).getFullYear();
  // 进行中周的结束日可能晚于最后数据日,留 10 天缓冲
  var dataEnd = fmtLocalDate(new Date(parseLocalDate(RAW[RAW.length - 1].date).getTime() + 10 * 86400000));
  for (var i = 0; i < weeklyData.length; i++) {
    var m = (weeklyData[i].label || '').match(/(\d{2})\/(\d{2})-(\d{2})\/(\d{2})/);
    if (!m) continue;
    for (var y = y0; y <= y1 + 1; y++) {
      var ey = (parseInt(m[3], 10) < parseInt(m[1], 10)) ? y + 1 : y;  // 跨年周
      var s = y + '-' + m[1] + '-' + m[2];
      var e = ey + '-' + m[3] + '-' + m[4];
      if (e >= RAW[0].date && s <= dataEnd) {
        weekBands.push({
          start: s,
          end: e,
          color: (i % 2 === 0) ? 'rgba(255,255,255,0.025)' : 'rgba(255,255,255,0.055)'
        });
        break;
      }
    }
  }
})();
var weekBandPlugin = {
  id: 'weekBands',
  beforeDatasetsDraw: function(chart) {
    if (chart.canvas.id !== 'timeline' || !weekBands.length) return;
    var ctx = chart.ctx;
    var xScale = chart.scales.x, yScale = chart.scales.y;
    var top = yScale.top, bottom = yScale.bottom;
    weekBands.forEach(function(band) {
      // time scale 的 getPixelForValue 需要时间戳,字符串会返回 null
      // 必须本地时区解析:数据点 x 由 date-fns parseISO 按本地午夜解析,
      // new Date('YYYY-MM-DD') 会按 UTC 解析 → 北京时间下色带右偏 8 小时
      var x0 = xScale.getPixelForValue(parseLocalDate(band.start).getTime());
      var x1 = xScale.getPixelForValue(parseLocalDate(band.end).getTime());
      if (x0 === null || x1 === null || isNaN(x0) || isNaN(x1)) return;
      ctx.save();
      ctx.fillStyle = band.color;
      ctx.fillRect(x0, top, x1 - x0, bottom - top);
      ctx.restore();
    });
  }
};
Chart.register(weekBandPlugin);

// ===== 破关里程碑竖线:在首次突破日画金色竖线 + 标签 (数据叙事) =====
// 检测每个里程碑(200.2/188/160/145)在实测序列里首次 <= 目标的日期
var milestoneBreaks = {};
(function() {
  var ms = [
    {weight: CONFIG.milestone200, label: '破 200'},
    {weight: CONFIG.milestone188, label: '破 188'},
    {weight: CONFIG.milestone175, label: '破 175'},
    {weight: CONFIG.target160, label: '破 160'},
    {weight: CONFIG.milestone150, label: '破 150'},
    {weight: CONFIG.target145, label: '破 145'}
  ];
  ms.forEach(function(m) {
    for (var i = 0; i < REAL_POINTS.length; i++) {
      if (REAL_POINTS[i].morning <= m.weight) { milestoneBreaks[m.weight] = { date: REAL_POINTS[i].date, label: m.label }; break; }
    }
  });
})();
var milestoneBreakPlugin = {
  id: 'milestoneBreaks',
  afterDatasetsDraw: function(chart) {
    if (chart.canvas.id !== 'timeline') return;
    var ctx = chart.ctx;
    var xScale = chart.scales.x, yScale = chart.scales.y;
    Object.keys(milestoneBreaks).forEach(function(milestone) {
      var b = milestoneBreaks[milestone];
      var date = b.date;
      var x = xScale.getPixelForValue(new Date(date + 'T00:00:00').getTime());
      if (x === null || isNaN(x)) return;
      var top = yScale.top, bottom = yScale.bottom;
      // 金色竖线
      ctx.save();
      ctx.setLineDash([5, 4]);
      ctx.strokeStyle = 'rgba(251,191,36,0.65)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(x, top);
      ctx.lineTo(x, bottom);
      ctx.stroke();
      ctx.restore();
      // 顶部标签 (多个破关错开高度,避免重叠)
      ctx.save();
      ctx.fillStyle = '#fbbf24';
      ctx.font = 'bold 11px system-ui, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.shadowColor = 'rgba(0,0,0,0.7)';
      ctx.shadowBlur = 4;
      ctx.fillText('🎉 ' + b.label + ' ' + date.slice(5).replace('-', '/'), x, top + 6);
      ctx.restore();
    });
  }
};
Chart.register(milestoneBreakPlugin);

// ===== 里程碑水平参考线:plugin 绘制 (原作 dataset 会把 y 轴撑到 140-260,2026-09-14 修) =====
// 只画落在 y 轴范围内的线,右端直接标注体重值 (原 legend 被 filter 隐藏,虚线无标识);
// 更远的目标线由进度环/里程碑行/模拟器呈现
var milestoneLinesPlugin = {
  id: 'milestoneLines',
  afterDatasetsDraw: function(chart) {
    if (chart.canvas.id !== 'timeline') return;
    var y = chart.scales.y, area = chart.chartArea;
    if (!y || !area) return;
    var ctx = chart.ctx;
    ctx.save();
    MILESTONES.forEach(function(m) {
      if (m.weight < y.min || m.weight > y.max) return;
      var py = y.getPixelForValue(m.weight);
      ctx.setLineDash([3, 3]);
      ctx.strokeStyle = m.color;
      ctx.globalAlpha = 0.55;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(area.left, py);
      ctx.lineTo(area.right, py);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.globalAlpha = 1;
      ctx.font = 'bold 10px system-ui, sans-serif';
      ctx.textAlign = 'right';
      ctx.textBaseline = 'bottom';
      ctx.shadowColor = 'rgba(0,0,0,0.75)';
      ctx.shadowBlur = 4;
      ctx.fillStyle = m.color;
      ctx.fillText(m.weight.toFixed(m.weight % 1 ? 1 : 0), area.right - 4, py - 3);
      ctx.shadowBlur = 0;
    });
    ctx.restore();
  }
};
Chart.register(milestoneLinesPlugin);

// ===== 十字参考线:hover 时在吸附点画竖虚线 + 焦点描圈 (数据勘探感) =====
var crosshairPlugin = {
  id: 'crosshair',
  afterDraw: function(chart) {
    var id = chart.canvas.id;
    if (id !== 'timeline' && id !== 'last14') return;
    var tt = chart.tooltip;
    if (!tt || !tt.getActiveElements) return;
    var actives = tt.getActiveElements();
    if (!actives || !actives.length) return;
    var el = actives[0].element;
    if (!el) return;
    var yAxis = chart.scales.y;
    var ctx = chart.ctx;
    ctx.save();
    ctx.setLineDash([4, 4]);
    ctx.strokeStyle = 'rgba(148,163,184,0.35)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(el.x, yAxis.top);
    ctx.lineTo(el.x, yAxis.bottom);
    ctx.stroke();
    // 焦点描圈 (白圈放大套住当前点)
    ctx.setLineDash([]);
    ctx.strokeStyle = 'rgba(230,233,239,0.55)';
    ctx.lineWidth = 1.4;
    ctx.beginPath();
    ctx.arc(el.x, el.y, 7, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
  }
};
Chart.register(crosshairPlugin);

// ===== 最新实测点发光标记:timeline 当前位一眼锁定 (静态光晕+白芯描圈,不耗 rAF) =====
var latestPointGlowPlugin = {
  id: 'latestPointGlow',
  afterDatasetsDraw: function(chart) {
    if (chart.canvas.id !== 'timeline') return;
    var meta = chart.getDatasetMeta(0);  // dataset 0 = 晨重 (实测)
    if (!meta || !meta.data || !meta.data.length) return;
    // 晨重已铺到统一日期轴上,末尾可能是 null (当天只有晚重/只有注射),往前找最后一个实点
    var last = null;
    for (var i = meta.data.length - 1; i >= 0; i--) {
      var el = meta.data[i];
      if (el && !el.skip && isFinite(el.y)) { last = el; break; }
    }
    if (!last) return;
    var ctx = chart.ctx;
    ctx.save();
    var g = ctx.createRadialGradient(last.x, last.y, 0, last.x, last.y, 17);
    g.addColorStop(0, 'rgba(163,230,53,0.55)');
    g.addColorStop(1, 'rgba(163,230,53,0)');
    ctx.fillStyle = g;
    ctx.beginPath(); ctx.arc(last.x, last.y, 17, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.9)';
    ctx.lineWidth = 1.6;
    ctx.beginPath(); ctx.arc(last.x, last.y, 5.5, 0, Math.PI * 2); ctx.stroke();
    ctx.restore();
  }
};
Chart.register(latestPointGlowPlugin);

// ===== 1. 时间线 =====
lazyChart('timeline', function () {
  // Y 轴动态范围:取晨重+晚重全部数据 ± padding,注射标记钉在数据最高点上方
  var tlWeights = [];
  RAW.forEach(function(d) {
    if (d.morning !== null) tlWeights.push(d.morning);
    if (d.evening !== null) tlWeights.push(d.evening);
  });
  var tlMax = Math.max.apply(null, tlWeights);
  var tlMin = Math.min.apply(null, tlWeights);
  var tlMarkerY = Math.round((tlMax + 2) * 10) / 10;  // 注射标记:数据最高点上方 2 斤
  // Y 轴显式锁在数据范围 (原 suggestedMin/Max 只是建议,挡不住 10 条里程碑参考线
  // dataset 把轴撑到 140-260,数据被压进上半 44% —— 2026-09-14 实测修)。
  // 下限向下放宽一格,让最近的一个未破里程碑 (当前是 188) 仍留在图内。
  // ⚠️ 所有里程碑对照原始基线 tlBase 判断 (不能拿已改写的 tlYMin 比较而链式连拉
  //    160→150→145,重新撑大轴);tlYMin 取所有合格候选里最深的一条
  var tlBase = tlMin - 3;
  var tlYMin = tlBase;
  MILESTONES.forEach(function(m) {
    if (m.weight < tlBase && m.weight >= tlBase - 10) tlYMin = Math.min(tlYMin, m.weight - 2);
  });
  var tlYMax = Math.max(tlMax + 6, tlMarkerY + 2);
  // 晨重线下方渐变填充 (canvas 渐变,随高度渐变淡出)
  var ctxT = document.getElementById('timeline').getContext('2d');
  var gradT = ctxT.createLinearGradient(0, 0, 0, 440);
  gradT.addColorStop(0, 'rgba(163,230,53,0.16)');
  gradT.addColorStop(1, 'rgba(163,230,53,0.02)');

  // ⚠️ interaction mode:'index' 是按**数组下标**对齐,不是按日期。
  // 各 dataset 长度不同 (晨重实测 89 / 插值 27 / 晚重 28 / 注射 16) 时,
  // tooltip 会把别的日期的值和标题混进来 (实测:悬停 5/13 标题显示 5/29、
  // 晚重行显示 7/13 的值)。修法:所有 dataset 铺在同一条日期轴上,
  // 缺失处填 null,下标即日期,index 模式才成立。
  var AXIS = (function() {
    var seen = {}, list = [];
    RAW.forEach(function(d){ if (!seen[d.date]) { seen[d.date] = 1; list.push(d.date); } });
    INJECTIONS.forEach(function(i){ if (!seen[i.date]) { seen[i.date] = 1; list.push(i.date); } });
    return list.sort();
  })();
  function alignBy(records, pick) {
    var byDate = {};
    records.forEach(function(r){ byDate[r.date] = r; });
    return AXIS.map(function(date) {
      var r = byDate[date];
      var v = r ? pick(r) : null;
      return v === null || v === undefined ? {x: date, y: null} : v;
    });
  }
  var ma7ByDate = {};
  computeMA7(REAL_POINTS).forEach(function(p){ ma7ByDate[p.x] = p.y; });

  // 里程碑水平参考线不再作 dataset (会把 y 轴撑大,见上方 tlYMin 注释),改由
  // milestoneLinesPlugin 绘制;原 tooltip/legend 里的 isMilestone filter 已随 dataset 删除
  new Chart(document.getElementById('timeline').getContext('2d'), {
    type: 'line',
    data: { datasets: [
      {
        label: '晨重 (实测)',
        data: alignBy(REAL_POINTS, function(d) {
          return {x: d.date, y: d.morning, isQClaw: d.note && d.note.indexOf('QClaw') !== -1, note: d.note};
        }),
        borderColor: '#a3e635', backgroundColor: gradT, borderWidth: 2, spanGaps: true,
        pointRadius: function(ctx) { var v = ctx.raw; return v && v.isQClaw ? 2 : 2.5; },
        pointBackgroundColor: function(ctx) { var v = ctx.raw; return v && v.isQClaw ? '#94a3b8' : '#a3e635'; },
        pointHoverRadius: 6, tension: 0.1, fill: true, order: 1
      },
      {
        // spanGaps:false → 4/17-5/12 的插值段自成一条,不再和孤立的 8/14 插值点连一条横贯全图的虚线
        label: '晨重 (起点/插值)',
        data: alignBy(RAW, function(d) {
          if (d.morning === null) return null;
          var note = d.note || '';
          if (note.indexOf('[插值') === -1 && note.indexOf('[起点') === -1) return null;
          return {x: d.date, y: d.morning, isInterp: true, note: d.note};
        }),
        borderColor: COLOR_INTERP, backgroundColor: COLOR_INTERP + '0d', borderWidth: 1.5,
        borderDash: [5, 5], pointRadius: 2, pointBackgroundColor: COLOR_INTERP, spanGaps: false,
        pointHoverRadius: 5, tension: 0, fill: false, order: 3, animation: { delay: 120 }
      },
      {
        label: 'MA7 (7 日均)',
        data: AXIS.map(function(date){ return {x: date, y: ma7ByDate[date] != null ? ma7ByDate[date] : null}; }),
        borderColor: COLOR_MA7, borderWidth: 2, pointRadius: 0, pointHoverRadius: 4, spanGaps: true,
        tension: 0.3, fill: false, borderDash: [2, 3], order: 0, animation: { delay: 240 }
      },
      {
        label: '晚重',
        data: alignBy(RAW, function(d){ return d.evening === null ? null : {x: d.date, y: d.evening}; }),
        borderColor: '#fbbf24', borderWidth: 1.5, borderDash: [4,4], pointRadius: 3, pointStyle: 'triangle',
        spanGaps: true, tension: 0.1, fill: false, order: 2, animation: { delay: 360 }
      }
    ].concat([
      {
        label: '替尔泊肽注射',
        data: alignBy(INJECTIONS, function(i){
          return {x: i.date, y: tlMarkerY, note: '💉 ' + i.dose + 'mg' + (i.note && i.note !== '—' ? ' · ' + i.note : '')};
        }),
        borderColor: '#fb7185', pointRadius: 8, pointStyle: 'rectRot', showLine: false, order: -1, animation: { delay: 500 }
      }
    ]) },
    options: {
      responsive: true, maintainAspectRatio: false,
      interaction: {mode:'index', intersect:false},
      plugins: {
        legend: { position:'top', labels: { boxWidth: 12 } },
        tooltip: {
          callbacks: {
            label: function(ctx) {
              // 注射事件:显示剂量/备注 (y 值是伪坐标,无意义,不展示)
              if (ctx.dataset.label === '替尔泊肽注射') {
                return ctx.raw && ctx.raw.note ? ctx.raw.note : '注射';
              }
              return ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(1) + ' 斤';
            },
            afterBody: function(items) {
              // 取当天晨重点自带的 note (注射备注已在 label 里,跳过),折行后返回数组
              for (var i = 0; i < items.length; i++) {
                if (items[i].dataset.label === '替尔泊肽注射') continue;
                var raw = items[i].raw;
                if (raw && raw.note) return [''].concat(wrapNoteLines(noteToText(raw.note)));
              }
              return '';
            }
          }
        }
      },
      scales: {
        x: { type: 'time', time: {unit: 'week', displayFormats: {week: 'MM-dd'}}, title: {display: true, text: '日期'} },
        y: { title: {display: true, text: '体重 (斤)'},
          min: Math.floor(tlYMin), max: Math.ceil(tlYMax), reverse: false }
      }
    }
  });
});

// ===== 1b. 近 14 天体重曲线 =====
lazyChart('last14', function () {
  var last14 = REAL_POINTS.slice(-14);
  var pts = last14.map(function(d){return {x: d.date, y: d.morning};});
  // ⚠️ MA7 必须在**全序列**上算完再切尾,直接 computeMA7(last14) 会让窗口在切片边界被截断:
  //    首点窗口只有 1 个数 → 8/16 画成 199.6 而真值 201.07 (偏差 1.5 斤),
  //    同一条 MA7 在本图 / 时间线 / 卡片三处对不上 (2026-08-29 修)
  var ma7Pts = computeMA7(REAL_POINTS).slice(-14);
  var first = last14[0] ? last14[0].morning : 0;
  var last = last14[last14.length-1] ? last14[last14.length-1].morning : 0;
  var delta = (last - first).toFixed(1);
  var color = last < first ? '#a3e635' : '#fb7185';
  // 晨重线下方渐变填充
  var ctxL = document.getElementById('last14').getContext('2d');
  var gradL = ctxL.createLinearGradient(0, 0, 0, 360);
  gradL.addColorStop(0, color + '26');
  gradL.addColorStop(1, color + '00');
  new Chart(document.getElementById('last14').getContext('2d'), {
    type: 'line',
    data: { datasets: [
      { label: '晨重 (斤)', data: pts, borderColor: color, backgroundColor: gradL,
        borderWidth: 2, pointRadius: 2.5, pointHoverRadius: 5, tension: 0.25, fill: true, order: 2 },
      { label: 'MA7', data: ma7Pts, borderColor: COLOR_MA7, borderWidth: 1.5,
        borderDash: [2,3], pointRadius: 0, fill: false, tension: 0.3, order: 1 }
      // 颜色/虚线取 COLOR_MA7,与时间线同源 (原琥珀 #fbbf24,同一实体跨图不同色)
    ]},
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top' },
        tooltip: { callbacks: {
          label: function(ctx){ return ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(1) + ' 斤'; }
        }},
        title: { display: true, text: '近 14 天 Δ ' + (delta > 0 ? '+' : '') + delta + ' 斤', color: '#8892a0', font: { size: 13 } }
      },
      scales: {
        x: { type: 'time', time: { unit: 'day', displayFormats: { day: 'MM-dd' } }, title: { display: true, text: '日期' } },
        y: { title: { display: true, text: '体重 (斤)' }, ticks: { callback: function(v){ return v.toFixed(0); } } }
      }
    }
  });
});

// ===== (每周累计图已于 2026-08-26 移除:周结论由每周卡片 stat-week + 平台期雷达覆盖;
//  weeklyData 数据源保留,stat-week / 执行率卡 / 平台期周停滞仍在用) =====

// ===== (替尔泊肽剂量阶梯图已于 2026-08-26 移除:注射信息由
//  timeline 注射点 / 距下次注射卡 / 针后反弹卡覆盖) =====

// ===== (星期模式已于 2026-08-26 移除:周末效应信息增量低) =====

// ===== 8. 数据表 (默认最近 30 条,可"加载全部/收起") =====
var RECENT_DEFAULT = 30;
// 「较前值」= 与"前一条有晨重的记录"比 (含[插值]/[噪音]行,故表头叫较前值而非较上条实测)。
// ⚠️ 原实现在倒序数组上维护 prev,prev 指向的是更晚的一天 → 整列符号+基准全错
//    (如 8/22 实际 -2.0 被显示成 +0.4,首行差值永远丢失)。改为先按升序算好 delta。
var DELTA_BY_DATE = (function() {
  var map = {}, prev = null;
  for (var i = 0; i < RAW.length; i++) {
    var r = RAW[i];
    if (r.morning === null) continue;  // 跳过剔除行 (如 6/2 [异常 已剔除]),否则会算出假差值
    map[r.date] = prev ? (r.morning - prev.morning) : null;
    prev = r;
  }
  return map;
})();
function renderTableRows(startIdx, endIdx) {
  var tbody = document.querySelector('#recent tbody');
  var all = RAW.slice().reverse();
  var end = Math.min(endIdx, all.length);
  for (var i = startIdx; i < end; i++) {
    var row = all[i];
    var delta = row.morning !== null ? DELTA_BY_DATE[row.date] : null;
    if (delta === undefined) delta = null;
    var cumulative = row.morning !== null ? (row.morning - CONFIG.startWeight) : null;
    var tr = document.createElement('tr');
    var weekday = parseLocalDate(row.date).toLocaleDateString('zh-CN', {weekday:'short'});
    var deltaCell = delta === null ? '<td class="muted">—</td>'
      : '<td class="' + (delta < 0 ? 'negative' : delta > 0 ? 'positive' : 'muted') + '">' + (delta > 0 ? '+' : '') + delta.toFixed(1) + '</td>';
    var cumCell = cumulative === null ? '<td class="muted">—</td>'
      : '<td class="' + (cumulative <= 0 ? 'negative' : 'positive') + '">' + (cumulative > 0 ? '+' : '') + cumulative.toFixed(1) + '</td>';
    // 标签 + markdown 渲染 (备注里 **加粗** 星号不再裸奔)
    var noteHtml = noteToHtml(row.note || '');
    if (noteHtml.indexOf('QClaw') !== -1) noteHtml = '<span class="tag tag-qclaw">QClaw</span> ' + noteHtml;
    if (noteHtml.indexOf('噪音') !== -1) noteHtml += ' <span class="tag tag-noise">噪音</span>';
    tr.innerHTML =
      '<td>' + row.date + '</td>' +
      '<td>' + weekday + '</td>' +
      '<td><strong>' + (row.morning !== null ? row.morning.toFixed(1) : '—') + '</strong></td>' +
      '<td class="muted">' + (row.evening !== null ? row.evening.toFixed(1) : '—') + '</td>' +
      deltaCell + cumCell +
      '<td class="note-cell">' + noteHtml + '</td>';
    tbody.appendChild(tr);
  }
}
// 加载全部 ↔ 收起 (原实现只能"加载全部",无法收回)
var showAllRows = false;
function toggleTableRows() {
  showAllRows = !showAllRows;
  var tbody = document.querySelector('#recent tbody');
  tbody.innerHTML = '';
  var btn = document.getElementById('showAllBtn');
  if (showAllRows) {
    renderTableRows(0, RAW.length);
    btn.innerHTML = '收起';
  } else {
    renderTableRows(0, RECENT_DEFAULT);
    btn.innerHTML = '加载全部 <span id="total-records">' + RAW.length + '</span> 条';
  }
}
(function buildTable() {
  document.getElementById('record-count').textContent = RAW.length;
  // 累计列表头与 CONFIG.startWeight 联动 (原硬编码 244,绕过了 CONFIG 单一来源)
  var cumTh = document.querySelector('#recent thead th:nth-child(6)');
  if (cumTh) cumTh.textContent = '累计 (vs ' + CONFIG.startWeight.toFixed(0) + ')';
  renderTableRows(0, RECENT_DEFAULT);
  var btn = document.getElementById('showAllBtn');
  btn.innerHTML = '加载全部 <span id="total-records">' + RAW.length + '</span> 条';
  if (RAW.length <= RECENT_DEFAULT) btn.style.display = 'none';
  btn.addEventListener('click', toggleTableRows);
})();

// ===== 拖拽排序 (HTML5 Drag & Drop + localStorage 持久化) =====
(function initDragSort() {
  // v3:2026-08-26 卡区重排 + 新卡(针后反弹/9·27冲刺) —— 升 key 让所有用户吃到新默认顺序,
  // 旧 v2 记忆会把新卡片压在末尾
  var GRIDS = [
    { id: 'stat-cards-grid', key: 'weight-dash-order-summary-v3' },
    { id: 'pred-cards-grid', key: 'weight-dash-order-pred-v3' }
  ];

  GRIDS.forEach(function(g) {
    var grid = document.getElementById(g.id);
    if (!grid) return;

    // 恢复保存的顺序
    restoreOrder(grid, g.key);

    var dragSrc = null;

    grid.querySelectorAll('.card').forEach(function(card) {
      card.setAttribute('draggable', 'true');

      card.addEventListener('dragstart', function(e) {
        dragSrc = card;
        card.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', card.dataset.cardId || '');
      });

      card.addEventListener('dragend', function() {
        card.classList.remove('dragging');
        grid.querySelectorAll('.card').forEach(function(c) {
          c.classList.remove('drag-over');
        });
        saveOrder(grid, g.key);
        dragSrc = null;  // 不清空的话 touchstart 的 `if (dragSrc) return` 会永久挡住触屏拖拽
      });

      card.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        if (dragSrc && card !== dragSrc) {
          grid.querySelectorAll('.card').forEach(function(c) {
            c.classList.remove('drag-over');
          });
          card.classList.add('drag-over');
        }
      });

      card.addEventListener('dragleave', function() {
        card.classList.remove('drag-over');
      });

      card.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (!dragSrc || card === dragSrc) return;

        // 判断插入位置: 鼠标在卡片左半 → 插入前面, 右半 → 插入后面
        var rect = card.getBoundingClientRect();
        var midX = rect.left + rect.width / 2;
        if (e.clientX < midX) {
          grid.insertBefore(dragSrc, card);
        } else {
          grid.insertBefore(dragSrc, card.nextSibling);
        }
        saveOrder(grid, g.key);
      });

      // ===== 移动端触摸拖拽 (长按 250ms 激活,防滚动冲突) =====
      card.addEventListener('touchstart', function() {
        var self = this;
        self._lpTimer = setTimeout(function() {
          if (dragSrc) return;  // 已有拖拽进行中
          dragSrc = self;
          self.classList.add('dragging');
          self.style.touchAction = 'none';  // 激活后禁止页面滚动
          if (navigator.vibrate) navigator.vibrate(15);  // 触觉反馈
        }, 250);
      }, {passive: true});

      card.addEventListener('touchmove', function(e) {
        if (!dragSrc || dragSrc !== this) return;
        e.preventDefault();  // 拖拽中禁止滚动
        var touch = e.touches[0];
        var el = document.elementFromPoint(touch.clientX, touch.clientY);
        var target = el ? el.closest('.card') : null;
        grid.querySelectorAll('.card').forEach(function(c) { c.classList.remove('drag-over'); });
        if (target && target !== dragSrc) target.classList.add('drag-over');
      }, {passive: false});

      card.addEventListener('touchend', function(e) {
        clearTimeout(this._lpTimer);
        if (!dragSrc || dragSrc !== this) return;
        var touch = e.changedTouches[0];
        var el = document.elementFromPoint(touch.clientX, touch.clientY);
        var target = el ? el.closest('.card') : null;
        if (target && target !== dragSrc) {
          var rect = target.getBoundingClientRect();
          if (touch.clientX < rect.left + rect.width / 2) {
            grid.insertBefore(dragSrc, target);
          } else {
            grid.insertBefore(dragSrc, target.nextSibling);
          }
        }
        dragSrc.classList.remove('dragging');
        dragSrc.style.touchAction = '';
        grid.querySelectorAll('.card').forEach(function(c) { c.classList.remove('drag-over'); });
        saveOrder(grid, g.key);
        dragSrc = null;
      });

      card.addEventListener('touchcancel', function() {
        clearTimeout(this._lpTimer);
        if (dragSrc === this) {
          this.classList.remove('dragging');
          this.style.touchAction = '';
          grid.querySelectorAll('.card').forEach(function(c) { c.classList.remove('drag-over'); });
          dragSrc = null;
        }
      });

      // ===== 键盘可访问排序 (Alt+←/→ 交换位置,替代只能鼠标拖) =====
      card.setAttribute('tabindex', '0');
      card.addEventListener('keydown', function(e) {
        if (!e.altKey || (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight')) return;
        e.preventDefault();
        var cards = Array.prototype.slice.call(grid.querySelectorAll('.card'));
        var idx = cards.indexOf(card);
        var target = e.key === 'ArrowLeft' ? cards[idx - 1] : cards[idx + 1];
        if (target) {
          if (e.key === 'ArrowLeft') grid.insertBefore(card, target);
          else grid.insertBefore(card, target.nextSibling);
          saveOrder(grid, g.key);
          card.focus();
        }
      });
    });
  });

  function saveOrder(grid, key) {
    var ids = [];
    grid.querySelectorAll('.card').forEach(function(c) {
      var id = c.dataset.cardId;
      if (id) ids.push(id);
    });
    try {
      localStorage.setItem(key, JSON.stringify(ids));
    } catch(e) {}
  }

  function restoreOrder(grid, key) {
    var saved;
    try {
      saved = JSON.parse(localStorage.getItem(key) || '[]');
    } catch(e) { saved = []; }
    if (!saved.length) return;

    // 按 saved 顺序重排 DOM
    var cardMap = {};
    grid.querySelectorAll('.card').forEach(function(c) {
      var id = c.dataset.cardId;
      if (id) cardMap[id] = c;
    });

    saved.forEach(function(id) {
      var card = cardMap[id];
      if (card) {
        grid.appendChild(card);  // 移到末尾,按 saved 顺序逐个 append
        delete cardMap[id];
      }
    });

    // 未保存的新卡片留在末尾 (保持原相对顺序)
    Object.keys(cardMap).forEach(function(id) {
      grid.appendChild(cardMap[id]);
    });
  }
})();

function resetCardOrder(which) {
  var keyMap = {
    'summary': 'weight-dash-order-summary-v3',
    'pred': 'weight-dash-order-pred-v3'
  };
  var list = which === 'all' ? ['summary', 'pred'] : [which];
  var any = false;
  list.forEach(function(k) {
    if (!keyMap[k]) return;
    try { localStorage.removeItem(keyMap[k]); any = true; } catch(e) {}
  });
  if (any) location.reload();
}

// ===== 动效增强 =====
// 1. (鼠标跟随光晕已退役 —— Midnight Lime 重构后 style.css 里没有任何规则用
//    --mx/--my,原实现每次 mousemove 都 rAF + getBoundingClientRect() 强制布局,纯开销)
// 2. (扫光条注入已退役 —— 改用 CSS hover 高光)
// 3. 滚动渐入:给 section 下的主要块(图表/环/里程碑/表格)加 .reveal,进入视口时点亮
//    兜底:IO 失效/被扩展干扰时,滚动监听 + 定时检查强制点亮,杜绝整块空白
(function setupReveal() {
  var targets = document.querySelectorAll(
    '.chart-wrap, .ring-card, .milestones, .mile-ruler, table, .prediction-grid'
  );
  function forceShow(el) { el.classList.add('in'); }
  function checkVisible() {
    var vh = window.innerHeight || document.documentElement.clientHeight;
    var changed = false;
    targets.forEach(function (t) {
      if (t.classList.contains('in')) return;
      var r = t.getBoundingClientRect();
      if (r.top < vh && r.bottom > 0) { forceShow(t); changed = true; }
    });
    if (changed) window.removeEventListener('scroll', checkVisible);
  }
  if (!('IntersectionObserver' in window)) {
    targets.forEach(forceShow);
    return;
  }
  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add('in'); obs.unobserve(en.target); }
    });
  }, { threshold: 0.12 });
  targets.forEach(function (t) { t.classList.add('reveal'); obs.observe(t); });
  // 兜底 1:2.5s 后在视口内的元素强制点亮
  setTimeout(checkVisible, 2500);
  // 兜底 2:任何滚动都检查视口内元素 (兼容 IO 不回调的环境)
  window.addEventListener('scroll', checkVisible, { passive: true });
})();

// ===== 破关庆祝:检测最近 7 天内是否首次突破里程碑,是则播放一次 =====
(function playRecentBreakCelebration() {
  var el = document.getElementById('celebration');
  var textEl = document.getElementById('celebration-text');
  var partsEl = document.getElementById('celebration-particles');
  if (!el || !textEl || !partsEl) return;

  // 当前体重:未破关 / 已反弹回关口之上 → 不庆祝
  var cur = META.currentWeight != null ? META.currentWeight : null;
  if (cur == null) return;
  var curDate = META.currentDate || null;
  var milestones = [
    { weight: CONFIG.milestone200, label: '超越 2022 纪录' },
    { weight: CONFIG.milestone188, label: '追平历史最低' },
    { weight: CONFIG.milestone175, label: '中段关口' },
    { weight: CONFIG.target160, label: '过渡目标' },
    { weight: CONFIG.milestone150, label: '准正常线' },
    { weight: CONFIG.target145, label: '终极目标' }
  ];
  // 找"当前体重已破、且最近 7 天内首次突破"的里程碑 (取突破最近的那个)
  var recent = null;
  milestones.forEach(function(ms) {
    if (cur > ms.weight) return;  // 当前仍在关口之上 → 跳过
    for (var i = 0; i < REAL_POINTS.length; i++) {
      if (REAL_POINTS[i].morning <= ms.weight) {
        var breakDate = REAL_POINTS[i].date;
        var daysAgo = curDate ? Math.round((parseLocalDate(curDate) - parseLocalDate(breakDate)) / 86400000) : 0;
        if (daysAgo >= 0 && daysAgo <= 7) {
          if (!recent || daysAgo < recent.daysAgo) {
            recent = { weight: ms.weight, label: ms.label, date: breakDate, daysAgo: daysAgo };
          }
        }
        break;  // 每个里程碑只取首次突破日
      }
    }
  });

  if (!recent) return;

  // 每个里程碑只庆祝一次 (localStorage 记忆,刷新不重复播放)
  try {
    var celebKey = 'weightViz_celebrated_' + recent.weight;
    if (localStorage.getItem(celebKey)) return;
    localStorage.setItem(celebKey, '1');
  } catch (e) { /* localStorage 被禁用时仍播放 */ }

  textEl.textContent = '🎉 破 ' + recent.weight + ' · ' + recent.label;

  // 生成金色粒子 (24 颗,随机飞散方向)
  var colors = ['#fbbf24', '#f59e0b', '#fde68a', '#facc15', '#a3e635'];
  for (var p = 0; p < 24; p++) {
    var s = document.createElement('span');
    var ang = Math.random() * Math.PI * 2;
    var dist = 12 + Math.random() * 26;  // vmin 半径
    s.style.setProperty('--dx', Math.cos(ang) * dist + 'vmin');
    s.style.setProperty('--dy', Math.sin(ang) * dist + 'vmin');
    s.style.background = colors[p % colors.length];
    s.style.animationDelay = (Math.random() * 0.25) + 's';
    s.style.width = (5 + Math.random() * 6) + 'px';
    s.style.height = s.style.width;
    partsEl.appendChild(s);
  }

  // 播放一次,结束后清理
  el.classList.add('show');
  setTimeout(function() {
    el.classList.remove('show');
    partsEl.innerHTML = '';
  }, 2600);
})();

// ===== 初始化顺序:折叠状态恢复 (最后执行,此时 section 均已渲染) =====
(function initSections() {
  // 默认折叠的 section 初始化
  document.querySelectorAll('section.collapsed .section-body').forEach(function(b) {
    b.style.maxHeight = '0';
    b.style.opacity = '0';
  });
  document.querySelectorAll('section:not(.collapsed) .section-body').forEach(function(b) {
    b.style.maxHeight = 'none';
    b.style.opacity = '1';
  });
  // 加载用户上次的状态 (覆盖默认; key 稳定,不再受动态标题影响)
  restoreCollapsedState();
  // 同步"展开全部"按钮状态
  allExpanded = document.querySelectorAll('section.collapsed').length === 0;
  document.getElementById('expandAll').textContent = allExpanded ? '折叠全部' : '展开全部';
})();


// ============================================================
// 2026-08-22 优化新增:平台期雷达 + 节奏模拟器
// ============================================================

// ===== 平台期雷达:扫描历史新低间隙,统计每次平台期持续与突破后跌幅 =====
// 2026-08-26 升级:MA7 停滞口径 + 突破率 chip + "突破还需"诊断 + 反弹归因条
(function plateauRadar() {
  var pts = REAL_NO_NOISE;  // 已按日期升序;剔除噪音/插值/起点
  // 样本不足时原来直接 return,section 标题永远停在"分析中…"且面板全空
  if (!pts || pts.length < 10) {
    var sEl = document.getElementById('plateau-status');
    var nEl = document.getElementById('plateau-now');
    if (sEl) sEl.textContent = '数据不足';
    if (nEl) nEl.innerHTML = '<span class="pn-icon">⏳</span><div><div class="pn-main">样本不足,暂不分析</div>' +
      '<div class="pn-sub">需要 ≥10 条实测晨重 (当前 ' + (pts ? pts.length : 0) + ' 条)</div></div>';
    return;
  }
  function D(s) { return parseLocalDate(s); }
  function diffDays(a, b) { return Math.round((D(b) - D(a)) / 86400000); }

  // 单遍扫描:running-min 间隙 >=4 天记为一次平台期
  var plateaus = [], runMin = Infinity, lastLow = null;
  pts.forEach(function(p) {
    if (p.morning < runMin) {
      if (lastLow) {
        var gap = diffDays(lastLow, p.date);
        if (gap >= 4) plateaus.push({ from: lastLow, to: p.date, days: gap, low: runMin });
      }
      runMin = p.morning; lastLow = p.date;
    }
  });

  // 每次突破后 7 天内的最大额外跌幅
  plateaus.forEach(function(pl) {
    var t0 = D(pl.to).getTime(), end = t0 + 7 * 86400000, minAfter = Infinity;
    pts.forEach(function(p) {
      var t = D(p.date).getTime();
      if (t >= t0 && t <= end && p.morning < minAfter) minAfter = p.morning;
    });
    pl.drop = (minAfter < Infinity) ? +(pl.low - minAfter).toFixed(1) : null;
  });

  // 当前状态 口径A:新低停滞天数 (基准=数据最新日,与其它卡口径统一;
  // 数据滞后时 header 已有 "⚠ 最新 X (今天 Y)" 徽章提示,不在这里混用真实今天)
  var TODAY_REF = META.currentDate || fmtLocalDate(new Date());
  var stallDays = Math.max(0, diffDays(lastLow, TODAY_REF));
  var weeklyStall = 0;
  (typeof weeklyData !== 'undefined' ? weeklyData : []).forEach(function(w) {
    if (w.inProgress) return;  // 进行中周未结算,|delta| 偏小不代表停滞 (2026-09-16 修)
    if (Math.abs(w.delta) < 0.5) weeklyStall++; else weeklyStall = 0;
  });
  // 口径B:MA7 停滞 —— 近 5 个 MA7 点首尾漂移 <0.2 (水分掩盖脂肪下降的典型形态)
  var ma7Series = computeMA7(REAL_POINTS);
  var maTail = ma7Series.slice(-5);
  var maDrift = maTail.length >= 2 ? +(maTail[maTail.length - 1].y - maTail[0].y).toFixed(2) : 99;
  var maStall = Math.abs(maDrift) < 0.2;

  var avgDays = plateaus.length ? Math.round(plateaus.reduce(function(s, p) { return s + p.days; }, 0) / plateaus.length) : 0;
  var maxDays = plateaus.reduce(function(m, p) { return Math.max(m, p.days); }, 0);
  var drops = plateaus.filter(function(p) { return p.drop !== null; });
  var avgDrop = drops.length ? (drops.reduce(function(s, p) { return s + p.drop; }, 0) / drops.length).toFixed(1) : null;

  // "突破还需"诊断:当前 MA7 与新低的差距 (MA7 压在新低之上 = 还有水分要消化)
  var curMA7 = ma7Series.length ? ma7Series[ma7Series.length - 1].y : runMin;
  var waterLoad = +(curMA7 - runMin).toFixed(1);
  var breakHint = waterLoad > 0
    ? '上次新低 ' + (lastLow || '?').slice(5).replace('-', '/') + ' (' + runMin.toFixed(1) + ') · 当前 MA7 超新低 +' + waterLoad + ' · 先消化水分即可真突破'
    : 'MA7 已压到新低线 ' + runMin.toFixed(1) + ' · 突破随时兑现';

  // 状态条 (双口径:新低停滞 或 MA7 停滞)
  var statusEl = document.getElementById('plateau-status');
  var nowEl = document.getElementById('plateau-now');
  var main, sub, ok;
  if (stallDays >= 4) {
    ok = false;
    main = '⏸ 新低停滞第 ' + stallDays + ' 天';
    sub = '历史 ' + plateaus.length + ' 次平台期平均 ' + avgDays + ' 天突破 · 最长 ' + maxDays + ' 天 · 这次也会破 · ' + breakHint;
  } else if (maStall) {
    ok = false;
    main = '⏸ MA7 停滞 (近 5 天漂移 ' + Math.abs(maDrift).toFixed(1) + ' 斤)';
    sub = '新低 ' + stallDays + ' 天前刚刷新 · 水分掩盖脂肪下降的典型形态 · ' + breakHint;
  } else if (weeklyStall >= 2) {
    ok = false;
    main = '⏸ 周净跌 <0.5 斤已持续 ' + weeklyStall + ' 周';
    sub = '不过新低 ' + stallDays + ' 天前刚刷新 · 平台期多为水分重组，历史突破率 100%';
  } else {
    ok = true;
    main = '✅ 节奏正常 · 双口径通畅';
    sub = '新低 ' + stallDays + ' 天前刚刷新 · MA7 近5天漂移 ' + maDrift.toFixed(1) + ' 斤 · 保持当前节奏即可';
  }
  if (statusEl) statusEl.textContent = main.replace(/^⏸ |^✅ /, '');
  if (nowEl) nowEl.innerHTML =
    '<span class="pn-icon">' + (ok ? '🟢' : '🟡') + '</span>' +
    '<div><div class="pn-main">' + main + '</div><div class="pn-sub">' + sub + '</div></div>';

  // ===== 反弹归因条:近 30 天反弹日备注关键词分类 (备注体系本就含钠/排便/熬夜标注) =====
  var attrEl = document.getElementById('plateau-attr');
  if (attrEl) {
    var kw = [
      [/钠|咸|凉菜|外卖|华莱士|高钠/, '💧 高钠/外卖'],
      [/未排便|未排空|便秘|排空/, '🚽 未排空'],
      [/熬夜|凌晨|睡眠不足|睡晚/, '😴 熬夜缺觉'],
      [/加餐|水果|夜宵|深夜/, '🍬 加餐/水果']
    ];
    var attrCount = [0, 0, 0, 0], other = 0, rebTotal = 0;
    var cutoff30 = fmtLocalDate(new Date(parseLocalDate(TODAY_REF).getTime() - 30 * 86400000));
    for (var i = 1; i < pts.length; i++) {
      if (pts[i].date < cutoff30) continue;
      if (pts[i].morning > pts[i - 1].morning) {
        rebTotal++;
        var note = pts[i].note || '', hit = false;
        kw.forEach(function(k, j) { if (k[0].test(note)) { attrCount[j]++; hit = true; } });
        if (!hit) other++;
      }
    }
    if (rebTotal > 0) {
      attrEl.style.display = '';
      var segs = kw.map(function(k, j) { return '<span class="pa-item">' + k[1] + ' <b>' + attrCount[j] + '</b></span>'; });
      attrEl.innerHTML = '<span class="pa-lead">🔍 近 30 天 <b>' + rebTotal + '</b> 次反弹归因</span>' +
        segs.join('') + (other ? '<span class="pa-item">其他 <b>' + other + '</b></span>' : '') +
        '<span class="pa-hint">' + (attrCount[0] + attrCount[1] >= rebTotal * 0.5 ? ' → 主流是水钠+未排,不是脂肪,别慌' : ' → 归因分散,留意真实摄入') + '</span>';
    } else {
      attrEl.style.display = 'none';
    }
  }

  // 统计 chips (5 枚:含历史突破率;plateaus 定义即"最终被突破的间隙"→ 天然 100%)
  var statsEl = document.getElementById('plateau-stats');
  if (statsEl) {
    function chip(v, l) { return '<div class="plateau-stat"><div class="ps-val">' + v + '</div><div class="ps-lab">' + l + '</div></div>'; }
    statsEl.innerHTML =
      chip(plateaus.length + ' 次', '历史平台期 (≥4天)') +
      chip(avgDays + ' 天', '平均持续') +
      chip(maxDays + ' 天', '最长一次') +
      chip('100%', '历史突破率') +
      chip(avgDrop !== null ? '-' + avgDrop + ' 斤' : '—', '突破后 7 天均跌');
  }

  // 明细列表 (最近 6 次,倒序,条长=相对最长平台期)
  var listEl = document.getElementById('plateau-list');
  if (listEl) {
    var maxRef = maxDays || 1;
    listEl.innerHTML = plateaus.slice(-6).reverse().map(function(p) {
      var pct = Math.round(p.days / maxRef * 100);
      return '<div class="plateau-row">' +
        '<span class="pr-range">' + p.from.slice(5).replace('-', '/') + ' 低点后</span>' +
        '<span class="pr-days">' + p.days + ' 天</span>' +
        '<div class="pr-bar"><i style="width:' + pct + '%"></i></div>' +
        '<span class="pr-drop">' + (p.drop !== null ? '突破后7天再跌 ' + p.drop + ' 斤' : '—') + '</span>' +
        '</div>';
    }).join('');
  }
})();

// ===== 节奏模拟器:拖动滑块按不同节奏推算各目标达成日 =====
(function paceSimulator() {
  var slider = document.getElementById('sim-slider');
  if (!slider) return;
  var curW = parseFloat(META.currentWeight);
  // 推算基准日 = 数据最新日 (原用 Date.now(),与预测卡/冲刺卡的 META.currentDate 口径打架,
  // 数据晚一天时同一个目标会给出两个达成日)
  var SIM_BASE = parseLocalDate(META.currentDate).getTime();

  // 预设节奏:近N天实测斜率 / 整体均值 / 最佳单周
  function recentRate(n) {
    var pts = REAL_NO_NOISE.slice(-n);
    if (pts.length < 2) return parseFloat(META.dailyDrop14d) || 0.08;
    var days = Math.max(1, Math.round((parseLocalDate(pts[pts.length - 1].date) - parseLocalDate(pts[0].date)) / 86400000));
    return Math.max(0.01, (pts[0].morning - pts[pts.length - 1].morning) / days);
  }
  // 预设三处同源 (label/dataset/初始值):建值时就钳制到滑块范围;实测斜率 ≤0 (持平/反弹)
  // 的预设不放 —— 原 Math.max(0.01,·) 把假节奏当实测展示,而它现在还是开机默认值,危害更大
  var presets = [];
  function addPreset(label, v) {
    v = Math.min(parseFloat(slider.max), Math.max(parseFloat(slider.min), v));
    if (v > 0) presets.push({ label: label, v: v });
  }
  var r14 = parseFloat(META.dailyDrop14d);
  if (!isFinite(r14)) r14 = recentRate(14);
  if (r14 > 0) addPreset('近14天', r14);
  // 近7天同理:斜率 >0 才是有意义的"节奏",反弹期直接不放
  var r7 = parseFloat(META.dailyDrop7d);
  if (!isFinite(r7)) r7 = recentRate(7);
  if (r7 > 0) addPreset('近7天', r7);
  addPreset('🎯 目标 -4斤/周', CONFIG.weeklyTarget / 7);
  addPreset('整体均值', (META.startWeight - curW) / Math.max(1, META.days));
  // 最佳单周:从 META 取 (原硬编码 'W15 最佳周' + 4.6/7,纪录刷新后会过期)
  // META 缺失/异常时直接不放该预设,不再用 4.6 兜底冒充当前纪录 (2026-09-16 修)
  var bw = parseFloat(META.bestWeekDelta);
  if (isFinite(bw) && bw < 0) addPreset((META.bestWeekLabel || '最佳单周') + ' 最佳周', Math.abs(bw) / 7);
  // 初始值跟随当前真实节奏 (原写死 0.08);目标节奏恒在,presets[0] 必存在
  slider.value = presets[0].v;
  var targets = [
    { w: 195, label: '195 · 下阶段', c: '#a3e635' },
    { w: CONFIG.milestone188, label: '188 · 历史最低', c: '#38bdf8' },
    { w: CONFIG.milestone175, label: '175 · 中段关口', c: '#34d399' },
    { w: CONFIG.target160, label: '160 · 过渡目标', c: '#fbbf24' },
    { w: CONFIG.milestone150, label: '150 · 准正常线', c: '#f472b6' },
    { w: CONFIG.target145, label: '145 · 终极目标', c: '#c4b5fd' }
  ];

  var presetsEl = document.getElementById('sim-presets');
  var gridEl = document.getElementById('sim-grid');
  var noteEl = document.getElementById('sim-note');
  var rateLabel = document.getElementById('sim-rate-label');

  presets.forEach(function(p) {
    var b = document.createElement('button');
    b.className = 'sim-chip';
    b.type = 'button';
    b.textContent = p.label + ' ' + p.v.toFixed(2);
    b.dataset.v = p.v.toFixed(2);
    b.dataset.exact = p.v;  // 精确值:两个预设量化到同一 0.01 档时 (0.57 vs 0.5714) 靠它选唯一高亮
    b.addEventListener('click', function() {
      // 预设建值时已钳制;直接赋精确值 (step=0.001 保留 3 位),同档两预设 (0.57/0.5714) 高亮才不串
      slider.value = p.v;
      render(true);
    });
    presetsEl.appendChild(b);
  });

  // 天数一律向上取整后再换算日期,否则 fmtDate 用小数天会比 "还需 N 天" 早一天
  // (44 天却显示 10/11,与「下一关」卡的 10/12 打架)
  function simDate(days) { return new Date(SIM_BASE + Math.ceil(days) * 86400000); }
  function fmtDate(days) {
    if (!isFinite(days) || days > 730) return '> 2 年';
    var dt = simDate(days);
    // 补零并复用 fmtLocalDate,与预测卡/冲刺卡的 "2027/01/09" 同格式 (跨年口径不再漂移)
    var md = fmtLocalDate(dt).slice(5).replace('-', '/');
    return dt.getFullYear() !== new Date(SIM_BASE).getFullYear() ? dt.getFullYear() + '/' + md : md;
  }

  function render(animate) {
    var rate = parseFloat(slider.value);
    var pct = ((rate - parseFloat(slider.min)) / (parseFloat(slider.max) - parseFloat(slider.min)) * 100).toFixed(1) + '%';
    slider.style.setProperty('--fill', pct);
    if (rateLabel) rateLabel.textContent = rate.toFixed(2);
    // 只亮精确值最近的那个预设 (两个 chip 量化后同档时不再双亮);拖到非预设值则全不亮
    var bestChip = null, bestDiff = Infinity;
    presetsEl.querySelectorAll('.sim-chip').forEach(function(c) {
      var diff = Math.abs(parseFloat(c.dataset.exact) - rate);
      if (diff < bestDiff) { bestDiff = diff; bestChip = c; }
    });
    presetsEl.querySelectorAll('.sim-chip').forEach(function(c) {
      c.classList.toggle('on', c === bestChip && bestDiff < 0.005);
    });
    gridEl.innerHTML = targets.map(function(t) {
      // 已达成的目标不再算"还需 N 天"(否则出负天数 + 过去的日期)
      if (curW <= t.w) {
        return '<div class="sim-tile" style="--tile-c:' + t.c + '">' +
          '<div class="st-target">' + t.label + '</div>' +
          '<div class="st-date">✅</div>' +
          '<div class="st-meta">已达成 · 低于 ' + t.w + ' 斤</div></div>';
      }
      var days = (curW - t.w) / rate;
      var far = !isFinite(days) || days > 730;
      var dt = simDate(days);
      var meta = far ? '按此节奏较远'
        : '还需 ' + Math.ceil(days) + ' 天 · ' + dt.getFullYear() + '年' + (dt.getMonth() + 1) + '月';
      return '<div class="sim-tile" style="--tile-c:' + t.c + '">' +
        '<div class="st-target">' + t.label + '</div>' +
        '<div class="st-date">' + fmtDate(days) + '</div>' +
        '<div class="st-meta">' + meta + '</div></div>';
    }).join('');
    // pop 入场:cascade 阶梯延迟 (仅初始化/点预设时;拖滑块 animate=false 避免高频重建闪烁)
    if (animate !== false) {
      gridEl.querySelectorAll('.sim-tile').forEach(function(t, i) {
        t.classList.add('pop');
        t.style.animationDelay = (i * 0.07) + 's';
      });
    }
    if (noteEl) {
      var totalDays = (curW - META.target145) / rate;
      noteEl.innerHTML = '按 <b>' + rate.toFixed(2) + ' 斤/天</b> 相当于每周 <b>-' + (rate * 7).toFixed(1) + ' 斤</b>' +
        ' · 从 ' + curW.toFixed(1) + ' 斤到 ' + META.target145 + ' 共需约 <b>' + (isFinite(totalDays) ? Math.ceil(totalDays) : '∞') + '</b> 天' +
        ' · 数据: weight_data.js (' + (window.__SYNC_TIME__ || '') + ')';
    }
  }

  slider.addEventListener('input', function() { render(false); });
  render(true);
})();

// ===== 针后 DayN 反弹分布:反弹日集中在针后第几天 (验证 5 天 vs 6 天打针节奏) =====
(function injectionRebound() {
  var el = document.getElementById('stat-inj-rebound');
  var metaEl = document.getElementById('stat-inj-rebound-meta');
  if (!el || !metaEl) return;
  if (!INJECTIONS.length || REAL_NO_NOISE.length < 10) { el.textContent = '数据不足'; return; }
  function dayNof(dateStr) {
    var t = parseLocalDate(dateStr).getTime(), last = null;
    for (var i = 0; i < INJECTIONS.length; i++) {
      if (parseLocalDate(INJECTIONS[i].date).getTime() <= t) last = INJECTIONS[i]; else break;
    }
    return last ? Math.round((t - parseLocalDate(last.date).getTime()) / 86400000) + 1 : null;  // 针当日 = Day1
  }
  // 只统计"当前剂量阶段"(最后一针的剂量首次出现日起 —— 爬坡期水合反应不同会稀释信号)
  // 原来把 '2026-07-22' 写死,剂量再变(升档/降档)统计口径就错
  var curDose = INJECTIONS[INJECTIONS.length - 1].dose;
  var phaseStart = INJECTIONS[INJECTIONS.length - 1].date;
  for (var pi = 0; pi < INJECTIONS.length; pi++) {
    if (INJECTIONS[pi].dose === curDose) { phaseStart = INJECTIONS[pi].date; break; }
  }
  var pts = REAL_NO_NOISE.filter(function(d) { return d.date >= phaseStart; });
  var early = { reb: 0, tot: 0 }, late = { reb: 0, tot: 0 };  // D1-3 vs D4+
  for (var i = 1; i < pts.length; i++) {
    var dn = dayNof(pts[i].date);
    if (!dn || dn > 7) continue;
    var bucket = dn <= 3 ? early : late;
    bucket.tot++;
    if (pts[i].morning > pts[i - 1].morning) bucket.reb++;
  }
  if (late.tot < 3) { el.textContent = '数据不足'; metaEl.textContent = curDose + 'mg 阶段样本不够'; return; }
  // early.tot 可为 0 (该阶段 Day1-3 恰好没称):0/0 会渲染 "NaN% (0/0天)" 且 worse 恒 false (2026-09-16 修)
  var eRate = early.tot ? Math.round(early.reb / early.tot * 100) : null;
  var lRate = Math.round(late.reb / late.tot * 100);
  var worse = eRate != null && lRate > eRate;
  // data-noroll:数字嵌在 "Day4+" 里,animateCountUp 会滚成 Day0+/Day2+ (原注释以为改成
  // "Day4+" 就规避了,实测并没有;正解是标记本元素跳过滚动)
  el.setAttribute('data-noroll', '1');
  el.innerHTML = '<span style="color:' + (worse ? 'var(--up)' : 'var(--accent)') + '">Day4+ ' + lRate + '%</span><span class="unit"> 反弹率</span>';
  metaEl.textContent = curDose + 'mg 阶段 (' + phaseStart.slice(5).replace('-', '/') + '起) · ' +
    (eRate != null
      ? 'Day1-3 ' + eRate + '% (' + early.reb + '/' + early.tot + '天) vs Day4-7 ' + lRate + '% (' +
        late.reb + '/' + late.tot + '天)' + (worse ? ' · 缩短间隔有据' : ' · 当前间隔合适')
      : 'Day1-3 无样本 · Day4-7 ' + lRate + '% (' + late.reb + '/' + late.tot + '天)');
})();

// ===== 9/27 冲刺倒计时:deadline vs 当前节奏的对标 =====
(function sprintCountdown() {
  var el = document.getElementById('pred-sprint');
  var metaEl = document.getElementById('pred-sprint-meta');
  var lblEl = document.getElementById('pred-sprint-label');
  if (!el || !metaEl) return;
  var target = CONFIG.target160;
  var sd = CONFIG.sprintDate;
  if (lblEl) lblEl.textContent = sd.slice(5).replace('-', '/') + ' 冲刺 ' + target.toFixed(0);
  var daysLeft = Math.ceil((parseLocalDate(sd) - parseLocalDate(META.currentDate)) / 86400000);
  var remain = parseFloat(META.currentWeight) - target;
  var dailyDrop = parseFloat(META.dailyDrop14d) || 0;
  if (daysLeft <= 0) {
    el.textContent = META.currentWeight <= target ? '✅ 已达成' : '已过期';
    metaEl.textContent = '冲刺窗口已关闭';
    return;
  }
  var needPerDay = remain / daysLeft;
  var needColor = needPerDay <= dailyDrop ? 'var(--accent)' : needPerDay <= dailyDrop * 1.5 ? '#fbbf24' : 'var(--up)';
  el.innerHTML = '剩 <span style="color:' + needColor + '">' + daysLeft + '</span> <span class="unit">天 · 需 -' + needPerDay.toFixed(2) + ' 斤/天</span>';
  if (dailyDrop > 0) {
    var reachDays = Math.ceil(remain / dailyDrop);
    var reach = new Date(parseLocalDate(META.currentDate).getTime() + reachDays * 86400000);
    var gap = reachDays - daysLeft;
    // 跨年达成日带年份,否则 "01/17" 歧义
    var curYear = parseLocalDate(META.currentDate).getFullYear();
    var reachStr = fmtLocalDate(reach).slice(5).replace('-', '/');
    if (reach.getFullYear() !== curYear) reachStr = reach.getFullYear() + '/' + reachStr;
    // 目标节奏对照:-4 斤/周 = -0.57/天,若维持则何时达成
    var goalRate = CONFIG.weeklyTarget / 7;
    var goalReach = new Date(parseLocalDate(META.currentDate).getTime() + Math.ceil(remain / goalRate) * 86400000);
    var goalStr = fmtLocalDate(goalReach).slice(5).replace('-', '/');
    if (goalReach.getFullYear() !== curYear) goalStr = goalReach.getFullYear() + '/' + goalStr;
    metaEl.textContent = '还需 ' + remain.toFixed(1) + ' 斤 · 按 ' + dailyDrop.toFixed(2) + ' 预计 ' +
      reachStr + ' 达成' + (gap > 0 ? ' · 落后 ' + gap + ' 天' : ' · 可提前 ' + (-gap) + ' 天') +
      ' | 若达 -4/周 → ' + goalStr;
  } else {
    metaEl.textContent = '还需 ' + remain.toFixed(1) + ' 斤 · 当前节奏停滞,无法推算';
  }
})();

// ===== (坚持热力图已于 2026-08-26 移除:用户反馈信息增量低) =====

// ===== 数值滚动入场:所有动态区块(stats/等效条/平台期/预测)渲染完毕后统一触发 =====
// (原在 computeStats 内触发,晚渲染的等效条/平台期数字滚不到;移到文件末尾统一滚)
animateCountUp();

// ===== 顶部滚动进度条 + aurora 视差 (同一个 rAF 节流 scroll 监听,不重复挂) =====
(function scrollProgress() {
  var bar = document.getElementById('scroll-progress');
  var aurora = document.querySelector('.aurora');
  if (!bar && !aurora) return;
  var ticking = false;
  function update() {
    ticking = false;
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    if (bar) bar.style.width = (max > 0 ? (h.scrollTop / max * 100) : 0).toFixed(2) + '%';
    // 背景视差:aurora 柔光随滚动缓缓上移 (0.04 极轻,只制造层次深度)
    if (aurora) aurora.style.transform = 'translateY(' + (h.scrollTop * -0.04).toFixed(1) + 'px)';
  }
  window.addEventListener('scroll', function() {
    if (!ticking) { ticking = true; requestAnimationFrame(update); }
  }, { passive: true });
  update();
})();

// ===== 按钮点击涟漪 (事件委托,覆盖动态生成的 sim-chip) =====
(function rippleButtons() {
  // 尊重系统"减弱动态效果"
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  document.addEventListener('click', function(e) {
    var btn = e.target && e.target.closest
      ? e.target.closest('.expand-all, .reset-order-btn, .show-more-btn, .sim-chip, .hero-close')
      : null;
    if (!btn) return;
    var r = btn.getBoundingClientRect();
    var d = Math.max(r.width, r.height);
    var s = document.createElement('span');
    s.className = 'ripple-fx';
    s.style.width = s.style.height = d + 'px';
    s.style.left = (e.clientX - r.left - d / 2) + 'px';
    s.style.top = (e.clientY - r.top - d / 2) + 'px';
    if (getComputedStyle(btn).position === 'static') btn.style.position = 'relative';
    btn.style.overflow = 'hidden';
    btn.appendChild(s);
    setTimeout(function() { s.remove(); }, 680);
  });
})();
