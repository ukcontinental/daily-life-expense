#!/usr/bin/env python3
# 生成純靜態 HTML — 零 JavaScript，直接在 iOS QuickLook 顯示

import os
from datetime import datetime

# ============ 全部資料（來源：data.json；主資料庫＝Google Sheet）============
# 資料已從程式碼抽離，改由 data.json 提供。
# data.json 由 Google Sheet 同步而來（見 sync_from_sheet.py）。
import json
_HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_HERE, "data.json"), encoding="utf-8") as _f:
    _DB = json.load(_f)
GROCERY = _DB["grocery"]
DINING  = _DB["dining"]
OTHER   = _DB["other"]
DATA    = _DB["fuel"]

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
def _line_svg(labels, vals, color_line, fmt_val, empty_msg="無資料"):
    H = 110  # SVG 總高（viewBox 高度）
    h = color_line.lstrip('#')
    color_fill = f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},0.08)"
    n = len(vals)
    if n == 0:
        return f'<svg width="100%" viewBox="0 0 400 {H}"><text x="50%" y="55" fill="{C_TEXT3}" text-anchor="middle" font-size="9">{empty_msg}</text></svg>'
    width = max(340, n * 48 + 52)
    L, R, T, B = 36, 10, 14, 24
    cw = width - L - R
    ch = H - T - B
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
        parts.append(f'<text x="{x:.1f}" y="{H-3}" fill="{C_TEXT3}" font-size="7.5" text-anchor="middle">{labels[i]}</text>')
    return f'<svg width="100%" viewBox="0 0 {width} {H}" style="overflow:visible">{"".join(parts)}</svg>'

def make_price_svg(records):
    labels = [r["date"][5:] for r in records]
    vals   = [r["ppl"] * 100 for r in records]
    return _line_svg(labels, vals, C_BLUE, lambda v: f"{v:.1f}")

def make_eff_svg(records):
    eff = [(r["date"][5:], r["litres"]/r["km"]*100) for r in records if r.get("km")]
    labels = [d[0] for d in eff]
    vals   = [d[1] for d in eff]
    return _line_svg(labels, vals, C_GREEN, lambda v: f"{v:.2f}", empty_msg="填寫里程後顯示")

def make_spending_svg(records):
    sorted_r = sorted(records, key=lambda r: r["date"])
    labels = [r["date"][5:] for r in sorted_r]
    vals   = [r["total"]    for r in sorted_r]
    return _line_svg(labels, vals, C_ORANGE, lambda v: f"${v:.0f}")

# ============ 圖表外框 ============
def chart_block(title, svg):
    return f"""<div style="margin-bottom:24px">
  <div style="font-size:10px;color:{C_TEXT3};margin-bottom:10px;letter-spacing:0.12em;text-transform:uppercase">{title}</div>
  <div style="background:{C_SURFACE};border:1px solid {C_BORDER};border-radius:12px;padding:14px 12px;overflow:hidden">{svg}</div>
</div>"""

# ============ 空狀態 ============
def empty_state(label):
    return f'<div class="empty"><div style="font-size:13px;letter-spacing:0.04em;color:{C_TEXT2}">{label}</div><div style="font-size:12px;margin-top:10px;color:{C_TEXT3}">尚無記錄 · 拍收據傳給 Claude 即可新增</div></div>'

# ============ 小型大寫節區標籤 ============
def section_label(text):
    return f'<div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.12em;text-transform:uppercase;margin-bottom:12px">{text}</div>'

# ============ 統計數字卡片 ============
def stat_card(label, value, unit, color=None):
    col = color or C_TEXT1
    return f"""<div style="background:{C_SURFACE};border:1px solid {C_BORDER};border-radius:12px;padding:18px 16px">
  <div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px">{label}</div>
  <div style="font-size:26px;font-weight:600;color:{col};letter-spacing:-0.5px;line-height:1">{value}</div>
  <div style="font-size:11px;color:{C_TEXT3};margin-top:6px">{unit}</div>
</div>"""

# ============ 2 欄 stat_card 網格（車輛區塊 / 清單區塊 共用）============
def stat_grid(*cards):
    return '<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:24px">\n  ' + "\n  ".join(cards) + '\n</div>'

# ============ 共用：flex 內小型 stat cell（label-on-top + value + 可選 unit）============
def stat_cell(label, value, unit="", color=None, extra_style=""):
    col = color or C_TEXT1
    unit_html = f' <span style="font-size:11px;color:{C_TEXT3}">{unit}</span>' if unit else ''
    return f"""<div style="flex:1{extra_style}">
      <div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px">{label}</div>
      <div style="font-size:15px;font-weight:500;color:{col}">{value}{unit_html}</div>
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

# ============ 共用：底部 label-value meta 列 ============
def meta_row(pairs, padding_top="10px"):
    items = "\n    ".join(
        f'<div><span style="font-size:10px;color:{C_TEXT3};text-transform:uppercase;letter-spacing:0.08em">{label} </span><span style="font-size:12px;color:{C_TEXT2}">{value}</span></div>'
        for label, value in pairs
    )
    return f'<div style="display:flex;gap:16px;flex-wrap:wrap;padding-top:{padding_top};border-top:1px solid {C_BORDER}">\n    {items}\n  </div>'

# ============ 單筆加油記錄卡片 ============
def make_record_card(r):
    ppl_c = r["ppl"] * 100
    km_html = ""
    if r.get("km"):
        l100     = r["litres"] / r["km"] * 100
        cost_km  = r["total"] / r["km"]
        km_html = f"""
  <div style="margin-top:12px;padding-top:12px;border-top:1px solid {C_BORDER};display:flex;gap:0;flex-wrap:wrap">
    {stat_cell("里程", f"{r['km']:.1f}", "km", extra_style=";min-width:80px;padding-right:10px")}
    {stat_cell("油耗", f"{l100:.2f}", "L/100km", C_GREEN, ";min-width:80px;padding-right:10px")}
    {stat_cell("每公里", f"${cost_km:.4f}", "", C_ORANGE, ";min-width:80px")}
  </div>"""
    return f"""{card_header(r['station'], r['addr'], r['total'], r['date'], r['time'])}
  <div style="display:flex;gap:0;padding-top:10px;border-top:1px solid {C_BORDER}">
    {stat_cell("油量", f"{r['litres']:.3f}", "L")}
    {stat_cell("單價", f"{ppl_c:.1f}", "¢/L", C_BLUE)}
    {stat_cell("PC 點", f"+{r['ptsEarn']:,}")}
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
    pc_lbl = f"font-size:10px;color:{C_TEXT3};letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px"

    return f"""
<div style="background:{C_SURFACE};border:1px solid {C_BORDER};border-radius:12px;padding:18px;margin-bottom:14px;display:flex;justify-content:space-between;align-items:center">
  <div>
    <div style="{pc_lbl}">PC Optimum 餘額</div>
    <div style="font-size:32px;font-weight:600;color:{C_GREEN};letter-spacing:-0.5px">{last['ptsBal']:,}</div>
  </div>
  <div style="text-align:right">
    <div style="{pc_lbl}">累計賺取</div>
    <div style="font-size:22px;font-weight:600;color:{C_BLUE}">+{total_earned:,}</div>
  </div>
</div>
{stat_grid(
    stat_card("總花費", f"${total_spent:.0f}", f"CAD · {len(records)} 次", C_ORANGE),
    stat_card("總加油量", f"{total_litres:.0f}", "公升"),
    stat_card("平均油價", f"{avg_ppl*100:.1f}", "¢/L", C_BLUE),
    stat_card("最新油價", f"{last['ppl']*100:.1f}", "¢/L", C_GREEN),
)}
{chart_block("油價走勢  ¢/L", make_price_svg(records))}
{chart_block("油耗效率  L / 100 km", make_eff_svg(records))}
{chart_block("每次花費  CAD", make_spending_svg(records))}
{section_label("加油記錄")}
{cards_html}"""

# ============ 商品列表卡片（超市 / 餐廳 共用）============
def make_itemized_card(r):
    items_html = "".join(
        f'<div style="display:flex;justify-content:space-between;font-size:13px;color:{C_TEXT2};margin-bottom:5px;line-height:1.4"><span style="padding-right:12px">{it["name"]}</span><span style="flex-shrink:0">${it["price"]:.2f}</span></div>'
        for it in r["items"]
    )
    subtotal = sum(it["price"] for it in r["items"])
    return f"""{card_header(r['store'], r['addr'], r['total'], r['date'], r['time'])}
  <div style="border-top:1px solid {C_BORDER};padding-top:10px;margin-bottom:10px">{items_html}</div>
  {meta_row([("小計", f"${subtotal:.2f}"), ("HST", f"${r['hst']:.2f}"), ("付款", r['payment'])], "8px")}
</div>"""

# ============ 其他卡片 ============
def make_other_card(r):
    return f"""{card_header(r['desc'], r['note'], r['total'], r['date'], r['time'], ';line-height:1.5')}
  {meta_row([("類別", r['category']), ("付款", r['payment'])])}
</div>"""

# ============ 通用清單區塊（超市/其他/未來分頁共用）============
def make_list_section(records, empty_label, card_fn, count_unit, list_label):
    if not records:
        return empty_state(empty_label)
    total_spent = sum(r["total"] for r in records)
    n = len(records)
    cards_html = "".join(card_fn(r) for r in reversed(records))
    return f"""
{stat_grid(
    stat_card("總花費", f"${total_spent:.2f}", f"CAD · {n} {count_unit}", C_ORANGE),
    stat_card("筆數", str(n), "筆記錄"),
)}
{chart_block("每筆支出趨勢  CAD", make_spending_svg(records))}
{section_label(list_label)}
{cards_html}"""

# ============ 車輛分頁切換器（共用：兩個 gas section 都用同一份定義）============
def car_tabs(active):
    tabs = [
        ("#gas",      "Sienna", "白色  87 REG",     len(DATA["sienna"])),
        ("#gas-c300", "C300",   "黑色  91 Premium", len(DATA["c300"])),
    ]
    links = []
    for href, name, label, count in tabs:
        on = ' class="on"' if href == active else ''
        op = "0.6" if href == active else "0.4"
        links.append(f'<a href="{href}"{on}>{name}<br><small style="font-size:10px;letter-spacing:0.04em;opacity:{op}">{label}  {count} 筆</small></a>')
    return '<div class="car-tabs">\n    ' + '\n    '.join(links) + '\n  </div>'

# ============ 完整 HTML ============
def build_html():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sienna_html   = make_car_section("sienna", "Sienna")
    c300_html     = make_car_section("c300", "C300")
    grocery_html  = make_list_section(GROCERY, "超市購物", make_itemized_card, "次", "購物記錄")
    dining_html   = make_list_section(DINING,  "餐廳外食", make_itemized_card, "次", "消費記錄")
    other_html    = make_list_section(OTHER,   "其他支出", make_other_card,   "筆", "支出記錄")

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
body:has(#grocery:target) .nav a[href="#grocery"],
body:has(#dining:target)  .nav a[href="#dining"],
body:has(#other:target)   .nav a[href="#other"]   {{ color:{C_TEXT1}; border-bottom-color:{C_BLUE}; }}
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
  {car_tabs("#gas")}
  {sienna_html}
</div>

<div id="gas-c300" class="sec">
  {car_tabs("#gas-c300")}
  {c300_html}
</div>

<div id="grocery" class="sec">
  {grocery_html}
</div>

<div id="dining" class="sec">
  {dining_html}
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
