#!/usr/bin/env python3
"""Generate one original wuxia study chapter per Korea calendar day."""
import json, os, re, sys, datetime, urllib.request, urllib.error
from pathlib import Path
from zoneinfo import ZoneInfo
from draw_panel import draw_panel

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "episodes.json"
DATA = json.loads(DB.read_text(encoding="utf-8"))
TODAY = datetime.datetime.now(ZoneInfo("Asia/Seoul")).date().isoformat()
entries = DATA["episodes"]
if any(e.get("release_at") == TODAY for e in entries):
    print("Today's chapter already exists:", TODAY)
    sys.exit(0)
previous = entries[-1]
idx = int(previous["id"]) + 1
if idx > 999:
    raise RuntimeError("Reached designed ID limit")
history = [{"id": x["id"], "title": x["title"], "teaser": x.get("teaser",""),
            "panels": [p["zh"] for p in x.get("panels",[])]}
           for x in entries[-5:]]

STORY_BIBLE = """
Original long-running wuxia mystery series 江湖风云录 / 강호풍운록.
Set in a grounded, atmospheric late-imperial Chinese jianghu.
Protagonist 青风 (Qingfeng): young wandering swordsman, alert, skeptical, honors mentor's word.
顾伯 (Gu Bo): elderly innkeeper, former 青云门 courier, knows much but hides a personal betrayal.
洛雪 (Luo Xue): astute travelling doctor, dangerous knowledge of antidotes, independent agenda.
Opposing faction 黑风堂 controls shadow trade routes and forged martial manuals.
Central prop: jade pendant carved like a cloud, tied to mentor's disappearance.
Act 1 (episodes 1-20): hidden witnesses and the false charges that destroyed 青云门.
Act 2 (21-45): a lost sword manual whose 'secret' may be a cipher, not a technique.
Act 3 (46-75): regional journeys, shifting alliances, competing loyalties.
Act 4 (76-105): reveal of the mentor's true actions and Qingfeng's difficult choice.
Use geography, sect politics, economy of inns, physical technique and inner force believably.
Each page advances one causal clue and character goal, balances restraint with action,
includes a memorable twist or unanswered question, avoids episodic reset and empty clichés.
The first chapter has Qingfeng entering an inn in a storm. Gu Bo sees the pendant and warns:
"快收起来！这里有他们的人。" Continue directly from this situation.
"""
SYSTEM = """You are an expert original wuxia serial novelist, Chinese language teacher
and bilingual editor. Write intelligent, character-driven tension, grounded martial arts
and subtle wit. Output ONLY strict JSON object, no markdown.
Must NOT use copyrighted characters or plots from existing works.
Natural concise Chinese dialogue; every panel has 1-3 short utterances, 5-7 panels.
Pinyin with accurate tone diacritics, paired faithful Korean translation and short Korean grammar note.
A story-rich teaser in Korean, Korean preview of the plot without the ending.
Words array MUST contain all teachable words, in dialogue order, INCLUDING repetitions,
with zh, py, ko, usage; 14-35 entries.
Dialect examples 1-3 items: grounded standard Mandarin vs clearly labeled regional colloquial phrasing.
Never present Cantonese/Shanghai speech as standard Mandarin pinyin. Skip uncertain dialect.
No images inside text. The 5-7 scenes will have original monochrome illustrations drawn separately.
Provide keys title (Chinese), teaser (Korean), prep (Korean), grammar (Korean),
panels array of {zh,py,ko,note}, words array of {zh,py,ko,usage},
dialects array of {region,zh,py,ko,note}.
"""

def request_story():
    token = os.environ.get("GH_MODELS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not configured")
    reqbody = {
       "model": "openai/gpt-4.1-mini",
       "messages": [
           {"role": "system", "content": SYSTEM},
           {"role": "user", "content": "Story bible:\n"+STORY_BIBLE+
              "\nPublished recent continuity:\n"+json.dumps(history,ensure_ascii=False)+
              f"\nWrite precisely chapter {idx:03d}. Date {TODAY}. Keep all characters and events consistent. "+
              "Invent a new, suspenseful development with a closing cliffhanger. "+
              "Write richly distinct speech, real motive and consequences. Ensure the first panel connects to the previous last line."}
       ],
       "temperature": .85,
       "max_tokens": 5100,
       "response_format": {"type":"json_object"}
    }
    req = urllib.request.Request(
        "https://models.github.ai/inference/chat/completions",
        data=json.dumps(reqbody).encode(),
        headers={"Authorization":"Bearer "+token,"Content-Type":"application/json",
                 "Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"},
        method="POST")
    with urllib.request.urlopen(req,timeout=110) as res:
        raw=json.load(res)
    content=raw["choices"][0]["message"]["content"]
    return json.loads(content)

def fallback():
    # Carefully authored original bridge chapters; only used when inference is unavailable.
    if idx != 2:
        return None
    ps=[
      ("别出声！窗外有人在听。","Bié chūshēng! Chuāngwài yǒu rén zài tīng.","别作声：쉿! 창밖에 누군가 엿듣고 있소.","别 + 동사: ~하지 말라는 금지형 명령"),
      ("我从没见过这种刀痕。","Wǒ cóng méi jiànguo zhè zhǒng dāohén.","이런 칼자국은 한 번도 본 적이 없소.","从没 + 동사 + 过: 지금까지 한 번도 하지 않았다"),
      ("这玉佩背面，刻着一个名字。","Zhè yùpèi bèimiàn, kèzhe yí ge míngzi.","이 옥패 뒷면에 이름 하나가 새겨져 있소.","着는 동작 뒤에 붙어 상태의 지속을 나타냄"),
      ("青云门的人，不是全死了吗？","Qīngyúnmén de rén, bú shì quán sǐ le ma?","청운문 사람들은 전부 죽은 게 아니었소?","不是…吗는 화자의 놀람 또는 확인을 나타냄"),
      ("掌柜的，你为什么怕我师父？","Zhǎngguì de, nǐ wèishénme pà wǒ shīfu?","주인장, 어째서 내 사부를 두려워하시오?","为什么 + 동사: 왜 ~하느냐는 질문")
    ]
    ws=[
      ("别","bié","~하지 마세요"),("出声","chūshēng","소리를 내다"),
      ("窗外","chuāngwài","창밖"),("有人","yǒu rén","누군가 있다"),
      ("听","tīng","듣다"),("我","wǒ","나"),("从没","cóng méi","한 번도 ~없다"),
      ("见过","jiànguo","본 적이 있다"),("这种","zhè zhǒng","이런 종류"),
      ("刀痕","dāohén","칼자국"),("这","zhè","이것"),("玉佩","yùpèi","옥패"),
      ("背面","bèimiàn","뒷면"),("刻着","kèzhe","새겨져 있다"),
      ("一个","yí ge","한 개"),("名字","míngzi","이름"),
      ("青云门","Qīngyúnmén","청운문"),("人","rén","사람"),
      ("不是","bú shì","~이 아닌가"),("全","quán","전부"),
      ("死","sǐ","죽다"),("了","le","상태 변화·완료 조사"),
      ("掌柜的","zhǎngguì de","주인장"),("你","nǐ","너"),
      ("为什么","wèishénme","왜"),("怕","pà","두려워하다"),
      ("我","wǒ","나(반복)"),("师父","shīfu","사부")
    ]
    return {"title":"窗纸后的刀光","teaser":"종이창 뒤에서 번쩍이는 칼날. 죽은 줄 알았던 청운문의 이름이 옥패에 새겨져 있다.","prep":"객잔 주인이 창문을 잠그자 청풍은 기이한 칼자국을 발견한다. 옥패의 뒷면에는 누구도 입에 올리지 못했던 이름이 있다.","grammar":"别 + 동사(금지형), 从没…过(경험 부정), 为什么(이유 질문).",
            "panels":[{"zh":p[0],"py":p[1],"ko":p[2],"note":p[3]} for p in ps],
            "words":[{"zh":w[0],"py":w[1],"ko":w[2]} for w in ws],
            "dialects":[{"region":"베이징 구어","zh":"你打哪儿知道的？","py":"Nǐ dǎ nǎr zhīdao de?","ko":"그걸 어디서 알았어?","note":"‘哪儿’의 儿化가 나타나는 자연스러운 구어 표현"}]}

try:
    record=request_story()
    source="github-models"
except (Exception,) as err:
    print("AI service unavailable:",repr(err))
    record=fallback()
    if record is None:
        raise RuntimeError("AI unavailable and no vetted fallback chapter; refusing to publish filler") from err
    source="vetted-fallback"

if not isinstance(record,dict):
    raise ValueError("Chapter response is not an object")
required=("title","teaser","prep","grammar","panels","words","dialects")
if any(k not in record for k in required):
    raise ValueError("Missing required study fields")
panels=record["panels"]
if not (5<=len(panels)<=8):
    raise ValueError("Expected 5-8 original comic panels")
for p in panels:
    if any(not isinstance(p.get(k),str) or not p[k].strip() for k in ("zh","py","ko","note")):
        raise ValueError("Panel missing Chinese/pinyin/Korean/grammar notes")
    if not re.search(r"[\u3400-\u9fff]",p["zh"]):
        raise ValueError("Invalid dialogue: no Chinese characters")
words=record["words"]
if not isinstance(words,list) or len(words)<8:
    raise ValueError("Need detailed vocabulary for complete study")
for w in words:
    if any(not w.get(k) for k in ("zh","py","ko")):
        raise ValueError("Word lacks Chinese/pinyin/translation")
record["id"]=f"{idx:03d}"
record["release_at"]=TODAY
record["source"]=source
for i,p in enumerate(panels):
    imgname=f"assets/chapter-{idx:03d}-{i+1}.jpg"
    draw_panel(ROOT/imgname,idx,i,p["zh"],record["title"])
    p["image"]=imgname
entries.append(record)
DATA["updated"]=TODAY
DB.write_text(json.dumps(DATA,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"Published draft chapter {idx:03d} for {TODAY}: {len(panels)} images, {len(words)} word occurrences via {source}")
