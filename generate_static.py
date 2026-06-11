#!/usr/bin/env python3
# 生成純靜態 HTML — 零 JavaScript，直接在 iOS QuickLook 顯示

import os
from datetime import datetime
from zoneinfo import ZoneInfo

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

# Utility 帳單分析資料（來源：utilities.json，由帳單 PDF 抽取）
try:
    with open(os.path.join(_HERE, "utilities.json"), encoding="utf-8") as _uf:
        _UTIL = json.load(_uf)
except Exception:
    _UTIL = None

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
C_PURPLE   = "#9333ea"
# 四項 utility 配色
C_UTIL = {"瓦斯": C_ORANGE, "水費": C_BLUE, "熱水器": C_PURPLE, "電力": C_GREEN}

# ============ SVG 共用：十六進位色碼 → rgba(含 alpha) ============
def hex_rgba(hex_color, alpha):
    h = hex_color.lstrip('#')
    return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{alpha})"

# ============ SVG 共用：空狀態 placeholder（三個 SVG 函式共用）============
def _empty_svg(width, height, msg="無資料"):
    return f'<svg width="100%" viewBox="0 0 {width} {height}"><text x="50%" y="50%" fill="{C_TEXT3}" text-anchor="middle" font-size="9">{msg}</text></svg>'

# ============ SVG 共用：畫折線圖 ============
def _line_svg(labels, vals, color_line, fmt_val, empty_msg="無資料"):
    H = 110  # SVG 總高（viewBox 高度）
    color_fill = hex_rgba(color_line, "0.08")
    n = len(vals)
    if n == 0:
        return _empty_svg(400, H, empty_msg)
    width = max(340, n * 48 + 52)
    L, R, T, B = 36, 10, 14, 24
    cw = width - L - R
    ch = H - T - B
    lo = min(vals); hi = max(vals)
    pad = (hi - lo) * 0.12 if hi != lo else max(hi * 0.05, 1)
    lo -= pad; hi += pad
    def px(i): return L + (i / (n - 1) if n > 1 else 0.5) * cw
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
    filtered = [r for r in records if r.get("km")]
    labels = [r["date"][5:]           for r in filtered]
    vals   = [r["litres"]/r["km"]*100 for r in filtered]
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
    {stat_cell("單價", f"{r['ppl'] * 100:.1f}", "¢/L", C_BLUE)}
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

# ============ Utility 多線走勢圖（4 項並列）============
def _util_multi_svg(months, series, colors):
    W, H = 372, 182
    L, R, T, B = 34, 8, 14, 40
    cw, ch = W - L - R, H - T - B
    allv = [v for s in series.values() for v in s if v is not None]
    if not allv:
        return _empty_svg(W, H)
    lo, hi = 0.0, max(allv) * 1.12
    n = len(months)
    def px(i): return L + (i / (n - 1) if n > 1 else 0.5) * cw
    def py(v): return T + ch * (1 - (v - lo) / (hi - lo))
    parts = []
    for k in range(5):
        v = hi * k / 4; y = py(v)
        parts.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="rgba(0,0,0,0.06)" stroke-width="0.7"/>')
        parts.append(f'<text x="{L-3}" y="{y+3:.1f}" fill="{C_TEXT3}" font-size="7" text-anchor="end">${v:.0f}</text>')
    for i in range(0, n, 3):
        parts.append(f'<text x="{px(i):.1f}" y="{H-26:.1f}" fill="{C_TEXT3}" font-size="6.8" text-anchor="middle">{months[i][2:]}</text>')
    for name, vals in series.items():
        col = colors[name]
        pts = [(px(i), py(v)) for i, v in enumerate(vals) if v is not None]
        if len(pts) > 1:
            poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            parts.append(f'<polyline points="{poly}" fill="none" stroke="{col}" stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round"/>')
        for x, y in pts:
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" fill="{col}"/>')
    seg = cw / len(colors)
    for idx, (name, col) in enumerate(colors.items()):
        x = L + idx * seg
        parts.append(f'<rect x="{x:.1f}" y="{H-12:.1f}" width="9" height="3.2" rx="1.2" fill="{col}"/>')
        parts.append(f'<text x="{x+12:.1f}" y="{H-9:.1f}" fill="{C_TEXT2}" font-size="7.5">{name}</text>')
    return f'<svg width="100%" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'

# ============ Utility 合計面積圖（單線 + 數值標記）============
def _util_area_svg(months, vals, color):
    W, H = 372, 150
    L, R, T, B = 34, 8, 18, 26
    cw, ch = W - L - R, H - T - B
    if not vals:
        return _empty_svg(W, H)
    lo, hi = min(vals) * 0.92, max(vals) * 1.08
    n = len(vals)
    fill = hex_rgba(color, "0.10")
    def px(i): return L + (i / (n - 1) if n > 1 else 0.5) * cw
    def py(v): return T + ch * (1 - (v - lo) / (hi - lo))
    parts = []
    for k in range(4):
        v = lo + (hi - lo) * k / 3; y = py(v)
        parts.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="rgba(0,0,0,0.06)" stroke-width="0.7"/>')
        parts.append(f'<text x="{L-3}" y="{y+3:.1f}" fill="{C_TEXT3}" font-size="7" text-anchor="end">${v:.0f}</text>')
    poly = " ".join(f"{px(i):.1f},{py(vals[i]):.1f}" for i in range(n))
    parts.append(f'<polygon points="{px(0):.1f},{T+ch} {poly} {px(n-1):.1f},{T+ch}" fill="{fill}"/>')
    parts.append(f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>')
    for i in range(n):
        x, y = px(i), py(vals[i])
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" fill="{color}"/>')
        if i % 3 == 0 or i == n - 1:
            parts.append(f'<text x="{x:.1f}" y="{y-5:.1f}" fill="{C_TEXT1}" font-size="6.8" text-anchor="middle" font-weight="500">{vals[i]:.0f}</text>')
            parts.append(f'<text x="{x:.1f}" y="{H-3}" fill="{C_TEXT3}" font-size="6.8" text-anchor="middle">{months[i][2:]}</text>')
    return f'<svg width="100%" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'

# ============ Utility 可展開明細卡（點擊看每月）============
def make_util_detail(u):
    months = _UTIL["months"]
    series = _UTIL["series"][u]
    est = set(_UTIL.get("estimated", {}).get(u, []))
    col = C_UTIL[u]
    pairs = [(m, v) for m, v in zip(months, series) if v is not None]
    total = sum(v for _, v in pairs)
    first, last = (pairs[0][0], pairs[-1][0]) if pairs else ("—", "—")
    rows = []
    for m, v in pairs:
        badge = (f'<span style="font-size:9px;color:{C_TEXT3};border:1px solid {C_BORDER};'
                 f'border-radius:4px;padding:1px 5px;margin-left:8px">估算</span>') if m in est else ''
        note = (f' <span style="font-size:10px;color:{C_TEXT3}">補助抵扣</span>'
                if (u == "電力" and v == 0) else '')
        rows.append(
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:9px 2px;border-top:1px solid {C_BORDER}">'
            f'<span style="font-size:13px;color:{C_TEXT2}">{m}{badge}</span>'
            f'<span style="font-size:13px;color:{C_TEXT1};font-weight:500">${v:.2f}{note}</span></div>')
    rows_html = "".join(rows)
    return f"""<details style="background:{C_SURFACE};border:1px solid {C_BORDER};border-radius:12px;margin-bottom:10px;overflow:hidden">
  <summary style="cursor:pointer;padding:18px 16px;display:flex;justify-content:space-between;align-items:center">
    <div>
      <div style="font-size:10px;color:{C_TEXT3};letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px">{u}</div>
      <div style="font-size:26px;font-weight:600;color:{col};letter-spacing:-0.5px;line-height:1">${total:,.0f}</div>
      <div style="font-size:11px;color:{C_TEXT3};margin-top:6px">期間累計 · {first}–{last} · 點擊看每月</div>
    </div>
    <span class="util-caret" style="font-size:14px;color:{C_TEXT3};margin-left:12px">▾</span>
  </summary>
  <div style="padding:2px 16px 14px">{rows_html}</div>
</details>"""

# ============ Utility 分析區塊 ============
def make_utility_section():
    if not _UTIL:
        return empty_state("水電瓦斯")
    months = _UTIL["months"]
    series = _UTIL["series"]
    order = list(C_UTIL)

    grand = sum(v for u in order for v in series[u] if v is not None)

    combo_m, combo_v = [], []
    for i, m in enumerate(months):
        vs = [series[u][i] for u in order]
        if all(v is not None for v in vs):
            combo_m.append(m); combo_v.append(round(sum(vs), 2))
    if combo_v:
        avg = sum(combo_v) / len(combo_v)
        hi_v, lo_v = max(combo_v), min(combo_v)
        hi_m = combo_m[combo_v.index(hi_v)]
        lo_m = combo_m[combo_v.index(lo_v)]
    else:
        avg = hi_v = lo_v = 0
        hi_m = lo_m = "—"

    # 最新月份各項費用（含與上月比較）
    latest = months[-1]
    def _mom(u):
        cur, pr = series[u][-1], series[u][-2]
        if cur is None:
            return latest
        if pr is None:
            return f"{latest} · CAD"
        d = cur - pr
        if abs(d) < 0.005:
            return f"{latest} · 持平"
        arrow = "▲" if d > 0 else "▼"
        return f"{latest} · {arrow} ${abs(d):.0f} vs 上月"
    latest_total = sum(v for u in order for v in (series[u][-1],) if v is not None)

    stats = stat_grid(
        stat_card("期間總支出", f"${grand:,.0f}", f"CAD · {months[0]}–{months[-1]}", C_ORANGE),
        stat_card("月均合計", f"${avg:.0f}", f"CAD · 全覆蓋 {len(combo_v)} 月", C_BLUE),
        stat_card("最高月", f"${hi_v:.0f}", hi_m, C_PURPLE),
        stat_card("最低月", f"${lo_v:.0f}", lo_m, C_GREEN),
    )
    latest_cards = stat_grid(*[
        stat_card(u, f"${(series[u][-1] or 0):.2f}", _mom(u), C_UTIL[u]) for u in order
    ])
    per_util = "".join(make_util_detail(u) for u in order)
    note = _UTIL.get("note", "")
    note_html = (f'<div style="font-size:11px;color:{C_TEXT3};line-height:1.6;'
                 f'background:{C_SURFACE};border:1px solid {C_BORDER};border-radius:12px;'
                 f'padding:14px 16px;margin-bottom:8px">說明 · {note}</div>') if note else ""

    return f"""
{stats}
{section_label(f"最新月份 · {latest}　合計 ${latest_total:.0f}")}
{latest_cards}
{chart_block("每月各項費用走勢  CAD", _util_multi_svg(months, {u: series[u] for u in order}, C_UTIL))}
{chart_block("四項合計月總開支  CAD", _util_area_svg(combo_m, combo_v, C_ORANGE))}
{section_label("各項期間累計（點擊展開每月明細）")}
{per_util}
{note_html}"""

# ============ 月統計 ============
def make_monthly_section():
    from collections import defaultdict

    monthly = defaultdict(lambda: {"gas":0.0,"grocery":0.0,"dining":0.0,"other":0.0,"utility":0.0})

    for r in DATA["sienna"] + DATA["c300"]:
        monthly[r["date"][:7]]["gas"] += r["total"]
    for r in GROCERY:
        monthly[r["date"][:7]]["grocery"] += r["total"]
    for r in DINING:
        monthly[r["date"][:7]]["dining"] += r["total"]
    for r in OTHER:
        monthly[r["date"][:7]]["other"] += r["total"]
    if _UTIL:
        for i, m in enumerate(_UTIL["months"]):
            ym = m.replace(".", "-")
            for u in C_UTIL:
                v = _UTIL["series"][u][i]
                if v is not None:
                    monthly[ym]["utility"] += v

    if not monthly:
        return empty_state("月統計")

    sorted_ym = sorted(monthly.keys(), reverse=True)
    totals = {ym: sum(monthly[ym].values()) for ym in sorted_ym}
    grand  = sum(totals.values())
    avg    = grand / len(sorted_ym) if sorted_ym else 0
    max_m  = max(sorted_ym, key=lambda m: totals[m])
    min_m  = min(sorted_ym, key=lambda m: totals[m])

    asc = sorted(monthly.keys())
    chart_svg = _line_svg(
        [m[5:] for m in asc],
        [totals[m] for m in asc],
        C_ORANGE, lambda v: f"${v:.0f}"
    )

    CAT = [
        ("gas",     "加油",     C_BLUE),
        ("grocery", "超市",     C_GREEN),
        ("dining",  "餐廳",     C_ORANGE),
        ("other",   "其他",     C_PURPLE),
        ("utility", "水電瓦斯", C_TEXT2),
    ]

    cards = []
    for ym in sorted_ym:
        cats  = monthly[ym]
        total = totals[ym]
        y, mo = ym.split("-")
        label = f"{y}年 {int(mo)}月"
        rows  = ""
        for key, name, col in CAT:
            v = cats[key]
            if v < 0.005: continue
            pct = v / total * 100
            rows += f"""<div style="margin-bottom:9px">
  <div style="display:flex;justify-content:space-between;margin-bottom:4px">
    <span style="font-size:12px;color:{C_TEXT2}">{name}</span>
    <span style="font-size:12px;font-weight:500;color:{col}">${v:.0f} <span style="font-weight:400;color:{C_TEXT3}">{pct:.0f}%</span></span>
  </div>
  <div style="height:4px;background:{C_BG};border-radius:2px;overflow:hidden"><div style="height:4px;width:{pct:.1f}%;background:{col};border-radius:2px"></div></div>
</div>"""
        cards.append(f"""<div style="background:{C_SURFACE};border:1px solid {C_BORDER};border-radius:12px;padding:18px;margin-bottom:14px">
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:14px">
    <div style="font-size:16px;font-weight:600;color:{C_TEXT1}">{label}</div>
    <div style="font-size:22px;font-weight:700;color:{C_ORANGE};letter-spacing:-0.5px">${total:.0f}</div>
  </div>
  {rows}
</div>""")

    stats = stat_grid(
        stat_card("期間總支出", f"${grand:,.0f}", f"CAD · {len(sorted_ym)} 個月", C_ORANGE),
        stat_card("月均支出",  f"${avg:,.0f}",   "CAD · 月平均", C_BLUE),
        stat_card("最高月",    f"${totals[max_m]:,.0f}", max_m, C_PURPLE),
        stat_card("最低月",    f"${totals[min_m]:,.0f}", min_m, C_GREEN),
    )

    return f"""{stats}
{chart_block("月度總支出  CAD", chart_svg)}
{section_label("每月明細")}
{"".join(cards)}"""

# ============ 完整 HTML ============
def build_html():
    now = datetime.now(ZoneInfo("America/Toronto")).strftime("%Y-%m-%d %H:%M")
    sienna_html   = make_car_section("sienna", "Sienna")
    c300_html     = make_car_section("c300", "C300")
    grocery_html  = make_list_section(GROCERY, "超市購物", make_itemized_card, "次", "購物記錄")
    dining_html   = make_list_section(DINING,  "餐廳外食", make_itemized_card, "次", "消費記錄")
    other_html    = make_list_section(OTHER,   "其他支出", make_other_card,   "筆", "支出記錄")
    utility_html  = make_utility_section()
    monthly_html  = make_monthly_section()

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
/* Utility 展開卡：移除預設三角、加自繪箭頭旋轉 */
summary {{ list-style:none; }}
summary::-webkit-details-marker {{ display:none; }}
.util-caret {{ display:inline-block; transition:transform 0.2s ease; }}
details[open] .util-caret {{ transform:rotate(180deg); }}
/* 分頁切換邏輯 */
.sec {{ display:none; }}
#gas {{ display:block; }}
body:has(#gas-c300:target) #gas,
body:has(#grocery:target)  #gas,
body:has(#dining:target)   #gas,
body:has(#other:target)    #gas,
body:has(#utility:target)  #gas,
body:has(#monthly:target)  #gas {{ display:none; }}
:target {{ display:block !important; }}
/* 導航底線 */
.nav a[href="#gas"] {{ color:{C_TEXT1}; border-bottom-color:{C_BLUE}; }}
body:has(#grocery:target) .nav a[href="#gas"],
body:has(#dining:target)  .nav a[href="#gas"],
body:has(#other:target)   .nav a[href="#gas"],
body:has(#utility:target) .nav a[href="#gas"] {{ color:{C_TEXT3}; border-bottom-color:transparent; }}
body:has(#grocery:target) .nav a[href="#grocery"],
body:has(#dining:target)  .nav a[href="#dining"],
body:has(#other:target)   .nav a[href="#other"],
body:has(#utility:target) .nav a[href="#utility"],
body:has(#monthly:target) .nav a[href="#monthly"] {{ color:{C_TEXT1}; border-bottom-color:{C_BLUE}; }}
body:has(#monthly:target) .nav a[href="#gas"] {{ color:{C_TEXT3}; border-bottom-color:transparent; }}
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
  <a href="#utility">水電瓦斯</a>
  <a href="#monthly">月統計</a>
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

<div id="utility" class="sec">
  {utility_html}
</div>

<div id="monthly" class="sec">
  {monthly_html}
</div>

</body>
</html>"""

# ============ 輸出 ============
html = build_html()
out_path = os.path.join(_HERE, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"✅ HTML 已寫入：{out_path}")
print(f"   大小：{len(html):,} bytes")
print(f"   Sienna：{len(DATA['sienna'])} 筆  C300：{len(DATA['c300'])} 筆")
