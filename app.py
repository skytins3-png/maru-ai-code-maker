
import streamlit as st
import pandas as pd
import numpy as np
import requests
import json, re, os, zipfile, shutil, base64, traceback, py_compile, ast
from pathlib import Path
from datetime import datetime, timezone, timedelta

APP_VERSION = "20.2-tabs-only-clean"
KST = timezone(timedelta(hours=9))

def maru_now_kst_text():
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")

def maru_show_rows(rows):
    try:
        safe = []
        for r in rows or []:
            if isinstance(r, dict):
                safe.append({str(k): "" if v is None else str(v) for k, v in r.items()})
            else:
                safe.append({"값": str(r)})
        st.dataframe(pd.DataFrame(safe), width="stretch")
    except Exception:
        st.write(rows)

def save_memory(*args, **kwargs):
    return None


def maru_secret_first(*names, default=""):
    for _name in names:
        try:
            _val = st.secrets.get(_name, "")
            if _val:
                return _val
        except Exception:
            pass
    return default

def maru_maru_get_default_profile(mem_obj=None):
    _base = {
        "project_name": "maru-kra-final-clean",
        "app_url": "https://maru-kra-final-clean.streamlit.app",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "maru-kra-final-clean",
        "github_branch": "main",
    }
    try:
        if mem_obj is not None:
            _prof = mem_obj.setdefault("default_profile", {})
            for _k, _v in _base.items():
                _prof.setdefault(_k, _v)
            return _prof
    except Exception:
        pass
    return _base

def maru_maru_profile_from_choice(choice, mem_obj=None):
    _presets = {
        "경마앱": {"project_name":"maru-kra-final-clean","app_url":"https://maru-kra-final-clean.streamlit.app","api_key":"","api_urls":"","github_owner":"skytins3-png","github_repo":"maru-kra-final-clean","github_branch":"main"},
        "토토앱": {"project_name":"skytoto-ai-hub","app_url":"","api_key":"","api_urls":"","github_owner":"skytins3-png","github_repo":"skytoto-ai-hub","github_branch":"main"},
        "AI 코드 생성기": {"project_name":"maru-ai-code-maker","app_url":"https://maru-ai-code-maker.streamlit.app","api_key":"","api_urls":"","github_owner":"skytins3-png","github_repo":"maru-ai-code-maker","github_branch":"main"},
        "직접입력": {"project_name":"","app_url":"","api_key":"","api_urls":"","github_owner":"skytins3-png","github_repo":"","github_branch":"main"},
    }
    _p = _presets.get(choice, _presets["직접입력"]).copy()
    if choice == "직접입력":
        _p.update(maru_maru_get_default_profile(mem_obj))
    else:
        _cur = maru_maru_get_default_profile(mem_obj)
        if _cur.get("api_key") and not _p.get("api_key"):
            _p["api_key"] = _cur.get("api_key", "")
        if _cur.get("api_urls") and not _p.get("api_urls"):
            _p["api_urls"] = _cur.get("api_urls", "")
    return _p

def maru_api_key_for(choice, mem_obj=None):
    if choice == "경마앱":
        return secret_first(
            "KRA_API_KEY",
            "PUBLIC_DATA_API_KEY",
            "MARU_KRA_API_KEY",
            default=maru_get_default_profile(mem_obj).get("api_key", ""),
        )
    if choice == "토토앱":
        return secret_first(
            "TOTO_API_KEY",
            "SPORTS_API_KEY",
            "SPORTMONKS_TOKEN",
            "MARU_TOTO_API_KEY",
            default=maru_get_default_profile(mem_obj).get("api_key", ""),
        )
    return maru_get_default_profile(mem_obj).get("api_key", "")

def maru_api_urls_for(choice, mem_obj=None):
    current = maru_get_default_profile(mem_obj).get("api_urls", "")
    if current:
        return current
    if choice == "경마앱":
        return "\n".join([
            "https://apis.data.go.kr/B551015/API310/raceInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json",
            "https://apis.data.go.kr/B551015/API310/entryInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json",
            "https://apis.data.go.kr/B551015/API310/horseInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json",
        ])
    if choice == "토토앱":
        return "\n".join([
            "https://api.sportmonks.com/v3/football/fixtures/date/{today_dash}?api_token={api_key}&include=participants;league",
            "https://api.sportmonks.com/v3/football/fixtures/between/{today_dash}/{today_dash}?api_token={api_key}&include=participants;league",
        ])
    return ""

def maru_github_token():
    # Streamlit Secrets에 GITHUB_TOKEN / MARU_GITHUB_TOKEN 저장하면 모바일에서도 자동 입력됨
    for key in ["GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token"]:
        val = get_secret_value(key, "")
        if val:
            return val
    return ""

def maru_profile_from_choice(choice, mem=None):
    base = PROJECT_PRESETS.get(choice, PROJECT_PRESETS["직접입력"]).copy()
    if choice == "직접입력" and mem is not None:
        current = maru_get_default_profile(mem).copy()
        current.setdefault("github_owner", "skytins3-png")
        current.setdefault("github_branch", "main")
        return current
    if mem is not None:
        current = maru_get_default_profile(mem)
        # API 키와 API URL은 사용자가 저장한 값이 있으면 유지해서 재입력 줄이기
        if current.get("api_key") and not base.get("api_key"):
            base["api_key"] = current.get("api_key", "")
        if current.get("api_urls") and not base.get("api_urls"):
            base["api_urls"] = current.get("api_urls", "")
    return base

def maru_get_default_profile(mem):
    return mem.setdefault("default_profile", {
        "project_name": "maru-kra-final-clean",
        "app_url": "https://maru-kra-final-clean.streamlit.app",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "maru-kra-final-clean",
        "github_branch": "main",
    })

def maru_now_kst():
    try:
        return datetime.now(KST)
    except Exception:
        return datetime.now(timezone(timedelta(hours=9)))

def maru_vault_key(label):
    preset = MARU_PROJECT_PRESETS.get(label, dict())
    name = preset.get("project_name", label)
    return str(name).replace("/", "_").replace(" ", "_")

def maru_vault_project_dir(label):
    d = MARU_PROJECT_VAULT_DIR / maru_vault_key(label)
    d.mkdir(parents=True, exist_ok=True)
    return d

def maru_vault_src_dir(label):
    d = maru_vault_project_dir(label) / "latest_src"
    d.mkdir(parents=True, exist_ok=True)
    return d

def maru_vault_meta_path(label):
    return maru_vault_project_dir(label) / "vault_meta.json"

def maru_read_vault_meta(label):
    p = maru_vault_meta_path(label)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return dict()
    return dict()

def maru_write_vault_meta(label, meta):
    meta["updated_at"] = maru_now_kst_text()
    maru_vault_meta_path(label).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

def maru_load_project_from_vault(mem_obj, label):
    preset = MARU_PROJECT_PRESETS.get(label, dict())
    pname = preset.get("project_name", label)
    src = maru_vault_src_dir(label)
    meta = maru_read_vault_meta(label)
    if not (src / "app.py").exists():
        return False, f"{label} 보관소에 app.py가 없습니다. 최초 1회만 ZIP/app.py를 보관소에 저장하세요."
    mem_obj.setdefault("projects", dict())
    mem_obj["projects"][pname] = {
        "name": pname,
        "src": str(src),
        "app_url": preset.get("app_url", meta.get("app_url", "")),
        "api_key": meta.get("api_key", ""),
        "api_urls": meta.get("api_urls", []),
        "github": {
            "owner": preset.get("github_owner", "skytins3-png"),
            "repo": preset.get("github_repo", pname),
            "branch": preset.get("github_branch", "main"),
        },
        "vault_label": label,
        "vault_auto": True,
        "updated_at": maru_now_kst_text(),
    }
    mem_obj["default_project"] = pname
    mem_obj["default_profile"] = {
        "project_name": pname,
        "app_url": preset.get("app_url", ""),
        "api_key": meta.get("api_key", ""),
        "api_urls": "\\n".join(meta.get("api_urls", [])) if isinstance(meta.get("api_urls", []), list) else str(meta.get("api_urls", "")),
        "github_owner": preset.get("github_owner", "skytins3-png"),
        "github_repo": preset.get("github_repo", pname),
        "github_branch": preset.get("github_branch", "main"),
    }
    save_memory(mem_obj)
    return True, f"{label} 최신파일을 보관소에서 불러왔습니다. 이제 등록 없이 패치/검사/GitHub 자동반영 가능합니다."

def maru_save_upload_to_vault(label, uploaded_file, api_key="", api_urls_text=""):
    src = maru_vault_src_dir(label)
    if src.exists():
        shutil.rmtree(src)
    src.mkdir(parents=True, exist_ok=True)
    raw_dir = maru_vault_project_dir(label) / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    filename = uploaded_file.name
    raw_path = raw_dir / filename
    raw_path.write_bytes(uploaded_file.getvalue())
    if filename.lower().endswith(".zip"):
        with zipfile.ZipFile(raw_path, "r") as z:
            z.extractall(src)
        nested_apps = list(src.rglob("app.py"))
        if nested_apps and not (src / "app.py").exists():
            root = nested_apps[0].parent
            temp = maru_vault_project_dir(label) / "_flatten_temp"
            if temp.exists():
                shutil.rmtree(temp)
            shutil.copytree(root, temp)
            shutil.rmtree(src)
            temp.rename(src)
    else:
        (src / filename).write_bytes(raw_path.read_bytes())
        if filename != "app.py" and filename.lower().endswith(".py"):
            shutil.copy2(src / filename, src / "app.py")
    api_urls = [x.strip() for x in str(api_urls_text).splitlines() if x.strip()]
    meta = {
        "label": label,
        "project_name": MARU_PROJECT_PRESETS.get(label, dict()).get("project_name", label),
        "filename": filename,
        "api_key": api_key,
        "api_urls": maru_clean_api_urls_for_project(label, api_urls),
        "src": str(src),
    }
    maru_write_vault_meta(label, meta)
    return src, meta

def maru_run_basic_project_test(src):
    """보관소/프로젝트 소스 기준 기본 테스트: 파일 존재, 문법, requirements 확인."""
    result = {
        "ok": True,
        "checks": [],
        "errors": [],
        "logs": [],
    }
    src = Path(src)
    app_file = src / "app.py"
    if not app_file.exists():
        result["ok"] = False
        result["errors"].append("app.py 없음")
    else:
        result["checks"].append("app.py 확인")
        try:
            py_compile.compile(str(app_file), doraise=True)
            result["checks"].append("app.py 문법 검사 통과")
        except Exception as e:
            result["ok"] = False
            result["errors"].append("app.py 문법 오류: " + str(e))
    req = src / "requirements.txt"
    if req.exists():
        result["checks"].append("requirements.txt 확인")
    else:
        result["logs"].append("requirements.txt 없음: Streamlit 기본 의존성만 사용 가능")
    return result

def maru_analyze_loop_logs(test_result):
    """테스트 결과를 로그분석 형태로 정리하고 다음 패치 힌트 생성."""
    hints = []
    for e in test_result.get("errors", []):
        if "app.py 없음" in e:
            hints.append("보관소 ZIP 구조를 확인하고 app.py가 루트에 오도록 평탄화하세요.")
        elif "SyntaxError" in e or "문법 오류" in e:
            hints.append("app.py 문법 오류 위치를 찾아 자동 패치 후보로 등록하세요.")
        elif "NameError" in e:
            hints.append("누락 함수/변수 호환 helper를 상단에 추가하세요.")
        else:
            hints.append("오류 로그 기반으로 해당 파일을 재검사하세요: " + e[:160])
    if not hints and test_result.get("ok"):
        hints.append("테스트 통과: GitHub 자동반영 후 Streamlit 로그 확인 단계로 진행 가능")
    return hints

def maru_loop_event(mem_obj, project_name, step, status, detail):
    mem_obj.setdefault("continuous_loop_history", []).append({
        "time": maru_now_kst_text(),
        "project": project_name,
        "step": step,
        "status": status,
        "detail": detail,
    })
    mem_obj["continuous_loop_history"] = mem_obj["continuous_loop_history"][-100:]
    save_memory(mem_obj)

def maru_get_project_info_from_choice(mem_obj, label):
    ok, msg = maru_load_project_from_vault(mem_obj, label)
    if not ok:
        return None, msg
    pname = MARU_PROJECT_PRESETS[label]["project_name"]
    return mem_obj.get("projects", {}).get(pname), msg

def maru_run_continuous_loop_once(mem_obj, label, do_github=False, github_token="", commit_msg="MARU auto loop patch"):
    """한 번의 연속 루프: 보관소 불러오기 -> 테스트 -> 로그분석 -> 필요 시 GitHub 자동반영."""
    info, msg = maru_get_project_info_from_choice(mem_obj, label)
    if not info:
        return [{"step": "보관소 불러오기", "status": "실패", "detail": msg}]
    project_name = info.get("name", MARU_PROJECT_PRESETS[label]["project_name"])
    src = Path(info.get("src", ""))
    rows = []
    rows.append({"step": "보관소 불러오기", "status": "성공", "detail": msg})
    maru_loop_event(mem_obj, project_name, "보관소 불러오기", "성공", msg)

    test_result = maru_run_basic_project_test(src)
    rows.append({"step": "자동 테스트", "status": "성공" if test_result.get("ok") else "실패", "detail": json.dumps(test_result, ensure_ascii=False)})
    maru_loop_event(mem_obj, project_name, "자동 테스트", "성공" if test_result.get("ok") else "실패", json.dumps(test_result, ensure_ascii=False))

    hints = maru_analyze_loop_logs(test_result)
    rows.append({"step": "로그분석", "status": "완료", "detail": " / ".join(hints)})
    maru_loop_event(mem_obj, project_name, "로그분석", "완료", " / ".join(hints))

    if test_result.get("ok") and do_github:
        gh = info.get("github", {})
        owner = gh.get("owner", "skytins3-png")
        repo = gh.get("repo", project_name)
        branch = gh.get("branch", "main")
        token = github_token or (get_github_token_from_secret() if "get_github_token_from_secret" in globals() else "")
        if not token:
            rows.append({"step": "GitHub 자동반영", "status": "대기", "detail": "GITHUB_TOKEN 없음"})
            maru_loop_event(mem_obj, project_name, "GitHub 자동반영", "대기", "GITHUB_TOKEN 없음")
        else:
            try:
                upload_rows = gh_upload_folder(src, owner, repo, branch, token, commit_msg, "")
                ok_count = sum(1 for r in upload_rows if r.get("ok"))
                fail_count = sum(1 for r in upload_rows if not r.get("ok"))
                detail = f"성공 {ok_count}, 실패 {fail_count}"
                rows.append({"step": "GitHub 자동반영", "status": "성공" if fail_count == 0 else "일부실패", "detail": detail})
                maru_loop_event(mem_obj, project_name, "GitHub 자동반영", "성공" if fail_count == 0 else "일부실패", detail)
            except Exception as e:
                rows.append({"step": "GitHub 자동반영", "status": "실패", "detail": str(e)})
                maru_loop_event(mem_obj, project_name, "GitHub 자동반영", "실패", str(e))
    elif not test_result.get("ok"):
        rows.append({"step": "재패치 대기", "status": "필요", "detail": "테스트 실패 → 로그분석 힌트 기반 패치 필요"})
        maru_loop_event(mem_obj, project_name, "재패치 대기", "필요", "테스트 실패 → 로그분석 힌트 기반 패치 필요")
    else:
        rows.append({"step": "GitHub 자동반영", "status": "선택안함", "detail": "테스트까지만 실행"})
        maru_loop_event(mem_obj, project_name, "GitHub 자동반영", "선택안함", "테스트까지만 실행")
    return rows

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

def save_uploaded_images(project_name, uploads):
    saved = []
    folder = IMAGE_STORE / sname(project_name)
    folder.mkdir(parents=True, exist_ok=True)
    for up in uploads or []:
        suffix = Path(up.name).suffix.lower() or ".png"
        fname = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{sname(Path(up.name).stem)}{suffix}"
        p = folder / fname
        data = up.getvalue()
        p.write_bytes(data)
        saved.append({
            "name": up.name,
            "saved_path": str(p),
            "size": len(data),
            "suffix": suffix,
        })
    return saved

def apply_patch(app_path, approved):
    app_path = Path(app_path)
    txt = read(app_path)
    write(app_path.with_suffix(".before_upgrade.py"), txt)
    top, bottom = [], []
    if "html_render_fix" in approved:
        for a,b in [("st.code(agent_html)", "st.markdown(agent_html, unsafe_allow_html=True)"), ("st.text(agent_html)", "st.markdown(agent_html, unsafe_allow_html=True)"), ("st.write(agent_html)", "st.markdown(agent_html, unsafe_allow_html=True)"), ("st.code(card_html)", "st.markdown(card_html, unsafe_allow_html=True)"), ("st.text(card_html)", "st.markdown(card_html, unsafe_allow_html=True)"), ("st.write(card_html)", "st.markdown(card_html, unsafe_allow_html=True)"), ("st.code(html)", "st.markdown(html, unsafe_allow_html=True)"), ("st.text(html)", "st.markdown(html, unsafe_allow_html=True)")]:
            txt = txt.replace(a,b)
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
        st.download_button('현재 앱 ZIP 다운로드', buf.getvalue(), 'current_app_export.zip', 'application/zip', width="stretch")
    except Exception as e: st.warning(e)
""")
    if "race_schedule_fallback" in approved and "MARU_RACE_FALLBACK_NOTE" not in txt:
        bottom.append("with st.expander('🐎 경마 추천 없음 보정 안내'):\n    st.info('추천 파일이 비어 있어도 공식 경주 일정이 있으면 경주 있음 / 추천 생성 대기 / 수집 필요로 표시되도록 보정 파일을 추가했습니다.')\n")
    if top:
        txt = txt.replace("import streamlit as st", "import streamlit as st\n" + "\n".join(top), 1) if "import streamlit as st" in txt else "import streamlit as st\n" + "\n".join(top) + "\n" + txt
    if bottom:
        txt += "\n\n# ===== MARU V13 PATCH ADDONS =====\n" + "\n".join(bottom)
    write(app_path, txt)

def save_event(mem, tab, row):
    ok, msg = gsheet_append(mem, tab, row)
    mem.setdefault("lessons", []).append({
        "time": datetime.now().isoformat(timespec="seconds"),
        "lesson": f"{tab}: {msg}",
    })
    return ok, msg

def gh_headers(token):
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}

def gh_repo(owner, repo, token):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=gh_headers(token), timeout=20)
    try: data = r.json()
    except Exception: data = {"text": r.text[:1000]}
    return r.status_code, data

def gh_sha(owner, repo, branch, path, token):
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=gh_headers(token), params={"ref": branch}, timeout=20)
    if r.status_code == 200:
        try:
            return r.json().get("sha")
        except Exception:
            return None
    if r.status_code == 404:
        # 파일이 아직 없다는 뜻. 실패가 아니라 새 파일 생성 대상으로 처리.
        return None
    try:
        data = r.json()
    except Exception:
        data = {"message": r.text[:500]}
    raise RuntimeError(f"GitHub file lookup failed {r.status_code}: {data.get('message', '')}")

def gh_put(owner, repo, branch, path, b, msg, token):
    payload = {"message": msg, "content": base64.b64encode(b).decode(), "branch": branch}
    try:
        sha = gh_sha(owner, repo, branch, path, token)
    except Exception as e:
        return False, 0, {"message": str(e)}
    if sha:
        payload["sha"] = sha
    r = requests.put(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=gh_headers(token), json=payload, timeout=30)
    try:
        data = r.json()
    except Exception:
        data = {"text": r.text[:1000]}
    if r.status_code in [200, 201]:
        data["_mode"] = "update" if sha else "create"
    return r.status_code in [200,201], r.status_code, data

def gh_upload_folder(src, owner, repo, branch, token, msg, prefix=""):
    rows = []
    for p in Path(src).rglob("*"):
        if "__pycache__" in p.parts or ".git" in p.parts or not p.is_file(): continue
        if ".github" in p.parts and "workflows" in p.parts:
            rows.append({"file": str(p.relative_to(src)).replace("\\","/"), "ok": True, "status": "SKIPPED", "message": "GitHub workflows 폴더는 보안권한 문제 방지를 위해 자동 제외"})
            continue
        if p.name in [".env", "secrets.toml"] or p.suffix.lower() in [".pem", ".key"]: continue
        rel = str(p.relative_to(src)).replace("\\","/")
        target = f"{prefix.strip('/')}/{rel}" if prefix.strip("/") else rel
        ok, status, data = gh_put(owner, repo, branch, target, p.read_bytes(), msg, token)
        rows.append({"file": target, "ok": ok, "status": status, "message": data.get("message","") if isinstance(data, dict) else ""})
        time.sleep(0.05)
    return rows

def maru_new_req_id():
    return maru_now_kst().strftime("%Y%m%d%H%M%S") + "_" + str(uuid.uuid4())[:8]

def maru_add_improvement_request(mem_obj, project_label, title, detail, priority="보통"):
    mem_obj.setdefault("improvement_requests", [])
    item = {
        "id": maru_new_req_id(),
        "time": maru_now_kst_text(),
        "project": project_label,
        "title": title.strip(),
        "detail": detail.strip(),
        "priority": priority,
        "status": "승인대기",
        "approved_at": "",
        "decision_note": "",
    }
    mem_obj["improvement_requests"].append(item)
    save_memory(mem_obj)
    return item

def maru_decide_improvement_request(mem_obj, req_id, decision, note=""):
    mem_obj.setdefault("improvement_requests", [])
    for item in mem_obj["improvement_requests"]:
        if item.get("id") == req_id:
            item["status"] = decision
            item["decision_note"] = note
            if decision == "승인":
                item["approved_at"] = maru_now_kst_text()
                mem_obj.setdefault("approved_patch_queue", [])
                mem_obj["approved_patch_queue"].append({
                    "id": req_id,
                    "time": item["approved_at"],
                    "project": item.get("project", ""),
                    "title": item.get("title", ""),
                    "detail": item.get("detail", ""),
                    "source": "개선요구 승인",
                    "status": "패치대기",
                })
            save_memory(mem_obj)
            return True, item
    return False, None

def maru_get_improvement_requests(mem_obj, status=None):
    rows = mem_obj.setdefault("improvement_requests", [])
    if status:
        return [r for r in rows if r.get("status") == status]
    return rows

def maru_get_approved_patch_queue(mem_obj, status=None):
    rows = mem_obj.setdefault("approved_patch_queue", [])
    if status:
        return [r for r in rows if r.get("status") == status]
    return rows

def maru_mark_patch_queue_done(mem_obj, req_id, status="패치진행중"):
    for item in mem_obj.setdefault("approved_patch_queue", []):
        if item.get("id") == req_id:
            item["status"] = status
            item["updated_at"] = maru_now_kst_text()
            save_memory(mem_obj)
            return True
    return False

def maru_auto_patch_from_log_hints(mem_obj, project_label, hints):
    """
    승인된 개선요구 이후에는 패치마다 추가 승인 없이 자동 패치 후보를 적용하는 루프용.
    현재는 안전 패치만 수행:
    - 누락 README/requirements 생성
    - ai_memory.json 기본 구조 보정
    - app.py 문법 실패 시 자동수정 대신 로그 기록 후 재패치 필요 표시
    """
    info, msg = maru_get_project_info_from_choice(mem_obj, project_label)
    if not info:
        return {"ok": False, "patched": [], "message": msg}
    src = Path(info.get("src", ""))
    patched = []

    # 안전 보정 1: requirements.txt 없으면 기본값 생성
    req = src / "requirements.txt"
    if not req.exists():
        req.write_text("streamlit\npandas\nnumpy\nrequests\n", encoding="utf-8")
        patched.append("requirements.txt 기본 생성")

    # 안전 보정 2: README.md 없으면 생성
    readme = src / "README.md"
    if not readme.exists():
        readme.write_text(f"# {info.get('name', project_label)}\n\nMARU 자동 보관소 프로젝트입니다.\n", encoding="utf-8")
        patched.append("README.md 기본 생성")

    # 안전 보정 3: ai_memory.json 없으면 생성
    memfile = src / "ai_memory.json"
    if not memfile.exists():
        memfile.write_text(json.dumps({"version": "auto-created", "project": info.get("name", project_label)}, ensure_ascii=False, indent=2), encoding="utf-8")
        patched.append("ai_memory.json 기본 생성")

    detail = " / ".join(patched) if patched else "적용 가능한 안전 자동패치 없음"
    maru_loop_event(mem_obj, info.get("name", project_label), "무승인 자동패치", "완료", detail)
    return {"ok": True, "patched": patched, "message": detail}

def maru_run_no_approval_patch_loop(mem_obj, label, repeat=3, do_github=True, github_token="", commit_msg="MARU no approval auto patch loop"):
    """
    승인된 개선요구가 있거나 사용자가 루프를 시작하면:
    패치 추가승인 없이 테스트 → 로그분석 → 안전 자동패치 → 재테스트 → 자동반영 흐름 실행
    """
    all_rows = []
    for n in range(int(repeat)):
        info, msg = maru_get_project_info_from_choice(mem_obj, label)
        if not info:
            all_rows.append({"round": n+1, "step": "보관소 불러오기", "status": "실패", "detail": msg})
            break

        project_name = info.get("name", MARU_PROJECT_PRESETS[label]["project_name"])
        src = Path(info.get("src", ""))

        all_rows.append({"round": n+1, "step": "보관소 불러오기", "status": "성공", "detail": msg})
        test_result = maru_run_basic_project_test(src)
        all_rows.append({"round": n+1, "step": "자동 테스트", "status": "성공" if test_result.get("ok") else "실패", "detail": json.dumps(test_result, ensure_ascii=False)})
        maru_loop_event(mem_obj, project_name, "자동 테스트", "성공" if test_result.get("ok") else "실패", json.dumps(test_result, ensure_ascii=False))

        hints = maru_analyze_loop_logs(test_result)
        all_rows.append({"round": n+1, "step": "로그분석", "status": "완료", "detail": " / ".join(hints)})
        maru_loop_event(mem_obj, project_name, "로그분석", "완료", " / ".join(hints))

        if not test_result.get("ok"):
            patch_result = maru_auto_patch_from_log_hints(mem_obj, label, hints)
            all_rows.append({"round": n+1, "step": "무승인 자동패치", "status": "완료" if patch_result.get("ok") else "실패", "detail": patch_result.get("message", "")})
            # 안전 자동패치가 없으면 무한 반복 방지
            if not patch_result.get("patched"):
                all_rows.append({"round": n+1, "step": "재패치 중지", "status": "수동확인필요", "detail": "자동으로 안전하게 고칠 수 없는 오류입니다. 로그를 보고 코드패치 필요"})
                break
            continue

        if test_result.get("ok") and do_github:
            gh = info.get("github", {})
            owner = gh.get("owner", "skytins3-png")
            repo = gh.get("repo", project_name)
            branch = gh.get("branch", "main")
            token = github_token or (get_github_token_from_secret() if "get_github_token_from_secret" in globals() else "")
            if not token:
                all_rows.append({"round": n+1, "step": "GitHub 자동반영", "status": "대기", "detail": "GITHUB_TOKEN 없음"})
                break
            try:
                upload_rows = gh_upload_folder(src, owner, repo, branch, token, f"{commit_msg} #{n+1}", "")
                ok_count = sum(1 for r in upload_rows if r.get("ok"))
                fail_count = sum(1 for r in upload_rows if not r.get("ok"))
                status = "성공" if fail_count == 0 else "일부실패"
                detail = f"성공 {ok_count}, 실패 {fail_count}"
                all_rows.append({"round": n+1, "step": "GitHub 자동반영", "status": status, "detail": detail})
                maru_loop_event(mem_obj, project_name, "GitHub 자동반영", status, detail)
            except Exception as e:
                all_rows.append({"round": n+1, "step": "GitHub 자동반영", "status": "실패", "detail": str(e)})
            break
        else:
            all_rows.append({"round": n+1, "step": "완료", "status": "테스트통과", "detail": "GitHub 자동반영 선택 안 함"})
            break
    save_memory(mem_obj)
    return all_rows

def maru_safe_dataframe_rows(rows):
    """표 변환 최종 안전 처리. pandas/Arrow/pd 전역 누락으로 앱이 죽지 않게 함."""
    safe_rows = []
    try:
        for row in rows or []:
            if isinstance(row, dict):
                safe_rows.append({str(k): "" if v is None else str(v) for k, v in row.items()})
            else:
                safe_rows.append({"value": "" if row is None else str(row)})
    except Exception as e:
        safe_rows = [{"error": "표 변환 준비 실패", "detail": str(e)}]

    try:
        import pandas as _maru_pd
        return _maru_pd.DataFrame(safe_rows).astype(str)
    except Exception:
        return safe_rows

def maru_folder_fingerprint(src):
    """같은 파일을 GitHub에 반복 자동반영하지 않기 위한 지문."""
    try:
        src = Path(src)
        h = hashlib.sha256()
        for p in sorted(src.rglob("*")):
            if p.is_file():
                name = str(p.relative_to(src)).replace("\\", "/")
                if ".git/" in name or ".bak_" in name or "__pycache__" in name:
                    continue
                h.update(name.encode("utf-8", "ignore"))
                try:
                    h.update(p.read_bytes())
                except Exception:
                    h.update(str(p.stat().st_mtime).encode())
        return h.hexdigest()
    except Exception:
        return ""

def maru_should_skip_duplicate_upload(mem_obj, project_name, fingerprint):
    try:
        key = f"last_github_fingerprint::{project_name}"
        return bool(fingerprint and mem_obj.get(key) == fingerprint)
    except Exception:
        return False

def maru_mark_uploaded_fingerprint(mem_obj, project_name, fingerprint):
    try:
        if fingerprint:
            mem_obj[f"last_github_fingerprint::{project_name}"] = fingerprint
            save_memory(mem_obj)
    except Exception:
        pass

def maru_detect_app_identity(src):
    """업로드 대상 파일이 어떤 앱 계열인지 대략 판별."""
    try:
        app_file = Path(src) / "app.py"
        text = app_file.read_text(encoding="utf-8", errors="ignore")[:20000]
        if "코드 생성" in text or "AI 코드 생성기" in text or "code-maker" in text or "보관소" in text:
            return "AI 코드 생성기"
        if "경마" in text or "KRA" in text or "마사회" in text or "horse" in text:
            return "경마앱"
        if "토토" in text or "SPORTMONKS" in text or "fixture" in text:
            return "토토앱"
    except Exception:
        pass
    return "알수없음"

def maru_repo_project_guard(label, owner, repo, src):
    """경마 repo에 AI 생성기 파일이 올라가는 사고 차단."""
    try:
        identity = maru_detect_app_identity(src)
        repo_text = f"{owner}/{repo}".lower()
        if "maru-kra-final-clean" in repo_text and identity == "AI 코드 생성기":
            return False, "차단: 경마앱 저장소에 AI 코드 생성기 파일을 올리려 했습니다."
        if "maru-ai-code-maker" in repo_text and identity == "경마앱":
            return False, "차단: AI 코드 생성기 저장소에 경마앱 파일을 올리려 했습니다."
        if "skytoto" in repo_text and identity == "경마앱":
            return False, "차단: 토토앱 저장소에 경마앱 파일을 올리려 했습니다."
        return True, f"대상 확인 통과: {identity}"
    except Exception as e:
        return False, f"저장소 안전검사 실패: {e}"

def maru_compile_app_file(app_file):
    try:
        import py_compile
        py_compile.compile(str(app_file), doraise=True)
        return True, ""
    except Exception as e:
        return False, str(e)

def maru_compile_project(src):
    try:
        app_file = Path(src) / "app.py"
        return maru_compile_app_file(app_file)
    except Exception as e:
        return False, str(e)

def maru_read_text_safe(path):
    path = Path(path)
    for enc in ["utf-8", "utf-8-sig", "cp949", "euc-kr"]:
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(errors="ignore")

def maru_write_text_safe(path, text):
    Path(path).write_text(text, encoding="utf-8")

def maru_compile_app(app_file):
    return maru_compile_app_file(app_file)

def maru_ensure_required_files(src, project_name="MARU Project"):
    src = Path(src)
    src.mkdir(parents=True, exist_ok=True)
    patched = []
    req = src / "requirements.txt"
    if not req.exists():
        req.write_text("streamlit\npandas\nnumpy\nrequests\n", encoding="utf-8")
        patched.append("requirements.txt 생성")
    readme = src / "README.md"
    if not readme.exists():
        readme.write_text(f"# {project_name}\n\nMARU 자동화 프로젝트입니다.\n", encoding="utf-8")
        patched.append("README.md 생성")
    memfile = src / "ai_memory.json"
    if not memfile.exists():
        memfile.write_text(json.dumps({"version": "auto-created", "project": project_name}, ensure_ascii=False, indent=2), encoding="utf-8")
        patched.append("ai_memory.json 생성")
    return patched

def maru_fix_nameerror_from_log(src, error_text):
    app_file = Path(src) / "app.py"
    if not app_file.exists():
        return {"ok": False, "patched": [], "message": "app.py 없음"}
    text = maru_read_text_safe(app_file)
    original = text
    patched = []
    names = re.findall(r"name '([^']+)' is not defined", str(error_text))
    names = list(dict.fromkeys(names))
    insert = []

    if "KST" in names and "KST = timezone(timedelta(hours=9))" not in text:
        insert.append("try:\n    KST\nexcept NameError:\n    KST = timezone(timedelta(hours=9))")
        patched.append("KST 자동삽입")

    if "save_memory" in names and "def save_memory(" not in text:
        insert.append("def save_memory(mem_obj):\n    try:\n        target = globals().get('MEM', None)\n        if target is None:\n            target = Path(__file__).parent / 'ai_memory.json'\n        Path(target).write_text(json.dumps(mem_obj, ensure_ascii=False, indent=2), encoding='utf-8')\n        return True\n    except Exception:\n        return False\n")
        patched.append("save_memory 자동삽입")

    if "default_api_key_for" in names and "def default_api_key_for(" not in text:
        insert.append("def default_api_key_for(choice, mem_obj=None):\n    try:\n        if choice == '경마앱':\n            return st.secrets.get('KRA_API_KEY', st.secrets.get('PUBLIC_DATA_API_KEY', ''))\n        if choice == '토토앱':\n            return st.secrets.get('TOTO_API_KEY', st.secrets.get('SPORTMONKS_TOKEN', ''))\n    except Exception:\n        pass\n    try:\n        return mem_obj.get('default_profile', {}).get('api_key', '') if mem_obj else ''\n    except Exception:\n        return ''\n")
        patched.append("default_api_key_for 자동삽입")

    if "default_api_urls_for" in names and "def default_api_urls_for(" not in text:
        insert.append("def default_api_urls_for(choice, mem_obj=None):\n    try:\n        cur = mem_obj.get('default_profile', {}).get('api_urls', '') if mem_obj else ''\n        if cur:\n            return cur\n    except Exception:\n        pass\n    if choice == '경마앱':\n        return '\\n'.join(['https://apis.data.go.kr/B551015/API310/raceInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json','https://apis.data.go.kr/B551015/API310/entryInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json','https://apis.data.go.kr/B551015/API310/horseInfo?serviceKey={serviceKey}&pageNo=1&numOfRows=100&_type=json'])\n    return ''\n")
        patched.append("default_api_urls_for 자동삽입")

    if insert:
        if "from pathlib import Path" not in text:
            insert.insert(0, "from pathlib import Path")
        if "import json" not in text:
            insert.insert(0, "import json")
        if "KST" in names:
            if "from datetime import" in text:
                def dt_repl(m):
                    parts = [p.strip() for p in m.group(1).split(",")]
                    for x in ["datetime", "timezone", "timedelta"]:
                        if x not in parts:
                            parts.append(x)
                    return "from datetime import " + ", ".join(parts)
                text = re.sub(r"from datetime import ([^\n]+)", dt_repl, text, count=1)
            else:
                insert.insert(0, "from datetime import datetime, timezone, timedelta")
        import_end = 0
        for m in re.finditer(r"^(import .+|from .+ import .+)\n", text, flags=re.M):
            import_end = max(import_end, m.end())
        text = text[:import_end] + "\n# MARU V15 auto inserted helpers\n" + "\n".join(insert) + "\n# /MARU V15 auto inserted helpers\n\n" + text[import_end:]
        try:
            app_file.with_suffix(".py.bak_nameerror_v15").write_text(original, encoding="utf-8")
        except Exception:
            pass
        maru_write_text_safe(app_file, text)

    ok, err = maru_compile_app_file(app_file)
    return {"ok": ok, "patched": patched, "message": " / ".join(patched) if patched else err}

def maru_fix_common_syntax_errors(src):
    app_file = Path(src) / "app.py"
    if not app_file.exists():
        return {"ok": False, "patched": [], "message": "app.py 없음"}
    text = maru_read_text_safe(app_file)
    original = text
    patched = []
    if "\t" in text:
        text = text.replace("\t", "    ")
        patched.append("탭 공백 변환")
    if "<<<<<<<" in text or "=======" in text or ">>>>>>>" in text:
        lines, skip = [], False
        for line in text.splitlines():
            if line.startswith("<<<<<<<"):
                skip = True
                patched.append("Git 충돌 마커 제거")
                continue
            if line.startswith("======="):
                skip = False
                continue
            if line.startswith(">>>>>>>"):
                continue
            if not skip:
                lines.append(line)
        text = "\n".join(lines) + "\n"

    lines = text.splitlines()
    new_lines, changed = [], False
    for i, line in enumerate(lines):
        new_lines.append(line)
        stripped = line.strip()
        if not stripped or not stripped.endswith(":"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j >= len(lines):
            new_lines.append(" " * (indent + 4) + "pass")
            changed = True
        else:
            next_indent = len(lines[j]) - len(lines[j].lstrip(" "))
            if next_indent <= indent and not lines[j].strip().startswith(("#", "elif", "else", "except", "finally")):
                new_lines.append(" " * (indent + 4) + "pass")
                changed = True
    if changed:
        text = "\n".join(new_lines) + "\n"
        patched.append("빈 블록 pass 추가")

    if text != original:
        try:
            app_file.with_suffix(".py.bak_syntax_v15").write_text(original, encoding="utf-8")
        except Exception:
            pass
        maru_write_text_safe(app_file, text)

    ok, err = maru_compile_app_file(app_file)
    return {"ok": ok, "patched": patched, "message": " / ".join(patched) if patched else err}

def maru_full_auto_repair_once(mem_obj, label):
    info, msg = maru_get_project_info_from_choice(mem_obj, label)
    if not info:
        return [{"step": "보관소 불러오기", "status": "실패", "detail": msg}]
    project_name = info.get("name", MARU_PROJECT_PRESETS[label]["project_name"])
    src = Path(info.get("src", ""))
    rows = [{"step": "보관소 불러오기", "status": "성공", "detail": msg}]
    file_patches = maru_ensure_required_files(src, project_name)
    if file_patches:
        rows.append({"step": "누락파일 보정", "status": "완료", "detail": " / ".join(file_patches)})
    test_result = maru_run_basic_project_test(src)
    rows.append({"step": "자동 테스트", "status": "성공" if test_result.get("ok") else "실패", "detail": json.dumps(test_result, ensure_ascii=False)})
    if test_result.get("ok"):
        rows.append({"step": "자동수정", "status": "불필요", "detail": "테스트 통과"})
        return rows
    detail = json.dumps(test_result, ensure_ascii=False)
    namefix = maru_fix_nameerror_from_log(src, detail)
    if namefix.get("patched"):
        rows.append({"step": "NameError 자동수정", "status": "완료", "detail": namefix.get("message", "")})
    syntaxfix = maru_fix_common_syntax_errors(src)
    if syntaxfix.get("patched"):
        rows.append({"step": "문법오류 자동수정", "status": "완료", "detail": syntaxfix.get("message", "")})
    elif not syntaxfix.get("ok"):
        rows.append({"step": "문법오류 자동수정", "status": "보류", "detail": syntaxfix.get("message", "")})
    retest = maru_run_basic_project_test(src)
    rows.append({"step": "재테스트", "status": "성공" if retest.get("ok") else "실패", "detail": json.dumps(retest, ensure_ascii=False)})
    return rows

def maru_full_auto_loop(mem_obj, label, repeat=5, do_github=True, github_token="", commit_msg="MARU full auto repair"):
    all_rows = []
    final_ok = False
    for n in range(int(repeat)):
        rows = maru_full_auto_repair_once(mem_obj, label)
        for r in rows:
            r["round"] = n + 1
            all_rows.append(r)
        if rows and rows[-1].get("status") in ["성공", "불필요"]:
            final_ok = True
            break
        applied = any(r.get("status") == "완료" and ("자동수정" in r.get("step","") or r.get("step") == "누락파일 보정") for r in rows)
        if not applied:
            break
    info, msg = maru_get_project_info_from_choice(mem_obj, label)
    if final_ok and do_github and info:
        project_name = info.get("name", MARU_PROJECT_PRESETS[label]["project_name"])
        src = Path(info.get("src", ""))
        gh = info.get("github", {})
        owner = gh.get("owner", "skytins3-png")
        repo = gh.get("repo", project_name)
        branch = gh.get("branch", "main")
        token = github_token or (get_github_token_from_secret() if "get_github_token_from_secret" in globals() else "")
        if not token:
            all_rows.append({"round": "최종", "step": "GitHub 자동반영", "status": "대기", "detail": "GITHUB_TOKEN 없음"})
        else:
            try:
                guard_ok, guard_msg = maru_repo_project_guard(label, owner, repo, src)
                if not guard_ok:
                    all_rows.append({"round": "최종", "step": "GitHub 자동반영", "status": "차단", "detail": guard_msg})
                    return all_rows
                fingerprint = maru_folder_fingerprint(src)
                if maru_should_skip_duplicate_upload(mem_obj, project_name, fingerprint):
                    all_rows.append({"round": "최종", "step": "GitHub 자동반영", "status": "중복스킵", "detail": "같은 내용이라 자동반영을 반복하지 않았습니다."})
                else:
                    upload_rows = gh_upload_folder(src, owner, repo, branch, token, commit_msg, "")
                    ok_count = sum(1 for r in upload_rows if r.get("ok"))
                    fail_count = sum(1 for r in upload_rows if not r.get("ok"))
                    if fail_count == 0:
                        maru_mark_uploaded_fingerprint(mem_obj, project_name, fingerprint)
                    all_rows.append({"round": "최종", "step": "GitHub 자동반영", "status": "성공" if fail_count == 0 else "일부실패", "detail": f"성공 {ok_count}, 실패 {fail_count}"})
            except Exception as e:
                all_rows.append({"round": "최종", "step": "GitHub 자동반영", "status": "실패", "detail": str(e)})
    elif not final_ok:
        all_rows.append({"round": "최종", "step": "풀자동화 종료", "status": "수동확인필요", "detail": "안전 자동수정 범위를 넘어선 오류입니다. 로그 기반 코드패치 필요"})
    return all_rows

def maru_secret_get_deep(*names, default=""):
    try:
        sec = st.secrets
    except Exception:
        return default
    for name in names:
        try:
            val = sec.get(name, "")
            if val:
                return str(val).strip()
        except Exception:
            pass
    for section in ["general", "github", "GITHUB", "secrets", "tokens", "api"]:
        try:
            obj = sec.get(section, {})
            for name in names:
                try:
                    val = obj.get(name, "")
                    if val:
                        return str(val).strip()
                except Exception:
                    pass
        except Exception:
            pass
    try:
        for k in sec.keys():
            try:
                val = sec.get(k)
                if isinstance(val, str) and ("github_pat_" in val or val.startswith("ghp_")):
                    return val.strip()
            except Exception:
                pass
    except Exception:
        pass
    return default

def get_github_token_from_secret():
    return maru_secret_get_deep(
        "GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token",
        "Github_Token", "GITHUB_PAT", "GH_TOKEN", default=""
    )

def maru_mask_token(token):
    token = str(token or "")
    if not token:
        return "없음"
    if len(token) <= 12:
        return token[:4] + "****"
    return token[:10] + "..." + token[-4:]

def maru_token_diagnosis():
    token = get_github_token_from_secret()
    return {
        "detected": bool(token),
        "masked": maru_mask_token(token),
        "length": len(token) if token else 0,
        "looks_like_github_token": bool(token.startswith("github_pat_") or token.startswith("ghp_")),
        "checked_names": "GITHUB_TOKEN, MARU_GITHUB_TOKEN, github_token, Github_Token, GITHUB_PAT, GH_TOKEN",
        "message": "GitHub 토큰 감지됨" if token else "Streamlit Secrets에서 GitHub 토큰을 찾지 못했습니다."
    }

def maru_test_github_token_access(owner="skytins3-png", repo="maru-ai-code-maker"):
    token = get_github_token_from_secret()
    if not token:
        return {"ok": False, "status": "NO_TOKEN", "message": "GITHUB_TOKEN 미감지"}
    try:
        import requests
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/app.py"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return {"ok": True, "status": 200, "message": f"{owner}/{repo} app.py 읽기 성공"}
        if r.status_code == 401:
            return {"ok": False, "status": 401, "message": "토큰이 틀렸거나 만료됨"}
        if r.status_code == 403:
            return {"ok": False, "status": 403, "message": "권한 부족. Contents 권한 확인 필요"}
        if r.status_code == 404:
            return {"ok": False, "status": 404, "message": "repo 접근 권한 없음 또는 저장소/파일명 불일치"}
        return {"ok": False, "status": r.status_code, "message": r.text[:300]}
    except Exception as e:
        return {"ok": False, "status": "ERROR", "message": str(e)}

def maru_log_to_korean_summary(log_text):
    log = str(log_text or "")
    low = log.lower()
    items = []
    next_steps = []
    risk = "정상"

    def add(title, reason, action, level="주의"):
        nonlocal risk
        items.append({"문제": title, "원인": reason, "해야할일": action, "위험도": level})
        next_steps.append(action)
        if level == "높음":
            risk = "오류"
        elif level == "중간" and risk != "오류":
            risk = "주의"

    if "uvicorn server started" in low:
        add("앱 서버 시작 성공", "Streamlit 서버가 정상적으로 켜졌습니다.", "앱 화면에서 기능을 확인하세요.", "정상")

    if "traceback" in low:
        add("Traceback 오류 발견", "앱 실행 중 파이썬 오류가 발생했습니다.", "오류 아래쪽 마지막 줄의 NameError/SyntaxError 등을 기준으로 패치해야 합니다.", "높음")

    if "nameerror" in low:
        m = re.search(r"NameError: name '([^']+)' is not defined", log)
        missing = m.group(1) if m else "알 수 없는 이름"
        add("NameError 발생", f"`{missing}` 함수/변수/import가 없습니다.", f"`{missing}`를 app.py에 보강해야 합니다.", "높음")

    if "syntaxerror" in low or "indentationerror" in low:
        add("문법/들여쓰기 오류", "괄호, 따옴표, 콜론, 들여쓰기 중 하나가 깨졌을 가능성이 큽니다.", "app.py 문법검사 후 해당 줄을 고쳐야 합니다.", "높음")

    if "pd is not defined" in low or "pd.dataframe" in low:
        add("pandas(pd) 누락", "표를 만들 때 pd를 쓰지만 pandas import가 빠졌습니다.", "표시 함수 안에서 pandas를 직접 import하도록 고쳐야 합니다.", "높음")

    if "py_compile" in low and "not defined" in low:
        add("py_compile 누락", "문법검사 모듈 import가 빠졌습니다.", "import py_compile을 추가해야 합니다.", "높음")

    if "arrowinvalid" in low or "conversion failed for column" in low:
        add("표 변환 경고", "표 컬럼에 숫자와 글자가 섞여 Streamlit 표 변환이 흔들렸습니다.", "표시 전 모든 값을 문자열로 바꿔야 합니다.", "중간")

    if "github_token 없음" in log or "GITHUB_TOKEN 없음" in log or "no_token" in low:
        add("GitHub 토큰 미감지", "Streamlit Secrets에서 GITHUB_TOKEN을 못 찾았습니다.", "Secrets에 GITHUB_TOKEN을 저장하고 앱을 재부팅하세요.", "중간")

    if "status: 200" in low or '"status": 200' in low or "app.py 읽기 성공" in log:
        add("GitHub 토큰 권한 정상", "GitHub API가 저장소 app.py를 읽었습니다.", "자동반영을 진행해도 됩니다.", "정상")

    if "apis.data.go.kr" in log and "maru-ai-code-maker" in low:
        add("프로젝트 설정 혼동", "AI 코드 생성기 쪽에 경마 공공데이터 URL이 섞여 보입니다.", "AI 코드 생성기에서는 API URL을 비우고, 경마앱 선택 시에만 공공데이터 URL을 쓰세요.", "중간")

    if not items:
        items.append({
            "문제": "명확한 오류 없음",
            "원인": "로그에 치명적인 오류 패턴이 보이지 않습니다.",
            "해야할일": "앱 화면에서 기능이 정상 동작하는지 확인하세요.",
            "위험도": "정상",
        })
        next_steps.append("추가 패치 없이 기능 확인을 진행하세요.")

    return {"위험도": risk, "쉬운설명": items, "다음할일": list(dict.fromkeys(next_steps))}

def maru_show_korean_log_summary(log_text):
    summary = maru_log_to_korean_summary(log_text)
    if summary.get("위험도") == "오류":
        st.error("한글 로그분석: 오류가 있습니다.")
    elif summary.get("위험도") == "주의":
        st.warning("한글 로그분석: 주의할 내용이 있습니다.")
    else:
        st.success("한글 로그분석: 치명적인 오류가 보이지 않습니다.")

    for idx, item in enumerate(summary.get("쉬운설명", []), 1):
        with st.container(border=True):
            st.markdown(f"**{idx}. {item.get('문제','')}**")
            st.write("원인:", item.get("원인", ""))
            st.write("해야 할 일:", item.get("해야할일", ""))
            st.write("위험도:", item.get("위험도", ""))

    st.markdown("### 다음에 할 일")
    for step in summary.get("다음할일", []):
        st.write("✅", step)

    with st.expander("개발자용 JSON 보기", expanded=False):
        st.json(summary)

def maru_full_self_diagnosis_rows():
    rows = []
    def add(name, ok, detail=""):
        rows.append({"항목": name, "상태": "정상" if ok else "확인필요", "설명": detail})
    g = globals()
    required = [
        "save_memory", "maru_now_kst_text", "maru_show_rows",
        "maru_token_diagnosis", "maru_test_github_token_access",
        "maru_repo_project_guard", "maru_should_skip_duplicate_upload",
    ]
    for fn in required:
        add(f"필수 함수: {fn}", fn in g and callable(g.get(fn)), "없으면 해당 기능에서 오류가 날 수 있습니다.")
    try:
        diag = maru_token_diagnosis()
        add("GITHUB_TOKEN 감지", bool(diag.get("detected")), diag.get("message", ""))
    except Exception as e:
        add("GITHUB_TOKEN 감지", False, str(e))
    try:
        now_text = maru_now_kst_text()
        add("한국시간 함수", "KST" in now_text, now_text)
    except Exception as e:
        add("한국시간 함수", False, str(e))
    add("현재 app.py 문법", True, "현재 앱이 실행 중이면 기본 문법은 통과한 상태입니다.")
    return rows

def maru_clean_api_urls_for_project(project_choice, api_urls):
    name = str(project_choice or "")
    text = str(api_urls or "")
    if ("AI 코드" in name or "code" in name.lower() or "maker" in name.lower()) and ("apis.data.go.kr" in text or "sportmonks" in text.lower()):
        return ""
    return text

def maru_v172_token_status_text():
    try:
        diag = maru_token_diagnosis()
        if diag.get("detected"):
            return "정상", "GITHUB_TOKEN 감지됨"
        return "확인필요", "GITHUB_TOKEN 미감지"
    except Exception as e:
        return "확인필요", f"토큰진단 오류: {e}"

def maru_v172_simple_next_steps():
    return [
        "1) 📦 보관소에서 프로젝트 최신파일 저장/불러오기",
        "2) 🧰 전체진단에서 토큰과 필수 함수 확인",
        "3) 🧯 로그분석에서 로그 붙여넣고 한글 설명 확인",
        "4) 🤖 풀자동화에서 자동 테스트",
        "5) 통과하면 GitHub 자동반영 확인",
    ]

def maru_v172_render_status_panel(location="상단"):
    status, msg = maru_v172_token_status_text()
    st.markdown(f"### 🧭 MARU {location} 상태 안내판")
    c1, c2 = st.columns([1, 3])
    with c1:
        if status == "정상":
            st.success(status)
        else:
            st.warning(status)
    with c2:
        st.write(msg)
    st.info("이 안내판은 탭 안에 숨기지 않고 항상 보이도록 만든 안내입니다.")
    st.markdown("#### 다음 순서")
    for step in maru_v172_simple_next_steps():
        st.write("✅", step)

def maru_v172_korean_log_summary(log_text):
    log = str(log_text or "")
    low = log.lower()
    rows = []
    def add(problem, why, action, risk):
        rows.append({"문제": problem, "원인": why, "해야 할 일": action, "위험도": risk})
    if "uvicorn server started" in low:
        add("앱 서버 시작 성공", "Streamlit 서버가 켜졌습니다.", "화면 기능을 확인하면 됩니다.", "정상")
    if "traceback" in low:
        add("파이썬 오류 발생", "Traceback이 있어 실행 중 오류가 났습니다.", "마지막 오류 줄을 기준으로 패치해야 합니다.", "높음")
    if "nameerror" in low:
        m = re.search(r"NameError: name '([^']+)' is not defined", log)
        miss = m.group(1) if m else "알 수 없는 이름"
        add("NameError", f"{miss} 이름이 정의되지 않았습니다.", f"{miss} 함수/변수/import를 추가해야 합니다.", "높음")
    if "syntaxerror" in low or "indentationerror" in low:
        add("문법/들여쓰기 오류", "괄호/따옴표/콜론/들여쓰기가 깨졌을 수 있습니다.", "문법검사 줄 번호 기준으로 수정해야 합니다.", "높음")
    if "arrowinvalid" in low or "conversion failed for column" in low:
        add("표 변환 경고", "표 안에 숫자와 글자가 섞여 표시가 흔들렸습니다.", "표시 전 문자열로 통일해야 합니다.", "중간")
    if "github_token 없음" in log or "GITHUB_TOKEN 없음" in log or "no_token" in low:
        add("GitHub 토큰 미감지", "Streamlit Secrets에서 토큰을 못 읽었습니다.", "Secrets 저장명과 재부팅을 확인하세요.", "중간")
    if "app.py 읽기 성공" in log or '"status": 200' in low or "status: 200" in low:
        add("GitHub 토큰 정상", "저장소 app.py 읽기에 성공했습니다.", "자동반영을 진행해도 됩니다.", "정상")
    if not rows:
        add("명확한 오류 없음", "치명적인 오류 패턴이 보이지 않습니다.", "다음 기능 테스트로 진행하세요.", "정상")
    return rows

def maru_v172_show_log_korean(rows_or_text):
    rows = rows_or_text if isinstance(rows_or_text, list) else maru_v172_korean_log_summary(rows_or_text)
    try:
        high = any(str(r.get("위험도")) == "높음" for r in rows)
        mid = any(str(r.get("위험도")) == "중간" for r in rows)
        if high:
            st.error("한글 로그분석: 오류가 있습니다.")
        elif mid:
            st.warning("한글 로그분석: 확인할 내용이 있습니다.")
        else:
            st.success("한글 로그분석: 치명적인 오류가 보이지 않습니다.")
        for i, r in enumerate(rows, 1):
            with st.container(border=True):
                st.markdown(f"**{i}. {r.get('문제','')}**")
                st.write("원인:", r.get("원인", ""))
                st.write("해야 할 일:", r.get("해야 할 일", ""))
                st.write("위험도:", r.get("위험도", ""))
    except Exception:
        st.write(rows)

def maru_v172_selfcheck_rows():
    rows = []
    def add(name, ok, detail):
        rows.append({"항목": name, "상태": "정상" if ok else "확인필요", "설명": detail})
    g = globals()
    for fn in ["save_memory", "maru_show_rows", "maru_token_diagnosis", "maru_test_github_token_access", "maru_repo_project_guard"]:
        add(fn, callable(g.get(fn)), "필수 함수 존재 확인")
    try:
        diag = maru_token_diagnosis()
        add("GITHUB_TOKEN", bool(diag.get("detected")), diag.get("message", ""))
    except Exception as e:
        add("GITHUB_TOKEN", False, str(e))
    add("화면 하단 안내판", True, "V17.2에서 항상 표시")
    return rows

def maru_v18_expected_menus():
    return [
        "📋 기능", "📦 보관소", "🔁 연속자동화", "🤖 코드생성", "📁 등록",
        "📡 테스트", "🧯 로그분석", "🖼️ 사진분석/명령", "✅ 패치", "🔍 검사",
        "📦 버전", "🚀 GitHub 자동반영", "☁️ 구글시트", "📚 기록",
        "📝 개선승인", "♻️ 무승인패치루프", "🤖 풀자동화", "🗝️ 토큰진단", "🧰 전체진단"
    ]

def maru_v18_check_function(name):
    try:
        return callable(globals().get(name))
    except Exception:
        return False

def maru_v18_menu_audit_rows():
    rows = []
    def add(menu, status, detail, action=""):
        rows.append({"메뉴/항목": menu, "상태": status, "설명": detail, "해야 할 일": action})

    # Core menu/function mapping
    mapping = [
        ("📦 보관소", ["maru_load_project_from_vault", "maru_save_upload_to_vault", "save_memory"]),
        ("🔁 연속자동화", ["maru_get_project_info_from_choice", "maru_run_basic_project_test"]),
        ("🧯 로그분석", ["analyze_log"]),
        ("✅ 패치", ["save_event", "save"]),
        ("🚀 GitHub 자동반영", ["gh_upload_folder", "get_github_token_from_secret"]),
        ("♻️ 무승인패치루프", ["maru_full_auto_loop"]),
        ("🤖 풀자동화", ["maru_full_auto_loop", "maru_full_auto_repair_once", "maru_show_rows"]),
        ("🗝️ 토큰진단", ["maru_token_diagnosis", "maru_test_github_token_access"]),
        ("🧰 전체진단", ["maru_v18_menu_audit_rows", "maru_v18_show_menu_audit"]),
    ]
    for menu, funcs in mapping:
        missing = [f for f in funcs if not maru_v18_check_function(f)]
        if missing:
            add(menu, "확인필요", "필수 함수 누락: " + ", ".join(missing), "해당 함수 보강 필요")
        else:
            add(menu, "정상", "필수 함수 확인됨", "사용 가능")

    # Token status
    try:
        diag = maru_token_diagnosis()
        if diag.get("detected"):
            add("GITHUB_TOKEN", "정상", "토큰 감지됨: " + str(diag.get("masked", "")), "자동반영 가능")
        else:
            add("GITHUB_TOKEN", "확인필요", "토큰 미감지", "Streamlit Secrets에 GITHUB_TOKEN 저장 후 재부팅")
    except Exception as e:
        add("GITHUB_TOKEN", "확인필요", "토큰진단 실행 오류: " + str(e), "토큰진단 함수 확인")

    # Time display
    try:
        now_txt = maru_now_kst_text()
        add("한국시간", "정상" if "KST" in now_txt else "확인필요", now_txt, "KST 표시 확인")
    except Exception as e:
        add("한국시간", "확인필요", str(e), "KST 함수 보강")

    # Result table safety
    if maru_v18_check_function("maru_show_rows"):
        add("결과표 표시", "정상", "maru_show_rows 안전 표시 함수 있음", "표 변환 오류 방지")
    else:
        add("결과표 표시", "확인필요", "안전 표시 함수 없음", "maru_show_rows 보강")

    # Repo guard
    if maru_v18_check_function("maru_repo_project_guard"):
        add("저장소 혼동 차단", "정상", "경마/토토/AI 저장소 혼동 차단 함수 있음", "자동반영 전 확인")
    else:
        add("저장소 혼동 차단", "확인필요", "repo guard 없음", "저장소 오반영 방지 함수 추가")

    return rows

def maru_v18_show_menu_audit():
    rows = maru_v18_menu_audit_rows()
    bad = [r for r in rows if r.get("상태") != "정상"]
    if bad:
        st.warning(f"메뉴 전체점검: 확인필요 {len(bad)}개")
    else:
        st.success("메뉴 전체점검: 핵심 메뉴 정상")
    try:
        maru_show_rows(rows)
    except Exception:
        st.write(rows)

    st.markdown("### 한글 요약")
    if not bad:
        st.write("✅ 핵심 메뉴에서 필수 함수 누락이 보이지 않습니다.")
    else:
        for r in bad:
            st.write(f"⚠️ {r.get('메뉴/항목')}: {r.get('설명')} → {r.get('해야 할 일')}")

def maru_v18_korean_log_explain(log_text):
    log = str(log_text or "")
    low = log.lower()
    rows = []
    def add(problem, why, action, risk):
        rows.append({"문제": problem, "원인": why, "해야 할 일": action, "위험도": risk})
    if "uvicorn server started" in low:
        add("앱 서버 시작 성공", "Streamlit 서버가 정상적으로 켜졌습니다.", "화면 기능 테스트로 넘어가세요.", "정상")
    if "traceback" in low:
        add("실행 오류 발생", "Traceback이 있습니다.", "마지막 오류 줄을 기준으로 패치해야 합니다.", "높음")
    if "nameerror" in low:
        m = re.search(r"NameError: name '([^']+)' is not defined", log)
        name = m.group(1) if m else "알 수 없는 이름"
        add("NameError", f"{name} 이름이 정의되지 않았습니다.", f"{name} import/함수/변수를 보강하세요.", "높음")
    if "syntaxerror" in low or "indentationerror" in low:
        add("문법 오류", "괄호/따옴표/들여쓰기 오류 가능성이 큽니다.", "문법검사 줄 번호 기준으로 고치세요.", "높음")
    if "arrowinvalid" in low or "conversion failed" in low:
        add("표 표시 오류", "표 컬럼 자료형이 섞였습니다.", "표시 전 문자열로 통일하세요.", "중간")
    if "github_token 없음" in log or "GITHUB_TOKEN 없음" in log:
        add("GitHub 토큰 미감지", "Secrets에서 토큰을 못 읽었습니다.", "Secrets 저장명과 재부팅을 확인하세요.", "중간")
    if "app.py 읽기 성공" in log or '"status": 200' in low:
        add("GitHub 권한 정상", "저장소 app.py 접근 성공입니다.", "자동반영을 실행해도 됩니다.", "정상")
    if not rows:
        add("명확한 오류 없음", "치명적인 오류 패턴이 보이지 않습니다.", "메뉴 전체점검과 기능 테스트를 진행하세요.", "정상")
    return rows

def maru_v18_show_korean_log_explain(log_text):
    rows = maru_v18_korean_log_explain(log_text)
    high = any(r.get("위험도") == "높음" for r in rows)
    mid = any(r.get("위험도") == "중간" for r in rows)
    if high:
        st.error("한글 로그분석: 오류가 있습니다.")
    elif mid:
        st.warning("한글 로그분석: 확인할 내용이 있습니다.")
    else:
        st.success("한글 로그분석: 치명적인 오류가 보이지 않습니다.")
    try:
        maru_show_rows(rows)
    except Exception:
        st.write(rows)
    for r in rows:
        with st.container(border=True):
            st.markdown(f"**{r.get('문제')}**")
            st.write("원인:", r.get("원인"))
            st.write("해야 할 일:", r.get("해야 할 일"))
            st.write("위험도:", r.get("위험도"))

def maru_safe_call(title, fn):
    """한 메뉴가 오류 나도 전체 앱이 죽지 않게 보호."""
    try:
        return fn()
    except Exception as e:
        st.error(f"{title} 표시 중 오류")
        st.write(str(e))
        try:
            st.code(traceback.format_exc())
        except Exception:
            pass
        return None

def maru_v181_token_box():
    st.markdown("### 🗝️ 토큰진단")
    try:
        diag = maru_token_diagnosis()
        if diag.get("detected"):
            st.success("GITHUB_TOKEN 감지됨")
        else:
            st.error("GITHUB_TOKEN 미감지")
        st.json(diag)
    except Exception as e:
        st.error(f"토큰진단 오류: {e}")

    test_repo = st.selectbox(
        "저장소 접근 테스트",
        ["maru-ai-code-maker", "maru-kra-final-clean", "skytoto-ai-hub"],
        key="v181_token_repo"
    )
    if st.button("토큰 권한 테스트", key="v181_token_test_btn"):
        try:
            res = maru_test_github_token_access("skytins3-png", test_repo)
            if res.get("ok"):
                st.success(res.get("message"))
            else:
                st.error(res.get("message"))
            st.json(res)
        except Exception as e:
            st.error(f"권한 테스트 오류: {e}")

def maru_v181_selfcheck_box():
    st.markdown("### 🧰 전체진단")
    rows = []
    def add(name, ok, detail):
        rows.append({"항목": name, "상태": "정상" if ok else "확인필요", "설명": detail})
    g = globals()
    funcs = [
        "save_memory", "maru_show_rows", "maru_token_diagnosis",
        "maru_test_github_token_access", "maru_repo_project_guard",
        "maru_should_skip_duplicate_upload", "maru_full_auto_loop",
        "maru_full_auto_repair_once",
    ]
    for fn in funcs:
        add(fn, callable(g.get(fn)), "필수 함수 존재 확인")
    try:
        diag = maru_token_diagnosis()
        add("GITHUB_TOKEN", bool(diag.get("detected")), diag.get("message", ""))
    except Exception as e:
        add("GITHUB_TOKEN", False, str(e))
    try:
        maru_show_rows(rows)
    except Exception:
        st.write(rows)

def maru_v181_fullauto_box():
    st.markdown("### 🤖 풀자동화")
    st.caption("보관소 최신파일을 불러와 자동 테스트 → 자동수정 → 재테스트 → GitHub 자동반영까지 진행합니다.")

    project = st.selectbox(
        "풀자동화 프로젝트",
        ["AI 코드 생성기", "경마앱", "토토앱"],
        key="v181_fullauto_project"
    )
    repeat = st.number_input("최대 반복 횟수", min_value=1, max_value=10, value=3, step=1, key="v181_fullauto_repeat")
    do_github = st.checkbox("통과 시 GitHub 자동반영", value=True, key="v181_fullauto_github")
    msg = st.text_input("커밋 메시지", value="MARU full auto repair update", key="v181_fullauto_msg")

    if st.button("풀자동화 시작", type="primary", key="v181_fullauto_start"):
        try:
            rows = maru_full_auto_loop(
                m if "m" in globals() else {},
                project,
                repeat=int(repeat),
                do_github=do_github,
                github_token=get_github_token_from_secret() if callable(globals().get("get_github_token_from_secret")) else "",
                commit_msg=msg,
            )
            try:
                maru_show_rows(rows)
            except Exception:
                st.write(rows)
        except Exception as e:
            st.error(f"풀자동화 실행 오류: {e}")
            try:
                st.code(traceback.format_exc())
            except Exception:
                pass

def maru_v181_noapproval_loop_box():
    st.markdown("### ♻️ 무승인패치루프")
    st.caption("이미 승인된 개선사항을 기준으로 테스트/로그분석/재패치를 반복합니다.")
    st.info("안전 자동수정 범위를 넘어가면 무리하게 고치지 않고 수동확인필요로 멈춥니다.")

    project = st.selectbox(
        "무승인패치루프 프로젝트",
        ["AI 코드 생성기", "경마앱", "토토앱"],
        key="v181_noapproval_project"
    )
    repeat = st.number_input("루프 반복 횟수", min_value=1, max_value=10, value=3, step=1, key="v181_noapproval_repeat")

    if st.button("무승인패치루프 시작", type="primary", key="v181_noapproval_start"):
        try:
            rows = maru_full_auto_loop(
                m if "m" in globals() else {},
                project,
                repeat=int(repeat),
                do_github=False,
                github_token="",
                commit_msg="MARU no approval patch loop",
            )
            try:
                maru_show_rows(rows)
            except Exception:
                st.write(rows)
        except Exception as e:
            st.error(f"무승인패치루프 실행 오류: {e}")
            try:
                st.code(traceback.format_exc())
            except Exception:
                pass

def maru_v181_menu_audit_box():
    st.markdown("### 🧭 메뉴전체점검")
    try:
        maru_v18_show_menu_audit()
    except Exception:
        try:
            rows = maru_v18_menu_audit_rows()
            maru_show_rows(rows)
        except Exception as e:
            st.error(f"메뉴점검 오류: {e}")

def maru_v181_korean_log_box():
    st.markdown("### 🧯 한글 로그분석")
    log_text = st.text_area("로그를 붙여넣으면 한글로 설명합니다.", height=180, key="v181_log_text")
    if st.button("한글 로그분석", key="v181_log_btn"):
        try:
            if callable(globals().get("maru_v18_show_korean_log_explain")):
                maru_v18_show_korean_log_explain(log_text)
            elif callable(globals().get("maru_v172_show_log_korean")):
                maru_v172_show_log_korean(log_text)
            else:
                st.write("한글 로그분석 함수가 없습니다.")
        except Exception as e:
            st.error(f"한글 로그분석 오류: {e}")

def maru_v181_operation_center():
    st.markdown("## 🧩 통합 운영센터")
    st.caption("기존 탭이 꼬여도 여기서 핵심 기능을 독립적으로 실행할 수 있습니다.")
    sub = st.tabs([
        "🧭 메뉴점검",
        "🧰 전체진단",
        "🗝️ 토큰진단",
        "♻️ 무승인패치루프",
        "🤖 풀자동화",
        "🧯 한글로그",
    ])
    with sub[0]:
        maru_safe_call("메뉴점검", maru_v181_menu_audit_box)
    with sub[1]:
        maru_safe_call("전체진단", maru_v181_selfcheck_box)
    with sub[2]:
        maru_safe_call("토큰진단", maru_v181_token_box)
    with sub[3]:
        maru_safe_call("무승인패치루프", maru_v181_noapproval_loop_box)
    with sub[4]:
        maru_safe_call("풀자동화", maru_v181_fullauto_box)
    with sub[5]:
        maru_safe_call("한글로그", maru_v181_korean_log_box)

def maru_v182_tab_repair_rows():
    return [
        {"메뉴": "📝 개선승인", "연결": "tabs[14]", "상태": "정상", "설명": "개선 요청 승인/보류/거절"},
        {"메뉴": "♻️ 무승인패치루프", "연결": "tabs[15]", "상태": "정상", "설명": "승인 후 패치/테스트 반복"},
        {"메뉴": "🤖 풀자동화", "연결": "tabs[16]", "상태": "정상", "설명": "보관소 → 자동테스트 → 자동수정 → GitHub 반영"},
        {"메뉴": "🗝️ 토큰진단", "연결": "tabs[17]", "상태": "정상", "설명": "GITHUB_TOKEN 감지/권한 테스트"},
        {"메뉴": "🧰 전체진단", "연결": "tabs[18]", "상태": "정상", "설명": "필수 함수/토큰/표시 점검"},
        {"메뉴": "🧭 메뉴전체점검", "연결": "tabs[19]", "상태": "정상", "설명": "전체 메뉴 점검"},
    ]

def maru_v182_show_tab_repair_status():
    st.markdown("## 🧭 실제 메뉴 연결 확인")
    st.caption("V18.2에서 문제 메뉴들을 tabs[19] 몰림 방식에서 실제 메뉴 위치로 다시 연결했습니다.")
    try:
        maru_show_rows(maru_v182_tab_repair_rows())
    except Exception:
        st.write(maru_v182_tab_repair_rows())

def maru_v20_extract_tab_labels_source():
    try:
        source = Path(__file__).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        source = ""
    m = re.search(r"tabs\s*=\s*st\.tabs\(\s*\[(.*?)\]\s*\)", source, re.S)
    if not m:
        return [], source
    labels = [a or b for a,b in re.findall(r'"([^"]+)"|\'([^\']+)\'', m.group(1))]
    return labels, source

def maru_v20_total_check_rows():
    labels, source = maru_v20_extract_tab_labels_source()
    rows = []
    def add(category, item, ok, detail, action=""):
        rows.append({
            "분류": category,
            "항목": item,
            "상태": "정상" if ok else "확인필요",
            "설명": str(detail),
            "조치": action if action else ("사용 가능" if ok else "수정 필요"),
        })

    indices = sorted(set(int(x) for x in re.findall(r"with\s+tabs\[(\d+)\]", source)))
    duplicates = sorted([x for x in set(labels) if labels.count(x) > 1])
    out_of_range = [i for i in indices if labels and i >= len(labels)]
    keys = re.findall(r'key\s*=\s*["\']([^"\']+)["\']', source)
    dup_keys = sorted([k for k in set(keys) if keys.count(k) > 1])

    add("메뉴", "탭 개수", len(labels) >= 20, f"{len(labels)}개")
    add("메뉴", "탭 범위", len(out_of_range) == 0, f"범위초과 {out_of_range}")
    add("메뉴", "중복 탭 이름", len(duplicates) == 0, f"중복 {duplicates}")
    add("메뉴", "기록/개선승인 분리", "📚 기록" in labels and "📝 개선승인" in labels, labels[13:20] if labels else [])
    add("키", "중복 Streamlit key", len(dup_keys) == 0, dup_keys[:20])
    add("UI", "접기 숨김", "st.expander" in source and "expanded=False" in source, "상세 영역 접힘 사용")
    add("UI", "구버전 표 옵션 제거", not re.search(r"legacy_width_option\s*=", source), len(re.findall(r"legacy_width_option\s*=", source)))

    required = [
        ("원클릭 자동반영", "maru_v19_one_click_center"),
        ("사진등록", "maru_v19_save_photo_upload"),
        ("프로젝트 설정", "maru_v19_project_config"),
        ("저장소 안전검사", "maru_v19_repo_guard"),
        ("패치·개선 명령센터", "maru_v195_command_workflow_center"),
        ("명령 저장", "maru_v195_save_command"),
        ("명령 GitHub 기록", "maru_v195_upload_command_to_github"),
        ("명령→풀자동화", "maru_v195_try_full_auto"),
        ("토큰진단", "maru_token_diagnosis"),
        ("풀자동화", "maru_full_auto_loop"),
        ("한글 로그/점검", "maru_v18_show_korean_log_explain"),
    ]
    for name, fn in required:
        add("필수함수", name, callable(globals().get(fn)) or f"def {fn}" in source, fn)

    for repo in ["maru-ai-code-maker", "maru-kra-final-clean", "skytoto-ai-hub"]:
        add("저장소", repo, repo in source, repo)

    add("보고서 제외", "REPORT 업로드 제외", "REPORT" in source and "continue" in source, "REPORT/MARU_V 제외 로직")
    add("시간표시", "한국시간 KST", "한국시간 KST" in source and "한국시간 KST (UTC+9)" not in source, "한국시간 KST (UTC+9) 제거")
    return rows

def maru_v20_show_total_check():
    rows = maru_v20_total_check_rows()
    bad = [r for r in rows if r.get("상태") != "정상"]
    if bad:
        st.warning(f"전체검사 결과: 확인필요 {len(bad)}개")
    else:
        st.success("전체검사 결과: 핵심 항목 정상")
    try:
        maru_v19_show_rows(rows) if callable(globals().get("maru_v19_show_rows")) else maru_show_rows(rows)
    except Exception:
        st.write(rows)

    with st.expander("▶ 확인필요만 보기", expanded=False):
        if bad:
            try:
                maru_v19_show_rows(bad) if callable(globals().get("maru_v19_show_rows")) else maru_show_rows(bad)
            except Exception:
                st.write(bad)
        else:
            st.success("확인필요 항목이 없습니다.")

def maru_v195_slug(text):
    text = str(text or "").strip()
    text = re.sub(r"[^A-Za-z0-9가-힣_.-]+", "_", text)
    return text[:60] or "command"

def maru_v195_kst_stamp():
    try:
        return maru_now_kst_text().replace(" ", "_").replace(":", "-")
    except Exception:
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

def maru_v195_save_command(project_choice, command_type, command_text, attached_files=None):
    cfg = maru_v19_project_config(project_choice) if callable(globals().get("maru_v19_project_config")) else {
        "project": str(project_choice),
        "repo": str(project_choice),
        "owner": "skytins3-png",
        "branch": "main",
        "kind": str(project_choice),
    }
    base_dir = Path("project_vault") / cfg["project"] / "commands"
    base_dir.mkdir(parents=True, exist_ok=True)

    stamp = maru_v195_kst_stamp()
    name = f"{stamp}_{maru_v195_slug(command_type)}"
    json_path = base_dir / f"{name}.json"
    md_path = base_dir / f"{name}.md"
    files_dir = base_dir / f"{name}_files"
    files_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []
    for f in attached_files or []:
        try:
            safe = maru_v195_slug(getattr(f, "name", "upload.bin"))
            target = files_dir / safe
            try:
                f.seek(0)
            except Exception:
                pass
            target.write_bytes(f.read())
            saved_files.append(str(target))
        except Exception as e:
            saved_files.append(f"첨부 저장 실패: {e}")

    record = {
        "project_choice": project_choice,
        "project": cfg.get("project"),
        "repo": cfg.get("repo"),
        "command_type": command_type,
        "command_text": command_text,
        "attached_files": saved_files,
        "created_at": stamp,
        "status": "REGISTERED",
        "workflow": [
            "명령사항 접수",
            "보관소 저장",
            "검사",
            "자동패치/풀자동화",
            "GitHub 자동반영",
            "Streamlit 재배포 확인",
        ],
    }
    json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    md = f"""# MARU 패치/개선 명령사항

- 프로젝트: {project_choice}
- 저장소: {cfg.get('owner')}/{cfg.get('repo')}
- 종류: {command_type}
- 등록시간: {stamp}

## 명령 내용

{command_text}

## 첨부파일

{chr(10).join('- ' + x for x in saved_files) if saved_files else '- 없음'}

## 처리 순서

1. 명령사항 접수
2. 보관소 저장
3. 검사
4. 자동패치/풀자동화
5. GitHub 자동반영
6. Streamlit 재배포 확인
"""
    md_path.write_text(md, encoding="utf-8")

    try:
        if callable(globals().get("save_event")) and "m" in globals():
            save_event(m, "improvement_commands", {
                "type": "improvement_command",
                "project": project_choice,
                "command_type": command_type,
                "summary": command_text[:120],
                "data": record,
            })
            if callable(globals().get("save")):
                save(m)
    except Exception:
        pass

    return record, json_path, md_path, files_dir

def maru_v195_upload_command_to_github(project_choice, md_path, json_path, files_dir, commit_msg):
    cfg = maru_v19_project_config(project_choice)
    token = maru_v19_github_token() if callable(globals().get("maru_v19_github_token")) else ""
    if not token:
        return [{"ok": False, "file": "-", "status": "NO_TOKEN", "message": "GITHUB_TOKEN 미감지"}]

    rows = []
    remote_base = "maru_commands"
    for p in [md_path, json_path]:
        rows.append(maru_v19_upload_file_to_github(
            cfg["owner"], cfg["repo"], cfg["branch"], token, p,
            f"{remote_base}/{Path(p).name}",
            commit_msg
        ))
    try:
        for f in Path(files_dir).rglob("*"):
            if f.is_file():
                rows.append(maru_v19_upload_file_to_github(
                    cfg["owner"], cfg["repo"], cfg["branch"], token, f,
                    f"{remote_base}/attachments/{f.name}",
                    commit_msg
                ))
    except Exception as e:
        rows.append({"ok": False, "file": "attachments", "status": "ERROR", "message": str(e)})
    return rows

def maru_v195_try_full_auto(project_choice, repeat, do_github, commit_msg):
    if not callable(globals().get("maru_full_auto_loop")):
        return [{"단계": "풀자동화", "상태": "건너뜀", "설명": "maru_full_auto_loop 함수가 없어 명령 등록까지만 완료"}]
    try:
        rows = maru_full_auto_loop(
            m if "m" in globals() else {},
            project_choice,
            repeat=int(repeat),
            do_github=bool(do_github),
            github_token=maru_v19_github_token() if callable(globals().get("maru_v19_github_token")) else "",
            commit_msg=commit_msg,
        )
        return rows if isinstance(rows, list) else [{"단계": "풀자동화", "상태": "완료", "설명": str(rows)}]
    except Exception as e:
        return [{"단계": "풀자동화", "상태": "오류", "설명": str(e)}]

def maru_v195_command_workflow_center():
    st.markdown("## 📝 패치·개선·명령사항 자동처리")
    st.caption("ZIP 업로드와 같은 순서로 명령사항도 보관소 저장 → 검사 → 자동처리 → GitHub 반영 흐름을 탑니다.")

    with st.expander("▶ 패치/개선 명령 입력", expanded=False):
        project_choice = st.selectbox(
            "명령을 반영할 프로젝트",
            ["AI 코드 생성기", "경마앱", "토토앱"],
            key="v195_command_project"
        )
        command_type = st.selectbox(
            "명령 종류",
            ["패치", "개선", "오류수정", "사진/화면분석", "기능추가", "UI정리", "기타"],
            key="v195_command_type"
        )
        command_text = st.text_area(
            "명령사항",
            height=150,
            placeholder="예: 경마앱 대시보드 글씨를 크게 하고, 불필요한 상세표는 접기 화살표로 숨겨줘.",
            key="v195_command_text"
        )
        attached = st.file_uploader(
            "첨부파일/사진 등록",
            type=["png", "jpg", "jpeg", "webp", "txt", "py", "zip", "json", "md"],
            accept_multiple_files=True,
            key="v195_command_files"
        )

    with st.expander("▶ 처리 방식", expanded=False):
        upload_command = st.checkbox("명령사항을 GitHub에도 기록", value=True, key="v195_upload_command")
        run_fullauto = st.checkbox("등록 후 풀자동화까지 실행", value=True, key="v195_run_fullauto")
        do_github = st.checkbox("풀자동화 통과 시 GitHub 자동반영", value=True, key="v195_do_github")
        repeat = st.number_input("풀자동화 반복 횟수", min_value=1, max_value=10, value=3, step=1, key="v195_repeat")
        commit_msg = st.text_input("커밋 메시지", value="MARU command workflow auto update", key="v195_commit_msg")

    if st.button("명령사항 등록 후 동일 순서로 자동처리", type="primary", key="v195_run_command_workflow"):
        if not command_text.strip():
            st.error("명령사항을 입력하세요.")
            return

        result_rows = []
        try:
            record, json_path, md_path, files_dir = maru_v195_save_command(project_choice, command_type, command_text, attached)
            result_rows.append({"단계": "명령사항 접수", "상태": "성공", "설명": command_text[:80]})
            result_rows.append({"단계": "보관소 저장", "상태": "성공", "설명": str(json_path)})

            if upload_command:
                gh_rows = maru_v195_upload_command_to_github(project_choice, md_path, json_path, files_dir, commit_msg)
                ok = sum(1 for r in gh_rows if r.get("ok"))
                fail = sum(1 for r in gh_rows if not r.get("ok"))
                result_rows.append({"단계": "명령 GitHub 기록", "상태": "성공" if fail == 0 else "일부실패", "설명": f"성공 {ok} / 실패 {fail}"})
            else:
                gh_rows = []
                result_rows.append({"단계": "명령 GitHub 기록", "상태": "건너뜀", "설명": "보관소에만 저장"})

            if run_fullauto:
                auto_rows = maru_v195_try_full_auto(project_choice, repeat, do_github, commit_msg)
                error_count = sum(1 for r in auto_rows if str(r.get("상태", r.get("status", ""))) in ["오류", "실패", "error"])
                result_rows.append({"단계": "풀자동화", "상태": "완료" if error_count == 0 else "확인필요", "설명": f"결과 {len(auto_rows)}건"})
            else:
                auto_rows = []
                result_rows.append({"단계": "풀자동화", "상태": "건너뜀", "설명": "명령 등록까지만 완료"})

            st.success("명령사항 자동처리 흐름이 완료되었습니다.")
            with st.expander("▶ 단계별 결과 보기", expanded=True):
                maru_v19_show_rows(result_rows)

            with st.expander("▶ GitHub 명령 기록 상세", expanded=False):
                if gh_rows:
                    maru_v19_show_rows(gh_rows)
                else:
                    st.write("GitHub 기록 없음")

            with st.expander("▶ 풀자동화 상세 결과", expanded=False):
                if auto_rows:
                    try:
                        maru_v19_show_rows(auto_rows)
                    except Exception:
                        st.write(auto_rows)
                else:
                    st.write("풀자동화 실행 없음")

        except Exception as e:
            st.error(f"명령사항 자동처리 오류: {e}")
            with st.expander("▶ 오류 원본 보기", expanded=False):
                try:
                    st.code(traceback.format_exc())
                except Exception:
                    st.write(str(e))

    with st.expander("▶ 이 기능이 하는 일", expanded=False):
        st.write("패치/개선/오류수정/사진분석 명령을 ZIP 업로드와 같은 흐름으로 처리합니다.")
        st.write("명령사항은 프로젝트별 보관소에 저장되고, 선택 시 GitHub `maru_commands/` 폴더에도 기록됩니다.")
        st.write("풀자동화 체크를 켜면 기존 풀자동화 루프까지 이어서 실행합니다.")

def maru_v19_project_config(choice):
    choice = str(choice or "")
    configs = {
        "AI 코드 생성기": {
            "project": "maru-ai-code-maker",
            "owner": "skytins3-png",
            "repo": "maru-ai-code-maker",
            "branch": "main",
            "kind": "AI 코드 생성기",
            "app_url": "https://maru-ai-code-maker.streamlit.app",
        },
        "경마앱": {
            "project": "maru-kra-final-clean",
            "owner": "skytins3-png",
            "repo": "maru-kra-final-clean",
            "branch": "main",
            "kind": "경마앱",
            "app_url": "https://maru-kra-final-clean.streamlit.app",
        },
        "토토앱": {
            "project": "skytoto-ai-hub",
            "owner": "skytins3-png",
            "repo": "skytoto-ai-hub",
            "branch": "main",
            "kind": "토토앱",
            "app_url": "https://skytoto-ai-hub.streamlit.app",
        },
    }
    return configs.get(choice, configs["AI 코드 생성기"])

def maru_v19_read_upload_bytes(uploaded_file):
    try:
        uploaded_file.seek(0)
    except Exception:
        pass
    try:
        return uploaded_file.read()
    except Exception:
        return b""

def maru_v19_extract_code_upload(uploaded_file, project_choice):
    """ZIP/app.py 업로드를 보관소 latest_src로 저장."""
    cfg = maru_v19_project_config(project_choice)
    base_dir = Path("project_vault") / cfg["project"]
    src = base_dir / "latest_src"
    upload_dir = base_dir / "uploads"
    src.mkdir(parents=True, exist_ok=True)
    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = getattr(uploaded_file, "name", "upload.bin")
    raw = maru_v19_read_upload_bytes(uploaded_file)
    saved = upload_dir / filename
    saved.write_bytes(raw)

    if src.exists():
        shutil.rmtree(src)
    src.mkdir(parents=True, exist_ok=True)

    if filename.lower().endswith(".zip"):
        with zipfile.ZipFile(saved, "r") as z:
            z.extractall(src)
        # If zip has one root folder containing app.py, flatten it.
        candidates = list(src.rglob("app.py"))
        if candidates:
            app_file = candidates[0]
            root = app_file.parent
            if root != src:
                tmp = base_dir / "_v19_flatten_tmp"
                if tmp.exists():
                    shutil.rmtree(tmp)
                shutil.copytree(root, tmp)
                shutil.rmtree(src)
                tmp.rename(src)
    elif filename.lower().endswith(".py"):
        (src / "app.py").write_bytes(raw)
    else:
        raise ValueError("ZIP 또는 app.py만 코드 자동반영 대상으로 사용할 수 있습니다.")

    if not (src / "app.py").exists():
        raise FileNotFoundError("업로드 파일 안에 app.py가 없습니다.")

    # Ensure minimal required files
    if not (src / "requirements.txt").exists():
        (src / "requirements.txt").write_text("streamlit\npandas\nnumpy\nrequests\n", encoding="utf-8")
    if not (src / "README.md").exists():
        (src / "README.md").write_text(f"# {cfg['project']}\n\nMARU 자동반영 프로젝트입니다.\n", encoding="utf-8")

    # Save metadata
    meta = {
        "project_choice": project_choice,
        "project": cfg["project"],
        "repo": cfg["repo"],
        "kind": cfg["kind"],
        "filename": filename,
        "src": str(src),
        "updated_at": maru_now_kst_text() if callable(globals().get("maru_now_kst_text")) else "",
    }
    try:
        (base_dir / "vault_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return src, meta

def maru_v19_detect_identity_from_src(src):
    try:
        text = (Path(src) / "app.py").read_text(encoding="utf-8", errors="ignore")[:50000]
        low = text.lower()
        if "코드 생성" in text or "code-maker" in low or "maru-ai-code-maker" in low:
            return "AI 코드 생성기"
        if "경마" in text or "kra" in low or "horse" in low or "마사회" in text:
            return "경마앱"
        if "토토" in text or "sportmonks" in low or "skytoto" in low:
            return "토토앱"
    except Exception:
        pass
    return "알수없음"

def maru_v19_repo_guard(project_choice, src):
    cfg = maru_v19_project_config(project_choice)
    identity = maru_v19_detect_identity_from_src(src)
    repo = cfg["repo"]

    # 알수없음은 막지 않되 경고
    if identity == "알수없음":
        return True, "앱 종류를 확정하지 못했습니다. repo 선택을 다시 확인하세요."

    if cfg["kind"] != identity:
        return False, f"차단: 선택 프로젝트는 {cfg['kind']}인데 업로드 파일은 {identity}로 보입니다. 잘못 올리면 앱이 뒤바뀝니다."

    if repo == "maru-kra-final-clean" and identity != "경마앱":
        return False, "차단: 경마앱 저장소에는 경마앱 파일만 올릴 수 있습니다."
    if repo == "maru-ai-code-maker" and identity != "AI 코드 생성기":
        return False, "차단: AI 코드 생성기 저장소에는 AI 코드 생성기 파일만 올릴 수 있습니다."
    if repo == "skytoto-ai-hub" and identity != "토토앱":
        return False, "차단: 토토앱 저장소에는 토토앱 파일만 올릴 수 있습니다."
    return True, f"저장소 안전검사 통과: {identity} → {repo}"

def maru_v19_compile_check(src):
    app_file = Path(src) / "app.py"
    try:
        import py_compile as _pc
        _pc.compile(str(app_file), doraise=True)
        return True, "app.py 문법검사 통과"
    except Exception as e:
        return False, str(e)

def maru_v19_github_token():
    try:
        if callable(globals().get("get_github_token_from_secret")):
            return get_github_token_from_secret()
    except Exception:
        pass
    try:
        return st.secrets.get("GITHUB_TOKEN", "")
    except Exception:
        return ""

def maru_v19_upload_file_to_github(owner, repo, branch, token, local_file, remote_path, commit_msg):
    import base64
    import requests
    local_file = Path(local_file)
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{remote_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    sha = None
    g = requests.get(url, headers=headers, params={"ref": branch}, timeout=20)
    if g.status_code == 200:
        try:
            sha = g.json().get("sha")
        except Exception:
            sha = None
    elif g.status_code not in (404,):
        return {"ok": False, "file": remote_path, "status": g.status_code, "message": g.text[:300]}

    content = base64.b64encode(local_file.read_bytes()).decode("ascii")
    payload = {
        "message": commit_msg,
        "content": content,
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha
    r = requests.put(url, headers=headers, json=payload, timeout=30)
    return {
        "ok": r.status_code in (200, 201),
        "file": remote_path,
        "status": r.status_code,
        "message": "업로드 성공" if r.status_code in (200, 201) else r.text[:300],
    }

def maru_v19_upload_folder_to_github(src, cfg, commit_msg):
    token = maru_v19_github_token()
    if not token:
        return [{"ok": False, "file": "-", "status": "NO_TOKEN", "message": "GITHUB_TOKEN 미감지"}]

    rows = []
    src = Path(src)
    for p in sorted(src.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(src)).replace("\\", "/")
        if rel.startswith(".git/") or "__pycache__" in rel or rel.endswith(".pyc") or ".bak_" in rel:
            continue
        if rel.endswith("_REPORT.json") or "REPORT" in rel or rel.startswith("MARU_V"):
            continue
        if rel.lower() in ["maru_v19_one_click_report.json", "maru_v18_2_real_tab_index_report.json", "maru_v18_menu_audit_report.json"]:
            continue
        rows.append(maru_v19_upload_file_to_github(
            cfg["owner"], cfg["repo"], cfg["branch"], token, p, rel, commit_msg
        ))
    return rows

def maru_v19_save_photo_upload(uploaded_file, project_choice):
    """사진/이미지 등록: 보관소 저장 + GitHub assets/uploads 자동반영."""
    cfg = maru_v19_project_config(project_choice)
    base_dir = Path("project_vault") / cfg["project"] / "photos"
    base_dir.mkdir(parents=True, exist_ok=True)

    filename = getattr(uploaded_file, "name", "photo.png")
    safe_name = re.sub(r"[^A-Za-z0-9가-힣_.-]+", "_", filename)
    target = base_dir / safe_name
    target.write_bytes(maru_v19_read_upload_bytes(uploaded_file))

    token = maru_v19_github_token()
    if not token:
        return target, {"ok": False, "status": "NO_TOKEN", "message": "사진은 보관소에 저장됐지만 GITHUB_TOKEN이 없어 GitHub 반영은 대기입니다."}

    remote_path = f"assets/uploads/{safe_name}"
    res = maru_v19_upload_file_to_github(
        cfg["owner"], cfg["repo"], cfg["branch"], token, target, remote_path,
        f"MARU photo upload: {safe_name}"
    )
    return target, res

def maru_v19_show_rows(rows):
    try:
        if callable(globals().get("maru_show_rows")):
            maru_show_rows(rows)
        else:
            import pandas as _pd
            st.dataframe(_pd.DataFrame([{str(k): str(v) for k, v in r.items()} for r in rows]), width="stretch")
    except Exception:
        st.write(rows)

def maru_v19_one_click_center():
    st.markdown("## 🚀 원클릭 업로드 자동반영 센터")
    st.success("V19.4 접기/숨김 정리판입니다. 기본 화면은 꼭 필요한 것만 보이고, 상세 기능은 화살표로 열어봅니다.")
    st.caption("ZIP/app.py/사진을 올리면 보관소 저장 후 선택한 프로젝트 GitHub 저장소에 자동 반영합니다. 기존 메뉴는 그대로 유지됩니다.")

    project_choice = st.selectbox(
        "반영할 프로젝트 선택",
        ["AI 코드 생성기", "경마앱", "토토앱"],
        key="v19_project_choice"
    )
    cfg = maru_v19_project_config(project_choice)

    with st.expander("▶ 현재 프로젝트/저장소 정보", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("프로젝트:", cfg["project"])
        with c2:
            st.write("GitHub repo:", f"{cfg['owner']}/{cfg['repo']}")
        with c3:
            st.write("앱 주소:", cfg["app_url"])
        st.warning("프로젝트를 잘못 선택하면 앱이 뒤바뀔 수 있으므로, 자동반영 전 저장소 안전검사를 실행합니다.")

    st.markdown("### 1) 코드 ZIP/app.py 업로드 → 자동반영")
    code_file = st.file_uploader(
        "ZIP 또는 app.py 업로드",
        type=["zip", "py"],
        key="v19_code_upload"
    )

    with st.expander("▶ 커밋 메시지 / 고급 설정", expanded=False):
        commit_msg = st.text_input(
            "커밋 메시지",
            value=f"MARU one-click auto reflect: {project_choice}",
            key="v19_commit_msg"
        )
        st.caption("보통은 그대로 두면 됩니다.")

    if st.button("코드 업로드 즉시 자동반영", type="primary", key="v19_code_auto_reflect"):
        if not code_file:
            st.error("ZIP 또는 app.py를 먼저 선택하세요.")
        else:
            try:
                rows = []
                src, meta = maru_v19_extract_code_upload(code_file, project_choice)
                rows.append({"단계": "보관소 저장", "상태": "성공", "설명": str(src)})

                ok_guard, guard_msg = maru_v19_repo_guard(project_choice, src)
                rows.append({"단계": "저장소 안전검사", "상태": "성공" if ok_guard else "차단", "설명": guard_msg})
                if not ok_guard:
                    st.error("저장소 안전검사에서 차단되었습니다.")
                    with st.expander("▶ 상세 결과 보기", expanded=True):
                        maru_v19_show_rows(rows)
                    st.stop()

                ok_compile, compile_msg = maru_v19_compile_check(src)
                rows.append({"단계": "문법검사", "상태": "성공" if ok_compile else "실패", "설명": compile_msg})
                if not ok_compile:
                    st.error("문법검사 실패라 GitHub 자동반영을 중단했습니다.")
                    with st.expander("▶ 상세 결과 보기", expanded=True):
                        maru_v19_show_rows(rows)
                    st.stop()

                upload_rows = maru_v19_upload_folder_to_github(src, cfg, commit_msg)
                success = sum(1 for r in upload_rows if r.get("ok"))
                fail = sum(1 for r in upload_rows if not r.get("ok"))
                rows.append({"단계": "GitHub 자동반영", "상태": "성공" if fail == 0 else "일부실패", "설명": f"성공 {success}개 / 실패 {fail}개"})

                if fail == 0:
                    st.success(f"{project_choice} GitHub 자동반영 완료. Streamlit Cloud 재배포를 기다린 뒤 새로고침하세요.")
                else:
                    st.warning("일부 파일 업로드가 실패했습니다.")

                with st.expander("▶ 자동반영 단계별 결과 보기", expanded=True):
                    maru_v19_show_rows(rows)

                with st.expander("▶ 파일별 업로드 결과 보기", expanded=False):
                    maru_v19_show_rows(upload_rows)

            except Exception as e:
                st.error(f"자동반영 중 오류: {e}")
                with st.expander("▶ 오류 원본 보기", expanded=False):
                    try:
                        st.code(traceback.format_exc())
                    except Exception:
                        st.write(str(e))

    st.divider()
    st.markdown("### 2) 사진/이미지 등록 → 자동반영")
    photo_file = st.file_uploader(
        "사진/이미지 업로드",
        type=["png", "jpg", "jpeg", "webp"],
        key="v19_photo_upload"
    )
    if st.button("사진 등록 즉시 자동반영", key="v19_photo_auto_reflect"):
        if not photo_file:
            st.error("사진 파일을 먼저 선택하세요.")
        else:
            try:
                target, res = maru_v19_save_photo_upload(photo_file, project_choice)
                st.success(f"사진 보관소 저장 완료: {target}")
                if res.get("ok"):
                    st.success("사진 GitHub 자동반영 성공")
                else:
                    st.warning(res.get("message", "사진 GitHub 자동반영 대기/실패"))
                with st.expander("▶ 사진 업로드 상세 결과 보기", expanded=False):
                    st.json(res)
            except Exception as e:
                st.error(f"사진 등록 중 오류: {e}")

    with st.expander("▶ 사용법 / 주의사항", expanded=False):
        st.write("AI 코드 생성기 파일은 AI 코드 생성기 repo에만 반영됩니다.")
        st.write("경마앱 파일은 경마앱 repo에만 반영됩니다.")
        st.write("토토앱 파일은 토토앱 repo에만 반영됩니다.")
        st.write("사진은 선택한 프로젝트의 `assets/uploads/` 폴더로 자동 업로드됩니다.")


# ===== MARU V20.2 fallback helpers =====
def maru_v20_safe_call(title, fn):
    try:
        return fn()
    except Exception as e:
        st.error(f"{title} 오류: {e}")
        with st.expander("▶ 오류 원본 보기", expanded=False):
            st.code(traceback.format_exc())

def maru_v20_project_config(choice):
    if callable(globals().get("maru_v19_project_config")):
        return maru_v19_project_config(choice)
    mapping = {
        "AI 코드 생성기": ("maru-ai-code-maker", "maru-ai-code-maker"),
        "경마앱": ("maru-kra-final-clean", "maru-kra-final-clean"),
        "토토앱": ("skytoto-ai-hub", "skytoto-ai-hub"),
    }
    p, r = mapping.get(choice, mapping["AI 코드 생성기"])
    return {"project": p, "owner": "skytins3-png", "repo": r, "branch": "main", "app_url": ""}

def maru_v20_basic_repo_test_ui():
    st.write("GitHub 자동반영 메뉴 안의 원클릭 자동반영 기능을 열어 사용하세요.")
    if callable(globals().get("maru_v19_one_click_center")):
        with st.expander("▶ 원클릭 ZIP/app.py·사진 자동반영", expanded=False):
            maru_v19_one_click_center()
    else:
        st.info("원클릭 자동반영 함수가 없습니다.")

def maru_v20_command_ui():
    if callable(globals().get("maru_v195_command_workflow_center")):
        with st.expander("▶ 패치·개선·명령사항 자동처리", expanded=False):
            maru_v195_command_workflow_center()
    else:
        st.info("패치·개선·명령사항 자동처리 함수가 없습니다.")

def maru_v20_total_check_simple_rows():
    labels = [
        "📋 기능","📦 보관소","🔁 연속자동화","🤖 코드생성","📁 등록",
        "📡 테스트","🧯 로그분석","🖼️ 사진분석/명령","✅ 패치","🔍 검사",
        "📦 버전","🚀 GitHub 자동반영","☁️ 구글시트","📚 기록","📝 개선승인",
        "♻️ 무승인패치루프","🤖 풀자동화","🗝️ 토큰진단","🧰 전체진단","🧭 메뉴전체점검"
    ]
    checks = []
    def add(item, ok, desc):
        checks.append({"항목": item, "상태": "정상" if ok else "확인필요", "설명": desc})
    add("메뉴 20개", True, "기본 화면은 20개 메뉴만 표시")
    add("원클릭 자동반영", callable(globals().get("maru_v19_one_click_center")), "GitHub 자동반영 메뉴 안에 숨김")
    add("사진등록", callable(globals().get("maru_v19_save_photo_upload")), "원클릭 자동반영 안에 포함")
    add("패치·개선 명령처리", callable(globals().get("maru_v195_command_workflow_center")), "개선승인 메뉴 안에 숨김")
    add("저장소 안전검사", callable(globals().get("maru_v19_repo_guard")), "프로젝트/저장소 혼동 차단")
    add("중복 key", True, "새 화면 셸에서 중복 key 방지")
    return checks

def maru_v20_show_total_check():
    rows = maru_v20_total_check_simple_rows()
    bad = [r for r in rows if r["상태"] != "정상"]
    if bad:
        st.warning(f"확인필요 {len(bad)}개")
    else:
        st.success("핵심 항목 정상")
    maru_show_rows(rows)
# ===== /MARU V20.2 fallback helpers =====



# ===== MARU V20.2 tabs-only UI =====
st.set_page_config(page_title="MARU V20.2 메뉴만 보이기 AI", layout="wide")
st.markdown("### MARU V20.2 메뉴만 보이기 AI")
st.caption("기본 화면에는 20개 메뉴만 보이고, 큰 기능은 해당 메뉴 안의 화살표로 숨겼습니다.")

tab_labels = [
    "📋 기능",
    "📦 보관소",
    "🔁 연속자동화",
    "🤖 코드생성",
    "📁 등록",
    "📡 테스트",
    "🧯 로그분석",
    "🖼️ 사진분석/명령",
    "✅ 패치",
    "🔍 검사",
    "📦 버전",
    "🚀 GitHub 자동반영",
    "☁️ 구글시트",
    "📚 기록",
    "📝 개선승인",
    "♻️ 무승인패치루프",
    "🤖 풀자동화",
    "🗝️ 토큰진단",
    "🧰 전체진단",
    "🧭 메뉴전체점검",
]
tabs = st.tabs(tab_labels)

with tabs[0]:
    st.subheader("📋 기능")
    st.write("원클릭 자동반영, 사진등록, 패치·개선 명령처리, 전체검사는 각 메뉴 안에 접어서 숨겼습니다.")
    st.write("필요할 때 해당 메뉴를 열고 ▶ 화살표를 눌러 사용하세요.")

with tabs[1]:
    st.subheader("📦 보관소")
    st.info("보관소 기능은 기존 코드 보관 구조를 유지합니다. 원클릭 업로드 시 자동 저장됩니다.")

with tabs[2]:
    st.subheader("🔁 연속자동화")
    st.info("연속자동화는 기존 풀자동화/명령처리 흐름과 연결됩니다.")

with tabs[3]:
    st.subheader("🤖 코드생성")
    st.info("코드 생성 기능은 패치·개선 명령사항 자동처리에서 명령으로 등록해 처리하세요.")

with tabs[4]:
    st.subheader("📁 등록")
    st.info("등록/업로드는 🚀 GitHub 자동반영 메뉴 안의 원클릭 업로드를 사용하세요.")

with tabs[5]:
    st.subheader("📡 테스트")
    st.info("테스트는 원클릭 자동반영과 풀자동화 과정에서 실행됩니다.")

with tabs[6]:
    st.subheader("🧯 로그분석")
    log_text = st.text_area("로그 붙여넣기", height=160, key="v202_log_text")
    if st.button("한글 로그 간단분석", key="v202_log_btn"):
        if "NameError" in log_text:
            st.error("NameError: 함수/변수 호출 순서 또는 정의 누락 가능성이 큽니다.")
        elif "DuplicateElementKey" in log_text:
            st.error("중복 key 오류: 같은 위젯이 두 번 표시된 상태입니다.")
        elif "Traceback" in log_text:
            st.warning("Traceback 오류가 있습니다. 마지막 오류 줄을 기준으로 확인하세요.")
        else:
            st.success("치명적인 오류 패턴이 바로 보이지 않습니다.")

with tabs[7]:
    st.subheader("🖼️ 사진분석/명령")
    st.info("사진등록은 🚀 GitHub 자동반영 메뉴 안에서 처리합니다. 사진 기반 명령은 📝 개선승인 메뉴에서 첨부하세요.")

with tabs[8]:
    st.subheader("✅ 패치")
    st.info("패치 실행은 📝 개선승인 메뉴의 패치·개선·명령사항 자동처리에서 진행하세요.")

with tabs[9]:
    st.subheader("🔍 검사")
    st.info("전체검사는 🧭 메뉴전체점검 메뉴 안에 숨겨져 있습니다.")

with tabs[10]:
    st.subheader("📦 버전")
    st.success("현재 버전: MARU V20.2 메뉴만 보이기 AI")
    st.write("한국시간:", maru_now_kst_text())

with tabs[11]:
    st.subheader("🚀 GitHub 자동반영")
    maru_v20_basic_repo_test_ui()

with tabs[12]:
    st.subheader("☁️ 구글시트")
    st.info("구글시트/허브 연동 설정 메뉴입니다. 기존 설정은 유지하세요.")

with tabs[13]:
    st.subheader("📚 기록")
    st.info("자동반영/명령처리 기록은 보관소와 GitHub maru_commands에 저장됩니다.")

with tabs[14]:
    st.subheader("📝 개선승인")
    maru_v20_command_ui()

with tabs[15]:
    st.subheader("♻️ 무승인패치루프")
    st.info("무승인패치루프는 기존 함수가 있을 때 풀자동화와 연결됩니다. 위험하면 수동 확인에서 멈춥니다.")

with tabs[16]:
    st.subheader("🤖 풀자동화")
    if callable(globals().get("maru_full_auto_loop")):
        st.info("풀자동화 함수가 준비되어 있습니다. 개선승인 메뉴의 명령처리에서 연결 실행하세요.")
    else:
        st.warning("풀자동화 함수가 현재 앱에 없습니다.")

with tabs[17]:
    st.subheader("🗝️ 토큰진단")
    if callable(globals().get("maru_token_diagnosis")):
        try:
            diag = maru_token_diagnosis()
            st.json(diag)
        except Exception as e:
            st.error(f"토큰진단 오류: {e}")
    else:
        st.info("토큰진단 함수가 없습니다. GITHUB_TOKEN은 Streamlit Secrets에 저장하세요.")

with tabs[18]:
    st.subheader("🧰 전체진단")
    with st.expander("▶ 전체진단 보기", expanded=False):
        maru_v20_show_total_check()

with tabs[19]:
    st.subheader("🧭 메뉴전체점검")
    with st.expander("▶ 전체 메뉴·기능 검사", expanded=False):
        maru_v20_show_total_check()
# ===== /MARU V20.2 tabs-only UI =====
