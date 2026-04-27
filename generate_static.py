#!/usr/bin/env python3
# 生成純靜態 HTML — 零 JavaScript，直接在 iOS QuickLook 顯示
# 每次新增資料後重跑此腳本，HTML 直接寫入 iCloud Claude Cowork 資料夾

import os
from datetime import datetime

# ============ 全部資料 ============
GROCERY = [
    {"date":"2026-04-13","time":"13:08","store":"Costco Wholesale","addr":"35 John Birchall Rd, Richmond Hill, ON L4S 0B2",
     "items":[{"name":"12GAL 折疊儲物箱（車用）","price":12.49}],
     "subtotal":12.49,"hst":1.62,"total":14.11,"payment":"Mastercard ****4134"},
    {"date":"2026-04-16","time":"–","store":"Chuang's Company LTD.","addr":"Richmond Hill, ON",
     "items":[{"name":"營業芋頭包子 x10","price":5.50}],
     "subtotal":5.50,"hst":0.00,"total":5.50,"payment":"–"},
    {"date":"2026-04-17","time":"12:38","store":"FreshPro Foodmart","addr":"Richmond Hill, ON",
     "items":[{"name":"番石榴","price":7.34},{"name":"黑莓 x2","price":7.98}],
     "subtotal":15.32,"hst":0.00,"total":15.32,"payment":"Mastercard ****4134"},
    {"date":"2026-04-24","time":"12:35","store":"FreshPro Foodmart","addr":"10488 Yonge St, Richmond Hill, ON L4C 3C2",
     "items":[{"name":"甘藍菜 (Green Kale)","price":2.59}],
     "subtotal":2.59,"hst":0.00,"total":2.60,"payment":"Cash"},
]

DATA = {
    "sienna": [
        {"date":"2025-12-12","time":"23:12","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON","litres":59.479,"ppl":1.053,"total":62.63,"ptsEarn":598,"ptsBal":18290},
        {"date":"2026-01-10","time":"23:07","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON","litres":45.580,"ppl":1.059,"total":48.28,"ptsEarn":450,"ptsBal":1010},
        {"date":"2026-01-28","time":"23:15","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON","litres":56.564,"ppl":1.079,"total":61.03,"ptsEarn":2560,"ptsBal":17900},
        {"date":"2026-02-18","time":"23:23","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON","litres":58.962,"ppl":1.129,"total":66.57,"ptsEarn":580,"ptsBal":19520},
        {"date":"2026-03-07","time":"23:05","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON","litres":44.031,"ppl":1.399,"total":61.60,"ptsEarn":440,"ptsBal":1290},
        {"date":"2026-03-10","time":"23:26","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON","litres":63.117,"ppl":1.539,"total":97.14,"ptsEarn":630,"ptsBal":7020},
        {"date":"2026-03-23","time":"23:27","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON","litres":51.240,"ppl":1.629,"total":83.47,"ptsEarn":510,"ptsBal":7530},
        {"date":"2026-04-02","time":"23:19","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON","litres":60.377,"ppl":1.666,"total":100.59,"ptsEarn":600,"ptsBal":8235},
        {"date":"2026-04-06","time":"23:16","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON","litres":40.754,"ppl":1.726,"total":70.34,"ptsEarn":400,"ptsBal":8635},
        {"date":"2026-04-13","time":"23:38","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON","litres":47.200,"ppl":1.599,"total":75.47,"ptsEarn":470,"ptsBal":17136,"km":606.4},
        {"date":"2026-04-20","time":"23:18","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON","litres":46.354,"ppl":1.476,"total":68.42,"ptsEarn":460,"ptsBal":17596,"payment":"Visa ****4106"},
    ],
    "c300": [
        {"date":"2026-04-13","time":"23:10","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON","litres":53.878,"ppl":1.909,"total":102.85,"ptsEarn":530,"ptsBal":16666,"km":530.3},
    ]
}

# ============ SVG 共用：畫折線圖 ============
def _line_svg(labels, vals, color_line, color_fill, color_label, fmt_val, height=110):
    n = len(vals)
    if n == 0:
        return f'<svg width="100%" viewBox="0 0 400 {height}"><text x="50%" y="{height//2}" fill="#3a4a6a" text-anchor="middle" font-size="9">無資料</text></svg>'
    # 每個點至少 48px 寬，確保日期標籤不擠
    width = max(340, n * 48 + 52)
    L, R, T, B = 36, 10, 14, 24
    cw = width - L - R
    ch = height - T - B
    lo = min(vals); hi = max(vals)
    pad = (hi - lo) * 0.12 if hi != lo else max(hi * 0.05, 1)
    lo -= pad; hi += pad
    def px(i): return L + (i / (n-1) if n > 1 else 0.5) * cw
    def py(v): return T + ch * (1 - (v - lo) / (hi - lo))
    parts = []
    # 三條橫格線
    for v in [lo + pad, (lo + hi) / 2, hi - pad]:
        y = py(v)
        parts.append(f'<line x1="{L}" y1="{y:.1f}" x2="{width-R}" y2="{y:.1f}" stroke="#1c1c32" stroke-width="0.8"/>')
        parts.append(f'<text x="{L-3}" y="{y+3:.1f}" fill="#3a4a62" font-size="7.5" text-anchor="end">{fmt_val(v)}</text>')
    # 填色面積
    if n > 1:
        poly = " ".join(f"{px(i):.1f},{py(vals[i]):.1f}" for i in range(n))
        area = f"{px(0):.1f},{T+ch} {poly} {px(n-1):.1f},{T+ch}"
        parts.append(f'<polygon points="{area}" fill="{color_fill}"/>')
        parts.append(f'<polyline points="{poly}" fill="none" stroke="{color_line}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>')
    # 資料點 + 標籤
    for i in range(n):
        x, y = px(i), py(vals[i])
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.8" fill="{color_line}"/>')
        parts.append(f'<text x="{x:.1f}" y="{y-6:.1f}" fill="{color_label}" font-size="7.5" text-anchor="middle">{fmt_val(vals[i])}</text>')
        parts.append(f'<text x="{x:.1f}" y="{height-3}" fill="#3a4a62" font-size="7.5" text-anchor="middle">{labels[i]}</text>')
    return f'<svg width="100%" viewBox="0 0 {width} {height}" style="overflow:visible">{"".join(parts)}</svg>'

# ============ SVG 折線圖（油價走勢）============
def make_price_svg(records):
    if not records: return _line_svg([], [], "#3a7bd5", "rgba(58,123,213,0.15)", "#5a9ad5", lambda v: f"{v:.1f}")
    labels = [r["date"][5:] for r in records]
    vals   = [r["ppl"] * 100 for r in records]
    return _line_svg(labels, vals, "#3a7bd5", "rgba(58,123,213,0.15)", "#5a9ad5", lambda v: f"{v:.1f}")

# ============ SVG 折線圖（油耗效率 L/100km）============
def make_eff_svg(records):
    eff = [(r["date"][5:], r["litres"]/r["km"]*100) for r in records if "km" in r]
    if not eff:
        return f'<svg width="100%" viewBox="0 0 340 110"><text x="50%" y="55" fill="#3a4a6a" text-anchor="middle" font-size="9">填寫里程後顯示</text></svg>'
    labels = [d[0] for d in eff]
    vals   = [d[1] for d in eff]
    return _line_svg(labels, vals, "#4caf90", "rgba(76,175,144,0.15)", "#4caf90", lambda v: f"{v:.2f}")

# ============ 圖表外框（共用包裹樣式）============
def chart_block(title, svg):
    return f"""<div style="margin-bottom:16px">
  <div style="font-size:13px;color:#7a7aaa;margin-bottom:8px;font-weight:600">{title}</div>
  <div style="background:#1a1a2e;border:1px solid #252545;border-radius:12px;padding:14px;overflow:hidden">{svg}</div>
</div>"""

# ============ SVG 折線圖（支出趨勢）============
def make_spending_svg(records, date_key="date", total_key="total"):
    """通用支出趨勢折線圖，records 按日期排序"""
    if not records: return _line_svg([], [], "#f7a048", "rgba(247,160,72,0.15)", "#f7a048", lambda v: f"${v:.0f}")
    sorted_r = sorted(records, key=lambda r: r[date_key])
    labels = [r[date_key][5:] for r in sorted_r]   # MM-DD
    vals   = [r[total_key]    for r in sorted_r]
    return _line_svg(labels, vals, "#f7a048", "rgba(247,160,72,0.15)", "#f7c948", lambda v: f"${v:.0f}")

# ============ 單筆記錄卡片 ============
def make_record_card(r):
    ppl_c = r["ppl"] * 100
    km_html = ""
    if "km" in r:
        kmpl     = r["km"] / r["litres"]
        l100     = r["litres"] / r["km"] * 100
        cost_km  = r["total"] / r["km"]
        km_html = f"""
  <div style="margin-top:8px;padding-top:8px;border-top:1px solid #1e1e3a;display:flex;gap:14px;flex-wrap:wrap">
    <span style="font-size:12px;color:#5a7a9a">里程 <b style="color:#c8d8a8">{r['km']:.1f} km</b></span>
    <span style="font-size:12px;color:#5a7a9a">效率 <b style="color:#4caf90">{kmpl:.2f} km/L</b></span>
    <span style="font-size:12px;color:#5a7a9a">油耗 <b style="color:#4caf90">{l100:.2f} L/100km</b></span>
    <span style="font-size:12px;color:#5a7a9a">每公里 <b style="color:#f7c948">${cost_km:.4f}</b></span>
  </div>"""
    return f"""
<div style="background:#1a1a2e;border:1px solid #252545;border-radius:12px;padding:14px;margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
    <span style="font-size:12px;color:#6a6a9a">{r['date']} {r['time']}</span>
    <span style="font-size:19px;font-weight:700;color:#f7c948">${r['total']:.2f}</span>
  </div>
  <div style="font-size:15px;color:#e0e0f0;margin-bottom:3px">⛽ {r['station']}</div>
  <div style="font-size:11px;color:#3a3a5a;margin-bottom:8px">📍 {r['addr']}</div>
  <div style="display:flex;gap:14px;flex-wrap:wrap">
    <span style="font-size:12px;color:#5a7a9a">油量 <b style="color:#a0b8d8">{r['litres']:.3f} L</b></span>
    <span style="font-size:12px;color:#5a7a9a">單價 <b style="color:#a0b8d8">{ppl_c:.1f} ¢/L</b></span>
    <span style="font-size:12px;color:#5a7a9a">PC點 <b style="color:#a0b8d8">+{r['ptsEarn']}</b></span>
    <span style="font-size:12px;color:#5a7a9a">PC餘額 <b style="color:#7eb8f7">{r['ptsBal']:,}</b></span>
  </div>{km_html}
</div>"""

# ============ 車輛區塊 ============
def make_car_section(car_key, car_label):
    records = DATA[car_key]
    if not records:
        icon = "🚗"
        return f"""<div style="text-align:center;padding:50px 20px;color:#4a4a6a">
  <div style="font-size:44px;margin-bottom:12px">{icon}</div>
  <div>尚無 {car_label} 記錄</div>
  <div style="font-size:12px;margin-top:8px;color:#2a2a4a">拍收據照片傳給 Claude 即可新增</div>
</div>"""

    total_spent  = sum(r["total"]  for r in records)
    total_litres = sum(r["litres"] for r in records)
    avg_ppl      = sum(r["ppl"]    for r in records) / len(records)
    last         = records[-1]
    total_earned = sum(r["ptsEarn"] for r in records)

    price_svg = make_price_svg(records)
    eff_svg   = make_eff_svg(records)
    spend_svg = make_spending_svg(records)
    cards_html = "".join(make_record_card(r) for r in reversed(records))

    return f"""
<!-- PC 點數 -->
<div style="background:linear-gradient(135deg,#162816,#0d160d);border:1px solid #253525;border-radius:12px;padding:14px;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center">
  <div>
    <div style="font-size:11px;color:#4a7a4a;margin-bottom:4px">PC Optimum 餘額</div>
    <div style="font-size:28px;font-weight:700;color:#4caf90">{last['ptsBal']:,}</div>
  </div>
  <div style="text-align:right">
    <div style="font-size:11px;color:#3a5a3a;margin-bottom:4px">全期累計賺取</div>
    <div style="font-size:20px;font-weight:700;color:#7eb8f7">+{total_earned:,}</div>
  </div>
</div>
<!-- 統計 -->
<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:16px">
  <div style="background:#1a1a2e;border:1px solid #252545;border-radius:12px;padding:14px">
    <div style="font-size:11px;color:#5a5a8a;margin-bottom:4px">總花費</div>
    <div style="font-size:22px;font-weight:700;color:#f7c948">${total_spent:.0f}</div>
    <div style="font-size:11px;color:#4a4a6a">CAD · {len(records)} 次</div>
  </div>
  <div style="background:#1a1a2e;border:1px solid #252545;border-radius:12px;padding:14px">
    <div style="font-size:11px;color:#5a5a8a;margin-bottom:4px">總加油量</div>
    <div style="font-size:22px;font-weight:700;color:#7eb8f7">{total_litres:.0f}</div>
    <div style="font-size:11px;color:#4a4a6a">公升</div>
  </div>
  <div style="background:#1a1a2e;border:1px solid #252545;border-radius:12px;padding:14px">
    <div style="font-size:11px;color:#5a5a8a;margin-bottom:4px">平均油價</div>
    <div style="font-size:22px;font-weight:700;color:#7eb8f7">{avg_ppl*100:.1f}</div>
    <div style="font-size:11px;color:#4a4a6a">¢/L</div>
  </div>
  <div style="background:#1a1a2e;border:1px solid #252545;border-radius:12px;padding:14px">
    <div style="font-size:11px;color:#5a5a8a;margin-bottom:4px">最新油價</div>
    <div style="font-size:22px;font-weight:700;color:#4caf90">{last['ppl']*100:.1f}</div>
    <div style="font-size:11px;color:#4a4a6a">¢/L</div>
  </div>
</div>
<!-- 圖表 -->
{chart_block("📈 油價走勢 (¢/L)", price_svg)}
{chart_block("🚗 油耗效率 (L/100km)", eff_svg)}
{chart_block("💸 每次加油花費 ($)", spend_svg)}
<!-- 記錄列表 -->
{cards_html}"""

# ============ 超市卡片 ============
def make_grocery_card(r):
    items_html = "".join(
        f'<div style="display:flex;justify-content:space-between;font-size:12px;color:#c0c0d8;margin-bottom:2px"><span>{it["name"]}</span><span>${it["price"]:.2f}</span></div>'
        for it in r["items"]
    )
    return f"""
<div style="background:#1a1a2e;border:1px solid #252545;border-radius:12px;padding:14px;margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
    <span style="font-size:12px;color:#6a6a9a">{r['date']} {r['time']}</span>
    <span style="font-size:19px;font-weight:700;color:#f7c948">${r['total']:.2f}</span>
  </div>
  <div style="font-size:15px;color:#e0e0f0;margin-bottom:3px">🛒 {r['store']}</div>
  <div style="font-size:11px;color:#3a3a5a;margin-bottom:8px">📍 {r['addr']}</div>
  <div style="border-top:1px solid #1e1e3a;padding-top:8px;margin-top:4px">{items_html}</div>
  <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;padding-top:6px;border-top:1px solid #1e1e3a">
    <span style="font-size:12px;color:#5a7a9a">小計 <b style="color:#a0b8d8">${r['subtotal']:.2f}</b></span>
    <span style="font-size:12px;color:#5a7a9a">HST <b style="color:#a0b8d8">${r['hst']:.2f}</b></span>
    <span style="font-size:12px;color:#5a7a9a">付款 <b style="color:#a0b8d8">{r['payment']}</b></span>
  </div>
</div>"""

def make_grocery_section():
    if not GROCERY:
        return '<div class="empty"><div class="ico">🛒</div><div>尚無超市記錄</div><div style="font-size:12px;margin-top:8px;color:#2a2a4a">拍收據傳給 Claude 即可新增</div></div>'
    total_spent = sum(r["total"] for r in GROCERY)
    total_tx    = len(GROCERY)
    spend_svg   = make_spending_svg(GROCERY)
    cards_html  = "".join(make_grocery_card(r) for r in reversed(GROCERY))
    return f"""
<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:16px">
  <div style="background:#1a1a2e;border:1px solid #252545;border-radius:12px;padding:14px">
    <div style="font-size:11px;color:#5a5a8a;margin-bottom:4px">總花費</div>
    <div style="font-size:22px;font-weight:700;color:#f7c948">${total_spent:.2f}</div>
    <div style="font-size:11px;color:#4a4a6a">CAD · {total_tx} 次</div>
  </div>
  <div style="background:#1a1a2e;border:1px solid #252545;border-radius:12px;padding:14px">
    <div style="font-size:11px;color:#5a5a8a;margin-bottom:4px">筆數</div>
    <div style="font-size:22px;font-weight:700;color:#7eb8f7">{total_tx}</div>
    <div style="font-size:11px;color:#4a4a6a">筆記錄</div>
  </div>
</div>
{chart_block("💸 每筆支出趨勢 ($)", spend_svg)}
{cards_html}"""

# ============ 完整 HTML ============
def build_html():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sienna_html   = make_car_section("sienna", "Sienna")
    c300_html     = make_car_section("c300", "C300")
    grocery_html  = make_grocery_section()

    total_sienna = len(DATA["sienna"])
    total_c300   = len(DATA["c300"])

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="包山包海包生活">
<title>包山包海包生活</title>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:#0d0d1a; color:#e0e0e0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }}
.hdr {{ background:#16213e; padding:14px 16px 10px; border-bottom:1px solid #252545; position:sticky; top:0; z-index:10; }}
.hdr h1 {{ font-size:19px; color:#7eb8f7; font-weight:700; }}
.hdr p  {{ font-size:11px; color:#4a4a6a; margin-top:2px; }}
.nav {{ display:flex; background:#16213e; border-bottom:1px solid #252545; overflow-x:auto; -webkit-overflow-scrolling:touch; }}
.nav a {{ flex:1; min-width:72px; padding:11px 6px; color:#5a5a8a; font-size:13px; text-align:center; border-bottom:3px solid transparent; white-space:nowrap; text-decoration:none; display:block; }}
.car-tabs {{ display:flex; gap:8px; margin:14px 0; }}
.car-tabs a {{ flex:1; padding:10px 8px; border:2px solid #252545; border-radius:10px; background:#14142a; color:#6a6a9a; font-size:13px; text-align:center; text-decoration:none; display:block; }}
.car-tabs a.on {{ border-color:#3a7bd5; color:#7eb8f7; background:#1a2840; }}
.sec {{ padding:14px; }}
.empty {{ text-align:center; padding:50px 20px; color:#3a3a5a; }}
.empty .ico {{ font-size:44px; margin-bottom:12px; }}
/* 所有分頁預設隱藏，#gas 為預設顯示 */
.sec {{ display:none; }}
#gas {{ display:block; }}
/* 切換邏輯：有其他分頁被 target 時，隱藏預設的 #gas */
body:has(#gas-c300:target) #gas,
body:has(#grocery:target)  #gas,
body:has(#dining:target)   #gas,
body:has(#other:target)    #gas {{ display:none; }}
/* 被 target 的分頁顯示 */
:target {{ display:block !important; }}
</style>
</head>
<body>

<div class="hdr">
  <h1>🏠 包山包海包生活</h1>
  <p>最後更新：{now}</p>
</div>

<div class="nav">
  <a href="#gas"      style="color:#7eb8f7;border-bottom:3px solid #3a7bd5">⛽ 加油</a>
  <a href="#grocery"  style="color:#5a5a8a;border-bottom:3px solid transparent">🛒 超市</a>
  <a href="#dining"   style="color:#5a5a8a;border-bottom:3px solid transparent">🍽 餐廳</a>
  <a href="#other"    style="color:#5a5a8a;border-bottom:3px solid transparent">📦 其他</a>
</div>

<!-- ⛽ 加油 — Sienna -->
<div id="gas" class="sec">
  <div class="car-tabs">
    <a href="#gas"      class="on">🚐 Sienna<br><small style="font-size:10px;color:#4a6a9a">白色 · 87 REG · {total_sienna}筆</small></a>
    <a href="#gas-c300"    >🚗 C300<br><small style="font-size:10px;color:#3a3a5a">黑色 · 91 Premium · {total_c300}筆</small></a>
  </div>
  {sienna_html}
</div>

<!-- ⛽ 加油 — C300 -->
<div id="gas-c300" class="sec">
  <div class="car-tabs">
    <a href="#gas"         >🚐 Sienna<br><small style="font-size:10px;color:#3a3a5a">白色 · 87 REG · {total_sienna}筆</small></a>
    <a href="#gas-c300" class="on">🚗 C300<br><small style="font-size:10px;color:#4a6a9a">黑色 · 91 Premium · {total_c300}筆</small></a>
  </div>
  {c300_html}
</div>

<!-- 🛒 超市 -->
<div id="grocery" class="sec">
  {grocery_html}
</div>

<!-- 🍽 餐廳 -->
<div id="dining" class="sec">
  <div class="empty"><div class="ico">🍽</div><div>尚無餐廳記錄</div><div style="font-size:12px;margin-top:8px;color:#2a2a4a">拍收據傳給 Claude 即可新增</div></div>
</div>

<!-- 📦 其他 -->
<div id="other" class="sec">
  <div class="empty"><div class="ico">📦</div><div>尚無其他記錄</div><div style="font-size:12px;margin-top:8px;color:#2a2a4a">拍收據傳給 Claude 即可新增</div></div>
</div>

</body>
</html>"""

# ============ 輸出 ============
html = build_html()

# 自動偵測腳本所在資料夾，輸出到同一位置
COWORK = os.path.dirname(os.path.abspath(__file__))

out_path = os.path.join(COWORK, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ HTML 已寫入：{out_path}")
print(f"   大小：{len(html):,} bytes")
print(f"   Sienna 記錄：{len(DATA['sienna'])} 筆")
print(f"   C300 記錄：{len(DATA['c300'])} 筆")
