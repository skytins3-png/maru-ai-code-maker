#!/usr/bin/env python3
"""Post each chapter as a self-contained, publicly viewable GitHub Issue.
This works even when GitHub Pages has not been enabled.
"""
import json, os, sys, urllib.request, urllib.parse, urllib.error
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

root=Path(__file__).resolve().parent.parent
data=json.loads((root/"episodes.json").read_text(encoding="utf-8"))["episodes"]
today=datetime.now(ZoneInfo("Asia/Seoul")).date().isoformat()
chapter=next((e for e in reversed(data) if e["release_at"]==today),None)
if not chapter:
    print("No chapter scheduled for today",today)
    sys.exit(0)
repo=os.environ.get("GITHUB_REPOSITORY","skytins3-png/maru-ai-code-maker")
token=os.environ.get("GITHUB_TOKEN")
if not token:
    raise RuntimeError("GITHUB_TOKEN required")
base="https://api.github.com/repos/"+repo+"/issues"
def api(url,method="GET",body=None):
    request=urllib.request.Request(url,data=json.dumps(body).encode("utf-8") if body else None,
        headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
                 "X-GitHub-Api-Version":"2022-11-28","Content-Type":"application/json"},
        method=method)
    with urllib.request.urlopen(request,timeout=45) as response:
        return json.load(response)
prev=api(base+"?state=all&per_page=100")
marker="제"+chapter["id"]+"화"
if any(marker in x.get("title","") for x in prev if "pull_request" not in x):
    print("Already published an issue for", marker)
    sys.exit(0)
title="《강호풍운록》 "+marker+" | "+chapter["title"]
src="https://raw.githubusercontent.com/"+repo+"/maru-wuxia-serial/"
body=[f"# 江湖风云录 · 第{chapter['id']}回",f"> {chapter['release_at']} · 중국어 대사만 읽는 무협 만화"]
for i,p in enumerate(chapter["panels"],1):
    body += [f"## {i}컷",f"![제{chapter['id']}화 {i}컷]({src}{p['image']})",
             "> **"+p["zh"]+"**"]
body += ["","<details><summary>📚 예습 · 문장 해석 · 단어 · 사투리 · 복습 펼치기</summary>",
         "### 예습",chapter.get("prep",""),"### 오늘의 문장"]
for i,p in enumerate(chapter["panels"],1):
    body += [f"{i}. **{p['zh']}**  \n   {p['py']}  \n   {p['ko']}  \n   💡 {p['note']}"]
body += ["### 단어(중복도 그대로 학습)"]
for i,w in enumerate(chapter["words"],1):
    body += [f"{i}. **{w['zh']}** · {w['py']} — {w['ko']} "+(w.get("usage") or "")]
body += ["### 지역별 표현(보통화와 비교)"]
for d in chapter.get("dialects",[]):
    body += [f"- **{d['region']}** · {d['zh']}  \n  {d.get('py','')} · {d['ko']} · {d.get('note','')}"]
body += ["### 복습","대사를 소리 내어 처음부터 끝까지 5회 읽고 1·3·7일 뒤 다시 연습하세요.","</details>",
         "\n[전체 연재 원본과 학습 파일](https://github.com/"+repo+"/tree/maru-wuxia-serial)"]
made=api(base,"POST",{"title":title,"body":"\n\n".join(body)})
print("Published online:",made["html_url"])
