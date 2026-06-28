
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

APP_VERSION = "MARU_MASTER_HUB_FINAL_1.0"
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

def project_cfg(project_choice):
    return PROJECTS.get(project_choice, PROJECTS["AI 코드 생성기"])

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

st.set_page_config(page_title="MARU MASTER HUB FINAL", layout="wide")
st.markdown("## MARU MASTER HUB FINAL")
st.caption("검사 → 패치 → 업그레이드 파일 생성 → 미리보기 확인 → 승인 후 GitHub 반영")

tabs = st.tabs(["📌 프로젝트 선택", "📤 파일·사진·명령 등록", "🧪 테스트·패치·업그레이드", "👀 미리보기·승인", "✅ 승인 후 GitHub 반영", "📚 기록·진단"])

with tabs[0]:
    st.subheader("📌 프로젝트 선택")
    st.write("세 앱은 저장소가 분리되어 있습니다. 잘못 섞이지 않게 전용 칸으로 처리합니다.")
    show_rows([{"앱": k, "저장소": f"{v['owner']}/{v['repo']}", "앱 주소": v["app_url"]} for k, v in PROJECTS.items()])

with tabs[1]:
    st.subheader("📤 파일·사진·명령 등록")
    project_choice = st.selectbox("대상 앱", list(PROJECTS.keys()), key="reg_project")
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
    project_choice = st.selectbox("업그레이드 대상 앱", list(PROJECTS.keys()), key="upgrade_project")
    uploaded = st.file_uploader("원본 ZIP 또는 app.py 업로드", type=["zip", "py"], key="upgrade_file")
    if st.button("테스트 → 패치 → 업그레이드 ZIP 생성", type="primary", key="run_upgrade"):
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
                patched_text, changes = patch_app_text(original_text)
                out_root, zip_path, report_path, syntax_ok, syntax_msg, pending = write_upgrade(src, patched_text, project_choice, original_name, scan_rows, changes)
                result_rows = [
                    {"단계": "원본 준비", "상태": "완료", "설명": str(src)},
                    {"단계": "저장소 안전검사", "상태": "통과", "설명": guard_msg},
                    {"단계": "검사", "상태": "완료", "설명": f"{len(scan_rows)}개 항목"},
                    {"단계": "자동패치", "상태": "완료", "설명": " / ".join(changes)},
                    {"단계": "재검사", "상태": "통과" if syntax_ok else "확인필요", "설명": syntax_msg},
                    {"단계": "업그레이드 ZIP 생성", "상태": "완료", "설명": str(zip_path)},
                    {"단계": "승인대기 등록", "상태": "완료", "설명": pending["id"]},
                ]
                st.success("업그레이드 ZIP 생성 완료. 다음 탭에서 미리보기 후 승인하세요.")
                show_rows(result_rows)
                with st.expander("▶ 검사 상세", expanded=False): show_rows(scan_rows)
                with st.expander("▶ 자동패치 내용", expanded=True):
                    for c in changes: st.write("✅", c)
                st.code(str(zip_path))
            except Exception as e:
                st.error(f"업그레이드 실패: {e}")
                with st.expander("▶ 오류 원본", expanded=False): st.code(traceback.format_exc())

with tabs[3]:
    st.subheader("👀 미리보기·승인")
    pending = load_status().get("pending", [])
    if not pending:
        st.info("승인 대기 중인 업그레이드 결과가 없습니다.")
    for item in pending[:20]:
        with st.expander(f"▶ {item.get('project')} / {item.get('created_at')} / 승인상태: {item.get('approved')}", expanded=False):
            st.write("저장소:", item.get("repo"))
            st.write("업그레이드 ZIP:", item.get("zip_path"))
            st.write("보고서:", item.get("report_path"))
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
            if st.button("승인된 파일 GitHub 반영", type="primary", key=f"deploy_{item['id']}"):
                folder = Path(item.get("folder_path", ""))
                if not folder.exists():
                    st.error("업그레이드 폴더가 없습니다. 다시 생성하세요.")
                else:
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
