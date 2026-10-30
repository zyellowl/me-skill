#!/usr/bin/env python3
"""Collect recent me-cli records and recurring keywords as material for me-skill reflection."""
import argparse, collections, datetime, os, re, sqlite3, pathlib
p = argparse.ArgumentParser(); p.add_argument("--days", type=int, default=30); p.add_argument("--top", type=int, default=15)
a = p.parse_args()
home = os.environ.get("ME_HOME")
if not home: raise SystemExit("请设置 ME_HOME 指向你的私有个人数据目录")
db = pathlib.Path(home) / "system" / "me.sqlite"
c = sqlite3.connect(f"{db.resolve().as_uri()}?mode=ro", uri=True)
since = (datetime.datetime.now().astimezone() - datetime.timedelta(days=a.days)).isoformat()
rows = c.execute("select id,kind,content,source,said_at,event_at from items where active=1 order by coalesce(event_at,said_at)").fetchall()
c.close()
recent = [r for r in rows if (r[5] or r[4] or "") >= since[:10]]
print(f"## 记录素材（有效记录 {len(rows)} 条，近 {a.days} 天 {len(recent)} 条）")
print("按事件日期优先、缺失时参考陈述日期筛选；两个日期都缺失的记录不计入近期素材。")
print("以下为原始记录，尚未核实；来源类别须区分本人陈述/他人转述/AI 假设，不能凭记录类型或关键词推断。")
for r in recent:
    print(f"- [{r[0]}] 记录类型：{r[1]} | 原文：{r[2]} | 来源：{r[3] or '未知/待核验'} | 陈述日期：{r[4] or '未知'} | 事件日期：{r[5] or '未知'}")
words = collections.Counter(w for r in recent for w in re.findall(r"[\u4e00-\u9fff]{2,4}|[A-Za-z0-9+]{2,}", r[2]))
print("\n## 高频词（仅供找证据，不能证明心理模式或自动打三层标签）")
print("、".join(f"{w}×{n}" for w, n in words.most_common(a.top) if n > 1) or "无")
