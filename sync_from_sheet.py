#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 Google Sheet（主資料庫）匯出的 CSV 還原成 data.json。

資料流：
  Google Sheet  --(Cowork 用連接器 download_file_content 匯出 CSV)-->  _db_export.csv
  _db_export.csv  --(本腳本)-->  data.json
  data.json  --(generate_static.py)-->  index.html  --> GitHub Pages

主資料庫（Google Sheet）：
  標題：包山包海包生活 開支資料庫
  檔案ID：11s4k59NMtALtaaZbLdAJkZMBlcUX-91MFJOzZGhyl2U

CSV 欄位（單一扁平資料表，用「分類」欄與「收據ID」分群）：
  收據ID, 分類, 日期, 時間, 商家, 地址, 品項, 單價, HST, 總額, 付款,
  公升, 每公升, 賺點, 點數餘額, 里程km, 備註

用法：
  python3 sync_from_sheet.py [csv路徑]      # 預設讀 _db_export.csv，輸出 data.json
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def num(v, kind=float):
    """空字串→None；否則轉成數字。"""
    if v is None:
        return None
    v = str(v).strip()
    if v == "":
        return None
    try:
        return kind(float(v))
    except ValueError:
        return v


def build(csv_path):
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    grocery, dining, other = {}, {}, {}
    sienna, c300 = [], []

    for r in rows:
        rid = (r.get("收據ID") or "").strip()
        cat = (r.get("分類") or "").strip()
        if not rid:
            continue

        if cat in ("超市", "餐廳"):
            bucket = grocery if cat == "超市" else dining
            rec = bucket.get(rid)
            if rec is None:
                rec = {
                    "date": r["日期"].strip(),
                    "time": r["時間"].strip(),
                    "store": r["商家"].strip(),
                    "addr": r["地址"].strip(),
                    "items": [],
                    "hst": num(r["HST"]) or 0.0,
                    "total": num(r["總額"]) or 0.0,
                    "payment": r["付款"].strip(),
                }
                bucket[rid] = rec
            name = (r.get("品項") or "").strip()
            if name:
                rec["items"].append({"name": name, "price": num(r["單價"]) or 0.0})

        elif cat == "其他":
            other[rid] = {
                "date": r["日期"].strip(),
                "time": r["時間"].strip(),
                "category": (r.get("品項") or "").strip(),
                "desc": r["商家"].strip(),
                "note": (r.get("備註") or "").strip(),
                "total": num(r["總額"]) or 0.0,
                "payment": r["付款"].strip(),
            }

        elif cat in ("油費-Sienna", "油費-C300"):
            rec = {
                "date": r["日期"].strip(),
                "time": r["時間"].strip(),
                "station": r["商家"].strip(),
                "addr": r["地址"].strip(),
                "litres": num(r["公升"]),
                "ppl": num(r["每公升"]),
                "total": num(r["總額"]),
                "ptsEarn": num(r["賺點"], int),
                "ptsBal": num(r["點數餘額"], int),
            }
            km = num(r["里程km"])
            if km is not None:
                rec["km"] = km
            (sienna if cat.endswith("Sienna") else c300).append(rec)

    data = {
        "grocery": list(grocery.values()),
        "dining": list(dining.values()),
        "other": list(other.values()),
        "fuel": {"sienna": sienna, "c300": c300},
    }
    return data


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "_db_export.csv")
    data = build(csv_path)
    out = os.path.join(HERE, "data.json")
    json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("已從 %s 還原 data.json：" % os.path.basename(csv_path))
    print("  超市 %d 筆 / 餐廳 %d 筆 / 其他 %d 筆 / Sienna %d 筆 / C300 %d 筆"
          % (len(data["grocery"]), len(data["dining"]), len(data["other"]),
             len(data["fuel"]["sienna"]), len(data["fuel"]["c300"])))


if __name__ == "__main__":
    main()
