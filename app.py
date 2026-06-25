
import streamlit as st
import zipfile, json, shutil, io, re, ast, subprocess, sys, base64, time
from pathlib import Path
from datetime import datetime
import requests

ROOT = Path(__file__).parent
MEM = ROOT / "ai_memory.json"
STORE = ROOT / "project_storage"
VERS = ROOT / "version_outputs"
STORE.mkdir(exist_ok=True)
VERS.mkdir(exist_ok=True)

DEFAULT = {
    "version": "11.1-github-auto-deploy-fix",
    "projects": {},
    "patch_records": [],
    "github_deploys": [],
    "test_records": [],
    "file_checks": [],
    "lessons": [],
}

PATCHES = {
    "mobile_ui": "모바일 큰 글씨/큰 버튼",
    "error_logger": "오류 로그 저장",
    "api_timeout": "API timeout/통신두절 방어",
    "debug_panel": "디버그 패널",
    "api_key_guard": "API KEY 보안 안내",
    "zip_export": "현재 앱 ZIP 다운로드",
    "kra_helper": "경마 API 점검 도구 파일 추가",
    "toto_helper": "토토/스포츠 API 점검 도구 파일 추가",
}

FEATURES = [
    "음성지시 제거", "OpenAI API 키 제거", "요금 발생 요소 제거",
    "ZIP 업로드 자동 압축해제", "프로젝트 보관함", "파일 목록 검사",
    "오류 파일 검사", "문법 검사", "기존 기능 분석", "자동테스트",
    "반복 자동테스트", "개선안 추천", "승인/미승인/추가지시",
    "승인한 항목 실제 패치", "app.py 실제 수정", "helper 파일 실제 추가",
    "새 버전 ZIP 생성", "GitHub 대상 저장소 자동 업로드/커밋",
    "Streamlit Cloud 자동 재배포 유도", "구글시트 저장 구조", 
    "GitHub Actions 예약 테스트 파일 생성", "자동구매/자동결제 차단"
]

def load():
    if MEM.exists():
        try:
            m = json.loads(MEM.read_text(encoding="utf-8"))
            for k, v in DEFAULT.items():
                m.setdefault(k, v)
            return m
        except Exception:
            pass
    save(DEFAULT.copy())
    return DEFAULT.copy()

def save(m):
    m["updated_at"] = datetime.now().isoformat(timespec="seconds")
    MEM.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

def sname(x):
    return re.sub(r"[^a-zA-Z0-9가-힣_.-]+", "_", str(x))[:80] or "project"

def read(p):
    for enc in ("utf-8", "cp949", "euc-kr"):
        try:
            return Path(p).read_text(encoding=enc)
        except Exception:
            pass
    return ""

def write(p, txt):
    Path(p).write_text(txt, encoding="utf-8")

def unzip_upload(up, name):
    pdir = STORE / sname(name)
    if pdir.exists():
        shutil.rmtree(pdir)
    pdir.mkdir(parents=True)
    raw = pdir / up.name
    raw.write_bytes(up.getvalue())
    src = pdir / "src"
    src.mkdir()
    if up.name.lower().endswith(".zip"):
        with zipfile.ZipFile(raw) as z:
            z.extractall(src)
    else:
        shutil.copy2(raw, src / up.name)
    kids = list(src.iterdir())
    if len(kids) == 1 and kids[0].is_dir():
        inner = kids[0]
        if (inner/"app.py").exists() or list(inner.glob("*.py")):
            tmp = pdir/"src_inner"
            shutil.move(str(inner), str(tmp))
            shutil.rmtree(src)
            tmp.rename(src)
    return src

def find_app(src):
    src = Path(src)
    for n in ["app.py", "streamlit_app.py", "main.py"]:
        p = src / n
        if p.exists():
            return p
    py = list(src.rglob("*.py"))
    return py[0] if py else None

def scan(src):
    src = Path(src)
    files, errors, suspicious = [], [], []
    for p in src.rglob("*"):
        if "__pycache__" in p.parts or ".git" in p.parts or not p.is_file():
            continue
        rel = str(p.relative_to(src))
        files.append({"path": rel, "size": p.stat().st_size})
        low = p.name.lower()
        if any(x in low for x in ["error", "log", "traceback", "debug"]):
            errors.append(rel)
        if p.suffix.lower() in [".env", ".pem", ".key"] or p.name == "secrets.toml":
            suspicious.append(rel)
    return {
        "file_count": len(files),
        "has_app_py": any(f["path"].endswith("app.py") for f in files),
        "has_requirements": any(f["path"].endswith("requirements.txt") for f in files),
        "error_files": errors,
        "suspicious_files": suspicious,
        "files": files[:500]
    }

def syntax_all(src):
    rows = []
    for p in Path(src).rglob("*.py"):
        if "__pycache__" in p.parts or ".git" in p.parts:
            continue
        r = subprocess.run([sys.executable, "-m", "py_compile", str(p)], capture_output=True, text=True)
        rows.append({"file": str(p.relative_to(src)), "ok": r.returncode == 0, "message": "OK" if r.returncode == 0 else r.stderr[-2000:]})
    return rows

def analyze_app(app_path):
    txt = read(app_path) if app_path and Path(app_path).exists() else ""
    if not txt:
        return {"features": ["app.py 없음"], "risks": ["app.py를 찾지 못함"]}
    features = []
    if "streamlit" in txt or "st." in txt: features.append("Streamlit UI")
    if "requests" in txt or ".get(" in txt: features.append("API 호출")
    if "timeout=" in txt: features.append("timeout 설정")
    if "try:" in txt and "except" in txt: features.append("오류 처리")
    if "download_button" in txt or "zipfile" in txt: features.append("다운로드/ZIP")
    if "file_uploader" in txt: features.append("파일 업로드")
    if "경마" in txt or "KRA" in txt or "horse" in txt: features.append("경마 관련")
    if "토토" in txt or "sports" in txt or "odds" in txt: features.append("토토/스포츠 관련")
    risks = []
    if re.search(r"(api[_-]?key|serviceKey|token)\s*=\s*['\"][A-Za-z0-9_\-]{16,}", txt, re.I):
        risks.append("API 키가 코드에 직접 들어갔을 가능성")
    if ".get(" in txt and "timeout=" not in txt:
        risks.append("API timeout 부족 가능성")
    if "자동구매" in txt or "자동결제" in txt:
        risks.append("자동구매/자동결제 문구 있음 - 차단 권장")
    if "openai" in txt.lower() or "audio_input" in txt.lower():
        risks.append("음성/OpenAI 코드가 남아 있음 - 제거 권장")
    try:
        ast.parse(txt)
    except Exception as e:
        risks.append("문법 오류: " + str(e))
    return {"features": features or ["기능 추출 부족"], "risks": risks or ["큰 위험 없음"], "lines": len(txt.splitlines())}

def parse_log(txt):
    t = (txt or "").lower()
    rec, patches = [], set()
    rules = [
        ("nameerror", ["error_logger", "debug_panel"], "정의되지 않은 변수"),
        ("keyerror", ["error_logger", "debug_panel"], "키 누락"),
        ("http 500", ["api_timeout", "debug_panel"], "서버/API 오류"),
        ("http 403", ["api_key_guard", "debug_panel"], "권한 문제"),
        ("http 401", ["api_key_guard", "debug_panel"], "키 인증 문제"),
        ("http 404", ["api_timeout", "debug_panel"], "URL 오류"),
        ("timeout", ["api_timeout", "debug_panel"], "타임아웃"),
        ("connectionerror", ["api_timeout", "debug_panel"], "통신두절"),
        ("modulenotfounderror", ["debug_panel"], "requirements 누락"),
        ("data[]", ["debug_panel"], "데이터 0건"),
        ("no result", ["debug_panel"], "데이터 없음"),
        ("통신두절", ["api_timeout", "debug_panel"], "통신두절"),
        ("오류", ["error_logger", "debug_panel"], "오류 기록 필요"),
    ]
    for key, ps, reason in rules:
        if key in t:
            rec.append({"keyword": key, "reason": reason, "patches": ps})
            patches.update(ps)
    return {"findings": rec or [{"keyword":"없음","reason":"명확한 오류 패턴 없음","patches":[]}], "recommended_patches": sorted(patches)}

def inspect_error_files(src):
    rows = []
    for p in Path(src).rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts and any(x in p.name.lower() for x in ["error", "log", "traceback", "debug"]):
            txt = read(p)
            rows.append({"file": str(p.relative_to(src)), "preview": txt[:1200], "analysis": parse_log(txt)})
    return rows

def test_url(label, url, key=""):
    today = datetime.now().strftime("%Y%m%d")
    dash = datetime.now().strftime("%Y-%m-%d")
    final = url.replace("{api_key}", key or "").replace("{serviceKey}", key or "").replace("{token}", key or "").replace("{today}", today).replace("{today_dash}", dash)
    out = {"label": label, "ok": False, "status_code": None, "error": "", "data_count": None, "preview": ""}
    try:
        r = requests.get(final, timeout=15)
        out["ok"] = r.ok; out["status_code"] = r.status_code
        try:
            data = r.json()
            if isinstance(data, dict) and isinstance(data.get("data"), list):
                out["data_count"] = len(data["data"])
            out["preview"] = json.dumps(data, ensure_ascii=False)[:1200]
        except Exception:
            out["preview"] = r.text[:1200]
    except Exception as e:
        out["error"] = str(e)
    return out

def analyze_tests(rows):
    patches, findings = set(), []
    for r in rows:
        stc = r.get("status_code")
        if r.get("error"):
            patches.update(["api_timeout", "debug_panel", "error_logger"])
            findings.append({"target": r["label"], "problem": "통신두절", "patches": ["api_timeout", "debug_panel"]})
        elif stc in [401,403]:
            patches.update(["api_key_guard", "debug_panel"])
            findings.append({"target": r["label"], "problem": f"HTTP {stc}", "patches": ["api_key_guard", "debug_panel"]})
        elif stc == 404 or (stc and stc >= 500):
            patches.update(["api_timeout", "debug_panel"])
            findings.append({"target": r["label"], "problem": f"HTTP {stc}", "patches": ["api_timeout", "debug_panel"]})
        elif r.get("ok") and r.get("data_count") == 0:
            patches.add("debug_panel")
            findings.append({"target": r["label"], "problem": "데이터 0건", "patches": ["debug_panel"]})
    return {"findings": findings or [{"problem": "큰 문제 없음"}], "recommended_patches": sorted(patches)}

def ensure_req(src):
    p = Path(src)/"requirements.txt"
    cur = [x.strip() for x in read(p).splitlines() if x.strip()] if p.exists() else []
    for pkg in ["streamlit", "pandas", "numpy", "requests"]:
        if pkg.lower() not in {x.lower() for x in cur}:
            cur.append(pkg)
    write(p, "\n".join(cur)+"\n")

def apply_patch(app_path, approved):
    app_path = Path(app_path)
    txt = read(app_path)
    write(app_path.with_suffix(".before_upgrade.py"), txt)
    top, bottom = [], []
    if "mobile_ui" in approved and "MARU_MOBILE_UI" not in txt:
        if "st.set_page_config" not in txt:
            top.append("st.set_page_config(page_title='업그레이드 앱', layout='wide')\n")
        top.append("st.markdown('<style>/* MARU_MOBILE_UI */ .block-container{padding-top:1rem;max-width:1200px}.stButton>button{height:3rem;font-weight:800} textarea,input{font-size:1.02rem!important}</style>', unsafe_allow_html=True)\n")
    if any(x in approved for x in ["error_logger","debug_panel","api_timeout","zip_export"]) and "MARU_COMMON_IMPORTS" not in txt:
        top.append("from pathlib import Path as _maru_Path\nfrom datetime import datetime as _maru_datetime\nimport json as _maru_json\n")
    if "error_logger" in approved and "MARU_ERROR_LOGGER" not in txt:
        top.append("""
# MARU_ERROR_LOGGER
_MARU_ERROR_LOG = _maru_Path(__file__).parent / 'error_log.json'
def maru_log_error(where, err):
    rec={'time':_maru_datetime.now().isoformat(timespec='seconds'),'where':str(where),'error':str(err)}
    try:
        old=_maru_json.loads(_MARU_ERROR_LOG.read_text(encoding='utf-8')) if _MARU_ERROR_LOG.exists() else []
        old.append(rec); _MARU_ERROR_LOG.write_text(_maru_json.dumps(old[-500:],ensure_ascii=False,indent=2),encoding='utf-8')
    except Exception: pass
    return rec
""")
    if "api_timeout" in approved and "MARU_SAFE_GET" not in txt:
        top.append("""
# MARU_SAFE_GET
def maru_safe_get(url, params=None, headers=None, timeout=15):
    import requests as _r
    try:
        res=_r.get(url, params=params, headers=headers, timeout=timeout)
        info={'ok':res.ok,'status_code':res.status_code,'url':str(res.url)[:300]}
        try: return info, res.json()
        except Exception: return info, {'text_preview':res.text[:3000]}
    except Exception as e:
        if 'maru_log_error' in globals(): maru_log_error('maru_safe_get', e)
        return {'ok':False,'status_code':'CONNECTION_ERROR','error':str(e)}, None
""")
    if "api_key_guard" in approved and "MARU_API_KEY_GUARD" not in txt:
        bottom.append("with st.expander('🔐 API KEY 보안 안내'):\n    st.warning('API KEY는 app.py에 직접 넣지 마세요. Streamlit Secrets 또는 입력창을 사용하세요.')\n")
    if "debug_panel" in approved and "MARU_DEBUG_PANEL" not in txt:
        bottom.append("""
with st.expander('🧯 MARU 디버그 패널'):
    try:
        _log=_maru_Path(__file__).parent/'error_log.json'
        st.json(_maru_json.loads(_log.read_text(encoding='utf-8'))[-30:] if _log.exists() else [])
    except Exception as e: st.warning(e)
""")
    if "zip_export" in approved and "MARU_ZIP_EXPORT" not in txt:
        bottom.append("""
with st.expander('📦 현재 앱 ZIP 다운로드'):
    try:
        import zipfile as _z, io as _io
        root=_maru_Path(__file__).parent; buf=_io.BytesIO()
        with _z.ZipFile(buf,'w',_z.ZIP_DEFLATED) as zz:
            for p in root.rglob('*'):
                if '__pycache__' not in p.parts and '.git' not in p.parts and p.is_file(): zz.write(p,p.relative_to(root))
        st.download_button('현재 앱 ZIP 다운로드', buf.getvalue(), 'current_app_export.zip', 'application/zip', use_container_width=True)
    except Exception as e: st.warning(e)
""")
    if top:
        txt = txt.replace("import streamlit as st", "import streamlit as st\n" + "\n".join(top), 1) if "import streamlit as st" in txt else "import streamlit as st\n" + "\n".join(top) + "\n" + txt
    if bottom:
        txt += "\n\n# ===== MARU V11.1 PATCH ADDONS =====\n" + "\n".join(bottom)
    write(app_path, txt)

def add_helpers(src, approved):
    src = Path(src)
    if "kra_helper" in approved:
        write(src/"kra_api_debug_helper.py", "import streamlit as st, requests\nst.title('🐎 경마 API 점검')\nurl=st.text_area('URL')\nkey=st.text_input('KEY',type='password')\nif st.button('점검'):\n    try:\n        r=requests.get(url.replace('{serviceKey}',key).replace('{api_key}',key),timeout=15); st.metric('HTTP',r.status_code); st.text(r.text[:5000])\n    except Exception as e: st.error(e)\n")
    if "toto_helper" in approved:
        write(src/"toto_api_debug_helper.py", "import streamlit as st, requests\nst.title('⚽ 토토/스포츠 API 점검')\nurl=st.text_area('URL')\ntoken=st.text_input('TOKEN',type='password')\nif st.button('점검'):\n    try:\n        r=requests.get(url.replace('{token}',token).replace('{api_key}',token),timeout=15); st.metric('HTTP',r.status_code); st.text(r.text[:5000])\n    except Exception as e: st.error(e)\n")

def make_zip(src, name, ver):
    out = VERS / f"{sname(name)}_v{ver:03d}_PATCHED.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in Path(src).rglob("*"):
            if "__pycache__" not in p.parts and ".git" not in p.parts and p.is_file():
                z.write(p, p.relative_to(src))
    return out


def zip_bytes(src):
    buf = io.BytesIO()
    src = Path(src)
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src.rglob("*"):
            if "__pycache__" in p.parts or ".git" in p.parts or not p.is_file():
                continue
            z.write(p, p.relative_to(src))
    return buf.getvalue()

def gh_headers(token):
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}

def gh_repo(owner, repo, token):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=gh_headers(token), timeout=20)
    try: data = r.json()
    except Exception: data = {"text": r.text[:1000]}
    return r.status_code, data

def gh_sha(owner, repo, branch, path, token):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=gh_headers(token), params={"ref": branch}, timeout=20)
    return r.json().get("sha") if r.status_code == 200 else None

def gh_put(owner, repo, branch, path, b, msg, token):
    payload = {"message": msg, "content": base64.b64encode(b).decode(), "branch": branch}
    sha = gh_sha(owner, repo, branch, path, token)
    if sha: payload["sha"] = sha
    r = requests.put(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=gh_headers(token), json=payload, timeout=30)
    try: data = r.json()
    except Exception: data = {"text": r.text[:1000]}
    return r.status_code in [200,201], r.status_code, data

def gh_upload_folder(src, owner, repo, branch, token, msg, prefix=""):
    rows = []
    for p in Path(src).rglob("*"):
        if "__pycache__" in p.parts or ".git" in p.parts or not p.is_file(): continue
        if p.name in [".env", "secrets.toml"] or p.suffix.lower() in [".pem", ".key"]: continue
        rel = str(p.relative_to(src)).replace("\\","/")
        target = f"{prefix.strip('/')}/{rel}" if prefix.strip("/") else rel
        ok, status, data = gh_put(owner, repo, branch, target, p.read_bytes(), msg, token)
        rows.append({"file": target, "ok": ok, "status": status, "message": data.get("message","") if isinstance(data, dict) else ""})
        time.sleep(0.05)
    return rows

def workflow(app_url, api_urls):
    return f"""name: MARU Auto Test
on:
  workflow_dispatch:
  schedule:
    - cron: '*/30 * * * *'
jobs:
  auto-test:
    runs-on: ubuntu-latest
    steps:
      - run: |
          python - <<'PY'
          import requests, json
          targets=[]
          app={app_url!r}
          if app: targets.append(("APP_URL", app))
          for i,u in enumerate({api_urls!r},1): targets.append((f"API_{{i}}", u))
          rows=[]
          for label,url in targets:
              try:
                  r=requests.get(url, timeout=15); rows.append({{"label":label,"ok":r.ok,"status":r.status_code,"preview":r.text[:500]}})
              except Exception as e:
                  rows.append({{"label":label,"ok":False,"error":str(e)}})
          print(json.dumps(rows,ensure_ascii=False,indent=2))
          if any(not x.get("ok") for x in rows): raise SystemExit(1)
          PY
"""

m = load()
st.set_page_config(page_title="MARU GitHub 자동반영 패치 AI V11.1.1", page_icon="🧠", layout="wide")
st.markdown("<style>.block-container{max-width:1280px;padding-top:1rem}.stButton>button{height:3rem;font-weight:800}</style>", unsafe_allow_html=True)
st.title("🧠 MARU GitHub 자동반영 패치 AI V11.1.1")
st.caption("패치 후 경마앱/토토앱 GitHub 저장소에 자동 업로드 → Streamlit Cloud 자동 재배포")
st.info("핵심: 이제 ZIP 다운로드 후 사람이 다시 올리는 단계 없이, 승인 후 대상 GitHub 저장소까지 자동 반영합니다.")

tabs = st.tabs(["📋 기능", "📁 등록", "🔍 검사", "📡 테스트", "✅ 패치", "🚀 GitHub 자동반영", "📦 버전", "📚 기록"])

with tabs[0]:
    st.write(FEATURES)
    st.warning("GitHub 자동반영은 GitHub 토큰이 필요합니다. 토큰은 공개 저장소에 절대 올리지 마세요.")

with tabs[1]:
    name = st.text_input("프로젝트 이름", placeholder="maru-kra-final-clean")
    app_url = st.text_input("배포 앱 주소", placeholder="https://maru-kra-final-clean.streamlit.app")
    api_key = st.text_input("API KEY/TOKEN 선택", type="password")
    api_urls = st.text_area("API URL 목록 - 한 줄에 하나")
    up = st.file_uploader("ZIP 또는 app.py", type=["zip","py"])
    if st.button("저장 + 자동검사", type="primary", use_container_width=True):
        if not name.strip(): st.warning("프로젝트 이름 필요")
        elif not up and name.strip() not in m["projects"]: st.warning("처음 등록은 ZIP 또는 app.py 필요")
        else:
            old = m["projects"].get(name.strip(), {})
            src = unzip_upload(up, name.strip()) if up else Path(old["src"])
            app_path = find_app(src)
            info = {
                "name": name.strip(), "src": str(src), "app_file": str(app_path) if app_path else "",
                "app_url": app_url.strip() or old.get("app_url",""),
                "api_key": api_key or old.get("api_key",""),
                "api_urls": [x.strip() for x in api_urls.splitlines() if x.strip()] or old.get("api_urls", []),
                "version": old.get("version", 0),
                "github": old.get("github", {}),
                "scan": scan(src), "syntax": syntax_all(src), "errors": inspect_error_files(src), "analysis": analyze_app(app_path)
            }
            m["projects"][name.strip()] = info
            m["file_checks"].append({"time": datetime.now().isoformat(timespec="seconds"), "project": name.strip(), "scan": info["scan"]})
            save(m)
            st.success("등록/검사 완료")
            st.json(info["scan"]); st.json(info["analysis"])

with tabs[2]:
    ps = list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel = st.selectbox("프로젝트", ps, key="scan")
        info = m["projects"][sel]; src = Path(info["src"])
        if st.button("다시 검사", type="primary", use_container_width=True):
            app_path = find_app(src)
            info.update({"scan": scan(src), "syntax": syntax_all(src), "errors": inspect_error_files(src), "analysis": analyze_app(app_path)})
            save(m); st.success("검사 완료")
        st.subheader("파일 목록"); st.json(info.get("scan", {}))
        st.subheader("문법 검사"); st.json(info.get("syntax", []))
        st.subheader("오류 파일"); st.json(info.get("errors", []))
        st.subheader("기능 분석"); st.json(info.get("analysis", {}))

with tabs[3]:
    ps = list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel = st.selectbox("프로젝트", ps, key="test")
        cnt = st.number_input("반복 횟수", 1, 20, 1)
        if st.button("자동/반복 테스트", type="primary", use_container_width=True):
            info = m["projects"][sel]
            results = []
            for i in range(int(cnt)):
                rows=[]
                if info.get("app_url"): rows.append(test_url("APP_URL", info["app_url"]))
                for j,u in enumerate(info.get("api_urls",[]),1): rows.append(test_url(f"API_{j}", u, info.get("api_key","")))
                rec={"time":datetime.now().isoformat(timespec="seconds"),"project":sel,"round":i+1,"rows":rows,"analysis":analyze_tests(rows)}
                results.append(rec); m["test_records"].append(rec); info["last_test"]=rec
            save(m); st.success("테스트 완료"); st.json(results)
        info = m["projects"][sel]
        st.download_button("PC 꺼져도 테스트용 maru_auto_test.yml", workflow(info.get("app_url",""), info.get("api_urls",[])).encode(), "maru_auto_test.yml", "text/yaml", use_container_width=True)

with tabs[4]:
    ps = list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel = st.selectbox("프로젝트", ps, key="patch")
        info = m["projects"][sel]; src=Path(info["src"]); app_path=Path(info.get("app_file","")) if info.get("app_file") else find_app(src)
        recset=set()
        if info.get("last_test"): recset.update(info["last_test"]["analysis"].get("recommended_patches",[]))
        for e in info.get("errors",[]): recset.update(e.get("analysis",{}).get("recommended_patches",[]))
        st.json(analyze_app(app_path))
        approved=[]
        for k,v in PATCHES.items():
            default = k in recset
            if st.checkbox(v, value=default, key=f"{sel}_{k}"): approved.append(k)
        st.error("자동구매/자동결제는 이 앱에서 지원하지 않고 차단합니다.")
        if st.button("승인 항목 실제 패치 → 새 ZIP 생성", type="primary", use_container_width=True):
            before=analyze_app(app_path)
            apply_patch(app_path, approved)
            add_helpers(src, approved)
            ensure_req(src)
            after=analyze_app(app_path)
            syn=syntax_all(src)
            ver=int(info.get("version",0))+1; info["version"]=ver; info["analysis"]=after
            write(src/f"feature_snapshot_v{ver:03d}.json", json.dumps({"before":before,"after":after,"approved":approved}, ensure_ascii=False, indent=2))
            zp=make_zip(src, sel, ver)
            ok=all(x["ok"] for x in syn)
            row={"time":datetime.now().isoformat(timespec="seconds"),"project":sel,"version":ver,"approved":approved,"syntax_ok":ok,"zip":str(zp)}
            m["patch_records"].append(row); save(m)
            st.success(f"패치 완료 v{ver:03d}" if ok else "패치됐지만 문법 오류 확인 필요")
            st.json({"before":before,"after":after,"syntax":syn})
            with open(zp,"rb") as f: st.download_button("패치 ZIP 다운로드", f, file_name=zp.name, mime="application/zip", use_container_width=True)

with tabs[5]:
    ps=list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel=st.selectbox("프로젝트", ps, key="gh")
        info=m["projects"][sel]; old=info.get("github",{})
        c1,c2=st.columns(2)
        with c1:
            owner=st.text_input("GitHub owner", old.get("owner","skytins3-png"))
            repo=st.text_input("대상 repo", old.get("repo","maru-kra-final-clean"))
            branch=st.text_input("branch", old.get("branch","main"))
            prefix=st.text_input("업로드 폴더 prefix", old.get("prefix",""), placeholder="비우면 루트")
        with c2:
            token=st.text_input("GitHub 토큰", type="password")
            msg=st.text_input("커밋 메시지", f"MARU auto patch deploy {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            savecfg=st.checkbox("토큰 제외 설정 저장", value=True)
            st.warning("토큰은 저장하지 않습니다. 매번 입력하거나 Streamlit Secrets를 쓰는 게 안전합니다.")
        if st.button("연결 확인", use_container_width=True):
            if not token: st.error("토큰 필요")
            else:
                code,data=gh_repo(owner,repo,token)
                st.success("연결 성공") if code==200 else st.error(f"실패 HTTP {code}")
                st.json(data)
        if st.button("대상 GitHub 저장소에 자동 업로드/커밋", type="primary", use_container_width=True):
            if not token: st.error("토큰 필요")
            else:
                if savecfg:
                    info["github"]={"owner":owner,"repo":repo,"branch":branch,"prefix":prefix}; save(m)
                rows=gh_upload_folder(Path(info["src"]), owner, repo, branch, token, msg, prefix)
                ok=sum(1 for r in rows if r["ok"]); fail=len(rows)-ok
                deploy={"time":datetime.now().isoformat(timespec="seconds"),"project":sel,"repo":f"{owner}/{repo}","branch":branch,"ok":ok,"fail":fail,"rows":rows}
                m["github_deploys"].append(deploy); save(m)
                st.success("GitHub 자동반영 완료. Streamlit Cloud가 곧 재배포합니다." if fail==0 else f"일부 실패: 성공 {ok}, 실패 {fail}")
                st.json(rows[:100])

with tabs[6]:
    ps=list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel=st.selectbox("프로젝트", ps, key="ver")
        info=m["projects"][sel]; src=Path(info["src"])
        st.metric("현재 버전", info.get("version",0))
        st.download_button("현재 보관본 ZIP", zip_bytes(src), f"{sname(sel)}_CURRENT.zip", "application/zip", use_container_width=True)
        app_path=Path(info.get("app_file","")) if info.get("app_file") else find_app(src)
        if app_path and app_path.exists():
            st.download_button("단일 app.py", read(app_path).encode(), f"{sname(sel)}_app.py", "text/x-python", use_container_width=True)

with tabs[7]:
    st.subheader("GitHub 자동반영 기록"); st.json(m.get("github_deploys", [])[-20:])
    st.subheader("패치 기록"); st.json(m.get("patch_records", [])[-20:])
    st.subheader("테스트 기록"); st.json(m.get("test_records", [])[-20:])
    st.subheader("학습"); st.json(m.get("lessons", [])[-50:])
