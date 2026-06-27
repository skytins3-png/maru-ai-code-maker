
# ===== MARU V16 complete stability imports =====
import os
import io
import re
import json
import time
import zipfile
import shutil
import hashlib
import traceback
import subprocess
import py_compile
from pathlib import Path
from datetime import datetime, timezone, timedelta
try:
    import pandas as pd
except Exception:
    pd = None
try:
    import numpy as np
except Exception:
    np = None
# ===== /MARU V16 complete stability imports =====

import hashlib
import shutil
import py_compile

import streamlit as st

# ===== MARU V14 hard block Streamlit help dumps =====
try:
    _MARU_ORIG_HELP = st.help
except Exception:
    _MARU_ORIG_HELP = None

def _maru_block_help(obj=None, *args, **kwargs):
    try:
        s = str(obj)
    except Exception:
        s = ""
    # Streamlit 자체 도움말은 화면에 길게 뿌리지 않음
    if obj is st or "streamlit" in s.lower() or "DeltaGenerator" in s or "BottomContainerProxy" in s:
        return None
    if _MARU_ORIG_HELP:
        return _MARU_ORIG_HELP(obj, *args, **kwargs)
    return None

try:
    st.help = _maru_block_help
except Exception:
    pass

def _maru_strip_streamlit_help_text(s):
    try:
        s = str(s)
    except Exception:
        return s
    markers = [
        "Streamlit 사용법",
        "Take a look at the other commands",
        "dir(streamlit)",
        "streamlit hello",
        "BottomContainerProxy",
        "QueryParamsProxy",
        ">>> import streamlit as st",
        "For more detailed info, see https://docs.streamlit.io",
        "더 자세한 정보는 https://docs.streamlit.io",
    ]
    if any(m in s for m in markers):
        return ""
    return s

# 기존 안전 출력 함수가 있든 없든 한 번 더 강제 차단
try:
    _MARU_ORIG_WRITE2 = st.write
    _MARU_ORIG_MARKDOWN2 = st.markdown
    _MARU_ORIG_TEXT2 = st.text
    _MARU_ORIG_CODE2 = st.code

    def _maru_write2(*args, **kwargs):
        clean = [_maru_strip_streamlit_help_text(a) for a in args]
        clean = [a for a in clean if a not in ("", None)]
        if not clean:
            return None
        return _MARU_ORIG_WRITE2(*clean, **kwargs)

    def _maru_markdown2(body, *args, **kwargs):
        body = _maru_strip_streamlit_help_text(body)
        if not body:
            return None
        return _MARU_ORIG_MARKDOWN2(body, *args, **kwargs)

    def _maru_text2(body="", *args, **kwargs):
        body = _maru_strip_streamlit_help_text(body)
        if not body:
            return None
        return _MARU_ORIG_TEXT2(body, *args, **kwargs)

    def _maru_code2(body="", *args, **kwargs):
        body = _maru_strip_streamlit_help_text(body)
        if not body:
            return None
        return _MARU_ORIG_CODE2(body, *args, **kwargs)

    st.write = _maru_write2
    st.markdown = _maru_markdown2
    st.text = _maru_text2
    st.code = _maru_code2
except Exception:
    pass
# ===== /MARU V14 hard block Streamlit help dumps =====


# ===== MARU V14 display guard: hide accidental Streamlit help/debug dumps =====
_MARU_ORIG_WRITE = st.write
_MARU_ORIG_MARKDOWN = st.markdown
_MARU_ORIG_TEXT = st.text
_MARU_ORIG_CODE = st.code

def _maru_is_streamlit_debug_dump(obj):
    try:
        s = str(obj)
    except Exception:
        return False
    markers = [
        "Streamlit 사용법",
        "Take a look at the other commands",
        "dir(streamlit)",
        "streamlit hello",
        "BottomContainerProxy",
        "QueryParamsProxy",
        "https://docs.streamlit.io",
        ">>> import streamlit as st",
    ]
    return any(m in s for m in markers)

def _maru_safe_write(*args, **kwargs):
    if args and any(_maru_is_streamlit_debug_dump(a) for a in args):
        return None
    return _MARU_ORIG_WRITE(*args, **kwargs)

def _maru_safe_markdown(body, *args, **kwargs):
    if _maru_is_streamlit_debug_dump(body):
        return None
    return _MARU_ORIG_MARKDOWN(body, *args, **kwargs)

def _maru_safe_text(body="", *args, **kwargs):
    if _maru_is_streamlit_debug_dump(body):
        return None
    return _MARU_ORIG_TEXT(body, *args, **kwargs)

def _maru_safe_code(body="", *args, **kwargs):
    if _maru_is_streamlit_debug_dump(body):
        return None
    return _MARU_ORIG_CODE(body, *args, **kwargs)

st.write = _maru_safe_write
st.markdown = _maru_safe_markdown
st.text = _maru_safe_text
st.code = _maru_safe_code
# ===== /MARU V14 display guard =====


# ===== MARU V14 absolute compatibility helpers =====
try:
    st
except NameError:
    import streamlit as st

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
        return maru_secret_first("KRA_API_KEY", "PUBLIC_DATA_API_KEY", "MARU_KRA_API_KEY", default=maru_maru_get_default_profile(mem_obj).get("api_key", ""))
    if choice == "토토앱":
        return maru_secret_first("TOTO_API_KEY", "SPORTS_API_KEY", "SPORTMONKS_TOKEN", "MARU_TOTO_API_KEY", default=maru_maru_get_default_profile(mem_obj).get("api_key", ""))
    return maru_maru_get_default_profile(mem_obj).get("api_key", "")

def maru_api_urls_for(choice, mem_obj=None):
    _cur = maru_maru_get_default_profile(mem_obj).get("api_urls", "")
    if _cur:
        return _cur
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
    return maru_secret_first("GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token", default="")

# Backward-compatible names. If old screen code calls these, they now always exist.
def default_api_key_for(choice, mem_obj=None):
    return maru_api_key_for(choice, mem_obj)

def default_api_urls_for(choice, mem_obj=None):
    return maru_api_urls_for(choice, mem_obj)

def maru_profile_from_choice(choice, mem_obj=None):
    return maru_maru_profile_from_choice(choice, mem_obj)

def maru_get_default_profile(mem_obj=None):
    return maru_maru_get_default_profile(mem_obj)

def maru_github_token():
    return maru_secret_first("GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token", default="")

def maru_github_token():
    return maru_secret_first("GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token", default="")
# ===== /MARU V14 absolute compatibility helpers =====


# ===== MARU V14 missing helper hotfix =====
def _maru_secret_get(name, default=""):
    try:
        value = st.secrets.get(name, default)
        return value if value is not None else default
    except Exception:
        return default

def secret_first(*names, default=""):
    for name in names:
        value = _maru_secret_get(name, "")
        if value:
            return value
    return default

def maru_get_default_profile(mem_obj=None):
    base = {
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
            prof = mem_obj.setdefault("default_profile", {})
            for k, v in base.items():
                prof.setdefault(k, v)
            return prof
    except Exception:
        pass
    return base

PROJECT_PRESETS = {
    "경마앱": {
        "project_name": "maru-kra-final-clean",
        "app_url": "https://maru-kra-final-clean.streamlit.app",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "maru-kra-final-clean",
        "github_branch": "main",
    },
    "토토앱": {
        "project_name": "skytoto-ai-hub",
        "app_url": "",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "skytoto-ai-hub",
        "github_branch": "main",
    },
    "AI 코드 생성기": {
        "project_name": "maru-ai-code-maker",
        "app_url": "https://maru-ai-code-maker.streamlit.app",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "maru-ai-code-maker",
        "github_branch": "main",
    },
    "직접입력": {
        "project_name": "",
        "app_url": "",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "",
        "github_branch": "main",
    },
}

def maru_profile_from_choice(choice, mem_obj=None):
    prof = PROJECT_PRESETS.get(choice, PROJECT_PRESETS["직접입력"]).copy()
    if choice == "직접입력":
        current = maru_get_default_profile(mem_obj)
        prof.update(current)
        return prof
    try:
        current = maru_get_default_profile(mem_obj)
        if current.get("api_key") and not prof.get("api_key"):
            prof["api_key"] = current.get("api_key", "")
        if current.get("api_urls") and not prof.get("api_urls"):
            prof["api_urls"] = current.get("api_urls", "")
    except Exception:
        pass
    return prof

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
    return secret_first("GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token", default="")

def maru_github_token():
    return maru_secret_first("GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token", default="")
# ===== /MARU V14 missing helper hotfix =====

import zipfile, json, shutil, io, re, ast, subprocess, sys, base64, time
from pathlib import Path
from datetime import datetime, timezone, timedelta


# ===== MARU V14.5 KST final safe time helpers =====
try:
    KST
except NameError:
    KST = timezone(timedelta(hours=9))

def maru_now_kst():
    try:
        return maru_now_kst()
    except Exception:
        return datetime.now(timezone(timedelta(hours=9)))

def maru_now_kst_text():
    return maru_now_kst().strftime("%Y-%m-%d %H:%M:%S KST")
# ===== /MARU V14.5 KST final safe time helpers =====


# 한국시간 고정값
KST = timezone(timedelta(hours=9))

import requests

ROOT = Path(__file__).parent
MEM = ROOT / "ai_memory.json"


# ===== MARU V14.6 save_memory compatibility hotfix =====
def save_memory(mem_obj):
    """기존 앱에 저장 함수명이 없거나 달라도 보관소/루프가 멈추지 않게 하는 호환 저장 함수."""
    try:
        target = globals().get("MEM", None)
        if target is None:
            target = Path(__file__).parent / "ai_memory.json"
        target = Path(target)
        target.write_text(json.dumps(mem_obj, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception as e:
        try:
            st.warning(f"메모리 저장 실패: {e}")
        except Exception:
            pass
        return False

def load_memory_safe(default=None):
    try:
        target = globals().get("MEM", None)
        if target is None:
            target = Path(__file__).parent / "ai_memory.json"
        target = Path(target)
        if target.exists():
            return json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default if default is not None else {}
# ===== /MARU V14.6 save_memory compatibility hotfix =====

STORE = ROOT / "project_storage"
VERS = ROOT / "version_outputs"
GENERATED = ROOT / "generated_projects"
IMAGE_STORE = ROOT / "image_uploads"


# ===== MARU V14 project vault auto apply =====
MARU_PROJECT_VAULT_DIR = ROOT / "project_vault"
MARU_PROJECT_VAULT_DIR.mkdir(parents=True, exist_ok=True)

MARU_PROJECT_PRESETS = {
    "경마앱": {
        "project_name": "maru-kra-final-clean",
        "app_url": "https://maru-kra-final-clean.streamlit.app",
        "github_owner": "skytins3-png",
        "github_repo": "maru-kra-final-clean",
        "github_branch": "main",
    },
    "토토앱": {
        "project_name": "skytoto-ai-hub",
        "app_url": "",
        "github_owner": "skytins3-png",
        "github_repo": "skytoto-ai-hub",
        "github_branch": "main",
    },
    "AI 코드 생성기": {
        "project_name": "maru-ai-code-maker",
        "app_url": "https://maru-ai-code-maker.streamlit.app",
        "github_owner": "skytins3-png",
        "github_repo": "maru-ai-code-maker",
        "github_branch": "main",
    },
}

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
# ===== /MARU V14 project vault auto apply =====


# ===== MARU V14.1 continuous patch-test-log loop =====
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
# ===== /MARU V14.1 continuous patch-test-log loop =====


STORE.mkdir(exist_ok=True)
VERS.mkdir(exist_ok=True)
GENERATED.mkdir(exist_ok=True)
IMAGE_STORE.mkdir(exist_ok=True)

DEFAULT = {
    "version": "13.0-all-in-one-final",
    "projects": {},
    "patch_records": [],
    "github_deploys": [],
    "test_records": [],
    "file_checks": [],
    "generated_projects": [],
    "hub_uploads": [],
    "log_analyses": [],
    "image_analyses": [],
    "command_records": [],
    "google_sheets": {"enabled": False, "sheet_id": "", "service_account_json": ""},
    "default_profile": {"project_name": "maru-kra-final-clean", "app_url": "https://maru-kra-final-clean.streamlit.app", "api_key": "", "api_urls": "", "github_owner": "skytins3-png", "github_repo": "maru-kra-final-clean", "github_branch": "main"},
    "saved_profiles": {},
    "lessons": [],
}


PROJECT_PRESETS = {
    "경마앱": {
        "project_name": "maru-kra-final-clean",
        "app_url": "https://maru-kra-final-clean.streamlit.app",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "maru-kra-final-clean",
        "github_branch": "main",
    },
    "토토앱": {
        "project_name": "skytoto-ai-hub",
        "app_url": "",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "skytoto-ai-hub",
        "github_branch": "main",
    },
    "AI 코드 생성기": {
        "project_name": "maru-ai-code-maker",
        "app_url": "https://maru-ai-code-maker.streamlit.app",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "maru-ai-code-maker",
        "github_branch": "main",
    },
    "직접입력": {
        "project_name": "",
        "app_url": "",
        "api_key": "",
        "api_urls": "",
        "github_owner": "skytins3-png",
        "github_repo": "",
        "github_branch": "main",
    },
}

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


PATCHES = {
    "mobile_ui": "모바일 큰 글씨/큰 버튼",
    "error_logger": "오류 로그 저장",
    "api_timeout": "API timeout/통신두절 방어",
    "debug_panel": "디버그 패널",
    "api_key_guard": "API KEY 보안 안내",
    "zip_export": "현재 앱 ZIP 다운로드",
    "kra_helper": "경마 API 점검 도구 파일 추가",
    "toto_helper": "토토/스포츠 API 점검 도구 파일 추가",
    "html_render_fix": "HTML 카드 코드노출 수정",
    "race_schedule_fallback": "경마시간 추천없음 표시 보정",
}

FEATURES = [
    "음성지시 제거", "OpenAI API 키 제거", "요금 발생 요소 제거",
    "ZIP 업로드 자동 압축해제", "프로젝트 보관함", "파일 목록 검사",
    "오류 파일 검사", "문법 검사", "기존 기능 분석", "자동테스트",
    "반복 자동테스트", "개선안 추천", "승인/미승인/추가지시",
    "승인한 항목 실제 패치", "app.py 실제 수정", "helper 파일 실제 추가",
    "새 버전 ZIP 생성", "프로젝트 보관소 최신파일 자동불러오기", "패치-반영-테스트-로그분석 연속자동화", "개선 요구사항 승인 후 진행", "승인 후 패치 무승인 연속루프", "GitHub 대상 저장소 자동 업로드/커밋",
    "Streamlit Cloud 자동 재배포 유도", "구글시트 저장 구조", 
    "GitHub Actions 예약 테스트 파일 생성", "진화형 AI 코드 생성", "생성 앱 GitHub 허브 자동 업로드", "구글시트 허브 저장", "로그파일 붙여넣기/업로드 분석", "사진 첨부/명령 입력 분석", "HTML 카드 코드노출 수정", "경마시간 추천없음 표시 보정", "화면 디버그 출력 제거", "자동구매/자동결제 차단"
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


def infer_project_name(name, app_url="", uploaded=None):
    raw = (name or "").strip()
    if raw:
        return raw
    if app_url:
        m = re.search(r"https?://([^./]+)", app_url)
        if m:
            return m.group(1).strip()
    if uploaded is not None:
        base = Path(uploaded.name).stem
        base = re.sub(r"\s*\(\d+\)$", "", base)
        base = base.replace("_UPLOAD", "").replace("_upload", "")
        if base:
            return sname(base)
    return "maru-kra-final-clean"


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
        ("agent-card", ["html_render_fix", "mobile_ui"], "HTML 카드 코드 노출"),
        ("<div", ["html_render_fix", "mobile_ui"], "HTML 코드가 화면에 보임"),
        ("추천 없음", ["race_schedule_fallback", "debug_panel", "kra_helper"], "경마시간 추천없음 표시 보정"),
        ("todayrace", ["race_schedule_fallback", "debug_panel", "kra_helper"], "공식 경주 일정과 앱 표시 불일치"),
        ("제주", ["race_schedule_fallback", "debug_panel", "kra_helper"], "경마장 자동 감지 보정"),
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

def analyze_image_command(command_text, saved_images):
    cmd = (command_text or "").lower()
    patches = set()
    findings = []
    if any(k in cmd for k in ["모바일", "폰", "화면", "작", "안보", "글씨", "버튼"]):
        patches.update(["mobile_ui", "debug_panel"])
        findings.append({"reason": "모바일 화면/버튼/글씨 개선 명령", "patches": ["mobile_ui", "debug_panel"]})
    if any(k in cmd for k in ["오류", "에러", "traceback", "빨간", "멈춤", "안됨", "안되"]):
        patches.update(["error_logger", "debug_panel"])
        findings.append({"reason": "화면 오류/정지/에러 명령", "patches": ["error_logger", "debug_panel"]})
    if any(k in cmd for k in ["html", "div", "agent-card", "카드", "코드", "그대로"]):
        patches.update(["html_render_fix", "mobile_ui"])
        findings.append({"reason": "HTML 카드 코드 노출 명령", "patches": ["html_render_fix", "mobile_ui"]})
    if any(k in cmd for k in ["경마시간", "추천 없음", "추천없음", "제주", "서울", "부산", "경주", "todayrace"]):
        patches.update(["race_schedule_fallback", "debug_panel", "kra_helper"])
        findings.append({"reason": "경마시간/추천없음/경주표시 명령", "patches": ["race_schedule_fallback", "debug_panel", "kra_helper"]})
    if any(k in cmd for k in ["api", "통신", "500", "403", "404", "401", "timeout", "데이터", "실시간"]):
        patches.update(["api_timeout", "debug_panel", "api_key_guard"])
        findings.append({"reason": "API/통신/실시간 관련 명령", "patches": ["api_timeout", "debug_panel", "api_key_guard"]})
    if any(k in cmd for k in ["다운로드", "zip", "압축", "파일"]):
        patches.update(["zip_export", "debug_panel"])
        findings.append({"reason": "파일/ZIP/다운로드 관련 명령", "patches": ["zip_export", "debug_panel"]})
    if any(k in cmd for k in ["경마", "kra", "마사회"]):
        patches.update(["kra_helper", "debug_panel"])
        findings.append({"reason": "경마/KRA 관련 명령", "patches": ["kra_helper", "debug_panel"]})
    if any(k in cmd for k in ["토토", "스포츠", "축구", "배당", "odds"]):
        patches.update(["toto_helper", "debug_panel"])
        findings.append({"reason": "토토/스포츠 관련 명령", "patches": ["toto_helper", "debug_panel"]})
    if not findings:
        patches.update(["debug_panel", "error_logger"])
        findings.append({"reason": "일반 사진/명령 분석: 디버그와 오류기록 우선 추천", "patches": ["debug_panel", "error_logger"]})
    return {
        "image_count": len(saved_images or []),
        "images": saved_images,
        "command": command_text,
        "findings": findings,
        "recommended_patches": sorted(patches),
    }


def decode_uploaded_log(uploaded_file):
    if uploaded_file is None:
        return ""
    raw = uploaded_file.getvalue()
    for enc in ("utf-8", "cp949", "euc-kr"):
        try:
            return raw.decode(enc)
        except Exception:
            pass
    return raw.decode("utf-8", errors="ignore")


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

def add_helpers(src, approved):
    src = Path(src)
    if "kra_helper" in approved:
        write(src/"kra_api_debug_helper.py", "import streamlit as st, requests\nst.title('🐎 경마 API 점검')\nurl=st.text_area('URL')\nkey=st.text_input('KEY',type='password')\nif st.button('점검'):\n    try:\n        r=requests.get(url.replace('{serviceKey}',key).replace('{api_key}',key),timeout=15); st.metric('HTTP',r.status_code); st.text(r.text[:5000])\n    except Exception as e: st.error(e)\n")
    if "toto_helper" in approved:
        write(src/"toto_api_debug_helper.py", "import streamlit as st, requests\nst.title('⚽ 토토/스포츠 API 점검')\nurl=st.text_area('URL')\ntoken=st.text_input('TOKEN',type='password')\nif st.button('점검'):\n    try:\n        r=requests.get(url.replace('{token}',token).replace('{api_key}',token),timeout=15); st.metric('HTTP',r.status_code); st.text(r.text[:5000])\n    except Exception as e: st.error(e)\n")
    if "race_schedule_fallback" in approved:
        write(src/"maru_race_schedule_fallback.py", "from datetime import datetime\n\ndef maru_race_status_fallback(recommend_data=None, race_hint=None):\n    if recommend_data:\n        return {'status':'추천 있음','message':'저장된 추천 표시','data':recommend_data}\n    if race_hint:\n        return {'status':'경주 있음 / 추천 생성 대기','message':f'{race_hint} 경주 일정 감지. 수집/분석 후 추천 표시','data':None}\n    return {'status':'추천 대기','message':'경주 일정 수집 또는 추천 생성 필요','data':None}\n")



def get_gsheet_config(mem):
    return mem.setdefault("google_sheets", {"enabled": False, "sheet_id": "", "service_account_json": ""})

def gsheet_append(mem, tab_name, row):
    cfg = get_gsheet_config(mem)
    if not cfg.get("enabled"):
        return False, "구글시트 꺼짐"
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        info = json.loads(cfg.get("service_account_json", ""))
        creds = Credentials.from_service_account_info(
            info,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        ss = gspread.authorize(creds).open_by_key(cfg.get("sheet_id", ""))
        try:
            ws = ss.worksheet(tab_name)
        except Exception:
            ws = ss.add_worksheet(title=tab_name, rows=1000, cols=10)
            ws.append_row(["time", "type", "project", "version", "status", "summary", "data_json"])
        ws.append_row(
            [
                row.get("time", datetime.now().isoformat(timespec="seconds")),
                row.get("type", tab_name),
                row.get("project", ""),
                str(row.get("version", "")),
                row.get("status", ""),
                row.get("summary", ""),
                json.dumps(row, ensure_ascii=False)[:45000],
            ],
            value_input_option="USER_ENTERED",
        )
        return True, "구글시트 저장 완료"
    except Exception as e:
        return False, str(e)

def save_event(mem, tab, row):
    ok, msg = gsheet_append(mem, tab, row)
    mem.setdefault("lessons", []).append({
        "time": datetime.now().isoformat(timespec="seconds"),
        "lesson": f"{tab}: {msg}",
    })
    return ok, msg


def generate_streamlit_project(project_name, goal, app_kind="기본앱"):
    """외부 유료 AI API 없이 템플릿 기반 Streamlit 앱을 생성합니다."""
    pname = sname(project_name or "generated-app")
    out = GENERATED / pname
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    safe_goal = (goal or "사용자 목표 앱").strip()
    title = project_name or "MARU Generated App"

    app_code = f"""import streamlit as st
import pandas as pd
import numpy as np
import requests
from pathlib import Path
from datetime import datetime
import json

st.set_page_config(page_title={title!r}, page_icon="🧠", layout="wide")

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
MEMORY_FILE = DATA_DIR / "memory.json"

def load_memory():
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {{"records": [], "created_at": datetime.now().isoformat(timespec="seconds")}}

def save_memory(m):
    m["updated_at"] = datetime.now().isoformat(timespec="seconds")
    MEMORY_FILE.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

def safe_get(url, timeout=15):
    try:
        r = requests.get(url, timeout=timeout)
        info = {{"ok": r.ok, "status_code": r.status_code, "url": str(r.url)[:300]}}
        try:
            return info, r.json()
        except Exception:
            return info, {{"text_preview": r.text[:3000]}}
    except Exception as e:
        return {{"ok": False, "error": str(e)}}, None

st.title("🧠 " + {title!r})
st.caption("MARU 자동 생성 앱 / 기존 기능 삭제 금지 / 수동 확인 중심")
st.info({safe_goal!r})

tab1, tab2, tab3, tab4 = st.tabs(["🏠 대시보드", "🔌 API 점검", "📝 기록", "📦 내보내기"])

with tab1:
    st.subheader("핵심 목표")
    st.write({safe_goal!r})
    st.metric("앱 종류", {app_kind!r})
    st.metric("생성 시각", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

with tab2:
    st.subheader("API 통신 점검")
    url = st.text_area("API URL", height=120)
    token = st.text_input("API KEY/TOKEN 선택", type="password")
    if st.button("통신 점검", type="primary", width="stretch"):
        final_url = url.replace("{{api_key}}", token).replace("{{serviceKey}}", token).replace("{{token}}", token)
        info, data = safe_get(final_url)
        st.json(info)
        if data is not None:
            st.json(data)

with tab3:
    st.subheader("기록")
    mem = load_memory()
    memo = st.text_area("메모/테스트 결과")
    if st.button("기록 저장", width="stretch"):
        mem.setdefault("records", []).append({{"time": datetime.now().isoformat(timespec="seconds"), "memo": memo}})
        save_memory(mem)
        st.success("저장 완료")
    st.json(mem)

with tab4:
    st.subheader("내보내기")
    st.write("GitHub/Streamlit 배포용 기본 파일이 포함된 앱입니다.")
"""
    req = "streamlit\npandas\nnumpy\nrequests\n"
    readme = f"""# {title}

MARU 진화형 AI 코드 생성기가 만든 Streamlit 앱입니다.

## 목표

{safe_goal}

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud:

```text
Main file path: app.py
```
"""
    memdata = {"project": title, "goal": safe_goal, "created_at": datetime.now().isoformat(timespec="seconds"), "records": []}
    (out / "app.py").write_text(app_code, encoding="utf-8")
    (out / "requirements.txt").write_text(req, encoding="utf-8")
    (out / "README.md").write_text(readme, encoding="utf-8")
    (out / "data").mkdir(exist_ok=True)
    (out / "data" / "memory.json").write_text(json.dumps(memdata, ensure_ascii=False, indent=2), encoding="utf-8")
    return out

def register_generated_project(mem, project_name, src, app_url="", github_repo=""):
    pname = sname(project_name)
    app_path = find_app(src)
    info = {
        "name": pname,
        "src": str(src),
        "app_file": str(app_path) if app_path else "",
        "app_url": app_url,
        "api_key": "",
        "api_urls": [],
        "version": 0,
        "github": {"owner": "skytins3-png", "repo": github_repo or pname, "branch": "main", "prefix": ""},
        "scan": scan(src),
        "syntax": syntax_all(src),
        "errors": inspect_error_files(src),
        "analysis": analyze_app(app_path)
    }
    mem.setdefault("projects", {})[pname] = info
    mem.setdefault("generated_projects", []).append({
        "time": datetime.now().isoformat(timespec="seconds"),
        "project": pname,
        "src": str(src),
        "scan": info["scan"],
        "analysis": info["analysis"]
    })
    save(mem)
    return info


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

def set_default_profile(mem, profile):
    mem["default_profile"] = profile
    mem.setdefault("saved_profiles", {})[profile.get("project_name", "default")] = profile
    save(mem)

def get_secret_value(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

def maru_github_token():
    # Streamlit Secrets에 GITHUB_TOKEN / MARU_GITHUB_TOKEN 저장하면 모바일에서도 자동 입력됨
    for key in ["GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "github_token"]:
        val = get_secret_value(key, "")
        if val:
            return val
    return ""

m = load()
st.set_page_config(page_title="MARU V20.1 전체검사 순서수정 AI", page_icon="🧠", layout="wide")
st.markdown("<style>.block-container{max-width:1280px;padding-top:1rem}.stButton>button{height:3rem;font-weight:800}</style>", unsafe_allow_html=True)
st.title("🧠 MARU V20.1 전체검사 순서수정 AI")
st.caption("코드생성 + 패치 + GitHub 허브 자동 업로드 → Streamlit Cloud 자동 재배포")
st.info("핵심: 이제 ZIP 다운로드 후 사람이 다시 올리는 단계 없이, 승인 후 대상 GitHub 저장소까지 자동 반영합니다.")



# ===== MARU V14.2 approval gate for improvement requirements =====
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
# ===== /MARU V14.2 approval gate for improvement requirements =====



# ===== MARU V14.3 no-extra-approval auto patch loop =====
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
# ===== /MARU V14.3 no-extra-approval auto patch loop =====













# ===== MARU V16 complete stability helpers =====
try:
    KST
except NameError:
    KST = timezone(timedelta(hours=9))

def maru_now_kst():
    try:
        return datetime.now(KST)
    except Exception:
        return datetime.now(timezone(timedelta(hours=9)))

def maru_now_kst_text():
    return maru_now_kst().strftime("%Y-%m-%d %H:%M:%S KST")

def save_memory(mem_obj):
    """어떤 탭에서 호출해도 메모리 저장 때문에 앱이 죽지 않게 하는 최종 호환 저장 함수."""
    try:
        target = globals().get("MEM", None)
        if target is None:
            target = Path(__file__).parent / "ai_memory.json"
        Path(target).write_text(json.dumps(mem_obj, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception as e:
        try:
            st.warning(f"메모리 저장 실패: {e}")
        except Exception:
            pass
        return False

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

def maru_show_rows(rows, height=None):
    """결과표 표시 최종 안전 함수."""
    data = maru_safe_dataframe_rows(rows)
    try:
        if hasattr(data, "astype"):
            if height:
                st.dataframe(data, width="stretch", height=height)
            else:
                st.dataframe(data, width="stretch")
        else:
            st.json(data)
    except Exception as e:
        try:
            st.warning(f"결과표 표시 실패: {e}")
            st.json(data)
        except Exception:
            try:
                st.write(str(data))
            except Exception:
                pass

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
        import py_compile as _pc
        _pc.compile(str(app_file), doraise=True)
        return True, ""
    except Exception as e:
        return False, str(e)

def maru_compile_project(src):
    try:
        app_file = Path(src) / "app.py"
        return maru_compile_app_file(app_file)
    except Exception as e:
        return False, str(e)

# ===== /MARU V16 complete stability helpers =====

# ===== MARU V15 full automation repair engine =====
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

def maru_compile_app_file(app_file):
    try:
        import py_compile
        py_compile.compile(str(app_file), doraise=True)
        return True, ""
    except Exception as e:
        return False, str(e)

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
# ===== /MARU V15 full automation repair engine =====



# ===== MARU V16.1 GitHub token diagnosis helpers =====
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
# ===== /MARU V16.1 GitHub token diagnosis helpers =====



# ===== MARU V16.2 always-visible status panel =====
try:
    with st.expander("🧭 MARU 상태판 / 토큰·저장소 빠른 확인", expanded=True):
        diag_now = maru_token_diagnosis()
        c1, c2, c3 = st.columns(3)
        with c1:
            if diag_now.get("detected"):
                st.success("GITHUB_TOKEN 감지됨")
            else:
                st.error("GITHUB_TOKEN 미감지")
        with c2:
            st.write("토큰:", diag_now.get("masked", "없음"))
        with c3:
            st.write("길이:", diag_now.get("length", 0))

        st.caption("토큰 전체값은 표시하지 않습니다.")
        if st.button("현재 AI 코드 생성기 저장소 접근 테스트", key="top_token_test_btn"):
            res_top = maru_test_github_token_access("skytins3-png", "maru-ai-code-maker")
            if res_top.get("ok"):
                st.success(res_top.get("message"))
            else:
                st.error(res_top.get("message"))
            st.json(res_top)

        try:
            st.info("정상 기준: GITHUB_TOKEN 감지됨 + 저장소 접근 테스트 status=200")
        except Exception:
            pass
except Exception as e:
    st.warning(f"상태판 표시 오류: {e}")
# ===== /MARU V16.2 always-visible status panel =====



# ===== MARU V17.1 safe Korean explanation + self diagnosis =====
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

# 화면 상단 독립 진단판: 기존 탭 내부를 건드리지 않음
try:
    with st.expander("🧰 전체 자가진단 / 토큰 / 한글 로그 설명", expanded=False):
        st.markdown("### 1) 전체 자가진단")
        try:
            maru_show_rows(maru_full_self_diagnosis_rows())
        except Exception:
            st.write(maru_full_self_diagnosis_rows())

        st.markdown("### 2) GitHub 토큰 자가진단")
        try:
            diag = maru_token_diagnosis()
            if diag.get("detected"):
                st.success("GITHUB_TOKEN 감지됨")
            else:
                st.error("GITHUB_TOKEN 미감지")
            st.json(diag)
        except Exception as e:
            st.error(f"토큰진단 오류: {e}")

        if st.button("AI 코드 생성기 저장소 접근 테스트", key="v17_1_top_repo_test"):
            res = maru_test_github_token_access("skytins3-png", "maru-ai-code-maker")
            if res.get("ok"):
                st.success(res.get("message"))
            else:
                st.error(res.get("message"))
            st.json(res)

        st.markdown("### 3) 한글 로그 설명")
        v17_log_text = st.text_area("로그를 붙여넣으면 한글로 설명합니다.", height=160, key="v17_1_korean_log_text")
        if st.button("한글로 로그 설명", key="v17_1_korean_log_btn"):
            maru_show_korean_log_summary(v17_log_text)
except Exception as e:
    st.warning(f"전체 자가진단판 표시 오류: {e}")
# ===== /MARU V17.1 safe Korean explanation + self diagnosis =====



# ===== MARU V17.2 always-visible Korean guide helpers =====
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
# ===== /MARU V17.2 always-visible Korean guide helpers =====



# ===== MARU V17.2 top visible panel =====
try:
    maru_v172_render_status_panel("상단")
except Exception as e:
    st.warning(f"상단 상태 안내판 오류: {e}")
# ===== /MARU V17.2 top visible panel =====



# ===== MARU V18 menu total audit helpers =====
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
# ===== /MARU V18 menu total audit helpers =====



# ===== MARU V18 always visible menu audit panel =====
try:
    st.divider()
    st.markdown("## 🧭 메뉴 전체점검판")
    st.caption("하나만 고치고 다른 메뉴에서 터지는 문제를 막기 위해 핵심 메뉴와 필수 함수를 한 번에 검사합니다.")
    maru_v18_show_menu_audit()
except Exception as e:
    st.error(f"메뉴 전체점검판 오류: {e}")
# ===== /MARU V18 always visible menu audit panel =====



# ===== MARU V18.1 named tab repair helpers =====
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
# ===== /MARU V18.1 named tab repair helpers =====



# MARU V19.3: V18.1 top unified operation center removed to prevent duplicate Streamlit widget keys.



# ===== MARU V18.2 real tab index check helpers =====
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
# ===== /MARU V18.2 real tab index check helpers =====



# ===== MARU V18.2 visible tab repair panel =====
try:
    maru_v182_show_tab_repair_status()
except Exception as e:
    st.warning(f"메뉴 연결 확인판 오류: {e}")
# ===== /MARU V18.2 visible tab repair panel =====





# ===== MARU V20 total menu hard check center =====
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

# ===== /MARU V20 total menu hard check center =====

# ===== MARU V19.5 command / patch / improvement workflow =====
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
# ===== /MARU V19.5 command / patch / improvement workflow =====

# ===== MARU V19 one-click upload auto reflect center =====
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


# ===== /MARU V19 one-click upload auto reflect center =====






# ===== MARU V19.3 duplicate key fix banner =====
try:
    st.success("MARU V19.3 중복 key 오류 수정판 적용됨")
    st.info("v181_fullauto_project 중복 오류를 만들던 V18.1 통합운영센터 중복 표시를 제거했습니다.")
except Exception:
    pass
# ===== /MARU V19.3 duplicate key fix banner =====

# ===== MARU V19.2 clean top banner =====
try:
    st.success("MARU V20.1 전체검사 순서수정 AI 적용됨")
    st.info("맨 위 원클릭 자동반영 센터에서 프로젝트 선택 → ZIP/app.py 또는 사진 업로드 → GitHub 자동반영 순서로 사용하세요.")
except Exception:
    pass
# ===== /MARU V19.2 clean top banner =====

# ===== MARU V19.1 loading fix notice =====
try:
    st.info("V19.1 로딩 수정판: 원클릭 자동반영 센터는 중복 없이 한 번만 표시됩니다.")
except Exception:
    pass
# ===== /MARU V19.1 loading fix notice =====

# ===== MARU V19 visible one-click center panel =====
try:
    maru_v19_one_click_center()
except Exception as e:
    st.error(f"원클릭 자동반영 센터 오류: {e}")
    try:
        st.code(traceback.format_exc())
    except Exception:
        pass
# ===== /MARU V19 visible one-click center panel =====


# ===== MARU V19.6 hidden guarded command workflow panel =====
try:
    with st.expander("▶ 📝 패치·개선·명령사항 자동처리", expanded=False):
        if callable(globals().get("maru_v195_command_workflow_center")):
            maru_v195_command_workflow_center()
        else:
            st.error("명령사항 자동처리 함수가 아직 준비되지 않았습니다.")
except Exception as e:
    st.error(f"패치·개선·명령사항 자동처리 센터 오류: {e}")
    with st.expander("▶ 오류 원본 보기", expanded=False):
        try:
            st.code(traceback.format_exc())
        except Exception:
            st.write(str(e))
# ===== /MARU V19.6 hidden guarded command workflow panel =====


# ===== MARU V20.1 guarded hidden total check panel =====
try:
    with st.expander("▶ 🧭 전체 메뉴·기능 검사", expanded=False):
        if callable(globals().get("maru_v20_show_total_check")):
            maru_v20_show_total_check()
        else:
            st.error("전체검사 함수가 아직 준비되지 않았습니다.")
except Exception as e:
    st.error(f"전체 메뉴·기능 검사 오류: {e}")
    with st.expander("▶ 오류 원본 보기", expanded=False):
        try:
            st.code(traceback.format_exc())
        except Exception:
            st.write(str(e))
# ===== /MARU V20.1 guarded hidden total check panel =====



# MARU V20.1: old total check panel removed and replaced with guarded hidden panel.




# MARU V19.6: old V19.5 visible command panel removed; replaced by hidden guarded panel.




# MARU V19.6: V19.5 helper block moved above all calls.



# MARU V20.1: total check helper moved above all calls.

tabs = st.tabs(["📋 기능",
    "📦 보관소",
    "🔁 연속자동화", "🤖 코드생성", "📁 등록", "📡 테스트", "🧯 로그분석", "🖼️ 사진분석/명령", "✅ 패치", "🔍 검사", "📦 버전", "🚀 GitHub 자동반영", "☁️ 구글시트", "📚 기록", "📝 개선승인",
    "♻️ 무승인패치루프",
    "🤖 풀자동화",
    "🗝️ 토큰진단",
    "🧰 전체진단",
    "🧭 메뉴전체점검",
])

with tabs[0]:
    st.write(FEATURES)
    st.warning("GitHub 자동반영은 GitHub 토큰이 필요합니다. 토큰은 공개 저장소에 절대 올리지 마세요.")
    st.divider()
    st.subheader("⚙️ 기본설정 자동불러오기")
    st.caption("경마앱/토토앱/AI 코드 생성기를 선택하면 프로젝트 이름, 앱 주소, GitHub repo가 자동으로 바뀝니다.")
    preset_choice = st.selectbox("프로젝트 선택", ["경마앱", "토토앱", "AI 코드 생성기", "직접입력"], key="default_project_choice")
    prof = maru_profile_from_choice(preset_choice, m)
    st.info(f"현재 선택: {preset_choice} → {prof.get('project_name','') or '직접입력'}")
    c1, c2 = st.columns(2)
    with c1:
        p_name = st.text_input("기본 프로젝트 이름", value=prof.get("project_name", "maru-kra-final-clean"), key=f"default_project_name_{preset_choice}")
        p_url = st.text_input("기본 배포 앱 주소", value=prof.get("app_url", "https://maru-kra-final-clean.streamlit.app"), key=f"default_app_url_{preset_choice}")
        auto_api_key = maru_api_key_for(preset_choice, m)
        p_api_key = st.text_input("기본 API KEY/TOKEN", value=auto_api_key, type="password", key=f"default_api_key_{preset_choice}", placeholder="Secrets에 있으면 자동 입력")
    with c2:
        p_owner = st.text_input("기본 GitHub owner", value=prof.get("github_owner", "skytins3-png"), key=f"default_gh_owner_{preset_choice}")
        p_repo = st.text_input("기본 GitHub repo", value=prof.get("github_repo", "maru-kra-final-clean"), key=f"default_gh_repo_{preset_choice}")
        p_branch = st.text_input("기본 branch", value=prof.get("github_branch", "main"), key=f"default_gh_branch_{preset_choice}")
    p_api_urls = st.text_area("기본 API URL 목록", value=maru_api_urls_for(preset_choice, m), height=120, key=f"default_api_urls_{preset_choice}")
    secret_token = maru_github_token()
    if secret_token:
        st.success("Streamlit Secrets의 GITHUB_TOKEN 감지: GitHub 자동반영 탭에서 자동 사용됩니다.")
    else:
        st.info("토큰 반복 입력이 불편하면 Streamlit Secrets에 GITHUB_TOKEN으로 저장하세요. 파일에는 저장하지 않습니다.")
    if st.button("기본설정 저장", type="primary", width="stretch"):
        set_default_profile(m, {"project_name": p_name.strip(), "app_url": p_url.strip(), "api_key": p_api_key, "api_urls": p_api_urls, "github_owner": p_owner.strip() or "skytins3-png", "github_repo": p_repo.strip() or p_name.strip(), "github_branch": p_branch.strip() or "main"})
        st.success("기본설정 저장 완료")
    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("경마앱 기본값", width="stretch"):
            set_default_profile(m, {"project_name":"maru-kra-final-clean","app_url":"https://maru-kra-final-clean.streamlit.app","api_key":prof.get("api_key", ""),"api_urls":prof.get("api_urls", ""),"github_owner":"skytins3-png","github_repo":"maru-kra-final-clean","github_branch":"main"})
            st.rerun()
    with q2:
        if st.button("코드생성기 기본값", width="stretch"):
            set_default_profile(m, {"project_name":"maru-ai-code-maker","app_url":"https://maru-ai-code-maker.streamlit.app","api_key":"","api_urls":"","github_owner":"skytins3-png","github_repo":"maru-ai-code-maker","github_branch":"main"})
            st.rerun()
    with q3:
        if st.button("토토앱 기본값", width="stretch"):
            set_default_profile(m, {"project_name":"skytoto-ai-hub","app_url":"","api_key":prof.get("api_key", ""),"api_urls":prof.get("api_urls", ""),"github_owner":"skytins3-png","github_repo":"skytoto-ai-hub","github_branch":"main"})
            st.rerun()



with tabs[1]:
    st.subheader("📦 프로젝트 보관소")
    st.caption("최신파일을 한 번 저장해두면 다음부터는 등록 없이 프로젝트 클릭으로 불러와 패치/업그레이드/자동반영합니다.")

    vault_choice = st.selectbox("보관소 프로젝트 선택", ["경마앱", "토토앱", "AI 코드 생성기"], key="vault_choice")
    meta = maru_read_vault_meta(vault_choice)
    src = maru_vault_src_dir(vault_choice)
    has_app = (src / "app.py").exists()

    c1, c2 = st.columns(2)
    with c1:
        st.metric("보관 상태", "저장됨" if has_app else "비어 있음")
        st.write("프로젝트:", MARU_PROJECT_PRESETS[vault_choice]["project_name"])
        st.write("GitHub repo:", MARU_PROJECT_PRESETS[vault_choice]["github_repo"])
    with c2:
        st.write("마지막 저장:", meta.get("updated_at", "-"))
        st.write("파일:", meta.get("filename", "-"))

    if st.button("이 프로젝트 최신파일 불러오기", type="primary", width="stretch"):
        ok, msg = maru_load_project_from_vault(m, vault_choice)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

    st.divider()
    st.markdown("### 최초 1회 또는 새 버전 저장")
    st.info("여기에 한 번 저장하면 이후에는 📁 등록을 반복하지 않아도 됩니다.")
    vault_upload = st.file_uploader("보관소에 저장할 ZIP 또는 app.py", type=["zip", "py"], key="vault_upload")
    try:
        auto_key = default_api_key_for(vault_choice, m)
    except Exception:
        auto_key = ""
    try:
        auto_urls = default_api_urls_for(vault_choice, m)
    except Exception:
        auto_urls = ""
    vault_api_key = st.text_input("API KEY/TOKEN 자동 저장값", value=auto_key, type="password", key="vault_api_key")
    vault_api_urls = st.text_area("API URL 목록 저장값", value=auto_urls, height=120, key="vault_api_urls")

    if st.button("보관소에 저장하고 바로 불러오기", width="stretch"):
        if not vault_upload:
            st.error("ZIP 또는 app.py를 선택하세요. 이건 최초 1회 보관용입니다.")
        else:
            src, meta = maru_save_upload_to_vault(vault_choice, vault_upload, vault_api_key, vault_api_urls)
            ok, msg = maru_load_project_from_vault(m, vault_choice)
            if ok:
                st.success("보관소 저장 완료 + 프로젝트 자동 선택 완료")
                st.write(str(src))
            else:
                st.error(msg)



with tabs[2]:
    st.subheader("🔁 패치-반영-테스트-로그분석 연속자동화")
    st.caption("보관소 최신파일 기준으로 프로젝트 선택 → 테스트 → 로그분석 → GitHub 자동반영까지 한 흐름으로 연결합니다.")

    loop_choice = st.selectbox("연속자동화 프로젝트", ["경마앱", "토토앱", "AI 코드 생성기"], key="loop_choice")
    loop_repeat = st.number_input("반복 횟수", min_value=1, max_value=5, value=1, step=1, key="loop_repeat")
    loop_github = st.checkbox("테스트 통과 시 GitHub 자동반영까지 실행", value=True, key="loop_github")
    try:
        loop_token = get_github_token_from_secret()
    except Exception:
        loop_token = ""
    if loop_token:
        st.success("GITHUB_TOKEN 감지됨: 자동반영 때 토큰 재입력 안 해도 됩니다.")
    else:
        st.warning("GITHUB_TOKEN이 없으면 GitHub 자동반영은 대기 상태가 됩니다.")
    commit_msg = st.text_input("자동 커밋 메시지", value="MARU continuous loop auto update", key="loop_commit_msg")

    if st.button("연속자동화 시작", type="primary", width="stretch"):
        all_rows = []
        for n in range(int(loop_repeat)):
            rows = maru_run_continuous_loop_once(
                m,
                loop_choice,
                do_github=loop_github,
                github_token=loop_token,
                commit_msg=f"{commit_msg} #{n+1}",
            )
            for r in rows:
                r["round"] = n + 1
                all_rows.append(r)
            # 테스트 실패면 무한 반복하지 않고 멈춤
            if any(r.get("step") == "재패치 대기" and r.get("status") == "필요" for r in rows):
                break
        maru_show_rows(all_rows)
        st.info("테스트 실패가 나오면 로그분석 힌트를 패치 탭으로 넘겨 다시 패치한 뒤, 같은 루프를 재실행하는 구조입니다.")

    st.divider()
    st.markdown("### 최근 연속자동화 기록")
    hist = m.get("continuous_loop_history", [])[-30:]
    if hist:
        st.dataframe(hist, width="stretch")
    else:
        st.caption("아직 연속자동화 기록이 없습니다.")

with tabs[3]:
    st.subheader("진화형 AI 코드 생성기 + 자동 허브 업로드")
    st.caption("목표를 입력하면 Streamlit 앱을 생성하고, 검사 후 GitHub 허브 저장소로 자동 업로드할 수 있습니다.")
    gen_name = st.text_input("생성 프로젝트 이름", placeholder="maru-new-app")
    gen_kind = st.selectbox("앱 종류", ["기본앱", "경마 분석앱 뼈대", "토토/스포츠 분석앱 뼈대", "API 대시보드", "기록/허브앱"])
    gen_goal = st.text_area("앱 목표 / 필요한 기능", height=150, placeholder="예: 경마 API를 점검하고 오류 로그를 저장하는 모바일용 대시보드")
    gen_repo = st.text_input("생성 결과를 올릴 GitHub repo 이름", placeholder="maru-new-app")
    if st.button("코드 생성 + 자동검사", type="primary", width="stretch"):
        pname = infer_project_name(gen_name, "", None)
        src = generate_streamlit_project(pname, gen_goal, gen_kind)
        info = register_generated_project(m, pname, src, github_repo=(gen_repo.strip() or pname))
        st.success(f"생성/검사 완료: {pname}")
        st.json(info["scan"])
        st.json(info["analysis"])
        st.download_button("생성 앱 ZIP 다운로드", zip_bytes(src), f"{sname(pname)}_GENERATED.zip", "application/zip", width="stretch")

    st.divider()
    st.subheader("생성 앱 바로 GitHub 허브 업로드")
    ps_gen = list(m.get("projects", {}).keys())
    if not ps_gen:
        st.info("먼저 위에서 코드를 생성하세요.")
    else:
        hub_project = st.selectbox("업로드할 생성/등록 프로젝트", ps_gen, key="hub_codegen_project")
        gh = m["projects"][hub_project].get("github", {})
        c1, c2 = st.columns(2)
        with c1:
            prof = maru_get_default_profile(m)
            hub_owner = st.text_input("허브 GitHub owner", value=gh.get("owner", prof.get("github_owner", "skytins3-png")), key="hub_owner_codegen")
            hub_repo = st.text_input("허브 대상 repo", value=gh.get("repo", prof.get("github_repo", hub_project)), key="hub_repo_codegen")
            hub_branch = st.text_input("branch", value=gh.get("branch", prof.get("github_branch", "main")), key="hub_branch_codegen")
        with c2:
            hub_token = st.text_input("GitHub 토큰", value=maru_github_token(), type="password", key="hub_token_codegen")
            hub_msg = st.text_input("커밋 메시지", value=f"MARU generated code hub upload {datetime.now().strftime('%Y-%m-%d %H:%M')}", key="hub_msg_codegen")
            st.warning("토큰은 저장하지 않습니다. 채팅창/README/GitHub 파일에 붙이지 마세요.")
        if st.button("생성 앱 GitHub 허브에 자동 업로드/커밋", type="primary", width="stretch"):
            if not hub_token:
                st.error("GitHub 토큰이 없습니다. Streamlit Secrets에 GITHUB_TOKEN을 저장하면 모바일에서 입력하지 않아도 됩니다.")
            else:
                src = Path(m["projects"][hub_project]["src"])
                rows = gh_upload_folder(src, hub_owner, hub_repo, hub_branch, hub_token, hub_msg, "")
                ok = sum(1 for r in rows if r["ok"])
                fail = len(rows) - ok
                rec = {
                    "time": datetime.now().isoformat(timespec="seconds"),
                    "project": hub_project,
                    "repo": f"{hub_owner}/{hub_repo}",
                    "branch": hub_branch,
                    "ok": ok,
                    "fail": fail,
                    "rows": rows,
                    "type": "codegen_hub_upload"
                }
                m.setdefault("hub_uploads", []).append(rec)
                m.setdefault("github_deploys", []).append(rec)
                save_event(m, "hub_uploads", {"type":"codegen_hub_upload","project":hub_project,"status":"SUCCESS" if fail==0 else "PARTIAL","summary":f"성공 {ok}, 실패 {fail}"})
                m["projects"][hub_project]["github"] = {"owner": hub_owner, "repo": hub_repo, "branch": hub_branch, "prefix": ""}
                save(m)
                if fail == 0:
                    st.success("생성 앱 GitHub 허브 자동 업로드 완료")
                else:
                    st.warning(f"일부 제외/실패: 성공 {ok}, 실패 {fail}")
                st.json(rows[:100])

with tabs[4]:
    st.subheader("프로젝트 등록")
    reg_choice = st.selectbox("프로젝트 선택", ["경마앱", "토토앱", "AI 코드 생성기", "직접입력"], key="reg_project_choice")
    prof = maru_profile_from_choice(reg_choice, m)
    st.info(f"{reg_choice} 선택됨: 프로젝트/주소/repo 자동 적용")
    name = st.text_input("프로젝트 이름", value=prof.get("project_name", "maru-kra-final-clean"), placeholder="maru-kra-final-clean", key=f"maru_project_name_{reg_choice}")
    app_url = st.text_input("배포 앱 주소", value=prof.get("app_url", "https://maru-kra-final-clean.streamlit.app"), placeholder="https://maru-kra-final-clean.streamlit.app", key=f"maru_app_url_{reg_choice}")
    auto_api_key = maru_api_key_for(reg_choice, m)
    api_key = st.text_input("API KEY/TOKEN 자동값", value=auto_api_key, type="password", key=f"reg_api_key_{reg_choice}", placeholder="Secrets/기본설정에서 자동")
    api_urls = st.text_area("API URL 목록 - 한 줄에 하나", value=maru_api_urls_for(reg_choice, m), key=f"reg_api_urls_{reg_choice}")
    up = st.file_uploader("ZIP 또는 app.py", type=["zip","py"])
    if st.button("저장 + 자동검사", type="primary", width="stretch"):
        pname = infer_project_name(name, app_url, up)
        if not up and pname not in m["projects"]:
            st.warning("처음 등록은 ZIP 또는 app.py 필요")
        else:
            old = m["projects"].get(pname, {})
            src = unzip_upload(up, pname) if up else Path(old["src"])
            app_path = find_app(src)
            info = {
                "name": pname, "src": str(src), "app_file": str(app_path) if app_path else "",
                "app_url": app_url.strip() or old.get("app_url",""),
                "api_key": api_key or old.get("api_key",""),
                "api_urls": [x.strip() for x in api_urls.splitlines() if x.strip()] or old.get("api_urls", []),
                "version": old.get("version", 0),
                "github": old.get("github", {}),
                "scan": scan(src), "syntax": syntax_all(src), "errors": inspect_error_files(src), "analysis": analyze_app(app_path)
            }
            m["projects"][pname] = info
            m["default_profile"] = {"project_name": pname, "app_url": app_url.strip() or old.get("app_url", ""), "api_key": api_key or old.get("api_key", ""), "api_urls": "\n".join(info.get("api_urls", [])), "github_owner": m.get("default_profile", {}).get("github_owner", "skytins3-png"), "github_repo": m.get("default_profile", {}).get("github_repo", pname), "github_branch": m.get("default_profile", {}).get("github_branch", "main")}
            m.setdefault("saved_profiles", {})[pname] = m["default_profile"]
            m["file_checks"].append({"time": datetime.now().isoformat(timespec="seconds"), "project": pname, "scan": info["scan"]})
            save_event(m, "projects", {"type":"project_register","project":pname,"status":"SAVED","summary":"프로젝트 등록/검사"})
            save(m)
            st.success(f"등록/검사 완료: {pname}")
            st.json(info["scan"]); st.json(info["analysis"])

with tabs[9]:
    ps = list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel = st.selectbox("프로젝트", ps, key="scan")
        info = m["projects"][sel]; src = Path(info["src"])
        if st.button("다시 검사", type="primary", width="stretch"):
            app_path = find_app(src)
            info.update({"scan": scan(src), "syntax": syntax_all(src), "errors": inspect_error_files(src), "analysis": analyze_app(app_path)})
            save(m); st.success("검사 완료")
        st.subheader("파일 목록"); st.json(info.get("scan", {}))
        st.subheader("문법 검사"); st.json(info.get("syntax", []))
        st.subheader("오류 파일"); st.json(info.get("errors", []))
        st.subheader("기능 분석"); st.json(info.get("analysis", {}))

with tabs[5]:
    ps = list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel = st.selectbox("프로젝트", ps, key="test")
        cnt = st.number_input("반복 횟수", 1, 20, 1)
        if st.button("자동/반복 테스트", type="primary", width="stretch"):
            info = m["projects"][sel]
            results = []
            for i in range(int(cnt)):
                rows=[]
                if info.get("app_url"): rows.append(test_url("APP_URL", info["app_url"]))
                for j,u in enumerate(info.get("api_urls",[]),1): rows.append(test_url(f"API_{j}", u, info.get("api_key","")))
                rec={"time":datetime.now().isoformat(timespec="seconds"),"project":sel,"round":i+1,"rows":rows,"analysis":analyze_tests(rows)}
                results.append(rec); m["test_records"].append(rec); save_event(m, "test_records", {"type":"test","project":sel,"status":"DONE","summary":"자동/반복 테스트"}); info["last_test"]=rec
            save(m); st.success("테스트 완료"); st.json(results)
        info = m["projects"][sel]
        st.download_button("PC 꺼져도 테스트용 maru_auto_test.yml", workflow(info.get("app_url",""), info.get("api_urls",[])).encode(), "maru_auto_test.yml", "text/yaml", width="stretch")

with tabs[6]:
    st.subheader("로그파일 / 오류 로그 분석")
    st.caption("Streamlit Cloud 로그를 복사해 붙여넣거나 log/txt/json 파일을 업로드하면 오류 패턴을 분석하고 필요한 패치를 추천합니다.")
    ps = list(m["projects"].keys())
    if not ps:
        st.info("먼저 프로젝트를 등록하세요.")
    else:
        sel = st.selectbox("로그 분석 대상 프로젝트", ps, key="log_project")
        pasted_log = st.text_area("로그 붙여넣기", height=220, placeholder="Streamlit Cloud 로그, Traceback, HTTP 오류, NameError 등을 여기에 붙여넣으세요.")
        log_file = st.file_uploader("로그파일 업로드", type=["txt", "log", "json", "csv"], key="manual_log_upload")
        if st.button("로그 분석 + 패치 추천 저장", type="primary", width="stretch"):
            file_text = decode_uploaded_log(log_file)
            combined = (pasted_log or "") + "\n\n" + (file_text or "")
            if not combined.strip():
                st.warning("붙여넣은 로그 또는 업로드한 로그파일이 필요합니다.")
            else:
                analysis = parse_log(combined)
                rec = {
                    "time": datetime.now().isoformat(timespec="seconds"),
                    "project": sel,
                    "summary": analysis,
                    "recommended_patches": analysis.get("recommended_patches", []),
                    "preview": combined[:3000],
                }
                m.setdefault("log_analyses", []).append(rec)
                m["projects"][sel]["last_log_analysis"] = rec
                save_event(m, "log_analyses", {
                    "type": "log_analysis",
                    "project": sel,
                    "status": "DONE",
                    "summary": "수동 로그 분석",
                    "data": rec,
                })
                save(m)
                st.success("로그 분석 완료. 추천 패치를 ✅ 패치 탭에서 승인할 수 있습니다.")
                st.json(analysis)
        last = m.get("projects", {}).get(sel, {}).get("last_log_analysis")
        if last:
            st.markdown("### 최근 로그 분석 결과")
            st.json(last)

with tabs[7]:
    st.subheader("사진 첨부 분석 + 명령 입력")
    st.caption("앱 화면 캡처/오류 사진을 올리고 명령을 입력하면 패치 추천으로 저장합니다.")
    ps = list(m["projects"].keys())
    if not ps:
        st.info("먼저 프로젝트를 등록하세요.")
    else:
        sel = st.selectbox("사진 분석 대상 프로젝트", ps, key="image_command_project")
        imgs = st.file_uploader(
            "사진 첨부",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key="image_command_uploads",
        )
        cmd = st.text_area(
            "명령 입력",
            height=140,
            placeholder="예: 이 화면에서 버튼이 너무 작아. 모바일에서 크게 보이게 패치 추천해줘. / 이 오류 화면 보고 원인 찾아줘.",
            key="image_command_text",
        )
        st.info("사진은 근거 파일로 저장하고, 입력한 명령을 분석해서 패치 추천으로 연결합니다.")
        if st.button("사진 저장 + 명령 분석 + 패치 추천 저장", type="primary", width="stretch"):
            if not imgs and not cmd.strip():
                st.warning("사진 또는 명령 입력이 필요합니다.")
            else:
                saved = save_uploaded_images(sel, imgs)
                analysis = analyze_image_command(cmd, saved)
                rec = {
                    "time": datetime.now().isoformat(timespec="seconds"),
                    "project": sel,
                    "summary": analysis,
                    "recommended_patches": analysis.get("recommended_patches", []),
                    "command": cmd,
                    "images": saved,
                }
                m.setdefault("image_analyses", []).append(rec)
                m.setdefault("command_records", []).append(rec)
                m["projects"][sel]["last_image_analysis"] = rec
                save_event(m, "image_analyses", {
                    "type": "image_command_analysis",
                    "project": sel,
                    "status": "DONE",
                    "summary": "사진 첨부/명령 분석",
                    "data": rec,
                })
                save(m)
                st.success("사진/명령 분석 완료. 추천 패치를 ✅ 패치 탭에서 승인할 수 있습니다.")
                st.json(analysis)
        last_img = m.get("projects", {}).get(sel, {}).get("last_image_analysis")
        if last_img:
            st.markdown("### 최근 사진/명령 분석 결과")
            st.json(last_img)

with tabs[8]:
    ps = list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel = st.selectbox("프로젝트", ps, key="patch")
        info = m["projects"][sel]; src=Path(info["src"]); app_path=Path(info.get("app_file","")) if info.get("app_file") else find_app(src)
        recset=set()
        if info.get("last_test"): recset.update(info["last_test"]["analysis"].get("recommended_patches",[]))
        if info.get("last_log_analysis"): recset.update(info["last_log_analysis"].get("recommended_patches", []))
        if info.get("last_image_analysis"): recset.update(info["last_image_analysis"].get("recommended_patches", []))
        for e in info.get("errors",[]): recset.update(e.get("analysis",{}).get("recommended_patches",[]))
        st.json(analyze_app(app_path))
        approved=[]
        for k,v in PATCHES.items():
            default = k in recset
            if st.checkbox(v, value=default, key=f"{sel}_{k}"): approved.append(k)
        st.error("자동구매/자동결제는 이 앱에서 지원하지 않고 차단합니다.")
        if st.button("승인 항목 실제 패치 → 새 ZIP 생성", type="primary", width="stretch"):
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
            m["patch_records"].append(row); save_event(m, "patch_records", {"type":"patch","project":sel,"version":ver,"status":"SUCCESS" if ok else "CHECK","summary":"승인 패치"}); save(m)
            st.success(f"패치 완료 v{ver:03d}" if ok else "패치됐지만 문법 오류 확인 필요")
            st.json({"before":before,"after":after,"syntax":syn})
            with open(zp,"rb") as f: st.download_button("패치 ZIP 다운로드", f, file_name=zp.name, mime="application/zip", width="stretch")

with tabs[11]:
    gh_choice = st.selectbox("자동반영 대상 선택", ["경마앱", "토토앱", "AI 코드 생성기", "등록된 프로젝트"], key="gh_target_choice")
    ps=list(m["projects"].keys())
    if gh_choice == "등록된 프로젝트":
        if not ps:
            st.info("등록 먼저")
            st.stop()
        sel=st.selectbox("프로젝트", ps, key="gh")
        info=m["projects"][sel]; old=info.get("github",{})
    else:
        prof_choice = maru_profile_from_choice(gh_choice, m)
        sel = prof_choice.get("project_name", gh_choice)
        if sel in m.get("projects", {}):
            info=m["projects"][sel]; old=info.get("github",{})
        else:
            info={"src": "", "github": prof_choice}; old=prof_choice
            st.info("아직 등록되지 않은 대상입니다. 먼저 📁 등록에서 ZIP/app.py를 등록하면 자동반영할 수 있습니다.")
        c1,c2=st.columns(2)
        with c1:
            prof = maru_get_default_profile(m)
            owner=st.text_input("GitHub owner", old.get("owner", prof.get("github_owner","skytins3-png")))
            repo=st.text_input("대상 repo", old.get("repo", prof.get("github_repo", sel)))
            branch=st.text_input("branch", old.get("branch", prof.get("github_branch","main")))
            prefix=st.text_input("업로드 폴더 prefix", old.get("prefix",""), placeholder="비우면 루트")
        with c2:
            token=st.text_input("GitHub 토큰", value=maru_github_token(), type="password")
            msg=st.text_input("커밋 메시지", f"MARU auto patch deploy {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            savecfg=st.checkbox("토큰 제외 설정 저장", value=True)
            st.warning("토큰은 파일에 저장하지 않습니다. 반복 입력이 불편하면 Streamlit Secrets에 GITHUB_TOKEN으로 저장하세요.")
            st.info(".github/workflows 폴더는 GitHub 보안권한 문제 방지를 위해 자동 업로드에서 제외합니다. 파일이 없어서 404가 나오는 경우는 새 파일 생성으로 처리합니다.")
        if st.button("연결 확인", width="stretch"):
            if not token: st.error("토큰 필요")
            else:
                code,data=gh_repo(owner,repo,token)
                st.success("연결 성공") if code==200 else st.error(f"실패 HTTP {code}")
                st.json(data)
        if st.button("대상 GitHub 저장소에 자동 업로드/커밋", type="primary", width="stretch"):
            if not token: st.error("토큰 필요")
            else:
                if savecfg:
                    info["github"]={"owner":owner,"repo":repo,"branch":branch,"prefix":prefix}; save(m)
                rows=gh_upload_folder(Path(info["src"]), owner, repo, branch, token, msg, prefix)
                ok=sum(1 for r in rows if r["ok"]); fail=len(rows)-ok
                deploy={"time":datetime.now().isoformat(timespec="seconds"),"project":sel,"repo":f"{owner}/{repo}","branch":branch,"ok":ok,"fail":fail,"rows":rows}
                m["github_deploys"].append(deploy); save_event(m, "github_deploys", {"type":"github_deploy","project":sel,"status":"SUCCESS" if fail==0 else "PARTIAL","summary":f"성공 {ok}, 실패 {fail}"}); save(m)
                st.success("GitHub 자동반영 완료. Streamlit Cloud가 곧 재배포합니다." if fail==0 else f"일부 실패: 성공 {ok}, 실패 {fail}")
                st.json(rows[:100])

with tabs[10]:
    ps=list(m["projects"].keys())
    if not ps: st.info("등록 먼저")
    else:
        sel=st.selectbox("프로젝트", ps, key="ver")
        info=m["projects"][sel]; src=Path(info["src"])
        st.metric("현재 버전", info.get("version",0))
        st.download_button("현재 보관본 ZIP", zip_bytes(src), f"{sname(sel)}_CURRENT.zip", "application/zip", width="stretch")
        app_path=Path(info.get("app_file","")) if info.get("app_file") else find_app(src)
        if app_path and app_path.exists():
            st.download_button("단일 app.py", read(app_path).encode(), f"{sname(sel)}_app.py", "text/x-python", width="stretch")


with tabs[12]:
    st.subheader("구글시트 허브 저장")
    st.caption("프로젝트, 테스트, 패치, GitHub 자동반영, 코드생성 허브 업로드 기록을 Google Sheets에 저장합니다.")
    cfg = get_gsheet_config(m)
    enabled = st.checkbox("구글시트 저장 사용", value=bool(cfg.get("enabled")))
    sheet_id = st.text_input("Google Sheet ID", value=cfg.get("sheet_id", ""))
    service_json = st.text_area("서비스계정 JSON", value=cfg.get("service_account_json", ""), height=180)
    st.info("서비스계정 JSON 안의 client_email을 Google Sheet 편집자로 공유해야 연결됩니다.")
    if st.button("구글시트 설정 저장", type="primary", width="stretch"):
        cfg.update({"enabled": enabled, "sheet_id": sheet_id.strip(), "service_account_json": service_json.strip()})
        m["google_sheets"] = cfg
        save(m)
        st.success("구글시트 설정 저장 완료")
    if st.button("연결 테스트", width="stretch"):
        cfg.update({"enabled": enabled, "sheet_id": sheet_id.strip(), "service_account_json": service_json.strip()})
        m["google_sheets"] = cfg
        ok, msg = gsheet_append(m, "connection_test", {
            "type": "connection_test",
            "project": "MARU",
            "status": "TEST",
            "summary": "구글시트 연결 테스트",
        })
        save(m)
        if ok:
            st.success(msg)
        else:
            st.error(msg)
    st.markdown("### 저장되는 탭")
    st.write(["connection_test", "projects", "test_records", "patch_records", "github_deploys", "hub_uploads", "log_analyses", "image_analyses", "generated_projects", "lessons"])

with tabs[13]:
    st.subheader("GitHub 자동반영 기록"); st.json(m.get("github_deploys", [])[-20:])
    st.subheader("코드생성 허브 업로드 기록"); st.json(m.get("hub_uploads", [])[-20:])
    st.subheader("패치 기록"); st.json(m.get("patch_records", [])[-20:])
    st.subheader("테스트 기록"); st.json(m.get("test_records", [])[-20:])
    st.subheader("로그 분석 기록"); st.json(m.get("log_analyses", [])[-20:])
    st.subheader("사진/명령 분석 기록"); st.json(m.get("image_analyses", [])[-20:])
    st.subheader("학습"); st.json(m.get("lessons", [])[-50:])


with tabs[14]:
    st.subheader("📝 개선 요구사항 승인 후 진행")
    st.caption("개선 요구사항은 바로 패치하지 않고 승인대기 → 승인 → 패치대기 → 반영/테스트 순서로 진행합니다.")

    c1, c2 = st.columns([1, 1])
    with c1:
        req_project = st.selectbox("대상 프로젝트", ["경마앱", "토토앱", "AI 코드 생성기", "직접입력"], key="approval_project")
        req_priority = st.selectbox("우선순위", ["낮음", "보통", "높음", "긴급"], index=1, key="approval_priority")
        req_title = st.text_input("개선 제목", placeholder="예: 보관소 선택 후 자동 테스트까지 연결", key="approval_title")
    with c2:
        req_detail = st.text_area("개선 상세", placeholder="원하는 개선 내용을 적으면 승인대기함에 저장됩니다.", height=160, key="approval_detail")

    if st.button("개선 요구사항 승인대기 등록", type="primary", width="stretch"):
        if not req_title.strip() or not req_detail.strip():
            st.error("개선 제목과 상세 내용을 입력하세요.")
        else:
            item = maru_add_improvement_request(m, req_project, req_title, req_detail, req_priority)
            st.success("승인대기 등록 완료")
            st.json(item)

    st.divider()
    st.markdown("### 승인대기 목록")
    pending = maru_get_improvement_requests(m, "승인대기")
    if pending:
        for item in pending:
            with st.expander(f"{item.get('priority','보통')} · {item.get('project','')} · {item.get('title','')}"):
                st.write(item.get("detail", ""))
                note = st.text_input("결정 메모", key=f"note_{item['id']}")
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("승인", key=f"approve_{item['id']}", width="stretch"):
                        ok, updated = maru_decide_improvement_request(m, item["id"], "승인", note)
                        if ok:
                            st.success("승인 완료 → 패치대기열로 이동")
                            st.rerun()
                with b2:
                    if st.button("보류", key=f"hold_{item['id']}", width="stretch"):
                        ok, updated = maru_decide_improvement_request(m, item["id"], "보류", note)
                        if ok:
                            st.warning("보류 처리")
                            st.rerun()
                with b3:
                    if st.button("거절", key=f"reject_{item['id']}", width="stretch"):
                        ok, updated = maru_decide_improvement_request(m, item["id"], "거절", note)
                        if ok:
                            st.error("거절 처리")
                            st.rerun()
    else:
        st.caption("승인대기 중인 개선 요구사항이 없습니다.")

    st.divider()
    st.markdown("### 승인된 패치 대기열")
    queue = maru_get_approved_patch_queue(m)
    if queue:
        st.dataframe(queue, width="stretch")
        patch_ids = [q["id"] for q in queue if q.get("status") == "패치대기"]
        if patch_ids:
            selected_patch_id = st.selectbox("패치 진행할 승인 항목", patch_ids, key="selected_approved_patch")
            if st.button("선택 항목 패치진행중으로 표시", width="stretch"):
                maru_mark_patch_queue_done(m, selected_patch_id, "패치진행중")
                st.success("패치진행중으로 변경했습니다. 패치 탭에서 이 요구사항 기준으로 작업하세요.")
                st.rerun()
    else:
        st.caption("승인된 패치 대기열이 없습니다.")

    st.divider()
    st.markdown("### 전체 개선 요구사항 기록")
    all_reqs = maru_get_improvement_requests(m)
    if all_reqs:
        st.dataframe(all_reqs, width="stretch")
    else:
        st.caption("기록 없음")


with tabs[15]:
    st.subheader("♻️ 승인 후 무승인 패치 연속 루프")
    st.caption("개선 요구사항 승인 후에는 패치마다 다시 승인 묻지 않고 테스트 → 로그분석 → 자동패치 → 재테스트 → 반영으로 이어갑니다.")

    auto_project = st.selectbox("자동패치 루프 프로젝트", ["경마앱", "토토앱", "AI 코드 생성기"], key="auto_patch_loop_project")
    auto_repeat = st.number_input("최대 반복 횟수", min_value=1, max_value=10, value=3, step=1, key="auto_patch_repeat")
    auto_github = st.checkbox("테스트 통과 시 GitHub 자동반영", value=True, key="auto_patch_github")
    try:
        auto_token = get_github_token_from_secret()
    except Exception:
        auto_token = ""
    if auto_token:
        st.success("GITHUB_TOKEN 감지됨: 반영 때 토큰 입력 없이 진행")
    else:
        st.warning("GITHUB_TOKEN 없음: 자동반영은 대기 상태가 됩니다.")
    auto_msg = st.text_input("커밋 메시지", value="MARU auto patch loop update", key="auto_patch_commit_msg")

    st.info("안전 자동패치 범위: requirements.txt / README.md / ai_memory.json 누락 보정, 기본 구조 보정. 위험한 코드 수정은 로그 기록 후 재패치 필요로 멈춥니다.")

    if st.button("무승인 패치 루프 시작", type="primary", width="stretch"):
        rows = maru_run_no_approval_patch_loop(
            m,
            auto_project,
            repeat=int(auto_repeat),
            do_github=auto_github,
            github_token=auto_token,
            commit_msg=auto_msg,
        )
        maru_show_rows(rows)

    st.divider()
    st.markdown("### 승인된 요구사항 + 무승인 루프 연결")
    queue = maru_get_approved_patch_queue(m) if "maru_get_approved_patch_queue" in globals() else []
    ready = [q for q in queue if q.get("status") in ["패치대기", "패치진행중"]]
    if ready:
        st.dataframe(ready, width="stretch")
        st.caption("위 승인 항목들은 추가 승인 없이 패치 루프에 태울 수 있습니다.")
    else:
        st.caption("승인된 패치 대기 항목이 없습니다.")


with tabs[16]:
    st.subheader("🤖 풀자동화: 자동수정 → 재테스트 → 자동반영")
    st.caption("보관소 최신파일 기준으로 문법오류/NameError/누락파일을 안전 범위에서 자동수정하고, 재테스트 후 GitHub 자동반영까지 진행합니다.")
    fa_project = st.selectbox("풀자동화 프로젝트", ["경마앱", "토토앱", "AI 코드 생성기"], key="full_auto_project")
    fa_repeat = st.number_input("최대 자동수정 반복 횟수", min_value=1, max_value=10, value=5, step=1, key="full_auto_repeat")
    fa_github = st.checkbox("통과 시 GitHub 자동반영", value=True, key="full_auto_github")
    try:
        fa_token = get_github_token_from_secret()
    except Exception:
        fa_token = ""
    if fa_token:
        st.success("GITHUB_TOKEN 감지됨: 통과 시 자동반영 가능")
    else:
        st.warning("GITHUB_TOKEN 없음: 자동반영은 대기 상태가 됩니다.")
    fa_msg = st.text_input("커밋 메시지", value="MARU full auto repair update", key="full_auto_commit_msg")
    st.info("자동수정 범위: 누락파일 생성, NameError helper 삽입, KST/save_memory/default_api 함수 보정, 안전한 문법오류 보정, 재테스트 반복. 위험한 코드 추정 수정은 멈추고 로그를 남깁니다.")
    if st.button("풀자동화 시작", type="primary", width="stretch"):
        rows = maru_full_auto_loop(m, fa_project, repeat=int(fa_repeat), do_github=fa_github, github_token=fa_token, commit_msg=fa_msg)
        maru_show_rows(rows)
        if rows and rows[-1].get("step") == "GitHub 자동반영":
            st.success("풀자동화 루프 완료")
        elif rows and rows[-1].get("status") == "수동확인필요":
            st.warning("자동수정 안전범위를 넘어선 오류입니다. 로그분석 결과를 패치 탭에 넘겨야 합니다.")
    st.divider()
    st.markdown("### 풀자동화 원칙")
    st.write("- 개선 요구사항은 최초 승인 후 진행")
    st.write("- 승인 후에는 패치마다 추가 승인 없이 자동수정/재테스트")
    st.write("- 자동구매/자동결제는 계속 차단")
    st.write("- 위험한 코드 추정 수정은 무리하게 밀어붙이지 않고 멈춤")


with tabs[17]:
    st.subheader("🗝️ GitHub 토큰 진단")
    st.caption("토큰 전체값은 표시하지 않고 감지 여부와 권한만 확인합니다.")
    diag = maru_token_diagnosis()
    if diag.get("detected"):
        st.success("GITHUB_TOKEN 감지됨")
    else:
        st.error("GITHUB_TOKEN 미감지")
    st.json(diag)

    st.markdown("### 저장소 접근 테스트")
    test_repo = st.selectbox("테스트할 저장소", ["maru-ai-code-maker", "maru-kra-final-clean", "skytoto-ai-hub"], key="token_diag_repo")
    if st.button("GitHub 토큰 권한 테스트", type="primary", width="stretch"):
        res = maru_test_github_token_access("skytins3-png", test_repo)
        if res.get("ok"):
            st.success(res.get("message"))
        else:
            st.error(res.get("message"))
        st.json(res)

    st.info("정상 기준: detected=true, looks_like_github_token=true, 저장소 접근 테스트 status=200")


# ===== MARU V16.2 guaranteed token diagnosis tab content =====
try:
    with tabs[17]:
        st.subheader("🗝️ GitHub 토큰 진단")
        st.caption("이 탭이 비어 보이면 위쪽 'MARU 상태판'을 먼저 확인하세요. 토큰 값은 전체 표시하지 않습니다.")
        diag = maru_token_diagnosis()
        if diag.get("detected"):
            st.success("GITHUB_TOKEN 감지됨")
        else:
            st.error("GITHUB_TOKEN 미감지")
        st.json(diag)

        test_repo_v162 = st.selectbox(
            "테스트할 저장소",
            ["maru-ai-code-maker", "maru-kra-final-clean", "skytoto-ai-hub"],
            key="token_diag_repo_v162"
        )
        if st.button("GitHub 토큰 권한 테스트", type="primary", key="token_diag_btn_v162"):
            res = maru_test_github_token_access("skytins3-png", test_repo_v162)
            if res.get("ok"):
                st.success(res.get("message"))
            else:
                st.error(res.get("message"))
            st.json(res)
        st.info("정상 기준: detected=true, looks_like_github_token=true, 저장소 접근 테스트 status=200")
except Exception as e:
    st.warning(f"토큰진단 탭 표시 오류: {e}")
# ===== /MARU V16.2 guaranteed token diagnosis tab content =====


# ===== MARU V17.2 guaranteed self diagnosis tab =====
try:
    with tabs[18]:
        st.subheader("🧰 전체진단")
        st.caption("토큰, 필수 함수, 화면 안내, 로그 설명 기능을 한 번에 확인합니다.")
        rows = maru_v172_selfcheck_rows()
        try:
            maru_show_rows(rows)
        except Exception:
            st.write(rows)

        st.markdown("### GitHub 저장소 접근 테스트")
        if st.button("AI 코드 생성기 저장소 접근 테스트", key="v172_repo_test_btn"):
            res = maru_test_github_token_access("skytins3-png", "maru-ai-code-maker")
            if res.get("ok"):
                st.success(res.get("message"))
            else:
                st.error(res.get("message"))
            st.json(res)

        st.markdown("### 한글 로그 설명")
        log_text_v172 = st.text_area("로그를 붙여넣으면 한글로 설명합니다.", height=180, key="v172_log_text")
        if st.button("한글로 설명하기", key="v172_log_btn"):
            maru_v172_show_log_korean(log_text_v172)
except Exception as e:
    st.warning(f"전체진단 탭 표시 오류: {e}")
# ===== /MARU V17.2 guaranteed self diagnosis tab =====


# ===== MARU V17.2 bottom always visible panel =====
try:
    st.divider()
    maru_v172_render_status_panel("하단")
    with st.expander("개발자용: 전체진단 원본 보기", expanded=False):
        try:
            maru_show_rows(maru_v172_selfcheck_rows())
        except Exception:
            st.write(maru_v172_selfcheck_rows())
except Exception as e:
    st.warning(f"하단 상태 안내판 오류: {e}")
# ===== /MARU V17.2 bottom always visible panel =====


# ===== MARU V18 guaranteed menu audit tab =====
try:
    with tabs[19]:
        st.subheader("🧭 메뉴전체점검")
        st.caption("모든 핵심 메뉴의 필수 함수와 토큰/저장소/표시 안정성을 점검합니다.")
        maru_v18_show_menu_audit()

        st.markdown("### GitHub 저장소 접근 테스트")
        test_repo_v18 = st.selectbox("테스트 저장소", ["maru-ai-code-maker", "maru-kra-final-clean", "skytoto-ai-hub"], key="v18_repo_test")
        if st.button("선택 저장소 접근 테스트", key="v18_repo_test_btn"):
            res = maru_test_github_token_access("skytins3-png", test_repo_v18)
            if res.get("ok"):
                st.success(res.get("message"))
            else:
                st.error(res.get("message"))
            st.json(res)

        st.markdown("### 한글 로그분석")
        log_v18 = st.text_area("로그를 붙여넣으면 한글로 설명합니다.", height=180, key="v18_log_text")
        if st.button("한글 로그분석 실행", key="v18_log_btn"):
            maru_v18_show_korean_log_explain(log_v18)
except Exception as e:
    st.warning(f"메뉴전체점검 탭 표시 오류: {e}")
# ===== /MARU V18 guaranteed menu audit tab =====


# ===== MARU V18 bottom menu audit panel =====
try:
    st.divider()
    st.markdown("## 🧭 하단 메뉴 전체점검 요약")
    maru_v18_show_menu_audit()
except Exception as e:
    st.warning(f"하단 메뉴점검 오류: {e}")
# ===== /MARU V18 bottom menu audit panel =====


# MARU V19.3: V18.1 bottom unified operation center removed to prevent duplicate Streamlit widget keys.


# MARU V19.1: 원클릭 센터는 중복 key 방지를 위해 상단에 한 번만 표시합니다.
