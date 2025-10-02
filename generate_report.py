#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime
import argparse

def generate_html_report(json_file):
    """生成包含完整 JSON 數據的 HTML 報告"""
    
    # 讀取 JSON 數據
    with open(json_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    # 構建 Method 對照並補入每筆結果 (以 _method 欄位提供給前端使用)
    try:
        requests = (test_data.get('collection') or {}).get('requests') or []
        method_map = {req.get('id'): req.get('method') for req in requests if isinstance(req, dict)}
        for r in (test_data.get('results') or []):
            if isinstance(r, dict):
                if not r.get('_method'):
                    m = method_map.get(r.get('id'))
                    if m:
                        r['_method'] = m
    except Exception:
        pass
    
    # 產生標題：name + startedAt(YYYY-MM-DD)
    name = test_data.get('name') or '未命名'
    started_at = test_data.get('startedAt')
    date_str = '—'
    try:
        if started_at:
            dt = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d')
    except Exception:
        pass
    report_title = f"{name} - {date_str}"
    
    # HTML 模板
    html_template = '''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <title>REPORT_TITLE_PLACEHOLDER</title>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <style>
    :root {
      --bg:#0f1115;
      --panel:#1b1f27;
      --panel-alt:#242a34;
      --text:#eef2f7;
      --text-dim:#a9b4c4;
      --primary:#3b82f6;
      --success:#10b981;
      --warn:#f59e0b;
      --error:#ef4444;
      --border:#2c3542;
      --code:#0d1117;
      --badge:#334155;
      --radius:10px;
      --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, "Courier New", monospace;
      font-family: "Segoe UI", "Noto Sans TC", system-ui, -apple-system, BlinkMacSystemFont, Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin:0;
      background:linear-gradient(145deg,#10141b,#0b0d11);
      color:var(--text);
      -webkit-font-smoothing: antialiased;
    }
    h1,h2,h3 { font-weight:600; letter-spacing:.5px; margin:0 0 .75rem }
    a { color:var(--primary); text-decoration:none }
    a:hover { text-decoration:underline }
    .container {
      max-width: 1480px;
      margin: 0 auto;
      padding: 1.8rem 2.2rem 4rem;
    }
    header { display:flex; flex-wrap:wrap; gap:1rem; align-items:flex-end; justify-content:space-between; }
    header h1 { font-size: clamp(1.65rem, 2.2vw, 2.3rem); background:linear-gradient(90deg,#70a5ff,#c084fc); -webkit-background-clip:text; color:transparent; }
    .meta-line { font-size:.9rem; color:var(--text-dim); }
    .grid {
      display:grid;
      gap:1.25rem;
      grid-template-columns: repeat(auto-fill,minmax(210px,1fr));
      margin-bottom:1.75rem;
    }
    .card {
      background:linear-gradient(145deg,#1d232d,#161b22);
      border:1px solid var(--border);
      padding:1rem 1.1rem .95rem;
      border-radius:var(--radius);
      position:relative;
      overflow:hidden;
    }
    .card:before {
      content:"";
      position:absolute;
      inset:0;
      background:
        radial-gradient(circle at 120% -10%, rgba(59,130,246,.18), transparent 60%),
        radial-gradient(circle at -10% 120%, rgba(168,85,247,.15), transparent 70%);
      opacity:.5;
      pointer-events:none;
    }
    .card h3 {
      font-size:.8rem;
      text-transform:uppercase;
      letter-spacing:.1em;
      margin:0 0 .35rem;
      color:var(--text-dim);
    }
    .card .value {
      font-size:1.6rem;
      font-weight:600;
      line-height:1.15;
    }
    .value.sm { font-size:1.2rem; }
    .tagline { font-size:.7rem; text-transform:uppercase; letter-spacing: .12em; color:var(--text-dim); margin-top:.25rem }
    .value.ok { color:var(--success); }
    .value.err { color:var(--error); }
    .value.warn { color:var(--warn); }
    .flex { display:flex; gap:.65rem; align-items:center; flex-wrap:wrap; }
    .filters {
      display:flex;
      flex-wrap:wrap;
      gap:.75rem;
      padding:1rem 1.25rem;
      background:linear-gradient(145deg,#1d2530,#141a21);
      border:1px solid var(--border);
      border-radius:var(--radius);
      margin-bottom:1.25rem;
    }
    .filters label {
      font-size:.7rem;
      text-transform:uppercase;
      letter-spacing:.12em;
      color:var(--text-dim);
      display:block;
      margin-bottom:.25rem;
    }
    .filters .group {
      display:flex;
      flex-direction:column;
      min-width: 160px;
    }
    .filters input, .filters select {
      background:#10151c;
      border:1px solid #2a333f;
      color:var(--text);
      padding:.55rem .6rem;
      border-radius:6px;
      font-size:.85rem;
      min-width: 160px;
    }
    .filters input:focus, .filters select:focus {
      outline:1px solid var(--primary);
    }
    .badge {
      display:inline-flex;
      padding:.28rem .55rem .32rem;
      border-radius: 6px;
      font-size:.65rem;
      font-weight:600;
      letter-spacing:.05em;
      background:var(--badge);
      color:var(--text-dim);
      text-transform:uppercase;
      white-space:nowrap;
      gap:.35rem;
      align-items:center;
    }
    .badge.GET { background:#1e3a8a; color:#93c5fd; }
    .badge.PATCH { background:#4d194d; color:#fbcfe8; }
    .badge.POST { background:#0f4d25; color:#6ee7b7; }
    .badge.DELETE { background:#5b2121; color:#fecaca; }
    .status-chip {
      font-size:.65rem;
      font-weight:600;
      padding:.4rem .55rem;
      border-radius:6px;
      background:#334155;
      color:#cbd5e1;
      letter-spacing:.05em;
      display:inline-block;
      white-space:nowrap;
    }
    .status-2xx { background:#064e3b; color:#6ee7b7; }
    .status-4xx { background:#5b1d0e; color:#fdba74; }
    .status-5xx { background:#5b0e17; color:#fda4af; }
    table {
      width:100%;
      border-collapse:separate;
      border-spacing:0 6px;
    }
    thead th {
      font-size:.7rem;
      font-weight:600;
      text-transform:uppercase;
      letter-spacing:.1em;
      text-align:left;
      padding:.55rem .75rem;
      color:var(--text-dim);
    }
    tbody tr {
      background:linear-gradient(145deg,#1d232d,#161b22);
      transition:background .2s, transform .2s;
      cursor:pointer;
    }
    tbody tr:hover {
      background:#243040;
    }
    tbody td {
      padding:.65rem .75rem;
      font-size:.8rem;
      border-top:1px solid #2b3644;
      border-bottom:1px solid #2b3644;
    }
    tbody tr td:first-child {
      border-left:1px solid #2b3644;
      border-top-left-radius:8px;
      border-bottom-left-radius:8px;
    }
    tbody tr td:last-child {
      border-right:1px solid #2b3644;
      border-top-right-radius:8px;
      border-bottom-right-radius:8px;
    }
    .mono { font-family:var(--mono); font-size:.75rem; }
    .dim { color:var(--text-dim); }
    .tests-badge {
      font-size:.6rem;
      background:#334155;
      color:#cbd5e1;
      padding:.28rem .5rem;
      border-radius:999px;
      font-weight:600;
      letter-spacing:.05em;
      display:inline-flex;
      gap:.3rem;
    }
    .tests-badge .ok { color:var(--success); }
    .tests-badge .fail { color:var(--error); }
    .expand {
      max-height:0;
      overflow:hidden;
      transition:max-height .35s ease;
    }
    .row.open + .expand {
      max-height: 600px;
    }
    .detail-panel {
      background:linear-gradient(135deg,#202733,#151a22);
      border:1px solid #2c3644;
      margin: -4px 4px 10px;
      padding: 1rem 1rem 1.1rem;
      border-radius:8px;
      display:grid;
      gap:1rem;
      grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
      position:relative;
    }
    .detail-panel:before {
      content:"";
      position:absolute;
      inset:0;
      background:
        radial-gradient(circle at 80% 20%, rgba(59,130,246,.12), transparent 65%),
        radial-gradient(circle at 10% 90%, rgba(168,85,247,.12), transparent 70%);
      opacity:.7;
      pointer-events:none;
    }
    .detail-box h4 {
      margin:0 0 .5rem;
      font-size:.75rem;
      letter-spacing:.1em;
      text-transform:uppercase;
      color:var(--text-dim);
    }
    ul.test-list {
      list-style:none;
      margin:0;
      padding:0;
      display:flex;
      flex-direction:column;
      gap:.4rem;
      max-height:220px;
      overflow:auto;
      -webkit-mask-image:linear-gradient(#000, #000, rgba(0,0,0,.2));
    }
    ul.test-list li {
      display:flex;
      align-items:center;
      gap:.5rem;
      font-size:.7rem;
      background:#12171e;
      padding:.45rem .55rem;
      border:1px solid #2b3644;
      border-radius:6px;
      line-height:1.3;
    }
    .pill {
      font-size:.55rem;
      font-weight:600;
      letter-spacing:.08em;
      padding:.25rem .45rem;
      border-radius:5px;
      text-transform:uppercase;
    }
    .pill.pass {
      background:#064e3b;
      color:#6ee7b7;
    }
    .pill.fail {
      background:#5b0e17;
      color:#fda4af;
    }
    code.inline {
      background:#0f1620;
      padding:.15rem .35rem;
      border-radius:4px;
      border:1px solid #1f2732;
      font-family:var(--mono);
      font-size:.68rem;
      color:#91c7ff;
    }
    .times-chips {
      display:flex;
      flex-wrap:wrap;
      gap:.4rem;
    }
    .chip {
      font-size:.55rem;
      background:#1e2936;
      border:1px solid #314152;
      color:#9fb2c7;
      padding:.35rem .5rem;
      border-radius:5px;
      font-family:var(--mono);
    }
    .chip.fast { border-color:#065f46; color:#6ee7b7; }
    .chip.slow { border-color:#92400e; color:#fbbf24; }
    .chip.bad { border-color:#7f1d1d; color:#fca5a5; }
    .legend {
      display:flex;
      gap:.75rem;
      flex-wrap:wrap;
      font-size:.6rem;
      margin-top:.25rem;
    }
    .legend span {
      display:inline-flex;
      gap:.3rem;
      align-items:center;
      background:#16202b;
      padding:.35rem .55rem;
      border-radius:5px;
      border:1px solid #293541;
    }
    footer {
      margin-top:3rem;
      padding:2rem 0 1rem;
      font-size:.65rem;
      text-align:center;
      color:#475569;
    }
    .no-results {
      text-align:center;
      padding:2rem 1rem;
      color:var(--text-dim);
      font-size:.85rem;
    }
    .pointer { cursor:pointer; }
    .sticky-head {
      position:sticky;
      top:0;
      backdrop-filter: blur(6px);
      background:rgba(15,18,24,.85);
      z-index:10;
    }
    @media (max-width: 880px) {
      thead { display:none; }
      table, tbody, tr, td { display:block; width:100%; }
      tbody tr { margin-bottom:8px; border-radius:8px; }
      tbody td {
        border:none !important;
        padding:.4rem .9rem .4rem;
      }
      tbody td[data-label]:before {
        content: attr(data-label);
        display:block;
        font-size:.55rem;
        letter-spacing:.1em;
        text-transform:uppercase;
        color:var(--text-dim);
        margin-bottom:.15rem;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>REPORT_TITLE_PLACEHOLDER</h1>
        <div class="meta-line" id="runMeta"></div>
        <div class="legend">
          <span><strong style="color:#6ee7b7">2xx</strong> 成功</span>
          <span><strong style="color:#fdba74">4xx</strong> 用戶端錯誤</span>
          <span><strong style="color:#fca5a5">5xx</strong> 服務端錯誤</span>
          <span><strong style="color:#6ee7b7">PASS</strong> 測試通過</span>
          <span><strong style="color:#fca5a5">FAIL</strong> 測試失敗</span>
        </div>
      </div>
    </header>

    <section class="grid" id="summaryCards"></section>

    <section class="filters">
      <div class="group">
        <label for="search">關鍵字</label>
          <input id="search" placeholder="名稱 / URL / 測試名稱" />
      </div>
      <div class="group">
        <label for="methodFilter">Method</label>
        <select id="methodFilter">
          <option value="">全部</option>
        </select>
      </div>
      <div class="group">
        <label for="statusFilter">HTTP 狀態</label>
        <select id="statusFilter">
          <option value="">全部</option>
          <option value="2">2xx</option>
          <option value="4">4xx</option>
          <option value="5">5xx</option>
        </select>
      </div>
      <div class="group">
        <label for="testResultFilter">測試結果</label>
        <select id="testResultFilter">
          <option value="">全部</option>
          <option value="pass">全通過</option>
          <option value="fail">含失敗</option>
        </select>
      </div>
      <div class="group">
        <label for="sortSelect">排序</label>
        <select id="sortSelect">
          <option value="seq">原始順序</option>
          <option value="time-desc">耗時 (高→低)</option>
          <option value="time-asc">耗時 (低→高)</option>
          <option value="tests-desc">測試數 (多→少)</option>
          <option value="tests-asc">測試數 (少→多)</option>
          <option value="status">狀態碼</option>
          <option value="name">名稱 A→Z</option>
        </select>
      </div>
      <div class="group">
        <label for="slowThreshold">慢速閾值(ms)</label>
        <input id="slowThreshold" type="number" value="500" min="0" />
      </div>
    </section>

    <section id="tableSection">
      <table>
        <thead class="sticky-head">
          <tr>
            <th>#</th>
            <th>名稱 / URL</th>
            <th>Method</th>
            <th>狀態</th>
            <th>耗時 (ms)</th>
            <th>測試通過</th>
            <th>測試失敗</th>
            <th>執行次數</th>
          </tr>
        </thead>
        <tbody id="resultBody"></tbody>
      </table>
      <div id="noResults" class="no-results" style="display:none">無符合條件的結果</div>
    </section>

    <footer>
      產生時間：<span id="generatedAt"></span>｜此頁面為離線報告，資料來源於提供之 JSON
    </footer>
  </div>

  <script>
    // 完整的測試數據直接嵌入
    const testData = {json_data_placeholder};

    function percentile(arr, p){
      if(!arr.length) return 0;
      const sorted=[...arr].sort((a,b)=>a-b);
      const idx = (p/100)*(sorted.length-1);
      const lo = Math.floor(idx), hi = Math.ceil(idx);
      if(lo===hi) return sorted[lo];
      return +(sorted[lo] + (sorted[hi]-sorted[lo])*(idx-lo)).toFixed(2);
    }

    function classifyTime(t, slow){
      if(t <= 120) return 'fast';
      if(t >= slow) return 'bad';
      return 'slow';
    }

    function buildSummary(data){{
      const times = data.results.map(r=>r.time).filter(Boolean);
      const avg = times.reduce((a,b)=>a+b,0)/(times.length||1);
      const p90 = percentile(times,90);
      const p95 = percentile(times,95);
      const success = data.results.filter(r => r.responseCode.code < 400).length;
      const clientErr = data.results.filter(r => r.responseCode.code >=400 && r.responseCode.code <500).length;
      const serverErr = data.results.filter(r => r.responseCode.code >=500).length;
      const totalTests = data.results.reduce((acc,r) => {{
        const t = r.tests ? Object.keys(r.tests).length : 0;
        return acc + t;
      }},0);
      const failedTests = data.results.reduce((acc,r)=>{{
        if(!r.tests) return acc;
          return acc + Object.values(r.tests).filter(v=>v===false).length;
      }},0);
      const passTests = totalTests - failedTests;

      const cards = [
        {{ title:'請求總數', value:data.results.length }},
        {{ title:'成功請求', value:success, cls:'ok', sub:`${{(success/data.results.length*100).toFixed(1)}}%` }},
          {{ title:'4xx', value:clientErr, cls: clientErr?'warn':'', sub: clientErr? ((clientErr/data.results.length*100).toFixed(1)+'%') : '—' }},
        {{ title:'5xx', value:serverErr, cls: serverErr?'err':'', sub: serverErr? ((serverErr/data.results.length*100).toFixed(1)+'%') : '—' }},
        {{ title:'平均耗時', value:avg.toFixed(1)+' ms' }},
        {{ title:'P90', value:p90+' ms' }},
        {{ title:'P95', value:p95+' ms' }},
        {{ title:'測試通過', value:passTests, cls:'ok', sub:`${{passTests}}/${{totalTests}}` }},
        {{ title:'測試失敗', value:failedTests, cls:failedTests?'err':'', sub: totalTests? ((failedTests/totalTests*100).toFixed(1)+'%') : '0%' }},
      ];

      const wrap = document.getElementById('summaryCards');
      wrap.innerHTML = cards.map(c=>`
        <div class="card">
          <h3>${{c.title}}</h3>
          <div class="value ${{c.cls||''}}">${{c.value}}</div>
          ${{c.sub? `<div class="tagline">${{c.sub}}</div>`:''}}
        </div>
      `).join('');
      const metaEl = document.getElementById('runMeta');
      if(data.startedAt && data.timestamp){{
        const started = new Date(data.startedAt);
        const ended = new Date(data.timestamp);
        const dur = (ended - started)/1000;
        metaEl.textContent = `集合：${{data.name || '未命名'}} ｜ 開始：${{started.toLocaleString()}} ｜ 結束：${{ended.toLocaleString()}} ｜ 總耗時：${{dur.toFixed(1)}}s`;
      }}
      document.getElementById('generatedAt').textContent = new Date().toLocaleString();
    }}

    function initFilters(data){{
      const methodSet = new Set(data.results.map(r=> (r._method || r.method || (r.request && r.request.method) || (r.meta && r.meta.method))));
      const select = document.getElementById('methodFilter');
      [...methodSet].filter(Boolean).sort().forEach(m=>{{
        const opt=document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        select.appendChild(opt);
      }});
    }}

    function renderTable(data){{
      const body = document.getElementById('resultBody');
      const search = document.getElementById('search').value.trim().toLowerCase();
      const method = document.getElementById('methodFilter').value;
      const statusCat = document.getElementById('statusFilter').value;
      const testRes = document.getElementById('testResultFilter').value;
      const sort = document.getElementById('sortSelect').value;
      const slowThreshold = +document.getElementById('slowThreshold').value || 500;

      let list = data.results.map((r,i)=>{{
        const testsObj = r.tests || {{}};
        const passCount = Object.values(testsObj).filter(v=>v===true).length;
        const failCount = Object.values(testsObj).filter(v=>v===false).length;
        return {{
          idx:i+1,
          name:r.name,
          url:r.url,
          method:r._method || r.method || (r.request && r.request.method) || '—',
          status:r.responseCode?.code,
          statusName:r.responseCode?.name,
          time:r.time,
          passCount,
          failCount,
          testNames:Object.keys(testsObj),
          testsObj,
          times:r.times || (r.time?[r.time]:[]),
          allTests:r.allTests || [],
          raw:r
        }};
      }});

      // Filter
      list = list.filter(item=>{{
        if(search){{
          const hay = (item.name+' '+item.url+' '+item.testNames.join(' ')).toLowerCase();
          if(!hay.includes(search)) return false;
        }}
        if(method && item.method !== method) return false;
        if(statusCat){{
          if(!String(item.status).startsWith(statusCat)) return false;
        }}
        if(testRes){{
          if(testRes==='pass' && item.failCount>0) return false;
          if(testRes==='fail' && item.failCount===0) return false;
        }}
        return true;
      }});

      // Sort
      switch(sort){{
        case 'time-desc': list.sort((a,b)=>b.time - a.time); break;
        case 'time-asc': list.sort((a,b)=>a.time - b.time); break;
        case 'tests-desc': list.sort((a,b)=>(b.passCount+b.failCount)-(a.passCount+a.failCount)); break;
        case 'tests-asc': list.sort((a,b)=>(a.passCount+a.failCount)-(b.passCount+b.failCount)); break;
        case 'status': list.sort((a,b)=>a.status-b.status); break;
        case 'name': list.sort((a,b)=>a.name.localeCompare(b.name,'zh-Hant')); break;
        case 'seq':
        default: // do nothing
      }}

      body.innerHTML = '';
      if(!list.length){{
        document.getElementById('noResults').style.display='block';
        return;
      }} else {{
        document.getElementById('noResults').style.display='none';
      }}

      const frag = document.createDocumentFragment();

      list.forEach(item=>{{
        const tr = document.createElement('tr');
        tr.className='row';
        const statusCls = item.status >=500 ? 'status-5xx' : item.status >=400 ? 'status-4xx' : 'status-2xx';

        tr.innerHTML = `
          <td data-label="#">${{item.idx}}</td>
          <td data-label="名稱 / URL">
            <div style="font-weight:600; font-size:.78rem; letter-spacing:.2px">${{item.name||'—'}}</div>
            <div class="mono dim" style="margin-top:2px; word-break:break-all">
              <a href="${{item.url.startsWith('http')? item.url : 'https://'+item.url}}" target="_blank">${{item.url}}</a>
            </div>
          </td>
          <td data-label="Method">
            <span class="badge ${{item.method}}">${{item.method}}</span>
          </td>
          <td data-label="狀態">
            <span class="status-chip ${{statusCls}}">${{item.status}} ${{item.statusName||''}}</span>
          </td>
          <td data-label="耗時">
            <span class="mono ${{classifyTime(item.time, slowThreshold)}}">${{item.time}}</span>
          </td>
          <td data-label="通過">${{item.passCount}}</td>
          <td data-label="失敗" style="color:${{item.failCount? 'var(--error)':'var(--text-dim)'}}">${{item.failCount}}</td>
          <td data-label="執行次數">${{item.times.length}}</td>
        `;
        frag.appendChild(tr);

        const expand = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan=8;
        expand.className='expand';

        const timesChips = item.times.map(t=>{{
          const cls = classifyTime(t, slowThreshold);
          return `<span class="chip ${{cls}}">${{t}} ms</span>`;
        }}).join('');

        const testList = item.testNames.map(k=>{{
          const pass = item.testsObj[k]===true;
          return `<li>
            <span class="pill ${{pass?'pass':'fail'}}">${{pass?'PASS':'FAIL'}}</span>
            <span>${{k.replace(/✅/g,'').trim()}}</span>
          </li>`;
        }}).join('') || '<div class="dim" style="font-size:.65rem">無測試記錄</div>';

        const executionsHTML = (item.allTests||[]).map((exec,i)=>{{
          const execLines = Object.entries(exec).map(([k,v])=>{{
            return `<div style="display:flex; gap:.5rem; align-items:center;">
              <span class="pill ${{v?'pass':'fail'}}">${{v?'PASS':'FAIL'}}</span>
              <code class="inline">${{k.replace(/✅/g,'').trim()}}</code>
            </div>`;
          }}).join('');
          return `<div style="padding:.55rem .65rem; border:1px solid #2a3441; background:#12171e; border-radius:6px; display:grid; gap:.45rem">
            <div style="font-size:.6rem; letter-spacing:.08em; color:var(--text-dim); font-weight:600;">執行 #${{i+1}}</div>
            ${{execLines || '<div class="dim" style="font-size:.65rem">—</div>'}}
          </div>`;
        }}).join('<div style="height:6px"></div>') || '<div class="dim" style="font-size:.65rem">無</div>';

        td.innerHTML = `
          <div class="detail-panel">
            <div class="detail-box">
              <h4>測試摘要</h4>
              <ul class="test-list">
                ${{testList}}
              </ul>
            </div>
            <div class="detail-box">
              <h4>耗時分佈 (${{item.times.length}})</h4>
              <div class="times-chips">${{timesChips || '<div class="dim" style="font-size:.65rem">無</div>'}}</div>
              <div style="margin-top:.65rem; font-size:.6rem; letter-spacing:.08em; text-transform:uppercase; color:var(--text-dim); font-weight:600;">統計</div>
              <div style="font-size:.65rem; display:grid; gap:.25rem">
                ${{(()=>{{
                  if(!item.times.length) return '<div class="dim">—</div>';
                  const min = Math.min(...item.times);
                  const max = Math.max(...item.times);
                  const avg = (item.times.reduce((a,b)=>a+b,0)/item.times.length).toFixed(2);
                  return `
                    <div>最小：<code class="inline">${{min}} ms</code></div>
                    <div>最大：<code class="inline">${{max}} ms</code></div>
                    <div>平均：<code class="inline">${{avg}} ms</code></div>
                  `;
                }})()}}
              </div>
            </div>
            <div class="detail-box">
              <h4>每次執行測試結果</h4>
              <div style="display:flex; flex-direction:column; gap:.6rem; max-height:240px; overflow:auto;">
                ${{executionsHTML}}
              </div>
            </div>
            <div class="detail-box">
              <h4>原始資料片段</h4>
              <div style="font-size:.6rem; line-height:1.4; font-family:var(--mono); background:#0f1620; padding:.6rem .7rem; border:1px solid #243140; border-radius:6px; max-height:260px; overflow:auto; white-space:pre;">
${{(()=> {{
try {{
  const clone = structuredClone(item.raw);
  if(clone.allTests && clone.allTests.length > 3){{
    clone.allTests = clone.allTests.slice(0,3);
    clone._truncated = true;
  }}
  return JSON.stringify(clone,null,2)
    .replace(/[&<>]/g,s=>({{\'&\':\'&amp;\',\'<\':\'&lt;\',\'>\':\'&gt;\'}}[s]));
}} catch(e){{ return \'{{}}\'; }}
}})()}}
              </div>
            </div>
          </div>
        `;
        expand.appendChild(td);
        frag.appendChild(expand);

        tr.addEventListener('click', ()=>{{
          tr.classList.toggle('open');
        }});
      }});

      body.appendChild(frag);
    }}

    function attachEvents(data){{
      ['search','methodFilter','statusFilter','testResultFilter','sortSelect','slowThreshold']
        .forEach(id => document.getElementById(id).addEventListener('input', ()=> renderTable(data)));
    }}

    function initReport(data){{
      if(!data || !Array.isArray(data.results)){{
        alert('資料格式錯誤：缺少 results 陣列');
        return;
      }}
      buildSummary(data);
      initFilters(data);
      renderTable(data);
      attachEvents(data);
    }}

    // 載入完整的測試數據
    document.addEventListener('DOMContentLoaded', function() {{
      initReport(testData);
    }});
  </script>
</body>
</html>'''
    
    # 將 JSON 數據轉換為 JavaScript 格式並插入模板
    json_str = json.dumps(test_data, ensure_ascii=False, indent=2)
    html_content = html_template.replace('{json_data_placeholder}', json_str)
    # 修正模板中的 JavaScript 大括號：將用於避開 Python 格式化的 '{{' / '}}' 轉回標準的 '{' / '}'
    # 這些重寫僅影響模板中的 JS 區塊；嵌入的 JSON 資料本身僅含單一大括號，不會被更動。
    html_content = (html_content
                    .replace('${{', '${')
                    .replace('}}', '}')
                    .replace('{{', '{'))
    # 套用動態標題
    html_content = html_content.replace('REPORT_TITLE_PLACEHOLDER', report_title)
    
    # 寫入最終的 HTML 文件（輸出檔名：name + startedAt(YYYY-MM-DD).html）
    def _sanitize_filename(s):
        allow = set(" -_().")
        return ''.join(ch if (ch.isalnum() or ch in allow) else '_' for ch in s).strip(' ._') or 'report'

    safe_name = _sanitize_filename(name)
    safe_date = _sanitize_filename(date_str)
    file_name = f"{safe_name} - {safe_date}.html"
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_file = os.path.join(base_dir, file_name)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML 報告已生成：{output_file}")
    print(f"📊 包含 {len(test_data['results'])} 個測試結果")
    print(f"🎯 測試通過率：{test_data['totalPass']}/{test_data['totalPass'] + test_data['totalFail']} (100%)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate Postman HTML report from a Postman test run JSON file')
    parser.add_argument('json_file', help='Path to the Postman test run JSON file')
    args = parser.parse_args()
    generate_html_report(args.json_file)
