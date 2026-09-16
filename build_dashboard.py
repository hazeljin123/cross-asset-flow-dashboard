# -*- coding: utf-8 -*-
"""读取 data.json，渲染跨资产资金流看板 dashboard.html。
每日自动化只需回填 data.json 后运行本脚本即可重新生成看板。"""
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parent

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>跨资产资金流日频看板 · 股债汇期加密</title>
<script src="echarts.min.js"></script>
<script>window.echarts||document.write('<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"><\\/script>')</script>
<style>
  :root{ --red:#d8392b; --green:#1a9c5b; --ink:#222; --sub:#6b7280; --line:#e6e8ec; --bg:#f6f7f9; }
  *{ box-sizing:border-box; }
  body{ margin:0; background:var(--bg); color:var(--ink);
        font-family:-apple-system,"PingFang SC","Microsoft YaHei",Segoe UI,sans-serif; }
  .wrap{ max-width:1180px; margin:0 auto; padding:24px 20px 48px; }
  header h1{ font-size:22px; margin:0 0 4px; }
  .meta{ color:var(--sub); font-size:13px; margin-bottom:14px; }
  .legend{ display:flex; gap:14px; flex-wrap:wrap; margin:10px 0 18px; font-size:12.5px; }
  .legend .pill{ padding:3px 10px; border-radius:20px; background:#fff; border:1px solid var(--line); }
  .legend .real{ color:var(--red); border-color:#f3c9c4; }
  .legend .proxy{ color:#b06a00; border-color:#f0dcb0; }

  .panel{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:16px 18px; margin-bottom:18px; }
  .panel h2{ font-size:16px; margin:0 0 4px; }
  .panel .cap{ font-size:12.5px; color:var(--sub); margin-bottom:10px; line-height:1.7; }
  .layer-h{ font-size:15px; font-weight:700; margin:0 0 12px; }
  .layer-h .num{ display:inline-block; width:22px; height:22px; line-height:22px; text-align:center; border-radius:50%; background:var(--ink); color:#fff; font-size:12px; margin-right:8px; }
  .chart{ width:100%; height:340px; }

  .intra-grid{ display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:12px; }
  .intra-card{ background:#fff; border:1px solid var(--line); border-left:4px solid #ccc; border-radius:10px; padding:12px 14px; }
  .intra-head{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:5px; }
  .intra-label{ font-weight:700; font-size:14px; }
  .intra-dir{ font-size:11.5px; font-weight:600; }
  .intra-str{ font-size:11.5px; color:var(--sub); margin-bottom:6px; }
  .intra-theme{ font-size:12.5px; line-height:1.65; color:#374151; }
  .tag{ font-size:10.5px; padding:1px 8px; border-radius:9px; font-weight:600; }
  .tag-real{ background:#fdecea; color:var(--red); }
  .tag-proxy{ background:#fdf3e0; color:#b06a00; }

  .stbl{ width:100%; border-collapse:collapse; font-size:13px; margin-top:4px; }
  .stbl th, .stbl td{ border:1px solid var(--line); padding:9px 12px; text-align:center; }
  .stbl th{ background:#fafbfc; color:var(--sub); font-weight:600; }
  .stbl td:first-child{ text-align:left; }
  .stbl tr:nth-child(even){ background:#fbfcfd; }

  .thread{ border:1px solid var(--line); border-radius:10px; padding:10px 13px; margin-bottom:9px; background:#fff; }
  .thread .t-title{ font-weight:700; font-size:13.5px; color:var(--ink); margin-bottom:3px; }
  .thread .t-det{ font-size:13px; color:#374151; line-height:1.65; }

  .detail h3{ font-size:15px; margin:0 0 10px; }
  .detail .cap{ font-size:12px; color:var(--sub); margin:6px 0 4px; }
  .plain{ background:#eef5ff; border:1px solid #cfe0fb; color:#14457a; border-radius:10px; padding:11px 14px; font-size:13px; line-height:1.75; margin:6px 0 12px; }
  .plain b{ color:#0b3a73; }

  .thesis{ background:linear-gradient(90deg,#fff7f6,#fff); border:1px solid #f3c9c4; border-left:5px solid var(--red); border-radius:12px; padding:14px 16px; margin-bottom:18px; font-size:14px; line-height:1.75; color:#7a261f; }
  .thesis .badge{ display:inline-block; font-size:11px; font-weight:700; color:#fff; background:var(--red); border-radius:6px; padding:2px 8px; margin-right:8px; vertical-align:middle; }
  .thesis b{ color:#b91c1c; }

  .narr{ font-size:13.5px; line-height:1.8; color:#374151; }
  .narr b{ color:var(--ink); }
  .risk{ background:#fff7ed; border:1px solid #fcd9b6; color:#9a3412; border-radius:10px; padding:10px 14px; font-size:13px; margin:6px 0 18px; }

  .tabs{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px; }
  .tab{ padding:7px 16px; border-radius:20px; border:1px solid var(--line); background:#fff; cursor:pointer; font-size:13px; font-weight:600; color:var(--sub); }
  .tab:hover{ border-color:#c9ccd1; }
  .tab.active{ background:var(--ink); color:#fff; border-color:var(--ink); }
  .detail-page{ display:none; }
  .detail-page.active{ display:block; }

  footer{ font-size:12px; color:var(--sub); line-height:1.7; border-top:1px solid var(--line); padding-top:14px; }
  .disc{ margin-top:10px; padding:10px 12px; background:#fbfbfc; border:1px dashed #d7dbe0; border-radius:8px; color:#525866; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>跨资产资金流日频看板 · 股 / 债 / 汇 / 期 / 加密</h1>
    <div class="meta" id="meta"></div>
    <div class="legend">
      <span class="pill real">真实：股板块主力净流入、宽基指数涨跌</span>
      <span class="pill proxy">代理：债券用期货+收益率+ETF；外汇用汇率涨跌；商品/加密用涨跌幅；美欧债用收益率</span>
    </div>
  </header>

  <section class="panel">
    <h2 class="layer-h"><span class="num">1</span>各板块内部的资金主旨（资金在每个大类里在押什么）</h2>
    <div class="cap">把每一类资产内部的资金流向归纳成一句话，并标出方向（红=流入、绿=流出）与数据性质。看清资金在单个市场里具体表达了什么——这是看板的核心。</div>
    <div class="intra-grid" id="intraGrid"></div>
  </section>

  <section class="panel">
    <h2 class="layer-h"><span class="num">2</span>资金强度排序（今日 vs 昨日，按强度降序；红=流入、绿=流出）</h2>
    <div class="cap">⚠️ 重要：资金关注度高（强度大）≠ 一定在流入。债券、外汇、大宗商品、加密货币均可反向交易（资金既能流入也能流出），所以按「资金净方向」着色：红=流入，绿=流出。强度=该方向资金关注度(0-100)，为相对强弱推断、非净头寸；债/汇/期/加密为代理信号。昨日=前一交易日(9/15)估算，仅供对比资金关注度变化。股债汇期加密之间无统一「搬运」数据源，此为相对强弱视图。</div>
    <div id="strengthTable"></div>
  </section>

  <section class="panel">
    <h2 class="layer-h"><span class="num">3</span>板块之间的资金主旨（跨资产的宏观主线）</h2>
    <div class="cap">只保留真正「跨板块之间」的资金逻辑链（地缘→能源→通胀→加息→强美元→各资产反应）；各板块<b>内部</b>的主旨已见第①层，此处不重复。</div>
    <div class="thesis" id="interTheme"></div>
    <div id="threads"></div>
    <div class="risk" id="risk"></div>
  </section>

  <section class="panel">
    <h2 class="layer-h"><span class="num">4</span>各板块资金流入流出明细（点击切换查看）</h2>
    <div class="cap">与①②③并列的「下钻」界面：点击标签查看每个大类内部的资金流入/流出细项。股票为真实主力净流入；债/汇/期/加密为代理信号（涨跌幅/汇率方向推断）。</div>
    <div class="tabs" id="detailTabs"></div>
    <div id="details"></div>
  </section>

  <footer>
    <div><b>数据来源</b></div>
    <div id="sources"></div>
    <div class="disc" id="disc"></div>
  </footer>
</div>

<script>
const DATA = ___DATA_JSON___;
INLINE_JS_PLACEHOLDER
</script>
</body>
</html>
"""

INLINE_JS = """
const order = ['stock','bond','fx','commodity','crypto'];
const DIR_COLOR = { long:'#d8392b', short:'#1a9c5b', neutral:'#8a8a8a' };
const KEY_BY_LABEL = { '股票':'stock', '债券':'bond', '外汇':'fx', '大宗商品':'commodity', '加密货币':'crypto' };
function dirText(d){ return d === 'long' ? '流入' : (d === 'short' ? '流出' : '中性'); }

document.getElementById('meta').textContent =
  '数据日期：' + DATA.date + '　|　更新：' + DATA.updated_at + '　|　口径：' + DATA.as_of;

// 第1层：各板块内部资金主旨（含方向/标签/强度，5张卡始终并列单行）
document.getElementById('intraGrid').innerHTML = DATA.cross_asset.intra_themes.map(function(t){
  const k = KEY_BY_LABEL[t.label];
  const c = DATA.categories[k];
  const col = DIR_COLOR[c.direction];
  const tag = c.signal === 'real'
    ? '<span class="tag tag-real">真实</span>'
    : '<span class="tag tag-proxy">代理</span>';
  return '<div class="intra-card" style="border-left-color:'+col+'">'
    + '<div class="intra-head"><span class="intra-label" style="color:'+col+'">'+t.label+'</span>'+tag
    + '<span class="intra-dir" style="color:'+col+';background:'+col+'1a;padding:1px 9px;border-radius:9px">'+dirText(c.direction)+'</span></div>'
    + '<div class="intra-str">资金强度 '+c.strength+'/100（'+c.strength_cn+'）　·　'+c.direction_cn+'</div>'
    + '<div class="intra-theme">'+t.theme+'</div></div>';
}).join('');

// 资金强度排序：单表，今日 vs 昨日，按今日强度降序，红=流入绿=流出
(function(){
  const cats = order.map(function(k){ return DATA.categories[k]; });
  cats.sort(function(a,b){ return b.strength - a.strength; });
  const rows = cats.map(function(c){
    const col = DIR_COLOR[c.direction];
    const prev = c.prev || { strength:null };
    let deltaHtml = '<span style="color:var(--sub)">—</span>';
    if(prev.strength != null){
      const d = c.strength - prev.strength;
      if(d !== 0){
        const up = d > 0;
        const dcol = up ? '#d8392b' : '#1a9c5b';
        deltaHtml = '<span style="color:'+dcol+';font-weight:700">'+(up?'▲ ':'▼ ')+Math.abs(d)+'</span>';
      } else { deltaHtml = '<span style="color:var(--sub)">0</span>'; }
    }
    return '<tr>'
      + '<td style="font-weight:700">'+c.label+'</td>'
      + '<td><span style="display:inline-block;padding:2px 12px;border-radius:11px;color:#fff;background:'+col+';font-size:12px;font-weight:600">'+dirText(c.direction)+'</span></td>'
      + '<td style="color:'+col+';font-weight:700;font-size:15px">'+c.strength+'</td>'
      + '<td style="color:var(--sub)">'+(prev.strength==null?'—':prev.strength)+'</td>'
      + '<td>'+deltaHtml+'</td>'
      + '</tr>';
  }).join('');
  document.getElementById('strengthTable').innerHTML =
    '<table class="stbl"><thead><tr><th>大类</th><th>方向</th><th>今日强度</th><th>昨日强度(9/15)</th><th>变化</th></tr></thead><tbody>'+rows+'</tbody></table>';
})();

// 第3层：板块间主旨（thesis 为一句话主线，threads 为真正跨资产的4条逻辑链）
document.getElementById('interTheme').innerHTML =
  '<span class="badge">主线</span><b>板块间主旨：</b>' + DATA.cross_asset.thesis;
document.getElementById('threads').innerHTML = DATA.cross_asset.threads.map(function(t){
  return '<div class="thread"><div class="t-title">'+t.title+'</div><div class="t-det">'+t.detail+'</div></div>';
}).join('');

function drawBar(id, items, mode){
  mode = mode || 'price';
  const chart = echarts.init(document.getElementById(id));
  chart.setOption({
    tooltip:{ trigger:'axis', axisPointer:{type:'shadow'},
      formatter:function(p){ const it=items[p[0].dataIndex]; return '<b>'+it.name+'</b><br/>数值：'+it.value+'<br/>'+(it.note||''); } },
    grid:{ left:150, right:60, top:20, bottom:30 },
    xAxis:{ type:'value' },
    yAxis:{ type:'category', data:items.map(function(it){ return it.name; }), inverse:true },
    series:[{ type:'bar',
      data:items.map(function(it){
        // price 模式：涨=红(流入)；yield 模式：收益率上行=绿(被抛/流出)
        const up = it.value >= 0;
        const color = mode === 'yield' ? (up ? '#1a9c5b' : '#d8392b') : (up ? '#d8392b' : '#1a9c5b');
        return { value:it.value, itemStyle:{ color:color } };
      }),
      label:{ show:true, position:'right', formatter:'{c}' } }]
  });
}

// 明细：标签分页，懒加载图表（默认显示首个标签）
const detailsEl = document.getElementById('details');
const tabsEl = document.getElementById('detailTabs');
const built = {};
order.forEach(function(k, idx){
  const c = DATA.categories[k];
  const btn = document.createElement('button');
  btn.className = 'tab' + (idx===0 ? ' active' : '');
  btn.textContent = c.label;
  btn.dataset.k = k;
  btn.onclick = function(){ switchDetail(k); };
  tabsEl.appendChild(btn);

  const page = document.createElement('div');
  page.className = 'detail-page' + (idx===0 ? ' active' : '');
  page.id = 'dp_'+k;
  page.innerHTML = '<div class="detail"><h3>'+c.label+' · '+(c.sub_title||'')+'</h3>'
    + (c.plain ? '<div class="plain">'+c.plain+'</div>' : '') + '</div>';
  detailsEl.appendChild(page);
  built[k] = false;
});

function buildCharts(k){
  const c = DATA.categories[k];
  const box = document.getElementById('dp_'+k).querySelector('.detail');
  if(c.indexes){
    const ig = 'idx_'+k;
    const sub = document.createElement('div');
    sub.innerHTML = '<div class="cap">宽基指数涨跌（%，红涨绿跌）</div><div class="chart" id="'+ig+'"></div>';
    box.appendChild(sub);
    drawBar(ig, c.indexes.map(function(s){ return { name:s.name, value:s.change, note:s.note||'' }; }));
  }
  if(c.segments){
    c.segments.forEach(function(seg, i){
      const gid = 'seg_'+k+'_'+i;
      const sub = document.createElement('div');
      sub.innerHTML = '<div class="cap" style="margin-top:8px;">'+seg.market+'　'+seg.sub_title+'</div><div class="chart" id="'+gid+'"></div>';
      box.appendChild(sub);
      drawBar(gid, seg.subsectors.map(function(s){ return { name:s.name, value:s.value, note:s.note||'' }; }), seg.mode || 'price');
      if(seg.subsectors.some(function(s){ return s.comment; })){
        const cid = 'cmt_'+k+'_'+i;
        const cdiv = document.createElement('div');
        cdiv.innerHTML = '<div class="cap" style="margin-top:8px;">期限解读（各变化代表的市场态度）</div><div id="'+cid+'"></div>';
        box.appendChild(cdiv);
        document.getElementById(cid).innerHTML = seg.subsectors.map(function(s){
          const sign = s.change >= 0 ? '+' : '';
          return '<div class="thread"><div class="t-title">'+s.name+'　'+sign+s.change+'%</div><div class="t-det">'+s.comment+'</div></div>';
        }).join('');
      }
    });
  } else if(c.groups){
    c.groups.forEach(function(g){
      const gid = 'grp_'+k+'_'+g.group;
      const sub = document.createElement('div');
      sub.innerHTML = '<div class="cap" style="margin-top:8px;">'+g.group+'（%，红涨绿跌）</div><div class="chart" id="'+gid+'"></div>';
      box.appendChild(sub);
      drawBar(gid, g.items.map(function(it){ return { name:it.name, value:it.value, note:it.note||'' }; }));
    });
  } else if(c.subsectors){
    const gid = 'chart_'+k;
    const sub = document.createElement('div');
    sub.innerHTML = '<div class="chart" id="'+gid+'"></div>';
    box.appendChild(sub);
    drawBar(gid, c.subsectors.map(function(s){ return { name:s.name, value:s.value, note:s.note||'' }; }));
  }
  built[k] = true;
}

function switchDetail(k){
  order.forEach(function(o){ document.getElementById('dp_'+o).classList.toggle('active', o===k); });
  Array.prototype.forEach.call(tabsEl.children, function(b){ b.classList.toggle('active', b.dataset.k===k); });
  if(!built[k]){ buildCharts(k); }
  else {
    document.querySelectorAll('#dp_'+k+' .chart').forEach(function(el){ const inst = echarts.getInstanceByDom(el); if(inst) inst.resize(); });
  }
}

buildCharts(order[0]);

document.getElementById('risk').innerHTML = '<b>关键风险：</b>' + DATA.cross_asset.key_risk;
document.getElementById('sources').innerHTML = DATA.sources.map(function(s){ return '· ' + s; }).join('<br/>');
document.getElementById('disc').innerHTML = '免责声明：以上内容基于公开数据和量化分析，仅供参考，不构成投资建议。市场有风险，投资需谨慎。'
  + '任何投资决策应结合个人风险承受能力、资金状况和投资目标独立判断，必要时咨询持牌专业机构。过往表现不预示未来收益。';

window.addEventListener('resize', function(){
  document.querySelectorAll('.chart').forEach(function(el){ const inst = echarts.getInstanceByDom(el); if(inst){ inst.resize(); } });
});
"""

def main():
    data = json.loads((BASE / "data.json").read_text(encoding="utf-8"))
    data_js = json.dumps(data, ensure_ascii=False)
    html = TEMPLATE.replace("___DATA_JSON___", data_js).replace("INLINE_JS_PLACEHOLDER", INLINE_JS)
    (BASE / "dashboard.html").write_text(html, encoding="utf-8")
    (BASE / "index.html").write_text(html, encoding="utf-8")
    (BASE / "inline_check.js").write_text("const DATA = " + data_js + ";\n" + INLINE_JS.strip(), encoding="utf-8")
    print("dashboard.html generated, bytes=", len(html))


if __name__ == "__main__":
    main()
