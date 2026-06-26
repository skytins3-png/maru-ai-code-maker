# MARU V13.4.4.3.2 통합 자동화 AI

오늘 대화 기준 통합본입니다. 기존 기능을 제거하지 않고 V12.3까지의 기능에 HTML 카드 코드노출 수정, 경마시간 추천없음 표시 보정 패치를 추가했습니다.

## 포함
- 경마앱/토토앱 ZIP 등록
- AI 코드생성기
- 로그 붙여넣기/로그파일 분석
- 사진 첨부/명령 입력
- 구글시트 저장
- 승인 패치
- GitHub 자동반영
- 모바일 사용
- HTML agent-card 코드노출 수정 패치
- 경마시간인데 추천 없음 표시 보정 패치
- 자동구매/자동결제 차단

## 올릴 파일
app.py
requirements.txt
README.md
ai_memory.json

Streamlit Cloud Main file path: app.py


## V13.4.4.3.2 추가

- 기본설정 자동불러오기
- 프로젝트 이름/배포주소/API KEY/API URL/GitHub owner/repo/branch 저장
- 등록 탭 자동 입력
- GitHub 자동반영 탭 자동 입력
- 모바일 재입력 불편 개선
- GitHub 토큰은 파일 저장하지 않고 Streamlit Secrets `GITHUB_TOKEN` 자동 사용 지원

Streamlit Secrets 예시:

```toml
GITHUB_TOKEN = "github_pat_..."
```


## V13.4.4.3 추가

- 프로젝트 이름 칸을 직접입력만 하지 않고 선택식으로 개선
- 경마앱 / 토토앱 / AI 코드 생성기 / 직접입력 선택 가능
- 선택하면 프로젝트 이름, 배포 앱 주소, GitHub owner/repo/branch 자동 변경
- 등록 탭과 GitHub 자동반영 탭에서 같은 선택 구조 적용
- 모바일에서 프로젝트 이름/API/GitHub repo 반복 입력 불편 개선


## V13.4.4 추가

- GitHub 토큰 매번 입력 불편 개선
- API KEY 매번 입력 불편 개선
- Streamlit Secrets에서 자동 불러오기
- 경마앱/토토앱 선택 시 기본 API URL 자동 채움

### Streamlit Secrets 권장값

```toml
GITHUB_TOKEN = "github_pat_..."
KRA_API_KEY = "공공데이터_API_KEY"
PUBLIC_DATA_API_KEY = "공공데이터_API_KEY"
SPORTMONKS_TOKEN = "스포츠_API_TOKEN"
TOTO_API_KEY = "토토_API_KEY"
```

토큰/API 키는 공개 GitHub 파일에 저장하지 마세요.


## V13.4 추가

- GitHub 자동 업로드 404 Not Found 보정
- 기존 파일이 없으면 실패가 아니라 새 파일 생성(create)으로 처리
- 기존 파일이 있으면 sha 기반 수정(update)
- app.py / README.md / requirements.txt / ai_memory.json 첫 업로드 실패 문제 수정
