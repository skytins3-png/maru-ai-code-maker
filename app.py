
import streamlit as st
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import zipfile

APP_DIR = Path(__file__).parent
MEMORY_FILE = APP_DIR / "ai_memory.json"
PROJECTS_DIR = APP_DIR / "generated_projects"
PROJECTS_DIR.mkdir(exist_ok=True)

STREAMLIT_BASIC_APP = """import streamlit as st

st.set_page_config(page_title='AI 생성 앱', layout='wide')

st.title('🤖 AI 생성 앱')
st.write('요청에 맞춰 생성된 기본 Streamlit 앱입니다.')

user_input = st.text_input('입력')
if st.button('실행'):
    st.success(f'입력값: {user_input}')
"""

API_DASHBOARD_APP = """import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title='API 대시보드', layout='wide')

CSS = '<style>.block-container {padding-top: 1rem;} .big-box {border:1px solid #ddd; border-radius:18px; padding:18px;} .big-text {font-size:28px; font-weight:900;}</style>'
st.markdown(CSS, unsafe_allow_html=True)

st.title('📡 실시간 API 대시보드')
st.caption('API URL에 {api_key}, {today}, {today_dash} 같은 값을 넣어두면 자동 치환합니다.')

api_url = st.text_input('API URL')
api_key = st.text_input('API KEY', type='password')

today = datetime.now().strftime('%Y%m%d')
today_dash = datetime.now().strftime('%Y-%m-%d')

if st.button('데이터 가져오기', type='primary', use_container_width=True):
    if not api_url:
        st.warning('API URL을 입력하세요.')
    else:
        try:
            url = (
                api_url
                .replace('{api_key}', api_key)
                .replace('{serviceKey}', api_key)
                .replace('{today}', today)
                .replace('{today_dash}', today_dash)
            )
            res = requests.get(url, timeout=15)
            st.write('상태코드:', res.status_code)

            if res.status_code >= 400:
                st.error('API 호출 오류입니다. URL, 키, 승인 여부, 파라미터를 확인하세요.')

            try:
                data = res.json()
                st.json(data)
            except Exception:
                st.text(res.text[:5000])

        except Exception as e:
            st.error(f'호출 실패: {e}')
"""

def make_default_memory():
    now = datetime.now().isoformat(timespec="seconds")
    return {
        "version": "1.0",
        "created_at": now,
        "lessons": [],
        "successful_patterns": [],
        "failed_patterns": [],
        "test_records": [],
        "templates": {
            "streamlit_basic": {
                "description": "간단한 Streamlit 대시보드 앱",
                "files": {
                    "app.py": STREAMLIT_BASIC_APP,
                    "requirements.txt": "streamlit\npandas\nnumpy\nrequests\n"
                }
            },
            "api_dashboard": {
                "description": "API 호출용 대시보드 기본형",
                "files": {
                    "app.py": API_DASHBOARD_APP,
                    "requirements.txt": "streamlit\npandas\nrequests\n"
                }
            }
        }
    }

def load_memory():
    if MEMORY_FILE.exists():
        try:
            memory = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
            if "templates" not in memory:
                default = make_default_memory()
                default["lessons"] = memory.get("lessons", [])
                default["successful_patterns"] = memory.get("successful_patterns", [])
                default["failed_patterns"] = memory.get("failed_patterns", [])
                default["test_records"] = memory.get("test_records", [])
                memory = default
                save_memory(memory)
            return memory
        except Exception:
            pass
    memory = make_default_memory()
    save_memory(memory)
    return memory

def save_memory(memory):
    memory["updated_at"] = datetime.now().isoformat(timespec="seconds")
    MEMORY_FILE.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")

def slugify(text):
    text = re.sub(r"[^a-zA-Z0-9가-힣_-]+", "_", text.strip())
    return text[:42] or "project"

def infer_project_type(goal):
    g = goal.lower()
    if any(x in g for x in ["api", "실시간", "대시보드", "경마", "토토", "데이터", "sportmonks", "공공데이터"]):
        return "api_dashboard"
    return "streamlit_basic"

def build_improvement_prompt(goal, memory):
    lessons = "\n".join([f"- {x.get('lesson', x)}" for x in memory.get("lessons", [])[-10:]]) or "- 아직 학습 기록 없음"
    success = "\n".join([f"- {x}" for x in memory.get("successful_patterns", [])[-10:]]) or "- 아직 성공 패턴 없음"
    failed = "\n".join([f"- {x}" for x in memory.get("failed_patterns", [])[-10:]]) or "- 아직 실패 패턴 없음"

    return f"""
너는 안전한 코드 생성 AI다.

[사용자 목표]
{goal}

[반드시 지킬 원칙]
1. 기존 기능을 함부로 삭제하지 않는다.
2. API KEY 같은 비밀값은 코드에 직접 박지 않는다.
3. 오류가 나면 원인을 기록하고 다음 생성 때 반영한다.
4. 사용자가 모바일에서 쓰기 쉽게 버튼과 글씨를 크게 만든다.
5. 자동구매, 불법 자동화, 악성 기능은 만들지 않는다.
6. 생성 후 requirements.txt도 함께 만든다.
7. 실패한 코드를 반복하지 말고, 실패 기록을 먼저 확인한다.

[최근 학습 기록]
{lessons}

[성공 패턴]
{success}

[실패 패턴]
{failed}

[출력 형식]
- app.py
- requirements.txt
- README.md
- 수정 요약
""".strip()

def generate_project(goal, memory):
    project_type = infer_project_type(goal)
    template = memory["templates"][project_type]
    name = slugify(goal)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_dir = PROJECTS_DIR / f"{timestamp}_{name}"
    project_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in template["files"].items():
        (project_dir / filename).write_text(content, encoding="utf-8")

    prompt = build_improvement_prompt(goal, memory)
    (project_dir / "AI_IMPROVEMENT_PROMPT.txt").write_text(prompt, encoding="utf-8")

    readme = f"""# 진화형 AI 생성 프로젝트

생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
요청 목표: {goal}

## 실행법

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 진화 방식

1. 목표 입력
2. 코드 생성
3. 문법 검사
4. 성공/실패 패턴 저장
5. 다음 코드 생성 때 기록 반영

## 포함 파일

- app.py
- requirements.txt
- AI_IMPROVEMENT_PROMPT.txt
"""
    (project_dir / "README.md").write_text(readme, encoding="utf-8")
    return project_dir, project_type

def run_python_check(project_dir):
    app_file = project_dir / "app.py"
    if not app_file.exists():
        return False, "app.py 파일이 없습니다."
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(app_file)],
            capture_output=True,
            text=True,
            timeout=20
        )
        if result.returncode == 0:
            return True, "문법 검사 성공"
        return False, result.stderr
    except Exception as e:
        return False, str(e)

def zip_project(project_dir):
    zip_path = project_dir.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in project_dir.rglob("*"):
            z.write(p, p.relative_to(project_dir))
    return zip_path

st.set_page_config(page_title="진화형 AI 코드 메이커", page_icon="🧠", layout="wide")

CSS_MAIN = '<style>.block-container {padding-top: 1.2rem; max-width: 1200px;} .big-card {border: 1px solid #ddd; border-radius: 18px; padding: 18px; background: rgba(250,250,250,0.75);} .big-title {font-size: 34px; font-weight: 900;} .big-score {font-size: 28px; font-weight: 800;} button[kind="primary"] {height: 3rem; font-size: 1.1rem;} textarea {font-size: 1.05rem !important;}</style>'
st.markdown(CSS_MAIN, unsafe_allow_html=True)

memory = load_memory()

st.markdown('<div class="big-title">🧠 진화형 AI 코드 메이커</div>', unsafe_allow_html=True)
st.caption("코드를 만들고, 테스트하고, 실패/성공 기록을 저장해서 다음 생성에 반영하는 안전형 AI 작업실")

tab1, tab2, tab3, tab4 = st.tabs(["🚀 코드 생성", "📚 학습 기록", "🧪 테스트 기록", "⚙️ 메모리 관리"])

with tab1:
    st.subheader("무엇을 만들까요?")
    goal = st.text_area(
        "만들고 싶은 앱/기능을 적으세요",
        height=160,
        placeholder="예: 경마 API 실시간 대시보드 만들어줘. 모바일에서 크게 보이고 API 키는 저장되게 해줘."
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        generate_btn = st.button("🚀 코드 생성", type="primary", use_container_width=True)
    with col2:
        st.info("생성 결과는 generated_projects 폴더에 저장됩니다.")

    if generate_btn:
        if not goal.strip():
            st.warning("목표를 먼저 입력하세요.")
        else:
            project_dir, project_type = generate_project(goal, memory)
            ok, msg = run_python_check(project_dir)
            zip_path = zip_project(project_dir)

            record = {
                "time": datetime.now().isoformat(timespec="seconds"),
                "goal": goal,
                "project_type": project_type,
                "project_dir": str(project_dir),
                "syntax_ok": ok,
                "message": msg
            }

            if ok:
                memory.setdefault("successful_patterns", []).append(
                    f"{project_type}: 문법 검사 통과 / 목표={goal[:80]}"
                )
                memory.setdefault("lessons", []).append({
                    "time": record["time"],
                    "lesson": f"{project_type} 템플릿은 '{goal[:60]}' 요청에서 문법 검사 통과"
                })
                st.success("코드 생성 + 문법 검사 성공")
            else:
                memory.setdefault("failed_patterns", []).append(
                    f"{project_type}: {msg[:120]}"
                )
                memory.setdefault("lessons", []).append({
                    "time": record["time"],
                    "lesson": f"오류 발생: {msg[:160]}"
                })
                st.error("코드는 생성했지만 문법 검사에서 문제가 발견되었습니다.")

            memory.setdefault("test_records", []).append(record)
            save_memory(memory)

            st.write("프로젝트 폴더:", str(project_dir))
            st.code(msg)

            with open(zip_path, "rb") as f:
                st.download_button(
                    "📦 생성 프로젝트 ZIP 다운로드",
                    data=f,
                    file_name=zip_path.name,
                    mime="application/zip",
                    use_container_width=True
                )

            st.subheader("다음 개선용 AI 프롬프트")
            st.code((project_dir / "AI_IMPROVEMENT_PROMPT.txt").read_text(encoding="utf-8")[:4000])

with tab2:
    st.subheader("AI가 기억하는 학습 내용")
    lessons = memory.get("lessons", [])
    if not lessons:
        st.info("아직 학습 기록이 없습니다.")
    else:
        for item in reversed(lessons[-30:]):
            st.markdown(f"""
<div class="big-card">
<b>{item.get('time', '')}</b><br>
{item.get('lesson', '')}
</div>
<br>
""", unsafe_allow_html=True)

    st.subheader("성공 패턴")
    st.json(memory.get("successful_patterns", [])[-20:])

    st.subheader("실패 패턴")
    st.json(memory.get("failed_patterns", [])[-20:])

with tab3:
    st.subheader("테스트 기록")
    records = memory.get("test_records", [])
    if not records:
        st.info("아직 테스트 기록이 없습니다.")
    else:
        for r in reversed(records[-20:]):
            status = "✅ 성공" if r.get("syntax_ok") else "❌ 실패"
            st.markdown(f"### {status} / {r.get('time')}")
            st.write("목표:", r.get("goal"))
            st.write("프로젝트:", r.get("project_dir"))
            st.code(r.get("message", ""))

with tab4:
    st.subheader("메모리 원본")
    st.caption("이 JSON이 이 앱의 학습 기억입니다.")
    st.json(memory)

    st.divider()
    lesson_text = st.text_area("직접 학습 내용 추가", placeholder="예: 모바일에서는 버튼을 크게 만들고, API 키는 secrets 또는 JSON 저장소를 사용한다.")
    if st.button("➕ 학습 내용 저장", use_container_width=True):
        if lesson_text.strip():
            memory.setdefault("lessons", []).append({
                "time": datetime.now().isoformat(timespec="seconds"),
                "lesson": lesson_text.strip()
            })
            save_memory(memory)
            st.success("학습 내용 저장 완료")
            st.rerun()

    if st.button("🧹 학습 메모리 초기화", use_container_width=True):
        save_memory(make_default_memory())
        st.warning("초기화 완료")
        st.rerun()
