// cdp_client.js —— 直连 Hermes agent-browser 的 CDP(绕过会卡死的 browser_exec)
// 用 Node 内置 WebSocket(Node 22+),自带 30s 超时,不会卡几分钟。
//
// 用法:
//   node cdp_client.js open  <url>                 # 新开标签页并等待加载
//   node cdp_client.js eval  "<js表达式>"           # 在当前页执行 JS
//   node cdp_client.js list                        # 列出所有页面
//   node cdp_client.js text [n]                    # 读当前页 innerText 前 n 字(默认 4000)
//   node cdp_client.js click "<css选择器>"          # 点击元素
const fs = require('fs');
const os = require('os');
const path = require('path');

function findPort() {
  const tmp = os.tmpdir();
  for (const d of fs.readdirSync(tmp)) {
    if (d.startsWith('agent-browser-chrome-')) {
      const f = path.join(tmp, d, 'DevToolsActivePort');
      if (fs.existsSync(f)) {
        const p = fs.readFileSync(f, 'utf8').split('\n')[0].trim();
        if (p) return p;
      }
    }
  }
  throw new Error('找不到 agent-browser 的 DevToolsActivePort(实例没在跑?)');
}

const base = () => `http://127.0.0.1:${findPort()}`;

async function pages() {
  const r = await fetch(`${base()}/json/list`);
  return (await r.json()).filter(t => t.type === 'page');
}

function connect(wsUrl) {
  return new Promise((res, rej) => {
    const s = new WebSocket(wsUrl);
    s.onopen = () => res(s);
    s.onerror = (e) => rej(new Error('ws connect failed'));
    setTimeout(() => rej(new Error('ws connect timeout')), 15000);
  });
}

function mkSend(sock) {
  let id = 0;
  return (method, params = {}, timeoutMs = 30000) =>
    new Promise((res, rej) => {
      const mid = ++id;
      const t = setTimeout(() => { sock.removeEventListener('message', h); rej(new Error(`timeout ${method}`)); }, timeoutMs);
      const h = (ev) => {
        let m; try { m = JSON.parse(ev.data); } catch { return; }
        if (m.id === mid) {
          clearTimeout(t); sock.removeEventListener('message', h);
          m.error ? rej(new Error(`${method}: ${JSON.stringify(m.error)}`)) : res(m.result);
        }
      };
      sock.addEventListener('message', h);
      sock.send(JSON.stringify({ id: mid, method, params }));
    });
}

async function pickPage() {
  const ps = await pages();
  if (!ps.length) throw new Error('没有可用页面');
  // 优先挑非 about:blank / 非 chrome:// 的
  const good = ps.find(p => p.url && !p.url.startsWith('chrome://') && p.url !== 'about:blank');
  return good || ps[0];
}

(async () => {
  const [cmd, arg] = process.argv.slice(2);
  if (cmd === 'list') {
    const ps = await pages();
    console.log(`共 ${ps.length} 个页面:`);
    ps.forEach(p => console.log(`  [${p.id.slice(0, 8)}] ${(p.title || '').slice(0, 40)} :: ${p.url.slice(0, 90)}`));
    return;
  }
  if (cmd === 'open') {
    const r = await fetch(`${base()}/json/new?${encodeURIComponent(arg)}`, { method: 'PUT' });
    const t = await r.json();
    console.log(`已开新页: ${t.id}`);
    const sock = await connect(t.webSocketDebuggerUrl);
    const send = mkSend(sock);
    await send('Page.enable');
    await new Promise(r => setTimeout(r, 6000));   // 等 SPA 渲染
    const info = await send('Runtime.evaluate', {
      expression: 'JSON.stringify({url: location.href, title: document.title, len: document.body ? document.body.innerText.length : 0})',
      returnByValue: true
    });
    console.log('页面状态:', info.result.value);
    sock.close();
    return;
  }
  // 其余命令作用于"当前页"
  const p = await pickPage();
  const sock = await connect(p.webSocketDebuggerUrl);
  const send = mkSend(sock);
  await send('Runtime.enable');
  let expr;
  if (cmd === 'eval') expr = arg;
  else if (cmd === 'text') expr = `document.body.innerText.slice(0, ${parseInt(arg) || 4000})`;
  else if (cmd === 'click') expr = `(() => { const el = document.querySelector(${JSON.stringify(arg)}); if (!el) return 'NOT_FOUND'; el.click(); return 'clicked: ' + el.tagName + ' ' + (el.innerText || '').slice(0, 40); })()`;
  else throw new Error('未知命令: ' + cmd);
  const out = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
  console.log(typeof out.result.value === 'string' ? out.result.value : JSON.stringify(out.result.value, null, 2));
  sock.close();
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
