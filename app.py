
import streamlit as st
import pandas as pd
import requests
import zipfile
import json
import re
import os
import shutil
import base64
import traceback
import py_compile
import ast
from pathlib import Path
from datetime import datetime, timezone, timedelta

APP_VERSION = "MARU_MASTER_HUB_FINAL_1.3_CUSTOM_PROJECTS"
KST = timezone(timedelta(hours=9))

PROJECTS = {
    "AI 코드 생성기": {
        "project": "maru-ai-code-maker",
        "owner": "skytins3-png",
        "repo": "maru-ai-code-maker",
        "branch": "main",
        "app_url": "https://maru-ai-code-maker.streamlit.app",
        "keywords": ["코드", "code", "maker", "maru-ai-code-maker"],
    },
    "경마앱": {
        "project": "maru-kra-final-clean",
        "owner": "skytins3-png",
        "repo": "maru-kra-final-clean",
        "branch": "main",
        "app_url": "https://maru-kra-final-clean.streamlit.app",
        "keywords": ["경마", "KRA", "마사회", "horse", "race"],
    },
    "토토앱": {
        "project": "skytoto-ai-hub",
        "owner": "skytins3-png",
        "repo": "skytoto-ai-hub",
        "branch": "main",
        "app_url": "https://skytoto-ai-hub.streamlit.app",
        "keywords": ["토토", "sport", "toto", "sportmonks", "skytoto"],
    },
}

def now_kst():
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")

def vault_root():
    p = Path("project_vault")
    p.mkdir(parents=True, exist_ok=True)
    return p

def safe_name(name):
    return re.sub(r"[^A-Za-z0-9가-힣_.-]+", "_", str(name or "file"))[:120]

def show_rows(rows):
    try:
        cleaned = []
        for r in rows or []:
            if isinstance(r, dict):
                cleaned.append({str(k): "" if v is None else str(v) for k, v in r.items()})
            else:
                cleaned.append({"값": str(r)})
        st.dataframe(pd.DataFrame(cleaned), width="stretch")
    except Exception:
        st.write(rows)

def read_upload(uploaded_file):
    try:
        uploaded_file.seek(0)
    except Exception:
        pass
    return uploaded_file.read()

def custom_projects_file():
    p = vault_root() / "_custom_projects.json"
    if not p.exists():
        p.write_text(json.dumps({}, ensure_ascii=False, indent=2), encoding="utf-8")
    return p

def load_custom_projects():
    try:
        data = json.loads(custom_projects_file().read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def save_custom_projects(data):
    custom_projects_file().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def get_all_projects():
    merged = dict(PROJECTS)
    merged.update(load_custom_projects())
    return merged

def add_custom_project(label, project_slug, owner, repo, branch="main", app_url="", keywords=None):
    label = str(label or "").strip()
    project_slug = str(project_slug or "").strip()
    owner = str(owner or "").strip()
    repo = str(repo or "").strip()
    branch = str(branch or "main").strip() or "main"
    app_url = str(app_url or "").strip()
    keywords = keywords or []
    if not label or not project_slug or not owner or not repo:
        return False, "프로젝트 표시이름 / project slug / owner / repo는 필수입니다."
    all_projects = get_all_projects()
    if label in all_projects:
        return False, f"이미 존재하는 프로젝트 이름입니다: {label}"
    custom = load_custom_projects()
    custom[label] = {
        "project": project_slug,
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "app_url": app_url,
        "keywords": [str(x).strip() for x in keywords if str(x).strip()],
    }
    save_custom_projects(custom)
    return True, f"새 프로젝트 등록 완료: {label} → {owner}/{repo}"

def project_cfg(project_choice):
    projects = get_all_projects()
    return projects.get(project_choice, projects["AI 코드 생성기"])

def get_token():
    for key in ["GITHUB_TOKEN", "MARU_GITHUB_TOKEN", "GITHUB_PAT", "GH_TOKEN"]:
        try:
            val = st.secrets.get(key, "")
            if val:
                return str(val)
        except Exception:
            pass
        val = os.environ.get(key, "")
        if val:
            return val
    return ""

def mask_token(token):
    if not token:
        return "없음"
    return token[:6] + "…" + token[-4:] if len(token) > 12 else token[:2] + "…"

def status_file():
    p = vault_root() / "_master_hub_status.json"
    if not p.exists():
        p.write_text(json.dumps({"events": [], "pending": []}, ensure_ascii=False, indent=2), encoding="utf-8")
    return p

def load_status():
    try:
        return json.loads(status_file().read_text(encoding="utf-8"))
    except Exception:
        return {"events": [], "pending": []}

def save_status(data):
    status_file().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def record_event(project_choice, event_type, status, detail="", file_name="", path="", repo=""):
    data = load_status()
    cfg = project_cfg(project_choice)
    event = {
        "time": now_kst(),
        "project": project_choice,
        "repo": repo or f"{cfg['owner']}/{cfg['repo']}",
        "event": event_type,
        "status": status,
        "file": file_name,
        "path": str(path),
        "detail": str(detail),
    }
    data.setdefault("events", []).insert(0, event)
    data["events"] = data["events"][:300]
    save_status(data)
    return event

def add_pending(item):
    data = load_status()
    item["created_at"] = now_kst()
    item["approved"] = False
    item["deployed"] = False
    item["id"] = item.get("id") or safe_name(item["project"] + "_" + item["created_at"])
    data.setdefault("pending", []).insert(0, item)
    data["pending"] = data["pending"][:100]
    save_status(data)
    return item

def update_pending(pending_id, **updates):
    data = load_status()
    for item in data.get("pending", []):
        if item.get("id") == pending_id:
            item.update(updates)
            item["updated_at"] = now_kst()
            save_status(data)
            return item
    return None

def github_put_file(owner, repo, branch, token, local_file, remote_path, message):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{remote_path}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    sha = None
    old = requests.get(url, headers=headers, params={"ref": branch}, timeout=20)
    if old.status_code == 200:
        sha = old.json().get("sha")
    elif old.status_code != 404:
        return {"ok": False, "file": remote_path, "status": old.status_code, "message": old.text[:300]}
    payload = {
        "message": message,
        "content": base64.b64encode(Path(local_file).read_bytes()).decode("ascii"),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha
    res = requests.put(url, headers=headers, json=payload, timeout=30)
    return {"ok": res.status_code in (200, 201), "file": remote_path, "status": res.status_code, "message": "업로드 성공" if res.status_code in (200, 201) else res.text[:300]}

def github_upload_folder(src_dir, cfg, message):
    token = get_token()
    if not token:
        return [{"ok": False, "file": "-", "status": "NO_TOKEN", "message": "GITHUB_TOKEN 없음"}]
    rows = []
    for p in sorted(Path(src_dir).rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(src_dir)).replace("\\", "/")
        if "__pycache__" in rel or rel.endswith(".pyc") or ".git/" in rel:
            continue
        if "REPORT" in rel or rel.startswith("MARU_V"):
            continue
        rows.append(github_put_file(cfg["owner"], cfg["repo"], cfg["branch"], token, p, rel, message))
    return rows

def test_github_access(project_choice):
    cfg = project_cfg(project_choice)
    token = get_token()
    if not token:
        return {"ok": False, "message": "GITHUB_TOKEN 없음", "masked": "없음"}
    url = f"https://api.github.com/repos/{cfg['owner']}/{cfg['repo']}/contents/app.py"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    try:
        res = requests.get(url, headers=headers, params={"ref": cfg["branch"]}, timeout=20)
        return {"ok": res.status_code == 200, "status": res.status_code, "message": f"{cfg['owner']}/{cfg['repo']} app.py 읽기 {'성공' if res.status_code == 200 else '실패'}", "masked": mask_token(token)}
    except Exception as e:
        return {"ok": False, "message": str(e), "masked": mask_token(token)}

def prepare_source(uploaded_file, project_choice):
    cfg = project_cfg(project_choice)
    root = vault_root() / cfg["project"] / "work"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    name = safe_name(getattr(uploaded_file, "name", "upload.bin"))
    saved = root / name
    saved.write_bytes(read_upload(uploaded_file))
    src = root / "src"
    src.mkdir(parents=True, exist_ok=True)
    if name.lower().endswith(".zip"):
        with zipfile.ZipFile(saved, "r") as z:
            z.extractall(src)
        candidates = list(src.rglob("app.py"))
        if not candidates:
            raise FileNotFoundError("ZIP 안에 app.py가 없습니다.")
        app_file = candidates[0]
        if app_file.parent != src:
            flat = root / "_flat"
            if flat.exists():
                shutil.rmtree(flat)
            shutil.copytree(app_file.parent, flat)
            shutil.rmtree(src)
            flat.rename(src)
    elif name.lower().endswith(".py"):
        (src / "app.py").write_bytes(saved.read_bytes())
    else:
        raise ValueError("ZIP 또는 app.py만 가능합니다.")
    if not (src / "requirements.txt").exists():
        (src / "requirements.txt").write_text("streamlit\npandas\nnumpy\nrequests\n", encoding="utf-8")
    if not (src / "README.md").exists():
        (src / "README.md").write_text(f"# {cfg['project']}\n", encoding="utf-8")
    return src, name

def detect_app_identity(text):
    low = text.lower()
    if "경마" in text or "마사회" in text or "kra" in low or "horse" in low:
        return "경마앱"
    if "토토" in text or "sportmonks" in low or "skytoto" in low:
        return "토토앱"
    if "코드" in text or "code" in low or "maker" in low or "maru-ai-code-maker" in low:
        return "AI 코드 생성기"
    return "알수없음"

def repo_guard(project_choice, src_dir):
    text = (Path(src_dir) / "app.py").read_text(encoding="utf-8", errors="ignore")
    detected = detect_app_identity(text)
    if detected == "알수없음":
        return True, "앱 종류를 확정하지 못했습니다. 전용 칸 선택을 다시 확인하세요."
    if detected != project_choice:
        return False, f"차단: 선택은 {project_choice}인데 파일은 {detected}로 보입니다."
    return True, f"저장소 안전검사 통과: {detected}"

def scan_app(src_dir):
    app_file = Path(src_dir) / "app.py"
    text = app_file.read_text(encoding="utf-8", errors="ignore")
    rows = []
    def add(name, ok, detail, action=""):
        rows.append({"검사항목": name, "상태": "통과" if ok else "확인필요", "설명": str(detail), "조치": action or ("없음" if ok else "패치/확인 필요")})
    try:
        ast.parse(text); add("AST 문법검사", True, "통과")
    except Exception as e:
        add("AST 문법검사", False, str(e), "수동 수정 필요")
    try:
        py_compile.compile(str(app_file), doraise=True); add("py_compile 검사", True, "통과")
    except Exception as e:
        add("py_compile 검사", False, str(e), "수동 수정 필요")
    old_width = len(re.findall(r"use_container_width\s*=", text))
    add("구버전 표 옵션", old_width == 0, f"{old_width}개", "width='stretch' 또는 width='content'로 교체")
    minus = text.count("tabs[-1]")
    add("tabs[-1] 몰림", minus == 0, f"{minus}개", "명시 탭으로 변경")
    keys = re.findall(r'key\s*=\s*["\']([^"\']+)["\']', text)
    dup = sorted([k for k in set(keys) if keys.count(k) > 1])
    add("중복 Streamlit key", len(dup) == 0, dup[:30], "key 고유화 필요")
    return rows, text

def patch_app_text(text):
    patched = text
    changes = []
    n = len(re.findall(r"use_container_width\s*=\s*True", patched))
    if n:
        patched = re.sub(r"use_container_width\s*=\s*True", 'width="stretch"', patched); changes.append(f"use_container_width=True {n}개 교체")
    n = len(re.findall(r"use_container_width\s*=\s*False", patched))
    if n:
        patched = re.sub(r"use_container_width\s*=\s*False", 'width="content"', patched); changes.append(f"use_container_width=False {n}개 교체")
    if "UTC+09:00" in patched or "UTC+09" in patched:
        patched = patched.replace("UTC+09:00", "한국시간 KST (UTC+9)").replace("UTC+09", "한국시간 KST (UTC+9)")
        changes.append("UTC+09 표시를 한국시간 KST로 교체")
    if not changes:
        changes.append("안전하게 자동 교체할 항목 없음. 검사 결과만 보고서에 기록")
    return patched, changes

def write_upgrade(src_dir, patched_text, project_choice, original_file, scan_rows, changes):
    cfg = project_cfg(project_choice)
    out_root = vault_root() / cfg["project"] / "upgraded"
    if out_root.exists():
        shutil.rmtree(out_root)
    shutil.copytree(src_dir, out_root)
    (out_root / "app.py").write_text(patched_text, encoding="utf-8")
    try:
        py_compile.compile(str(out_root / "app.py"), doraise=True)
        syntax_ok, syntax_msg = True, "py_compile 통과"
    except Exception as e:
        syntax_ok, syntax_msg = False, str(e)
    report = {
        "version": APP_VERSION, "created_at": now_kst(), "project": project_choice,
        "repo": f"{cfg['owner']}/{cfg['repo']}", "original_file": original_file,
        "syntax_ok": syntax_ok, "syntax_msg": syntax_msg, "changes": changes, "scan_rows": scan_rows
    }
    report_path = out_root / "MARU_UPGRADE_REPORT.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_root / "MARU_UPGRADE_REPORT.md").write_text("# MARU 업그레이드 보고서\n\n" + json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    zip_path = vault_root() / cfg["project"] / f"{cfg['project']}_UPGRADED.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in out_root.rglob("*"):
            if p.is_file() and "__pycache__" not in str(p):
                z.write(p, p.relative_to(out_root))
    pending = add_pending({"project": project_choice, "repo": f"{cfg['owner']}/{cfg['repo']}", "zip_path": str(zip_path), "folder_path": str(out_root), "report_path": str(report_path), "syntax_ok": syntax_ok, "syntax_msg": syntax_msg, "changes": changes})
    record_event(project_choice, "업그레이드 ZIP 생성", "성공" if syntax_ok else "확인필요", zip_path, original_file, zip_path)
    return out_root, zip_path, report_path, syntax_ok, syntax_msg, pending

def save_command(project_choice, command_type, command_text, files):
    cfg = project_cfg(project_choice)
    root = vault_root() / cfg["project"] / "commands" / safe_name(now_kst() + "_" + command_type)
    root.mkdir(parents=True, exist_ok=True)
    saved_files = []
    for f in files or []:
        name = safe_name(getattr(f, "name", "file.bin"))
        target = root / name
        target.write_bytes(read_upload(f))
        saved_files.append(str(target))
    record = {"created_at": now_kst(), "project": project_choice, "repo": f"{cfg['owner']}/{cfg['repo']}", "type": command_type, "text": command_text, "files": saved_files}
    (root / "command.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "command.md").write_text(f"# MARU 개선 명령\n\n- 프로젝트: {project_choice}\n- 저장소: {cfg['owner']}/{cfg['repo']}\n- 종류: {command_type}\n\n## 내용\n\n{command_text}\n", encoding="utf-8")
    record_event(project_choice, "개선 명령 저장", "성공", command_text[:120], "command.md", root)
    return record, root


def analyze_log_text(log_text):
    text = str(log_text or "")
    rows = []
    rules = [
        ("NameError", "정의되지 않은 변수/함수 호출", "함수 정의 순서 또는 변수명 누락 확인"),
        ("KeyError", "딕셔너리 키 없음", "기본값 .get() 또는 키 생성 로직 추가"),
        ("StreamlitDuplicateElementKey", "Streamlit 위젯 key 중복", "각 위젯 key를 앱/메뉴별 고유값으로 변경"),
        ("DuplicateElementId", "Streamlit 자동 ID 중복", "key를 직접 지정"),
        ("SyntaxError", "파이썬 문법 오류", "괄호/콜론/들여쓰기/문자열 닫힘 확인"),
        ("IndentationError", "들여쓰기 오류", "블록 들여쓰기 정리"),
        ("ModuleNotFoundError", "requirements.txt 누락 가능", "필요 패키지를 requirements.txt에 추가"),
        ("ImportError", "패키지/함수 import 실패", "패키지명 또는 버전 확인"),
        ("FileNotFoundError", "파일 경로 없음", "파일 생성/경로 확인"),
        ("HTTP 500", "외부 API 서버 오류 또는 파라미터 문제", "API URL/키/날짜 파라미터 확인"),
        ("403", "권한/토큰 문제", "GitHub Token/공공데이터 키 권한 확인"),
        ("401", "인증 실패", "토큰 또는 API Key 확인"),
    ]
    for key, meaning, fix in rules:
        if key.lower() in text.lower():
            rows.append({"발견": key, "뜻": meaning, "권장조치": fix})
    if not rows:
        rows.append({"발견": "특정 규칙 매칭 없음", "뜻": "일반 오류 또는 앱 내부 오류일 수 있음", "권장조치": "전체 로그와 app.py를 함께 업그레이드 엔진에 넣어 검사"})
    return rows

def latest_command_for_project(project_choice):
    cfg = project_cfg(project_choice)
    root = vault_root() / cfg["project"] / "commands"
    if not root.exists():
        return ""
    files = sorted(root.rglob("command.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return ""
    try:
        data = json.loads(files[0].read_text(encoding="utf-8"))
        return data.get("text", "")
    except Exception:
        return ""

def apply_command_patch(text, command_text, log_text=""):
    patched = text
    changes = []
    cmd = str(command_text or "")
    log = str(log_text or "")
    combined = (cmd + "\n" + log).lower()

    # Always run safe baseline patch first.
    patched, base_changes = patch_app_text(patched)
    changes.extend(base_changes)

    if "로그분석" in cmd or "로그 분석" in cmd:
        if "def analyze_log_text" not in patched:
            changes.append("로그분석 요청 확인: 현재 최종허브 자체에 로그분석 창 포함")
        else:
            changes.append("로그분석 기능 이미 존재")

    if "명령" in cmd and ("결과" in cmd or "코드" in cmd):
        changes.append("명령 기반 코드 결과창 요청 확인")

    if "다운로드" in cmd or "완성 파일" in cmd or "완성파일" in cmd:
        changes.append("완성 ZIP 다운로드창 요청 확인")

    # Common bug-specific safe patches
    if "streamlitduplicateelementkey" in combined or "duplicate" in combined:
        changes.append("중복 key 로그 감지: 자동 key 일괄변경은 위험하여 검사표에 표시하고 수동 승인 대상으로 남김")

    if "nameerror" in combined:
        changes.append("NameError 로그 감지: 함수 정의 순서/누락 항목을 검사표에 표시")

    if "keyerror" in combined:
        changes.append("KeyError 로그 감지: .get() 기본값 패치 후보로 표시")

    if not changes:
        changes.append("명령에서 안전 자동패치 항목을 찾지 못해 검사 결과와 보고서에 기록")

    return patched, changes

def make_code_preview(patched_text, max_chars=12000):
    text = str(patched_text or "")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n# ... 이하 생략됨. 완성 파일에는 전체 코드가 들어 있습니다."

def download_file_button(path, label, key):
    p = Path(path)
    if p.exists() and p.is_file():
        st.download_button(label, data=p.read_bytes(), file_name=p.name, mime="application/octet-stream", key=key)
        return True
    st.warning(f"파일이 보이지 않습니다: {p}")
    return False


def final_ready_check():
    rows = []
    token = get_token()
    rows.append({
        "점검": "GitHub Token",
        "상태": "통과" if token else "확인필요",
        "설명": "토큰 감지됨" if token else "Streamlit secrets에 GITHUB_TOKEN 필요",
        "다음행동": "진행 가능" if token else "Secrets에 GITHUB_TOKEN 저장",
    })

    for name, cfg in get_all_projects().items():
        rows.append({
            "점검": f"{name} 저장소 분리",
            "상태": "통과",
            "설명": f"{cfg['owner']}/{cfg['repo']}",
            "다음행동": "해당 앱 전용으로만 반영",
        })

    data = load_status()
    pending = data.get("pending", [])
    approved = [x for x in pending if x.get("approved") and not x.get("deployed")]
    created = [x for x in pending if x.get("zip_path")]

    rows.append({
        "점검": "업그레이드 완성파일",
        "상태": "통과" if created else "대기",
        "설명": f"{len(created)}개 생성됨",
        "다음행동": "미리보기·승인 확인" if created else "테스트·패치·업그레이드 먼저 실행",
    })
    rows.append({
        "점검": "승인 후 반영 대기",
        "상태": "통과" if approved else "대기",
        "설명": f"{len(approved)}개 승인됨",
        "다음행동": "GitHub 반영 가능" if approved else "미리보기 화면에서 승인 저장",
    })
    return rows

def show_final_file_board(project_choice=None):
    data = load_status()
    items = data.get("pending", [])
    if project_choice:
        items = [x for x in items if x.get("project") == project_choice]
    if not items:
        st.info("아직 생성된 완성 파일이 없습니다.")
        return

    for item in items[:20]:
        title = f"{item.get('project')} / {item.get('created_at')} / 승인:{item.get('approved')} / 반영:{item.get('deployed')}"
        with st.expander("▶ 완성 파일: " + title, expanded=False):
            st.write("저장소:", item.get("repo"))
            st.write("완성 ZIP:", item.get("zip_path"))
            st.write("완성 폴더:", item.get("folder_path"))
            st.write("보고서:", item.get("report_path"))
            st.write("재검사:", item.get("syntax_msg"))
            download_file_button(item.get("zip_path", ""), "완성 ZIP 다운로드", key=f"final_board_zip_{item['id']}")
            download_file_button(item.get("report_path", ""), "보고서 다운로드", key=f"final_board_report_{item['id']}")
            app_url = get_all_projects().get(item.get("project"), {}).get("app_url", "")
            if app_url:
                st.link_button("Streamlit 앱 열기", app_url)

def backup_before_deploy(item):
    folder = Path(item.get("folder_path", ""))
    if not folder.exists():
        return None, "업그레이드 폴더 없음"
    project = item.get("project", "unknown")
    cfg = project_cfg(project)
    backup_root = vault_root() / cfg["project"] / "backups"
    backup_root.mkdir(parents=True, exist_ok=True)
    stamp = safe_name(now_kst())
    backup_zip = backup_root / f"{cfg['project']}_backup_before_deploy_{stamp}.zip"
    with zipfile.ZipFile(backup_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for p in folder.rglob("*"):
            if p.is_file() and "__pycache__" not in str(p):
                z.write(p, p.relative_to(folder))
    record_event(project, "반영 전 백업 생성", "성공", backup_zip, path=backup_zip)
    return backup_zip, "백업 생성 완료"

def deploy_safety_check(item):
    rows = []
    project = item.get("project", "")
    folder = Path(item.get("folder_path", ""))

    rows.append({
        "점검": "승인 여부",
        "상태": "통과" if item.get("approved") else "차단",
        "설명": "승인됨" if item.get("approved") else "승인 안 됨",
    })
    rows.append({
        "점검": "완성 폴더",
        "상태": "통과" if folder.exists() else "차단",
        "설명": str(folder),
    })

    if folder.exists() and (folder / "app.py").exists():
        try:
            py_compile.compile(str(folder / "app.py"), doraise=True)
            rows.append({"점검": "반영 전 문법검사", "상태": "통과", "설명": "py_compile 통과"})
        except Exception as e:
            rows.append({"점검": "반영 전 문법검사", "상태": "차단", "설명": str(e)})
        try:
            ok, msg = repo_guard(project, folder)
            rows.append({"점검": "저장소 안전검사", "상태": "통과" if ok else "차단", "설명": msg})
        except Exception as e:
            rows.append({"점검": "저장소 안전검사", "상태": "확인필요", "설명": str(e)})
    else:
        rows.append({"점검": "app.py 존재", "상태": "차단", "설명": "완성 폴더 안 app.py 없음"})

    blocked = [r for r in rows if r.get("상태") == "차단"]
    return rows, len(blocked) == 0

def next_action_from_rows(rows):
    blocked = [r for r in rows if r.get("상태") in ["차단", "확인필요"]]
    if not blocked:
        return "진행 가능: 승인 후 GitHub 반영을 눌러도 됩니다."
    first = blocked[0]
    return f"먼저 해결: {first.get('점검')} / {first.get('설명')}"

st.set_page_config(page_title="MARU MASTER HUB FINAL", layout="wide")
st.markdown("## MARU MASTER HUB FINAL")
st.caption("검사 → 패치 → 업그레이드 파일 생성 → 미리보기 확인 → 승인 후 GitHub 반영 / 새 프로젝트도 직접 추가 가능")

tabs = st.tabs(["📌 프로젝트 선택", "📤 파일·사진·명령 등록", "🧪 테스트·패치·업그레이드", "👀 미리보기·승인", "✅ 승인 후 GitHub 반영", "📚 기록·진단"])

with tabs[0]:
    st.subheader("📌 프로젝트 선택")
    st.write("기본 3개 앱 + 나중에 추가할 새 프로젝트까지 여기서 함께 관리합니다.")
    show_rows([{"앱": k, "저장소": f"{v['owner']}/{v['repo']}", "앱 주소": v.get("app_url", "")} for k, v in get_all_projects().items()])

    with st.expander("▶ 새 프로젝트 추가 등록", expanded=False):
        new_label = st.text_input("프로젝트 표시이름", key="new_project_label", placeholder="예: 쇼핑몰앱")
        new_slug = st.text_input("프로젝트 slug", key="new_project_slug", placeholder="예: my-shop-app")
        new_owner = st.text_input("GitHub owner", key="new_project_owner", placeholder="예: skytins3-png")
        new_repo = st.text_input("GitHub repo", key="new_project_repo", placeholder="예: my-shop-app")
        new_branch = st.text_input("branch", value="main", key="new_project_branch")
        new_app_url = st.text_input("배포 앱 주소", key="new_project_app_url", placeholder="예: https://my-shop-app.streamlit.app")
        new_keywords = st.text_input("검색 키워드(쉼표 구분)", key="new_project_keywords", placeholder="예: 쇼핑몰, shop, mall")
        if st.button("새 프로젝트 등록", key="btn_add_custom_project"):
            ok, msg = add_custom_project(
                new_label,
                new_slug,
                new_owner,
                new_repo,
                new_branch,
                new_app_url,
                [x.strip() for x in str(new_keywords).split(",") if x.strip()],
            )
            if ok:
                record_event(new_label, "새 프로젝트 등록", "성공", msg, repo=f"{new_owner}/{new_repo}")
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    with st.expander("▶ 현재 등록된 프로젝트", expanded=True):
        show_rows([{"앱": k, "project": v.get("project",""), "저장소": f"{v.get('owner','')}/{v.get('repo','')}", "branch": v.get("branch",""), "앱 주소": v.get("app_url","")} for k, v in get_all_projects().items()])

    with st.expander("▶ 최종 준비상태 자동점검", expanded=True):
        ready_rows = final_ready_check()
        show_rows(ready_rows)
        st.info(next_action_from_rows(ready_rows))

with tabs[1]:
    st.subheader("📤 파일·사진·명령 등록")
    project_choice = st.selectbox("대상 앱", list(get_all_projects().keys()), key="reg_project")
    cfg = project_cfg(project_choice)
    st.info(f"대상 저장소: {cfg['owner']}/{cfg['repo']}")

    with st.expander("▶ 파일 업로드 저장", expanded=True):
        up = st.file_uploader("원본 ZIP 또는 app.py", type=["zip", "py"], key="reg_file")
        if st.button("허브에 파일 저장", key="reg_save_file"):
            if not up:
                st.error("파일을 먼저 선택하세요.")
            else:
                try:
                    src, name = prepare_source(up, project_choice)
                    ok, msg = repo_guard(project_choice, src)
                    record_event(project_choice, "원본 파일 허브 저장", "성공" if ok else "차단", msg, name, src)
                    st.success(f"허브 저장 완료: {src}") if ok else st.warning(msg)
                except Exception as e:
                    st.error(str(e))

    with st.expander("▶ 사진 업로드 저장", expanded=False):
        photo = st.file_uploader("사진/이미지", type=["png", "jpg", "jpeg", "webp"], key="reg_photo")
        if st.button("사진 허브 저장", key="reg_save_photo"):
            if not photo:
                st.error("사진을 먼저 선택하세요.")
            else:
                root = vault_root() / cfg["project"] / "photos"
                root.mkdir(parents=True, exist_ok=True)
                name = safe_name(getattr(photo, "name", "photo.png"))
                target = root / name
                target.write_bytes(read_upload(photo))
                record_event(project_choice, "사진 허브 저장", "성공", target, name, target)
                st.success(f"사진 저장 완료: {target}")

    with st.expander("▶ 패치·개선 명령 저장", expanded=False):
        ctype = st.selectbox("명령 종류", ["패치", "개선", "오류수정", "사진/화면분석", "기능추가", "UI정리", "기타"], key="cmd_type")
        ctext = st.text_area("명령 내용", height=140, key="cmd_text")
        cfiles = st.file_uploader("첨부파일", type=["png", "jpg", "jpeg", "webp", "txt", "py", "zip", "json", "md"], accept_multiple_files=True, key="cmd_files")
        if st.button("명령 허브 저장", key="cmd_save"):
            if not ctext.strip():
                st.error("명령 내용을 입력하세요.")
            else:
                _, folder = save_command(project_choice, ctype, ctext, cfiles)
                st.success(f"명령 저장 완료: {folder}")

with tabs[2]:
    st.subheader("🧪 테스트·패치·업그레이드")
    project_choice = st.selectbox("업그레이드 대상 앱", list(get_all_projects().keys()), key="upgrade_project")

    with st.expander("▶ 로그분석", expanded=True):
        log_text = st.text_area("오류 로그 붙여넣기", height=180, key="upgrade_log_text", placeholder="Streamlit 오류 로그, Traceback, HTTP 오류 등을 붙여넣으세요.")
        if st.button("로그 분석하기", key="run_log_analysis"):
            rows = analyze_log_text(log_text)
            record_event(project_choice, "로그분석", "완료", json.dumps(rows, ensure_ascii=False)[:300])
            show_rows(rows)

    with st.expander("▶ 명령지시창", expanded=True):
        command_text = st.text_area(
            "패치/개선 명령",
            height=180,
            key="upgrade_command_text",
            placeholder="예: 로그분석 창을 추가하고, 명령에 따라 수정된 코드 결과창과 완성 ZIP 다운로드 버튼을 보여줘."
        )
        col_cmd1, col_cmd2 = st.columns(2)
        with col_cmd1:
            if st.button("이 명령을 허브에 저장", key="save_upgrade_command"):
                if not command_text.strip():
                    st.error("명령 내용을 입력하세요.")
                else:
                    _, folder = save_command(project_choice, "업그레이드명령", command_text, [])
                    st.success(f"명령 저장 완료: {folder}")
        with col_cmd2:
            if st.button("최근 저장 명령 불러오기", key="load_latest_command"):
                latest = latest_command_for_project(project_choice)
                if latest:
                    st.session_state["upgrade_command_loaded"] = latest
                    st.success("최근 명령을 불러왔습니다. 아래 문장을 복사해서 명령창에 넣으세요.")
                    st.code(latest)
                else:
                    st.warning("저장된 명령이 없습니다.")

    uploaded = st.file_uploader("원본 ZIP 또는 app.py 업로드", type=["zip", "py"], key="upgrade_file")
    if st.button("테스트 → 로그분석 → 명령패치 → 업그레이드 ZIP 생성", type="primary", key="run_upgrade"):
        if not uploaded:
            st.error("원본 ZIP 또는 app.py를 먼저 업로드하세요.")
        else:
            try:
                src, original_name = prepare_source(uploaded, project_choice)
                ok_guard, guard_msg = repo_guard(project_choice, src)
                if not ok_guard:
                    record_event(project_choice, "저장소 안전검사", "차단", guard_msg, original_name, src)
                    st.error(guard_msg); st.stop()

                scan_rows, original_text = scan_app(src)
                log_rows = analyze_log_text(log_text)
                patched_text, changes = apply_command_patch(original_text, command_text, log_text)
                out_root, zip_path, report_path, syntax_ok, syntax_msg, pending = write_upgrade(src, patched_text, project_choice, original_name, scan_rows + log_rows, changes)

                result_rows = [
                    {"단계": "원본 준비", "상태": "완료", "설명": str(src)},
                    {"단계": "저장소 안전검사", "상태": "통과", "설명": guard_msg},
                    {"단계": "로그분석", "상태": "완료", "설명": f"{len(log_rows)}개 항목"},
                    {"단계": "검사", "상태": "완료", "설명": f"{len(scan_rows)}개 항목"},
                    {"단계": "명령패치", "상태": "완료", "설명": " / ".join(changes)},
                    {"단계": "재검사", "상태": "통과" if syntax_ok else "확인필요", "설명": syntax_msg},
                    {"단계": "업그레이드 ZIP 생성", "상태": "완료", "설명": str(zip_path)},
                    {"단계": "승인대기 등록", "상태": "완료", "설명": pending["id"]},
                ]
                st.success("업그레이드 ZIP 생성 완료. 아래에서 코드 결과와 완성 파일을 확인하세요.")
                show_rows(result_rows)

                with st.expander("▶ 로그분석 결과", expanded=False):
                    show_rows(log_rows)
                with st.expander("▶ 검사 상세", expanded=False):
                    show_rows(scan_rows)
                with st.expander("▶ 명령에 의해 적용된 패치 내용", expanded=True):
                    for c in changes:
                        st.write("✅", c)

                with st.expander("▶ 명령에 의해 생성된 코드 결과창", expanded=True):
                    st.caption("아래 코드는 미리보기입니다. 완성 파일에는 전체 app.py가 들어갑니다.")
                    st.code(make_code_preview(patched_text), language="python")

                with st.expander("▶ 완성 파일 확인/다운로드", expanded=True):
                    st.write("완성 ZIP:", str(zip_path))
                    st.write("보고서:", str(report_path))
                    download_file_button(zip_path, "완성 ZIP 다운로드", key=f"download_zip_{pending['id']}")
                    download_file_button(report_path, "업그레이드 보고서 다운로드", key=f"download_report_{pending['id']}")
            except Exception as e:
                st.error(f"업그레이드 실패: {e}")
                with st.expander("▶ 오류 원본", expanded=False): st.code(traceback.format_exc())

with tabs[3]:
    st.subheader("👀 미리보기·승인")
    with st.expander("▶ 완성 파일 목록판", expanded=True):
        show_final_file_board()
    pending = load_status().get("pending", [])
    if not pending:
        st.info("승인 대기 중인 업그레이드 결과가 없습니다.")
    for item in pending[:20]:
        with st.expander(f"▶ {item.get('project')} / {item.get('created_at')} / 승인상태: {item.get('approved')}", expanded=False):
            st.write("저장소:", item.get("repo"))
            st.write("업그레이드 ZIP:", item.get("zip_path"))
            st.write("보고서:", item.get("report_path"))
            download_file_button(item.get("zip_path", ""), "완성 ZIP 다운로드", key=f"preview_zip_{item['id']}")
            download_file_button(item.get("report_path", ""), "보고서 다운로드", key=f"preview_report_{item['id']}")
            st.write("재검사:", item.get("syntax_msg"))
            for c in item.get("changes", []): st.write("✅", c)
            approve = st.checkbox("이 결과를 확인했고 GitHub 반영을 승인합니다.", key=f"approve_{item['id']}")
            if st.button("승인 저장", key=f"approve_btn_{item['id']}"):
                if not approve:
                    st.error("승인 체크가 필요합니다.")
                else:
                    update_pending(item["id"], approved=True, approved_at=now_kst())
                    record_event(item["project"], "승인 저장", "성공", item["id"], path=item.get("zip_path"))
                    st.success("승인 저장 완료. 다음 탭에서 GitHub 반영하세요.")

with tabs[4]:
    st.subheader("✅ 승인 후 GitHub 반영")
    approved = [x for x in load_status().get("pending", []) if x.get("approved") and not x.get("deployed")]
    if not approved:
        st.info("승인 후 반영 대기 중인 결과가 없습니다.")
    for item in approved[:20]:
        with st.expander(f"▶ 반영 대기: {item.get('project')} / {item.get('created_at')}", expanded=False):
            st.write("저장소:", item.get("repo"))
            st.write("업그레이드 폴더:", item.get("folder_path"))
            msg = st.text_input("커밋 메시지", value=f"MARU approved upgrade: {item.get('project')}", key=f"commit_{item['id']}")
            with st.expander("▶ 반영 전 최종 안전검사", expanded=True):
                safety_rows, can_deploy = deploy_safety_check(item)
                show_rows(safety_rows)
                st.info(next_action_from_rows(safety_rows))

            if st.button("승인된 파일 GitHub 반영", type="primary", key=f"deploy_{item['id']}"):
                folder = Path(item.get("folder_path", ""))
                safety_rows, can_deploy = deploy_safety_check(item)
                if not can_deploy:
                    st.error("최종 안전검사에서 차단되어 GitHub 반영을 중단했습니다.")
                    show_rows(safety_rows)
                else:
                    backup_zip, backup_msg = backup_before_deploy(item)
                    st.info(f"반영 전 백업: {backup_msg}")
                    if backup_zip:
                        download_file_button(backup_zip, "반영 전 백업 ZIP 다운로드", key=f"backup_zip_{item['id']}")
                    cfg = project_cfg(item["project"])
                    rows = github_upload_folder(folder, cfg, msg)
                    ok = sum(1 for r in rows if r.get("ok"))
                    fail = sum(1 for r in rows if not r.get("ok"))
                    status = "성공" if fail == 0 else "일부실패"
                    record_event(item["project"], "승인 후 GitHub 반영", status, f"성공 {ok} / 실패 {fail}", path=folder)
                    show_rows(rows)
                    if fail == 0:
                        update_pending(item["id"], deployed=True, deployed_at=now_kst())
                        st.success("GitHub 반영 완료. Streamlit 재배포를 기다린 뒤 새로고침하세요.")
                        app_url = get_all_projects().get(item.get("project"), {}).get("app_url", "")
                        if app_url:
                            st.link_button("반영된 Streamlit 앱 열기", app_url)
                    else:
                        st.warning("일부 파일 반영 실패. 상세 결과를 확인하세요.")

with tabs[5]:
    st.subheader("📚 기록·진단")
    with st.expander("▶ GitHub 토큰 진단", expanded=True):
        st.write("토큰:", mask_token(get_token()))
        for name in PROJECTS:
            if st.button(f"{name} 저장소 접근 테스트", key=f"token_test_{name}"):
                st.json(test_github_access(name))
    with st.expander("▶ 전체 기록", expanded=True):
        events = load_status().get("events", [])
        show_rows(events[:100]) if events else st.info("기록이 없습니다.")
    with st.expander("▶ 승인대기/승인 목록", expanded=False):
        show_rows(load_status().get("pending", []))
    with st.expander("▶ 완성 파일 목록/다운로드", expanded=False):
        show_final_file_board()
