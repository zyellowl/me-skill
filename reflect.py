#!/usr/bin/env python3
"""Collect recent me-cli records and recurring keywords as material for me-skill reflection."""
import argparse, collections, datetime, os, re, sqlite3, pathlib
p = argparse.ArgumentParser(); p.add_argument("--days", type=int, default=30); p.add_argument("--top", type=int, default=15)
a = p.parse_args()
home = os.environ.get("ME_HOME")
if not home: raise SystemExit("请设置 ME_HOME 指向你的私有个人数据目录")
db = pathlib.Path(home) / "system" / "me.sqlite"
c = sqlite3.connect(db)
since = (datetime.datetime.now().astimezone() - datetime.timedelta(days=a.days)).isoformat()
rows = c.execute("select id,kind,content,source,coalesce(event_at,said_at) from items where active=1 order by 5").fetchall()
recent = [r for r in rows if r[4] >= since[:10]]
print(f"## 记录（全部 {len(rows)} 条，近 {a.days} 天 {len(recent)} 条）")
for r in rows: print(f"- [{r[0]}] {r[4][:10]} {r[1]} | {r[2]} | {r[3]}")
words = collections.Counter(w for r in rows for w in re.findall(r"[\u4e00-\u9fff]{2,4}|[A-Za-z0-9+]{2,}", r[2]))
print("\n## 高频词（找重复模式的线索）")
print("、".join(f"{w}×{n}" for w, n in words.most_common(a.top) if n > 1) or "无")
