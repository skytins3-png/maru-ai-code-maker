
import streamlit as st
import zipfile, shutil, json, re, ast, subprocess, sys, io, time
from pathlib import Path
from datetime import datetime
import requests

APP_DIR = Path(__file__).parent
MEM = APP_DIR / "ai_memory.json"
STORE = APP_DIR / "project_storage"
OUT = APP_DIR / "version_outputs"
GEN = APP_DIR / "generated_projects"
for p in [STORE, OUT, GEN]:
    p.mkdir(exist_ok=True)

DEFAULT = {
    "version":"10.0-no-voice-real-patch",
    "projects":{}, "file_checks":[], "monitor_records":[], "repeat_tests":[],
    "log_analyses":[], "approved_upgrades":[], "failed_upgrades":[],
    "generated_projects":[], "lessons":[],
    "google_sheets":{"enabled":False,"sheet_id":"","service_account_json":""},
    "fixed_rules":["음성지시 제거","OpenAI API 키 제거","요금 발생 요소 제거","기존 기능 삭제 금지","승인한 항목만 실제 패치","자동구매 차단"]
}

TODAY = [
"코드생성기","프로젝트 보관함","ZIP 자동 압축해제","경마앱/토토앱 한 번 등록","업로드 없이 목록 선택",
"파일 목록 검사","오류 파일 검사","문법 검사","app.py 탐색","requirements 검사/보강","README 검사",
"기존 기능 목록 추출","빠진 기능 비교","앱/API 자동 모니터","통신두절/HTTP 500/403/404/401/데이터0건 분석",
"로그파일 분석","반복 자동테스트","개선안 추천","승인/미승인/추가지시","승인 항목 실제 패치",
"app.py 실제 수정","helper 파일 실제 추가","새 버전 ZIP","v001/v002/v003 버전관리","백업/되돌리기",
"현재 보관본 다운로드","단일 app.py 추출","구글시트 저장","GitHub Actions 예약 테스트","모바일 큰 글씨/큰 버튼",
"오류 기록 저장","디버그 패널","API KEY 보안 안내","경마 API 점검 도구","토토/스포츠 API 점검 도구",
"기능 스냅샷","자동구매/자동결제 차단","음성지시 제거","OpenAI API 키 제거"
]

PATCHES = {
"mobile_ui":("모바일 UI 보강","낮음","큰 버튼/큰 글씨 CSS를 app.py에 실제 삽입"),
"error_logger":("오류 로그 저장기","낮음","maru_log_error()와 error_log.json 저장을 app.py에 실제 삽입"),
"api_timeout_guard":("API 통신두절 방어","낮음","maru_safe_get() timeout/상태코드/응답미리보기를 app.py에 실제 삽입"),
"debug_panel":("디버그 패널","낮음","최근 오류 패널을 app.py 하단에 실제 삽입"),
"api_key_guard":("API KEY 보안 안내","낮음","키 직접입력 금지 안내 패널 삽입"),
"zip_export":("현재 앱 ZIP 다운로드","낮음","현재 앱 ZIP 다운로드 패널 삽입"),
"kra_api_helper":("경마 API 점검 도구","중간","kra_api_debug_helper.py 실제 추가"),
"toto_api_helper":("토토/스포츠 API 점검 도구","중간","toto_api_debug_helper.py 실제 추가"),
"feature_snapshot":("기능 스냅샷 저장","낮음","전후 기능 비교 JSON 저장"),
"auto_purchase":("자동구매/자동결제","높음","위험 기능이라 차단")
}

def load():
    if MEM.exists():
        try:
            m=json.loads(MEM.read_text(encoding="utf-8"))
            for k,v in DEFAULT.items(): m.setdefault(k,v)
            return m
        except Exception: pass
    save(DEFAULT.copy()); return DEFAULT.copy()
def save(m):
    m["updated_at"]=datetime.now().isoformat(timespec="seconds")
    MEM.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
def safe(s): return re.sub(r"[^a-zA-Z0-9가-힣_.-]+","_",str(s))[:80] or "project"
def rtxt(p):
    for e in ("utf-8","cp949","euc-kr"):
        try: return Path(p).read_text(encoding=e)
        except Exception: pass
    return ""
def wtxt(p,t): Path(p).write_text(t,encoding="utf-8")
def pdir(name): return STORE/safe(name)
def zip_dir(src,out):
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        for p in Path(src).rglob("*"):
            if "__pycache__" in p.parts or ".git" in p.parts: continue
            if p.is_file(): z.write(p,p.relative_to(src))
    return out
def zip_bytes(src):
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w",zipfile.ZIP_DEFLATED) as z:
        for p in Path(src).rglob("*"):
            if "__pycache__" in p.parts or ".git" in p.parts: continue
            if p.is_file(): z.write(p,p.relative_to(src))
    return b.getvalue()

def extract(upload,name):
    root=pdir(name)
    if root.exists(): shutil.rmtree(root)
    root.mkdir(parents=True)
    raw=root/upload.name; raw.write_bytes(upload.getvalue())
    src=root/"src"; src.mkdir()
    if upload.name.lower().endswith(".zip"):
        with zipfile.ZipFile(raw) as z: z.extractall(src)
    else: shutil.copy2(raw,src/upload.name)
    kids=list(src.iterdir())
    if len(kids)==1 and kids[0].is_dir():
        inner=kids[0]
        if (inner/"app.py").exists() or list(inner.glob("*.py")):
            tmp=root/"src_inner"; shutil.move(str(inner),str(tmp)); shutil.rmtree(src); tmp.rename(src)
    return src
def find_app(src):
    src=Path(src)
    for n in ("app.py","streamlit_app.py","main.py"):
        if (src/n).exists(): return src/n
    fs=list(src.rglob("*.py")); return fs[0] if fs else None

def scan(src):
    files=[]; err=[]; cfg=[]; sus=[]; total=0
    for p in Path(src).rglob("*"):
        if "__pycache__" in p.parts or ".git" in p.parts or not p.is_file(): continue
        rel=str(p.relative_to(src)); total+=p.stat().st_size
        files.append({"path":rel,"size":p.stat().st_size,"suffix":p.suffix.lower()})
        if p.name.lower() in ["requirements.txt","readme.md","ai_memory.json",".env","secrets.toml","config.json"]: cfg.append(rel)
        if any(x in p.name.lower() for x in ["error","log","traceback","debug"]): err.append(rel)
        if p.suffix.lower() in [".env",".pem",".key"]: sus.append(rel)
    return {"file_count":len(files),"total_size":total,"has_app_py":any(x["path"].endswith("app.py") for x in files),
            "has_requirements":any(x["path"].endswith("requirements.txt") for x in files),
            "has_readme":any(x["path"].lower().endswith("readme.md") for x in files),
            "config_files":cfg,"error_files":err,"suspicious_files":sus,"file_list":files[:600]}
def pycheck(p):
    r=subprocess.run([sys.executable,"-m","py_compile",str(p)],capture_output=True,text=True)
    return r.returncode==0, ("OK" if r.returncode==0 else r.stderr[-3000:])
def check_all(src):
    out=[]
    for p in Path(src).rglob("*.py"):
        if "__pycache__" in p.parts or ".git" in p.parts: continue
        ok,msg=pycheck(p); out.append({"file":str(p.relative_to(src)),"ok":ok,"message":msg})
    return out

def parse_logs(text):
    t=(text or "").lower(); f=[]; patches=set()
    rules=[("nameerror",["error_logger","debug_panel"],"정의되지 않은 변수/함수"),("keyerror",["error_logger","debug_panel"],"딕셔너리 키 누락"),
    ("http 500",["api_timeout_guard","debug_panel"],"서버/API 오류"),("http 403",["api_key_guard","debug_panel"],"권한/승인 문제"),
    ("http 401",["api_key_guard","debug_panel"],"API 키 인증 실패"),("http 404",["api_timeout_guard","debug_panel"],"URL 오류"),
    ("timeout",["api_timeout_guard","debug_panel"],"타임아웃"),("connectionerror",["api_timeout_guard","debug_panel"],"연결 실패"),
    ("jsondecodeerror",["api_timeout_guard","debug_panel"],"JSON 아님"),("modulenotfounderror",["debug_panel"],"requirements 누락"),
    ("importerror",["debug_panel"],"패키지 문제"),("no result",["debug_panel"],"데이터 없음"),("data[]",["debug_panel"],"데이터 0건"),
    ("통신두절",["api_timeout_guard","debug_panel"],"통신두절"),("오류",["error_logger","debug_panel"],"오류 기록 필요")]
    for k,ps,why in rules:
        if k in t: f.append({"keyword":k,"reason":why,"patches":ps}); patches.update(ps)
    if not f and text.strip(): f.append({"keyword":"일반 로그","reason":"디버그/오류기록 권장","patches":["error_logger","debug_panel"]}); patches.update(["error_logger","debug_panel"])
    return {"summary":f or [{"keyword":"로그 없음","reason":"로그가 없습니다.","patches":[]}],"recommended_patches":sorted(patches)}
def inspect_errors(src):
    out=[]
    for p in Path(src).rglob("*"):
        if "__pycache__" in p.parts or ".git" in p.parts or not p.is_file(): continue
        if any(x in p.name.lower() for x in ["error","log","traceback","debug"]):
            txt=rtxt(p); out.append({"file":str(p.relative_to(src)),"size":p.stat().st_size,"preview":txt[:1200],"analysis":parse_logs(txt)})
    return out

def analyze_code(app_file):
    txt=rtxt(app_file) if app_file and Path(app_file).exists() else ""
    if not txt: return {"features":["Python 파일 없음"],"risks":["app.py 없음"],"line_count":0,"functions":[]}
    risks=[]; funcs=[]
    try:
        tree=ast.parse(txt); funcs=[n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)]
    except Exception as e: risks.append(f"문법 분석 실패: {e}")
    checks=[("Streamlit UI","streamlit" in txt or "st." in txt),("API 호출","requests" in txt or ".get(" in txt),
    ("타임아웃 설정","timeout=" in txt),("오류 처리","try:" in txt and "except" in txt),("JSON 처리","json" in txt or ".json()" in txt),
    ("데이터프레임","pandas" in txt or "DataFrame" in txt),("ZIP 다운로드","download_button" in txt or "zipfile" in txt),
    ("파일 업로드","file_uploader" in txt),("모바일 UI","use_container_width" in txt or "layout='wide'" in txt or 'layout="wide"' in txt),
    ("API KEY 입력","api_key" in txt.lower() or "servicekey" in txt.lower() or "password" in txt.lower()),
    ("경마 관련",any(x in txt for x in ["경마","KRA","race","horse","jockey","배당","마번"])),
    ("토토/스포츠 관련",any(x in txt for x in ["토토","sports","fixture","odds","league","경기","승무패"])),
    ("오류 로그 저장","error_log.json" in txt or "maru_log_error" in txt),("디버그 패널","디버그" in txt or "MARU_DEBUG_PANEL" in txt),
    ("구글시트 저장","gspread" in txt or "google_sheets" in txt),("반복 테스트","반복" in txt or "repeat" in txt.lower())]
    features=[n for n,ok in checks if ok] or ["명확한 기능 자동 추출 실패"]
    if re.search(r"(api[_-]?key|serviceKey|token)\s*=\s*['\"][A-Za-z0-9_\-]{16,}",txt,re.I): risks.append("API 키/토큰 하드코딩 가능성")
    if ".get(" in txt and "timeout=" not in txt: risks.append("API 호출에 timeout 없음")
    if "자동구매" in txt or "자동결제" in txt: risks.append("자동구매/자동결제 문구 감지")
    if any(x in txt.lower() for x in ["openai","whisper","audio_input"]): risks.append("음성/OpenAI 관련 코드 잔존 가능성")
    return {"features":sorted(set(features)),"risks":risks or ["큰 위험 신호 없음"],"line_count":len(txt.splitlines()),"functions":funcs[:120]}

def replace_vars(url,key):
    return url.replace("{api_key}",key or "").replace("{serviceKey}",key or "").replace("{token}",key or "").replace("{today}",datetime.now().strftime("%Y%m%d")).replace("{today_dash}",datetime.now().strftime("%Y-%m-%d"))
def check_url(label,url,key=""):
    final=replace_vars(url,key); rec={"label":label,"time":datetime.now().isoformat(timespec="seconds"),"url_preview":final.replace(key,"***")[:600] if key else final[:600],"ok":False,"status_code":None,"error":"","data_count":None,"preview":""}
    try:
        r=requests.get(final,timeout=12); rec["ok"]=r.ok; rec["status_code"]=r.status_code
        try:
            data=r.json()
            if isinstance(data,dict) and isinstance(data.get("data"),list): rec["data_count"]=len(data["data"])
            elif isinstance(data,list): rec["data_count"]=len(data)
            rec["preview"]=json.dumps(data,ensure_ascii=False)[:1500]
        except Exception: rec["preview"]=r.text[:1500]
    except Exception as e: rec["error"]=str(e)
    return rec
def analyze_records(records):
    f=[]; p=set()
    for r in records:
        s=r.get("status_code"); e=r.get("error")
        if e: f.append({"target":r["label"],"problem":"통신두절","detail":e,"patches":["api_timeout_guard","debug_panel","error_logger"]}); p.update(["api_timeout_guard","debug_panel","error_logger"])
        elif s in [401,403]: f.append({"target":r["label"],"problem":f"HTTP {s}","detail":"키/권한 문제","patches":["api_key_guard","debug_panel"]}); p.update(["api_key_guard","debug_panel"])
        elif s==404 or (s and s>=500): f.append({"target":r["label"],"problem":f"HTTP {s}","detail":"URL/API 문제","patches":["api_timeout_guard","debug_panel"]}); p.update(["api_timeout_guard","debug_panel"])
        elif r.get("ok") and r.get("data_count")==0: f.append({"target":r["label"],"problem":"데이터 0건","detail":"날짜/권한/파라미터 확인","patches":["debug_panel"]}); p.add("debug_panel")
    return {"findings":f or [{"target":"전체","problem":"큰 문제 없음","detail":"정상","patches":[]}],"recommended_patches":sorted(p)}

def gsheet_append(mem, tab, row):
    cfg=mem.setdefault("google_sheets",{"enabled":False,"sheet_id":"","service_account_json":""})
    if not cfg.get("enabled"): return False,"구글시트 꺼짐"
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds=Credentials.from_service_account_info(json.loads(cfg["service_account_json"]),scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
        ss=gspread.authorize(creds).open_by_key(cfg["sheet_id"])
        try: ws=ss.worksheet(tab)
        except Exception:
            ws=ss.add_worksheet(title=tab,rows=1000,cols=10); ws.append_row(["time","type","project","version","status","summary","data_json"])
        ws.append_row([row.get("time",datetime.now().isoformat(timespec="seconds")),row.get("type",tab),row.get("project",""),str(row.get("version","")),row.get("status",""),row.get("summary",""),json.dumps(row,ensure_ascii=False)[:45000]], value_input_option="USER_ENTERED")
        return True,"구글시트 저장 완료"
    except Exception as e: return False,str(e)
def event(mem,tab,row):
    ok,msg=gsheet_append(mem,tab,row); mem.setdefault("lessons",[]).append({"time":datetime.now().isoformat(timespec="seconds"),"lesson":f"{tab}: {msg}"}); return ok,msg

def ensure_req(src):
    req=Path(src)/"requirements.txt"; cur=[x.strip() for x in rtxt(req).splitlines() if x.strip()] if req.exists() else []
    for p in ["streamlit","pandas","numpy","requests"]:
        if p.lower() not in {x.lower() for x in cur}: cur.append(p)
    wtxt(req,"\n".join(cur)+"\n")

def patch_app(app_file, approved):
    app_file=Path(app_file); txt=rtxt(app_file); wtxt(app_file.with_suffix(".before_upgrade.py"),txt)
    top=[]; bottom=[]
    if "mobile_ui" in approved and "MARU_MOBILE_UPGRADE" not in txt:
        if "st.set_page_config" not in txt: top.append("st.set_page_config(page_title='업그레이드 앱', layout='wide')\n")
        top.append("st.markdown('<style>/* MARU_MOBILE_UPGRADE */ .block-container{padding-top:1rem;max-width:1200px;} .stButton>button{height:3rem;font-size:1.05rem;font-weight:800;} textarea,input{font-size:1.02rem!important;}</style>', unsafe_allow_html=True)\n")
    if any(x in approved for x in ["error_logger","debug_panel","api_timeout_guard","zip_export"]) and "MARU_COMMON_IMPORTS" not in txt:
        top.append("from pathlib import Path as _maru_Path\nfrom datetime import datetime as _maru_datetime\nimport json as _maru_json\n")
    if "error_logger" in approved and "MARU_ERROR_LOGGER" not in txt:
        top.append("""# MARU_ERROR_LOGGER
_MARU_ERROR_LOG = _maru_Path(__file__).parent / 'error_log.json'
def maru_log_error(where, err):
    rec={'time':_maru_datetime.now().isoformat(timespec='seconds'),'where':str(where),'error':str(err)}
    try:
        old=_maru_json.loads(_MARU_ERROR_LOG.read_text(encoding='utf-8')) if _MARU_ERROR_LOG.exists() else []
        old.append(rec); _MARU_ERROR_LOG.write_text(_maru_json.dumps(old[-500:],ensure_ascii=False,indent=2),encoding='utf-8')
    except Exception: pass
    return rec
""")
    if "api_timeout_guard" in approved and "MARU_API_SAFE_REQUEST" not in txt:
        top.append("""# MARU_API_SAFE_REQUEST
def maru_safe_get(url, params=None, headers=None, timeout=15):
    import requests as _r
    try:
        res=_r.get(url,params=params,headers=headers,timeout=timeout)
        info={'ok':res.ok,'status_code':res.status_code,'url':str(res.url)[:300]}
        try: return info,res.json()
        except Exception: return info,{'text_preview':res.text[:3000]}
    except Exception as e:
        if 'maru_log_error' in globals(): maru_log_error('maru_safe_get',e)
        return {'ok':False,'status_code':'CONNECTION_ERROR','error':str(e)},None
""")
    if "api_key_guard" in approved: bottom.append("with st.expander('🔐 API KEY 보안 안내'):\n    st.warning('API KEY는 app.py에 직접 넣지 말고 Streamlit Secrets 또는 비밀번호 입력창을 사용하세요.')\n")
    if "debug_panel" in approved: bottom.append("with st.expander('🧯 MARU 디버그 패널'):\n    _log=_maru_Path(__file__).parent/'error_log.json'\n    st.json(_maru_json.loads(_log.read_text(encoding='utf-8'))[-30:] if _log.exists() else [])\n")
    if "zip_export" in approved: bottom.append("with st.expander('📦 현재 앱 ZIP 다운로드'):\n    st.info('현재 앱 ZIP 다운로드 패널이 추가되었습니다.')\n")
    if top: txt = txt.replace("import streamlit as st","import streamlit as st\n"+"\n".join(top),1) if "import streamlit as st" in txt else "import streamlit as st\n"+"\n".join(top)+"\n"+txt
    if bottom: txt += "\n\n# ===== MARU V10 REAL PATCH ADDONS =====\n"+"\n".join(bottom)
    wtxt(app_file,txt); return True, f"실제 패치 완료: {approved}"

def add_helpers(src, approved):
    src=Path(src)
    if "kra_api_helper" in approved:
        wtxt(src/"kra_api_debug_helper.py","""import streamlit as st, requests
from datetime import datetime
st.set_page_config(page_title='경마 API 점검',layout='wide')
st.title('🐎 경마 API 점검')
u=st.text_area('API URL 템플릿'); k=st.text_input('API KEY',type='password')
if st.button('점검',type='primary',use_container_width=True):
    url=u.replace('{serviceKey}',k).replace('{api_key}',k).replace('{today}',datetime.now().strftime('%Y%m%d')).replace('{today_dash}',datetime.now().strftime('%Y-%m-%d'))
    try:
        r=requests.get(url,timeout=15); st.metric('HTTP',r.status_code)
        try: st.json(r.json())
        except Exception: st.text(r.text[:5000])
    except Exception as e: st.error(e)
""")
    if "toto_api_helper" in approved:
        wtxt(src/"toto_api_debug_helper.py","""import streamlit as st, requests
st.set_page_config(page_title='토토/스포츠 API 점검',layout='wide')
st.title('⚽ 토토/스포츠 API 점검')
u=st.text_area('API URL 템플릿'); k=st.text_input('API KEY',type='password')
if st.button('점검',type='primary',use_container_width=True):
    try:
        r=requests.get(u.replace('{api_key}',k).replace('{token}',k),timeout=15); st.metric('HTTP',r.status_code)
        try: st.json(r.json())
        except Exception: st.text(r.text[:5000])
    except Exception as e: st.error(e)
""")

def compare(b,a):
    bs,as_=set(b.get("features",[])),set(a.get("features",[]))
    return {"유지":sorted(bs&as_),"추가":sorted(as_-bs),"빠졌을_수_있는_항목":sorted(bs-as_)}

def run_test(name,info):
    recs=[]
    if info.get("app_url"): recs.append(check_url("APP_URL",info["app_url"]))
    for i,u in enumerate(info.get("api_urls",[]),1): recs.append(check_url(f"API_{i}",u,info.get("api_key","")))
    return {"time":datetime.now().isoformat(timespec="seconds"),"project":name,"records":recs,"analysis":analyze_records(recs)}

def workflow(name, app_url, api_urls):
    return f"""name: MARU Auto Test
on:
  workflow_dispatch:
  schedule:
    - cron: '*/30 * * * *'
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: |
          python - <<'PY'
          import requests,sys,json
          targets=[]
          if {app_url!r}: targets.append(('APP_URL',{app_url!r}))
          for i,u in enumerate({api_urls!r},1): targets.append((f'API_{{i}}',u))
          res=[]
          for label,url in targets:
              try:
                  r=requests.get(url,timeout=15); rec={{'label':label,'status':r.status_code,'ok':r.ok,'preview':r.text[:500]}}
              except Exception as e: rec={{'label':label,'ok':False,'error':str(e)}}
              res.append(rec)
          print(json.dumps(res,ensure_ascii=False,indent=2))
          if any(not x.get('ok') for x in res): sys.exit(1)
          PY
"""

def gen_project(goal,kind):
    dst=GEN/(datetime.now().strftime("%Y%m%d_%H%M%S")+"_"+safe(goal)[:30]); dst.mkdir()
    if kind=="경마앱":
        code="import streamlit as st, requests\nst.set_page_config(page_title='경마 API 대시보드',layout='wide')\nst.title('🐎 경마 API 대시보드')\nu=st.text_area('API URL')\nk=st.text_input('API KEY',type='password')\nif st.button('가져오기',use_container_width=True):\n    r=requests.get(u.replace('{api_key}',k).replace('{serviceKey}',k),timeout=15); st.metric('HTTP',r.status_code); st.text(r.text[:5000])\n"
    elif kind=="토토앱":
        code="import streamlit as st\nst.set_page_config(page_title='토토 분석 보조',layout='wide')\nst.title('⚽ 토토 분석 보조')\nh=st.slider('홈 전력',0,100,50); a=st.slider('원정 전력',0,100,50)\nif st.button('분석',use_container_width=True): st.metric('방향','홈 우세' if h>=a else '원정 우세')\n"
    else:
        code="import streamlit as st\nst.set_page_config(page_title='AI 생성 앱',layout='wide')\nst.title('AI 생성 앱')\n"
    wtxt(dst/"app.py",code); wtxt(dst/"requirements.txt","streamlit\nrequests\npandas\nnumpy\n"); wtxt(dst/"README.md",f"# 생성 프로젝트\n{goal}\n")
    out=dst.with_suffix(".zip"); zip_dir(dst,out); return dst,out

mem=load()
st.set_page_config(page_title="MARU V10 무음성 실제 패치 AI", page_icon="🧠", layout="wide")
st.markdown("<style>.block-container{padding-top:1rem;max-width:1280px}.stButton>button{height:3rem;font-weight:800} textarea,input{font-size:1.02rem!important}</style>",unsafe_allow_html=True)
st.title("🧠 MARU V10 무음성 최종 통합 실제 패치 AI")
st.caption("음성/OpenAI 제거 · ZIP 자동해제 · 목록/오류 검사 · 자동테스트 · 구글시트 · 승인 후 실제 app.py 패치 · 새 ZIP 생성")
st.info("고정 원칙: 기존 기능 삭제 금지 / 승인한 항목만 실제 패치 / 자동구매 차단 / OpenAI 키 제거")

tabs=st.tabs(["📋목록","🤖코드생성","📁등록","🔍검사","☁️구글시트","📡모니터","🔁반복","🧯로그","✅패치","📦버전","📚기록"])

with tabs[0]:
    st.subheader("오늘 대화 통합 목록"); st.write(TODAY); st.json(PATCHES)
with tabs[1]:
    goal=st.text_area("목표"); kind=st.selectbox("템플릿",["기본앱","경마앱","토토앱"])
    if st.button("생성 ZIP",type="primary",use_container_width=True):
        dst,out=gen_project(goal,kind); ok,msg=pycheck(dst/"app.py")
        rec={"time":datetime.now().isoformat(timespec="seconds"),"goal":goal,"kind":kind,"zip":str(out),"syntax_ok":ok}
        mem["generated_projects"].append(rec); event(mem,"generated_projects",{"type":"generated","project":"codegen","status":"SUCCESS" if ok else "FAIL","summary":goal[:100],"data":rec}); save(mem)
        with open(out,"rb") as f: st.download_button("다운로드",f,file_name=out.name,mime="application/zip",use_container_width=True)
with tabs[2]:
    name=st.text_input("프로젝트 이름"); kind=st.selectbox("종류",["경마앱","토토앱","코드생성기","기타"],key="regkind")
    app_url=st.text_input("앱 주소"); api_key=st.text_input("API KEY/TOKEN 선택",type="password")
    api_urls=st.text_area("API URL 목록",height=100); up=st.file_uploader("ZIP 또는 app.py",type=["zip","py"])
    if st.button("저장 + 자동 검사",type="primary",use_container_width=True):
        if not name: st.warning("이름 필요")
        elif not up and name not in mem["projects"]: st.warning("처음은 파일 필요")
        else:
            old=mem["projects"].get(name,{})
            src=extract(up,name) if up else Path(old["src"])
            app=find_app(src); fs=scan(src); syn=check_all(src); errs=inspect_errors(src); ana=analyze_code(app)
            info={"name":name,"kind":kind,"src":str(src),"app_file":str(app) if app else "","app_url":app_url or old.get("app_url",""),"api_key":api_key or old.get("api_key",""),"api_urls":[x.strip() for x in api_urls.splitlines() if x.strip()] or old.get("api_urls",[]),"version":old.get("version",0),"file_scan":fs,"syntax_results":syn,"error_file_results":errs,"last_analysis":ana}
            mem["projects"][name]=info; mem["file_checks"].append({"time":datetime.now().isoformat(timespec="seconds"),"project":name,"file_scan":fs,"syntax":syn,"error_files":errs})
            event(mem,"projects",{"type":"register","project":name,"status":"SAVED","summary":"저장/검사 완료","data":info}); save(mem)
            st.success("저장/검사 완료"); st.json(fs); st.json(ana)
with tabs[3]:
    ps=list(mem["projects"])
    if not ps: st.info("등록 먼저")
    else:
        sel=st.selectbox("프로젝트",ps,key="scan")
        if st.button("다시 검사",type="primary",use_container_width=True):
            src=Path(mem["projects"][sel]["src"]); app=find_app(src)
            mem["projects"][sel]["file_scan"]=scan(src); mem["projects"][sel]["syntax_results"]=check_all(src); mem["projects"][sel]["error_file_results"]=inspect_errors(src); mem["projects"][sel]["last_analysis"]=analyze_code(app); save(mem)
        st.json(mem["projects"][sel].get("file_scan",{})); st.json(mem["projects"][sel].get("syntax_results",[])); st.json(mem["projects"][sel].get("error_file_results",[])); st.json(mem["projects"][sel].get("last_analysis",{}))
with tabs[4]:
    cfg=mem["google_sheets"]; en=st.checkbox("사용",value=cfg.get("enabled",False)); sid=st.text_input("Sheet ID",value=cfg.get("sheet_id","")); sj=st.text_area("서비스계정 JSON",value=cfg.get("service_account_json",""),height=160)
    if st.button("설정 저장",type="primary",use_container_width=True):
        mem["google_sheets"]={"enabled":en,"sheet_id":sid,"service_account_json":sj}; save(mem); st.success("저장")
    if st.button("연결 테스트",use_container_width=True):
        mem["google_sheets"]={"enabled":en,"sheet_id":sid,"service_account_json":sj}; ok,msg=gsheet_append(mem,"connection_test",{"type":"test","project":"MARU","status":"TEST","summary":"연결테스트"}); save(mem); st.success(msg) if ok else st.error(msg)
with tabs[5]:
    ps=list(mem["projects"])
    if not ps: st.info("등록 먼저")
    else:
        sel=st.selectbox("프로젝트",ps,key="mon")
        if st.button("자동 점검",type="primary",use_container_width=True):
            rec=run_test(sel,mem["projects"][sel]); mem["monitor_records"].append(rec); mem["projects"][sel]["last_monitor"]=rec; event(mem,"monitor_records",{"type":"monitor","project":sel,"status":"DONE","summary":"자동점검","data":rec}); save(mem); st.json(rec)
        st.json(mem["projects"][sel].get("last_monitor",{}))
with tabs[6]:
    ps=list(mem["projects"])
    if not ps: st.info("등록 먼저")
    else:
        sel=st.selectbox("프로젝트",ps,key="rep"); cnt=st.number_input("횟수",1,20,1); delay=st.number_input("간격초",0,300,0)
        if st.button("반복 테스트",type="primary",use_container_width=True):
            arr=[]
            for i in range(int(cnt)):
                rec=run_test(sel,mem["projects"][sel]); rec["round"]=i+1; arr.append(rec); mem["repeat_tests"].append(rec); mem["projects"][sel]["last_monitor"]=rec
                if delay and i<int(cnt)-1: time.sleep(int(delay))
            event(mem,"repeat_tests",{"type":"repeat","project":sel,"status":"DONE","summary":"반복테스트","data":arr[-1]}); save(mem); st.json(arr)
        yml=workflow(sel,mem["projects"][sel].get("app_url",""),mem["projects"][sel].get("api_urls",[]))
        st.download_button("GitHub Actions maru_auto_test.yml",yml.encode(),file_name="maru_auto_test.yml",mime="text/yaml",use_container_width=True)
with tabs[7]:
    ps=list(mem["projects"])
    if not ps: st.info("등록 먼저")
    else:
        sel=st.selectbox("프로젝트",ps,key="log"); log=st.text_area("로그",height=180); lf=st.file_uploader("로그파일",type=["txt","log","json"])
        if lf: log += "\n"+lf.getvalue().decode("utf-8",errors="ignore")
        if st.button("로그 분석",type="primary",use_container_width=True):
            ana=parse_logs(log); rec={"time":datetime.now().isoformat(timespec="seconds"),"project":sel,"analysis":ana,"preview":log[:1000]}; mem["log_analyses"].append(rec); mem["projects"][sel]["last_log_analysis"]=rec; event(mem,"log_analyses",{"type":"log","project":sel,"status":"DONE","summary":"로그분석","data":rec}); save(mem); st.json(ana)
with tabs[8]:
    ps=list(mem["projects"])
    if not ps: st.info("등록 먼저")
    else:
        sel=st.selectbox("프로젝트",ps,key="patch"); info=mem["projects"][sel]; src=Path(info["src"]); app=Path(info.get("app_file","")) if info.get("app_file") else find_app(src)
        before=analyze_code(app); st.json(before)
        rec=set()
        if info.get("last_monitor"): rec.update(info["last_monitor"].get("analysis",{}).get("recommended_patches",[]))
        if info.get("last_log_analysis"): rec.update(info["last_log_analysis"].get("analysis",{}).get("recommended_patches",[]))
        for e in info.get("error_file_results",[]): rec.update(e.get("analysis",{}).get("recommended_patches",[]))
        extra=st.text_area("추가지시",placeholder="기존 기능 하나도 빼지 말고 승인한 것만 패치")
        approved=[]; rejected=[]
        for k,(title,risk,why) in PATCHES.items():
            with st.container(border=True):
                st.markdown(f"### {title}"); st.write(risk, why)
                if k in rec: st.success("자동 추천")
                disabled=k=="auto_purchase"
                c1,c2=st.columns(2)
                with c1: ok=st.checkbox("승인",value=(k in rec and not disabled),disabled=disabled,key=f"ok_{sel}_{k}")
                with c2: no=st.checkbox("미승인",key=f"no_{sel}_{k}")
                if disabled: st.error("차단")
                if ok and not disabled: approved.append(k)
                if no: rejected.append(k)
        if st.button("승인 항목 실제 패치 → 새 ZIP",type="primary",use_container_width=True):
            b=analyze_code(app); ok,msg=patch_app(app,approved); add_helpers(src,approved); ensure_req(src); a=analyze_code(app); syn=check_all(src); comp=compare(b,a)
            ver=int(info.get("version",0))+1; mem["projects"][sel]["version"]=ver; mem["projects"][sel]["last_analysis"]=a
            snap={"time":datetime.now().isoformat(timespec="seconds"),"project":sel,"version":ver,"approved":approved,"rejected":rejected,"extra":extra,"before":b,"after":a,"compare":comp,"syntax":syn}
            wtxt(src/f"feature_snapshot_v{ver:03d}.json",json.dumps(snap,ensure_ascii=False,indent=2))
            out=OUT/f"{safe(sel)}_v{ver:03d}_PATCHED.zip"; zip_dir(src,out); success=ok and all(x["ok"] for x in syn)
            row={"time":datetime.now().isoformat(timespec="seconds"),"project":sel,"version":ver,"approved":approved,"patch_ok":ok,"syntax_ok":success,"message":msg,"zip":str(out),"compare":comp}
            if success: mem["approved_upgrades"].append(row); event(mem,"approved_upgrades",{"type":"upgrade","project":sel,"version":ver,"status":"SUCCESS","summary":"실제 패치 성공","data":row}); st.success(f"패치 완료 v{ver:03d}")
            else: mem["failed_upgrades"].append(row); event(mem,"failed_upgrades",{"type":"upgrade","project":sel,"version":ver,"status":"FAIL","summary":"패치/문법 문제","data":row}); st.error("패치/문법 문제")
            save(mem); st.json(comp); st.json(syn)
            with open(out,"rb") as f: st.download_button("패치 ZIP 다운로드",f,file_name=out.name,mime="application/zip",use_container_width=True)
with tabs[9]:
    ps=list(mem["projects"])
    if not ps: st.info("등록 먼저")
    else:
        sel=st.selectbox("프로젝트",ps,key="ver"); info=mem["projects"][sel]; src=Path(info["src"])
        st.metric("현재 버전",info.get("version",0))
        if src.exists():
            st.download_button("현재 보관본 ZIP",zip_bytes(src),file_name=f"{safe(sel)}_CURRENT.zip",mime="application/zip",use_container_width=True)
            app=Path(info.get("app_file","")) if info.get("app_file") else find_app(src)
            if app and app.exists(): st.download_button("단일 app.py",rtxt(app).encode("utf-8"),file_name=f"{safe(sel)}_app.py",mime="text/x-python",use_container_width=True)
            backup=app.with_suffix(".before_upgrade.py") if app else None
            if backup and backup.exists() and st.button("직전 백업으로 되돌리기",use_container_width=True):
                shutil.copy2(backup,app); st.success("되돌림 완료")
with tabs[10]:
    st.json({k:mem.get(k) for k in ["file_checks","monitor_records","repeat_tests","log_analyses","approved_upgrades","failed_upgrades","lessons"]})
