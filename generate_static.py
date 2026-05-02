#!/usr/bin/env python3
# 生成純靜態 HTML — 零 JavaScript，直接在 iOS QuickLook 顯示

import os
from datetime import datetime

# ============ 全部資料 ============
GROCERY = [
    {"date":"2025-11-14","time":"–","store":"Chuang's Company LTD. 莊記","addr":"110 Denison St. Unit #8, Markham, ON L3R 1B6",
     "items":[{"name":"「莊記」板麻 XO 魷魚醬 250g","price":13.00}],
     "subtotal":13.00,"hst":0.00,"total":13.00,"payment":"Debit"},
    {"date":"2026-05-01","time":"–","store":"Chuang's Company LTD. 莊記","addr":"110 Denison St. Unit #8, Markham, ON L3R 1B6",
     "items":[
       {"name":"台灣香腸味黏糯米飯糰 Sausage Sticky Rice Snack","price":1.00},
       {"name":"茉莉魚子香黏糯米水果飯 Midfin Roe Rice Snack","price":1.00},
       {"name":"茉莉芒果味黏糯米水果飯 Mango Rice Snack","price":1.00},
       {"name":"大師傅皮蛋味零食 Century Egg Flavor Snack x2","price":6.00},
       {"name":"芒果白木瓜仙貝 Mango Papaya Rice Cake Chips","price":3.00},
       {"name":"白胡椒天婦羅蝦條 White Pepper Tempura Chips","price":3.80},
       {"name":"清淡拌油素蘿蔔細麵 DaDan Thin Noodles","price":0.00},
       {"name":"清淡拌油花椒麵 Peppercorn Noodle","price":0.00},
     ],
     "subtotal":15.80,"hst":1.99,"total":17.79,"payment":"Debit"},
    {"date":"2026-05-01","time":"12:14","store":"FreshPro Foodmart","addr":"10488 Yonge St, Richmond Hill, ON L4C 3C2",
     "items":[{"name":"走地雞奧美加黃雞蛋 Free Run Brown Omega-3 Egg x2（ON SALE）","price":9.98}],
     "subtotal":9.98,"hst":0.00,"total":9.98,"payment":"Visa ****4106"},
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
    {"date":"2026-04-25","time":"11:07","store":"Freshway Foodmart","addr":"3275 Highway 7, Markham, ON",
     "items":[{"name":"韓國魚餅","price":5.99},{"name":"走地雞蛋 18粒","price":7.99},{"name":"中廚 燒餅系列","price":9.99},{"name":"新鮮金錢腱","price":17.35},{"name":"Onion 2LB","price":1.79},{"name":"Onion 2LB","price":1.21},{"name":"CM 皮蛋/紅心鹹蛋","price":2.99},{"name":"豐業 上海五香豆乾","price":3.99},{"name":"白蘿蔔","price":2.28},{"name":"新鮮金錢腱","price":16.95},{"name":"芥蘭菇","price":2.99},{"name":"有頭菠菜","price":3.02},{"name":"番薯葉","price":5.79},{"name":"草莓 x2","price":11.76},{"name":"Lucky 7's 牛油果","price":3.59},{"name":"Sweet Potato","price":12.23},{"name":"蜜豆","price":4.04}],
     "subtotal":113.95,"hst":0.00,"total":113.95,"payment":"Visa ****0891"},
    {"date":"2026-04-25","time":"10:36","store":"Kuo Hua 國華","addr":"270 Ferrier Street, Markham, ON L3R 2Z5",
     "items":[{"name":"KC 港橋拱包 650g","price":5.99},{"name":"AGV 蜜底瓜片 140g","price":2.49},{"name":"AGV 豆乾筋 170g","price":2.49},{"name":"AGV 鮮脆瓜 180g","price":2.49},{"name":"蒜味香腸","price":8.99},{"name":"國華無刺虱目魚肚 180g","price":9.90},{"name":"麒麟 新竹米粉 340g","price":2.99}],
     "subtotal":35.34,"hst":0.00,"total":35.34,"payment":"Cash"},
    {"date":"2026-04-25","time":"11:51","store":"T&T Supermarket","addr":"9255 Woodbine Avenue, Markham, ON L6C 1Y9",
     "items":[{"name":"Kewpie 沙拉醬","price":5.97},{"name":"大腸切片","price":6.85},{"name":"十粒粽（冷）","price":42.21},{"name":"T&T 保溫袋","price":2.50},{"name":"頂級叉燒肉片 x2","price":12.21},{"name":"水晶梨","price":2.78},{"name":"盒裝精品貝貝小南瓜","price":4.98},{"name":"日昇西施豆腐","price":2.59},{"name":"T&T 中式豬肉腸","price":7.59},{"name":"保溫袋折扣","price":-2.50}],
     "subtotal":85.18,"hst":0.89,"total":86.07,"payment":"Visa ****0891"},
    {"date":"2026-04-25","time":"21:29","store":"Walmart","addr":"1070 Major Mackenzie Dr E, Richmond Hill, ON L4S 1P3",
     "items":[{"name":"RESG 1.38kg","price":11.47},{"name":"PNT BTR 750g","price":5.97},{"name":"Dole Pineapple","price":2.47},{"name":"CL Cltuna SJ x4","price":7.52},{"name":"Tabasco Red","price":7.27}],
     "subtotal":34.70,"hst":1.49,"total":36.19,"payment":"Visa ****0891"},
    {"date":"2026-05-01","time":"12:14","store":"FreshPro Foodmart","addr":"10488 Yonge St, Richmond Hill, ON L4C 3C2",
     "items":[{"name":"走地雞奧美加黃雞蛋 大粒 (ON SALE)","price":4.99},{"name":"走地雞奧美加黃雞蛋 大粒 (ON SALE)","price":4.99}],
     "subtotal":9.98,"hst":0.00,"total":9.98,"payment":"Visa ****4106"},
    {"date":"2026-05-01","time":"–","store":"Chuang's Company LTD. 莊記","addr":"110 Denison St. Unit #8, Markham, ON L3R 1B6",
     "items":[{"name":"乖乖大腸包小腸風味米乖乖 60g","price":1.00},{"name":"乖乖烏魚子風味米乖乖 52g","price":1.00},{"name":"乖乖夏雪芒果風味米乖乖 52g","price":1.00},{"name":"Doritos 皮蛋口味玉米片 102g x2","price":6.00},{"name":"永恆世成 全素白胡椒風味米血脆片 45g","price":3.00},{"name":"永恆世成 白胡椒風味甜不辣脆片 45g","price":3.00},{"name":"深夜食堂 麻油蒜香麵線 108g x4pc","price":6.00},{"name":"深夜食堂 油蔥椒麻乾拌麵 116g x4pc","price":6.00}],
     "subtotal":27.00,"hst":1.95,"total":28.95,"payment":"Debit"},
]

OTHER = [
    {"date":"2026-04-30","time":"–","category":"罰單","desc":"City of Toronto APS 超速罰單",
     "note":"Penalty Order #2026-901-51-27930082-001 | 罰款 $260 + Victim Justice Fund $60 + MTO Look Up $8.25",
     "total":328.25,"payment":"線上繳費"},
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
        {"date":"2026-04-27","time":"23:20","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON L4E 0V5","litres":39.658,"ppl":1.616,"total":64.09,"ptsEarn":4390,"ptsBal":21986,"km":558.5},
    ],
    "c300": [
        {"date":"2026-04-13","time":"23:10","station":"Esso Circle K","addr":"12338 Yonge St, Richmond Hill, ON","litres":53.878,"ppl":1.909,"total":102.85,"ptsEarn":530,"ptsBal":16666,"km":530.3},
    ]
}

# ============ 顏色常數（淺色系 Apple/MUJI 風）============
C_BG       = "#f5f5f7"   # 頁面背景
C_SURFACE  = "#ffffff"   # 卡片白
C_BORDER   = "rgba(0,0,0,0.08)"
C_TEXT1    = "#1d1d1f"   # 主文字
C_TEXT2    = "rgba(0,0,0,0.5)"   # 次要文字
C_TEXT3    = "rgba(0,0,0,0.3)"   # 輔助文字
C_BLUE     = "#0071e3"
C_GREEN    = "#1a8c3e"
C_ORANGE   = "#c45000"
C_NAV_BG   = "rgba(245,245,247,0.9)"

# ============ SVG 共用：畫折線圖 ============
def _line_svg(labels, vals, color_line, color_fill, fmt_val, height=110):
    n = len(vals)
    if n == 0:
        return f'<svg width="100%" viewBox="0 0 400 {height}"><text x="50%" y="{height//2}" fill="{C_TEXT3}" text-anchor="middle" font-size="9">無資料</text></svg>'
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
    for v in [lo + pad, (lo + hi) / 2, hi - pad]:
        y = py(v)
        parts.append(f'<line x1="{L}" y1="{y:.1f}" x2="{width-R}" y2="{y:.1f}" stroke="rgba(0,0,0,0.06)" stroke-width="0.8"/>')
        parts.append(f'<text x="{L-3}" y="{y+3:.1f}" fill="{C_TEXT3}" font-size="7.5" text-anchor="end">{fmt_val(v)}</text>')
    if n > 1:
        poly = " ".join(f"{px(i):.1f},{py(vals[i]):.1f}" for i in range(n))
        area = f"{px(0):.1f},{T+ch} {poly} {px(n-1):.1f},{T+ch}"
        parts.append(f'<polygon points="{area}" fill="{color_fill}"/>')
        parts.append(f'<polyline points="{poly}" fill="none" stroke="{color_line}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>')
    for i in range(n):
        x, y = px(i), py(vals[i])
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{color_line}"/>')
        parts.append(f'<text x="{x:.1f}" y="{y-6:.1f}" fill="{C_TEXT1}" font-size="7.5" text-anchor="middle" font-weight="500">{fmt_val(vals[i])}</text>')
        parts.append(f'<text x="{x:.1f}" y="{height-3}" fill="{C_TEXT3}" font-size="7.5" text-anchor="middle">{labels[i]}</text>')
    return f'<svg width="100%" viewBox="0 0 {width} {height}" style="overflow:visible">{"".join(parts)}</svg>'

def make_price_svg(records):
    labels = [r["date"][5:] for r in records]
    vals   = [r["ppl"] * 100 for r in records]
    return _line_svg(labels, vals, C_BLUE, "rgba(0,113,227,0.08)", lambda v: f"{v:.1f}")

def make_eff_svg(records):
    eff = [(r["date"][5:], r["litres"]/r["km"]*100) for r in records if "km" in r]
    if not eff:
        return f'<svg width="100%" viewBox="0 0 340 110"><text x="50%" y="55" fill="{C_TEXT3}" text-anchor="middle" font-size="9">填寫里程後顯示</text></svg>'
    labels = [d[0] for d in eff]
    vals   = [d[1] for d in eff]
    return _line_svg(labels, vals, C_GREEN, "rgba(26,140,62,0.08)", lambda v: f"{v:.2f}")

def make_spending_svg(records, date_key="date", total_key="total"):
    sorted_r = sorted(records, key=lambda r: r[date_key])
    labels = [r[date_key][5:] for r in sorted_r]
    vals   = [r[total_key]    for r in sorted_r]
    return _line_svg(labels, vals, C_ORANGE, "rgba(196,80,0,0.08)", lambda v: f"${v:.0f}")

# ============ 圖表外框 ============
def chart_block(title, svg):
    return f"""<div style="margin-bottom:24px">
  <div style="font-size:10px;color:{C_TEXT3};margin-bottom:10px;letter-spacing:0.12em;text-transform:uppercase">{title}</div>
  <div style="background:{C_SURFACE};border:1px solid {C_BORDER};border-radius:12px;padding:14px 12px;overflow:hidden">{svg}</div>
</div>"""

# ============ 空狀態 ============
def empty_state(label):
    return f'<div class="empty"><div style="font-size:13px;letter-spacing:0.04em;color:{C_TEXT2}">{label}</div><div style="font-size:12px;margin-top:10px;color:{C_TEXT3}">尚無記錄 · 拍收據傳給 Claude 即可新增</div></div>'

# ============ 統計數字卡片 ============
def stat_card(label, value, unit, color=None):
    col = color or C_TEXT1
    return f"""<div style="background:{C_SURFACE};border:1px solid {C_BORDER};border-radius:12px;padding:18px 16px">
  <div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px">{label}</div>
  <div style="font-size:26px;font-weight:600;color:{col};letter-spacing:-0.5px;line-height:1">{value}</div>
  <div style="font-size:11px;color:{C_TEXT3};margin-top:6px">{unit}</div>
</div>"""

# ============ 卡片頭（標題/副標 + 右側總額/日期）共用 ============
def card_header(title, subtitle, total, date, time, subtitle_extra=""):
    return f"""
<div style="background:{C_SURFACE};border:1px solid {C_BORDER};border-radius:12px;padding:16px;margin-bottom:10px">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px">
    <div>
      <div style="font-size:15px;font-weight:500;color:{C_TEXT1}">{title}</div>
      <div style="font-size:11px;color:{C_TEXT3};margin-top:3px{subtitle_extra}">{subtitle}</div>
    </div>
    <div style="text-align:right;flex-shrink:0;margin-left:12px">
      <div style="font-size:22px;font-weight:600;color:{C_ORANGE};letter-spacing:-0.3px">${total:.2f}</div>
      <div style="font-size:11px;color:{C_TEXT3};margin-top:2px">{date} · {time}</div>
    </div>
  </div>"""

# ============ 單筆加油記錄卡片 ============
def make_record_card(r):
    ppl_c = r["ppl"] * 100
    km_html = ""
    if "km" in r:
        l100     = r["litres"] / r["km"] * 100
        cost_km  = r["total"] / r["km"]
        km_html = f"""
  <div style="margin-top:12px;padding-top:12px;border-top:1px solid {C_BORDER};display:flex;gap:0;flex-wrap:wrap">
    <div style="flex:1;min-width:80px;padding-right:10px">
      <div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px">里程</div>
      <div style="font-size:15px;font-weight:500;color:{C_TEXT1}">{r['km']:.1f} <span style="font-size:11px;color:{C_TEXT3}">km</span></div>
    </div>
    <div style="flex:1;min-width:80px;padding-right:10px">
      <div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px">油耗</div>
      <div style="font-size:15px;font-weight:500;color:{C_GREEN}">{l100:.2f} <span style="font-size:11px;color:{C_TEXT3}">L/100km</span></div>
    </div>
    <div style="flex:1;min-width:80px">
      <div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px">每公里</div>
      <div style="font-size:15px;font-weight:500;color:{C_ORANGE}">${cost_km:.4f}</div>
    </div>
  </div>"""
    return f"""{card_header(r['station'], r['addr'], r['total'], r['date'], r['time'])}
  <div style="display:flex;gap:0;padding-top:10px;border-top:1px solid {C_BORDER}">
    <div style="flex:1">
      <div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px">油量</div>
      <div style="font-size:15px;font-weight:500;color:{C_TEXT1}">{r['litres']:.3f} <span style="font-size:11px;color:{C_TEXT3}">L</span></div>
    </div>
    <div style="flex:1">
      <div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px">單價</div>
      <div style="font-size:15px;font-weight:500;color:{C_BLUE}">{ppl_c:.1f} <span style="font-size:11px;color:{C_TEXT3}">¢/L</span></div>
    </div>
    <div style="flex:1">
      <div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px">PC 點</div>
      <div style="font-size:15px;font-weight:500;color:{C_TEXT1}">+{r['ptsEarn']:,}</div>
    </div>
  </div>{km_html}
</div>"""

# ============ 車輛區塊 ============
def make_car_section(car_key, car_label):
    records = DATA[car_key]
    if not records:
        return empty_state(f"{car_label} 加油")

    total_spent  = sum(r["total"]  for r in records)
    total_litres = sum(r["litres"] for r in records)
    avg_ppl      = sum(r["ppl"]    for r in records) / len(records)
    last         = records[-1]
    total_earned = sum(r["ptsEarn"] for r in records)

    cards_html = "".join(make_record_card(r) for r in reversed(records))

    return f"""
<div style="background:{C_SURFACE};border:1px solid {C_BORDER};border-radius:12px;padding:18px;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center">
  <div>
    <div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px">PC Optimum 餘額</div>
    <div style="font-size:32px;font-weight:600;color:{C_GREEN};letter-spacing:-0.5px">{last['ptsBal']:,}</div>
  </div>
  <div style="text-align:right">
    <div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px">累計賺取</div>
    <div style="font-size:22px;font-weight:600;color:{C_BLUE}">+{total_earned:,}</div>
  </div>
</div>
<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:24px">
  {stat_card("總花費", f"${total_spent:.0f}", f"CAD · {len(records)} 次", C_ORANGE)}
  {stat_card("總加油量", f"{total_litres:.0f}", "公升")}
  {stat_card("平均油價", f"{avg_ppl*100:.1f}", "¢/L", C_BLUE)}
  {stat_card("最新油價", f"{last['ppl']*100:.1f}", "¢/L", C_GREEN)}
</div>
{chart_block("油價走勢  ¢/L", make_price_svg(records))}
{chart_block("油耗效率  L / 100 km", make_eff_svg(records))}
{chart_block("每次花費  CAD", make_spending_svg(records))}
<div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px">加油記錄</div>
{cards_html}"""

# ============ 超市卡片 ============
def make_grocery_card(r):
    items_html = "".join(
        f'<div style="display:flex;justify-content:space-between;font-size:13px;color:{C_TEXT2};margin-bottom:5px;line-height:1.4"><span style="padding-right:12px">{it["name"]}</span><span style="flex-shrink:0">${it["price"]:.2f}</span></div>'
        for it in r["items"]
    )
    return f"""{card_header(r['store'], r['addr'], r['total'], r['date'], r['time'])}
  <div style="border-top:1px solid {C_BORDER};padding-top:10px;margin-bottom:10px">{items_html}</div>
  <div style="display:flex;gap:16px;flex-wrap:wrap;padding-top:8px;border-top:1px solid {C_BORDER}">
    <div><span style="font-size:10px;color:{C_TEXT3};text-transform:uppercase;letter-spacing:0.08em">小計 </span><span style="font-size:12px;color:{C_TEXT2}">${r['subtotal']:.2f}</span></div>
    <div><span style="font-size:10px;color:{C_TEXT3};text-transform:uppercase;letter-spacing:0.08em">HST </span><span style="font-size:12px;color:{C_TEXT2}">${r['hst']:.2f}</span></div>
    <div><span style="font-size:10px;color:{C_TEXT3};text-transform:uppercase;letter-spacing:0.08em">付款 </span><span style="font-size:12px;color:{C_TEXT2}">{r['payment']}</span></div>
  </div>
</div>"""

# ============ 其他卡片 ============
def make_other_card(r):
    return f"""{card_header(r['desc'], r['note'], r['total'], r['date'], r['time'], ';line-height:1.5')}
  <div style="display:flex;gap:16px;flex-wrap:wrap;padding-top:10px;border-top:1px solid {C_BORDER}">
    <div><span style="font-size:10px;color:{C_TEXT3};text-transform:uppercase;letter-spacing:0.08em">類別 </span><span style="font-size:12px;color:{C_TEXT2}">{r['category']}</span></div>
    <div><span style="font-size:10px;color:{C_TEXT3};text-transform:uppercase;letter-spacing:0.08em">付款 </span><span style="font-size:12px;color:{C_TEXT2}">{r['payment']}</span></div>
  </div>
</div>"""

# ============ 通用清單區塊（超市/其他/未來分頁共用）============
def make_list_section(records, empty_label, card_fn, count_unit, list_label):
    if not records:
        return empty_state(empty_label)
    total_spent = sum(r["total"] for r in records)
    n = len(records)
    cards_html = "".join(card_fn(r) for r in reversed(records))
    return f"""
<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:24px">
  {stat_card("總花費", f"${total_spent:.2f}", f"CAD · {n} {count_unit}", C_ORANGE)}
  {stat_card("筆數", str(n), "筆記錄")}
</div>
{chart_block("每筆支出趨勢  CAD", make_spending_svg(records))}
<div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px">{list_label}</div>
{cards_html}"""

# ============ 完整 HTML ============
def build_html():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sienna_html   = make_car_section("sienna", "Sienna")
    c300_html     = make_car_section("c300", "C300")
    grocery_html  = make_list_section(GROCERY, "超市購物", make_grocery_card, "次", "購物記錄")
    other_html    = make_list_section(OTHER,   "其他支出", make_other_card,   "筆", "支出記錄")
    total_sienna  = len(DATA["sienna"])
    total_c300    = len(DATA["c300"])

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="生活支出">
<title>生活支出</title>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
html, body {{ background:{C_BG}; }}
body {{
  color:{C_TEXT1};
  font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Helvetica Neue',sans-serif;
  -webkit-font-smoothing:antialiased;
}}
.hdr {{
  background:{C_NAV_BG};
  padding:16px 20px 12px;
  border-bottom:1px solid rgba(0,0,0,0.1);
  position:sticky; top:0; z-index:10;
  backdrop-filter:saturate(180%) blur(20px);
  -webkit-backdrop-filter:saturate(180%) blur(20px);
}}
.hdr h1 {{ font-size:18px; color:{C_TEXT1}; font-weight:700; letter-spacing:-0.2px; }}
.hdr p  {{ font-size:11px; color:{C_TEXT3}; margin-top:3px; letter-spacing:0.02em; }}
.nav {{
  display:flex;
  background:{C_NAV_BG};
  border-bottom:1px solid rgba(0,0,0,0.1);
  overflow-x:auto;
  -webkit-overflow-scrolling:touch;
  backdrop-filter:saturate(180%) blur(20px);
  -webkit-backdrop-filter:saturate(180%) blur(20px);
}}
.nav a {{
  flex:1; min-width:80px; padding:12px 8px 11px;
  color:{C_TEXT3};
  font-size:13px; text-align:center;
  border-bottom:2px solid transparent;
  white-space:nowrap; text-decoration:none; display:block;
  letter-spacing:0.01em;
}}
.car-tabs {{ display:flex; gap:10px; margin:16px 0; }}
.car-tabs a {{
  flex:1; padding:12px 10px;
  border:1px solid rgba(0,0,0,0.1);
  border-radius:10px;
  background:{C_SURFACE};
  color:{C_TEXT3};
  font-size:13px; text-align:center; text-decoration:none; display:block;
}}
.car-tabs a.on {{ border-color:{C_BLUE}; color:{C_BLUE}; background:rgba(0,113,227,0.05); }}
.sec {{ padding:20px 20px 50px; }}
.empty {{ text-align:center; padding:60px 20px; }}
/* 分頁切換邏輯 */
.sec {{ display:none; }}
#gas {{ display:block; }}
body:has(#gas-c300:target) #gas,
body:has(#grocery:target)  #gas,
body:has(#dining:target)   #gas,
body:has(#other:target)    #gas {{ display:none; }}
:target {{ display:block !important; }}
/* 導航底線 */
.nav a[href="#gas"] {{ color:{C_TEXT1}; border-bottom-color:{C_BLUE}; }}
body:has(#grocery:target) .nav a[href="#gas"],
body:has(#dining:target)  .nav a[href="#gas"],
body:has(#other:target)   .nav a[href="#gas"] {{ color:{C_TEXT3}; border-bottom-color:transparent; }}
body:has(#grocery:target) .nav a[href="#grocery"] {{ color:{C_TEXT1}; border-bottom-color:{C_BLUE}; }}
body:has(#dining:target)  .nav a[href="#dining"]  {{ color:{C_TEXT1}; border-bottom-color:{C_BLUE}; }}
body:has(#other:target)   .nav a[href="#other"]   {{ color:{C_TEXT1}; border-bottom-color:{C_BLUE}; }}
body:has(#gas-c300:target) .nav a[href="#gas"]    {{ color:{C_TEXT1}; border-bottom-color:{C_BLUE}; }}
</style>
</head>
<body>

<div class="hdr">
  <h1>生活支出</h1>
  <p>更新於 {now}</p>
</div>

<div class="nav">
  <a href="#gas">加油</a>
  <a href="#grocery">超市</a>
  <a href="#dining">餐廳</a>
  <a href="#other">其他</a>
</div>

<div id="gas" class="sec">
  <div class="car-tabs">
    <a href="#gas" class="on">Sienna<br><small style="font-size:10px;letter-spacing:0.04em;opacity:0.6">白色  87 REG  {total_sienna} 筆</small></a>
    <a href="#gas-c300">C300<br><small style="font-size:10px;letter-spacing:0.04em;opacity:0.4">黑色  91 Premium  {total_c300} 筆</small></a>
  </div>
  {sienna_html}
</div>

<div id="gas-c300" class="sec">
  <div class="car-tabs">
    <a href="#gas">Sienna<br><small style="font-size:10px;letter-spacing:0.04em;opacity:0.4">白色  87 REG  {total_sienna} 筆</small></a>
    <a href="#gas-c300" class="on">C300<br><small style="font-size:10px;letter-spacing:0.04em;opacity:0.6">黑色  91 Premium  {total_c300} 筆</small></a>
  </div>
  {c300_html}
</div>

<div id="grocery" class="sec">
  {grocery_html}
</div>

<div id="dining" class="sec">
  {empty_state("餐廳")}
</div>

<div id="other" class="sec">
  {other_html}
</div>

</body>
</html>"""

# ============ 輸出 ============
html = build_html()
COWORK = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(COWORK, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"✅ HTML 已寫入：{out_path}")
print(f"   大小：{len(html):,} bytes")
print(f"   Sienna：{len(DATA['sienna'])} 筆  C300：{len(DATA['c300'])} 筆")
