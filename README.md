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


## V13.5 긴급 수정

- `NameError: default_api_key_for` 오류 수정
- 누락된 자동 API 키/URL 함수 상단 고정
- 프로젝트 선택 자동변경 유지
- GitHub 토큰/API 키 Secrets 자동불러오기 유지
- GitHub 404 Not Found → 새 파일 생성 처리 유지


## V13.6 긴급 안정화

- `default_api_key_for` NameError 재발 방지
- 기존 함수명을 쓰는 코드와 새 함수명을 모두 호환 처리
- 화면 코드에서 안전 함수 직접 사용
- GitHub 404 새 파일 생성 처리 유지
- 프로젝트 선택/토큰/API 자동불러오기 유지


## V13.7 화면 정리

- Streamlit 도움말/dir(streamlit) 디버그 출력 제거
- 앱 상단에 길게 나오던 Streamlit 설명문 제거
- V13.6 NameError 호환 수정 유지
- GitHub 토큰/API 키 Secrets 자동감지 유지
- 프로젝트 선택/자동반영 유지


## V13.8 완전 화면 정리

- Streamlit 도움말 원문 출력 제거
- `st.help(st)`, `st.write(st)`, `dir(streamlit)` 계열 출력 제거
- 혹시 남은 도움말/디버그 덤프도 화면에 표시되지 않도록 안전 가드 추가
- V13.6 NameError 호환 수정 유지
- V13.7 화면정리 유지
- GitHub 토큰/API 키 Secrets 자동감지 유지


## V13.9 긴급 화면 고정

- `st.help(st)` / `st.help(streamlit)` 출력 차단
- Streamlit 도움말/명령어 목록 출력 하드 차단
- V13.8 화면정리 유지
- V13.6 NameError 호환 수정 유지
- GitHub 토큰/API 키 Secrets 자동감지 유지


## V14 프로젝트 보관소 자동반영

- 경마앱 / 토토앱 / AI 코드 생성기 최신파일을 보관소에 저장
- 이후 등록 반복 없이 프로젝트 클릭으로 최신파일 자동 불러오기
- 보관소에서 불러온 파일 기준으로 패치/검사/GitHub 자동반영
- 프로젝트 이름/앱 주소/GitHub repo/branch 자동 적용
- 토큰/API 키 Secrets 자동감지 유지
- 기존 V13.9 화면정리, V13.6 NameError 방지, GitHub 404 새 파일 생성 처리 유지


## V14.1 연속자동화 루프

- 보관소 최신파일 불러오기
- 자동 테스트
- 로그분석
- 테스트 통과 시 GitHub 자동반영
- 실패 시 재패치 대기 기록
- 패치 → 반영 → 테스트 → 로그분석 → 재패치 흐름을 한 화면에서 연결
- 연속자동화 기록 저장

주의: 실제 코드 수정 패치는 승인 기반으로 유지합니다. 자동구매/자동결제는 계속 차단합니다.


## V14.2 개선 요구사항 승인 후 진행

- 개선 요구사항을 바로 패치하지 않고 승인대기함에 저장
- 승인 / 보류 / 거절 선택 가능
- 승인된 항목만 패치 대기열로 이동
- 패치 대기열 기준으로 패치 → 반영 → 테스트 → 로그분석 루프 진행
- 자동화는 유지하되 승인 없는 임의 진행은 차단
- 기존 V14 보관소, V14.1 연속자동화 루프 유지


## V14.3 승인 후 무승인 패치 루프

- 개선 요구사항은 최초 승인 필요
- 승인된 뒤에는 패치마다 추가 승인 없이 연속 진행
- 흐름: 테스트 → 로그분석 → 안전 자동패치 → 재테스트 → GitHub 자동반영
- 안전 자동패치 범위:
  - requirements.txt 누락 생성
  - README.md 누락 생성
  - ai_memory.json 누락 생성
- 위험한 코드 수정은 자동으로 밀어붙이지 않고 로그 기록 후 재패치 필요로 멈춤
- 기존 보관소, 연속자동화, GitHub 자동반영, Secrets 자동감지 유지


## V14.4 KST 보관소 긴급 수정

- `NameError: KST` 오류 수정
- 보관소 최신파일 불러오기에서 한국시간 기록 가능
- KST가 누락되어도 fallback으로 한국시간 사용
- V14 보관소 자동반영 유지
- V14.1 연속자동화 유지
- V14.2 개선승인 유지
- V14.3 승인 후 무승인 패치루프 유지


## V14.5 KST 최종 안정화

- `NameError: KST` 재발 방지
- `datetime.now(KST)` 직접 호출 제거
- `maru_now_kst_text()` 안전 함수로 통일
- KST 변수가 없어도 한국시간 fallback 사용
- 보관소 저장/불러오기 시간 기록 안정화
- V14 보관소, V14.1 연속자동화, V14.2 개선승인, V14.3 무승인 패치루프 유지


## V14.6 저장 함수 긴급 수정

- `NameError: save_memory` 오류 수정
- 보관소/연속루프에서 메모리 저장 함수가 없어도 안전하게 저장
- `MEM` 경로가 있으면 그 파일에 저장
- `MEM` 경로가 없으면 `ai_memory.json`에 저장
- V14.5 KST 안전시간 수정 유지
- V14 보관소, V14.1 연속자동화, V14.2 개선승인, V14.3 무승인 패치루프 유지


## V15 풀자동화 통합판

기존 기능을 제거하지 않고 풀자동화 엔진을 추가했습니다.

유지 기능:
- 프로젝트 보관소
- 개선 요구사항 승인
- 승인 후 무승인 패치 루프
- 자동 테스트
- 로그분석
- GitHub 자동반영
- 구글시트
- 사진/명령 분석
- 패치/검사/버전 기록
- 토큰/API Secrets 자동감지
- 자동구매/자동결제 차단

추가 기능:
- 🤖 풀자동화 탭
- 누락파일 자동생성
- NameError 자동수정
- KST/save_memory/default_api 계열 누락 자동삽입
- 안전한 문법오류 자동수정
- 재테스트 반복
- 통과 시 GitHub 자동반영


## V15.1 Streamlit 경고 제거

- `use_container_width=True` → `width="stretch"` 변경
- `use_container_width=False` → `width="content"` 변경
- 변경 개수: True 41개, False 0개
- V15 풀자동화 엔진 유지
- 프로젝트 보관소 유지
- 개선승인 / 무승인 패치루프 / 로그분석 / GitHub 자동반영 유지
- 자동구매/자동결제 차단 유지


## V15.2 풀자동화 모듈 보강

- `NameError: py_compile is not defined` 수정
- 풀자동화 엔진 필수 모듈 보강: `py_compile`, `re`, `shutil`, `json`, `Path`
- `maru_compile_app_file()` 내부에서도 `py_compile`를 직접 import하도록 이중 안전 처리
- V15.1 `use_container_width` 경고 제거 유지
- V15 풀자동화 / 보관소 / 개선승인 / 무승인 패치루프 / GitHub 자동반영 유지


## V15.3 결과표 안정화 + 중복반영 방지

- Streamlit/Arrow dataframe 변환 경고 수정
- `round` 컬럼에 숫자와 문자열이 섞여도 표시 전 문자열로 통일
- 풀자동화 결과표 `maru_show_rows()`로 안전 표시
- GitHub 자동반영 같은 내용 반복 업로드 방지
- V15.2 `py_compile` 보강 유지
- V15.1 `use_container_width` 경고 제거 유지
- V15 풀자동화 / 보관소 / 개선승인 / 무승인 패치루프 유지


## V15.4 표 표시 긴급 안정화

- `NameError: pd is not defined` 수정
- 표 표시 함수가 전역 `pd`에 의존하지 않도록 변경
- 함수 안에서 `import pandas as _maru_pd` 직접 수행
- pandas/Arrow 실패 시 `st.json` 또는 `st.write`로 fallback
- 결과표 표시 때문에 앱이 죽지 않도록 방어 처리
- V15.3 중복 GitHub 자동반영 방지 유지
- V15.2 py_compile 보강 유지
- V15 풀자동화 / 보관소 / 개선승인 / 무승인 패치루프 유지


## V16 완성 안정화판

단일 오류 땜빵이 아니라 전체 안정화 보강판입니다.

### 안정화 내용
- 필수 import 전부 보강: os/io/re/json/time/zipfile/shutil/hashlib/traceback/subprocess/py_compile/Path/datetime/pandas/numpy
- `KST` 누락 방지
- `save_memory` 누락 방지
- `pd` 누락 방지
- `py_compile` 누락 방지
- 표 표시 실패 시 앱이 죽지 않도록 `maru_show_rows()` 최종 방어
- `use_container_width` 제거 유지
- GitHub 자동반영 중복 반복 방지
- 경마앱 저장소에 AI 코드 생성기 파일이 올라가는 사고 차단
- 문법검사 `py_compile` 통과 확인

### 유지 기능
- V15 풀자동화
- 프로젝트 보관소
- 개선승인
- 승인 후 무승인 패치루프
- 자동 테스트
- 로그분석
- GitHub 자동반영
- 구글시트
- 사진분석/명령
- 토큰/API 자동감지
- 자동구매/자동결제 차단

## V16.1 토큰 진단 추가
- GitHub 토큰 감지 강화
- 여러 이름과 섹션에서 토큰 탐색
- 🗝️ 토큰진단 탭 추가
- 토큰 전체값은 노출하지 않고 마스킹 표시
- GitHub 저장소 app.py 읽기 테스트로 권한 확인

## V16.2 상태판 안정화
- 탭 아래가 비어 보이는 문제 대응
- 화면 상단에 항상 보이는 MARU 상태판 추가
- GITHUB_TOKEN 감지 여부 상단 표시
- AI 코드 생성기 저장소 접근 테스트 상단 버튼 추가
- 토큰진단 탭 내용 보장 블록 추가
- V16/V16.1 안정화 기능 유지

## V17.1 한글 로그 + 전체 자가진단 안전판

- 기존 탭 내부를 억지로 건드리지 않고 상단 독립 진단판으로 추가
- 토큰 자가진단 포함
- GitHub 저장소 접근 테스트 포함
- 한글 로그 설명 포함
- 전체 필수 함수 자가진단 포함
- UTC+09:00 문구를 한국시간 KST (UTC+9)로 정리
- AI 코드 생성기 저장 시 경마/토토 API URL 섞임 정리

## V17.2 하단 안내판 고정판
- 탭 아래에 아무것도 안 보이는 문제 대응
- 상단 상태 안내판 추가
- 하단 상태 안내판 추가
- 전체진단 탭 보장
- 한글 로그 설명을 전체진단 탭에서 바로 사용
- 토큰 자가진단 포함
- GitHub 저장소 접근 테스트 포함
- 문법검사/AST 검사 통과


## V18 메뉴전체점검 완성판

이번 버전은 한 메뉴만 고치는 방식이 아니라 핵심 메뉴 전체를 점검하는 안내판을 추가했습니다.

### 추가
- 상단 메뉴 전체점검판
- 하단 메뉴 전체점검 요약
- 메뉴전체점검 탭
- 각 메뉴 필수 함수 존재 검사
- 토큰 자가진단
- GitHub 저장소 접근 테스트
- 한글 로그분석
- 한국시간 KST 표시 정리

### 유지
- 보관소
- 연속자동화
- 로그분석
- 패치
- GitHub 자동반영
- 풀자동화
- 토큰진단
- 경마/토토/AI 저장소 혼동 차단
- 자동구매/자동결제 차단


## V18.1 탭 오류 복구판

문제:
- 무승인패치루프 / 풀자동화 / 토큰진단 / 전체진단 탭이 오류 또는 빈 화면처럼 보임
- 여러 기능을 `tabs[-1]`에 계속 붙여 탭 구조가 꼬일 가능성 있음

수정:
- 통합 운영센터 추가
- 메뉴점검 / 전체진단 / 토큰진단 / 무승인패치루프 / 풀자동화 / 한글로그를 독립 하위 탭으로 제공
- 기존 탭이 꼬여도 통합 운영센터에서 핵심 기능 실행 가능
- 각 기능은 try/except로 보호하여 한 기능 오류가 전체 앱을 죽이지 않음
- 탭 이름 붙음 문제 보정
- 문법검사 및 AST 검사 통과


## V18.2 실제 메뉴 연결 복구판

문제:
- 개선승인/무승인패치루프/풀자동화/토큰진단/전체진단/메뉴전체점검이 `tabs[-1]`에 몰려 실제 메뉴와 내용이 맞지 않았습니다.
- `📚 기록📝 개선승인`처럼 메뉴가 붙어 보였습니다.

수정:
- 개선승인 → tabs[14]
- 무승인패치루프 → tabs[15]
- 풀자동화 → tabs[16]
- 토큰진단 → tabs[17]
- 전체진단 → tabs[18]
- 메뉴전체점검 → tabs[19]
- 메뉴 연결 확인판 추가
- 문법검사/AST 검사 통과


## V19 원클릭 업로드 자동반영판

목적:
- ZIP/app.py를 업로드하면 보관소 저장 후 자동으로 GitHub에 반영
- 사진/이미지도 등록하면 보관소 저장 후 `assets/uploads/`에 자동 반영
- AI 코드 생성기 / 경마앱 / 토토앱을 정확히 구분
- 기존 메뉴와 사진분석/명령 기능은 제거하지 않음

핵심:
- 프로젝트 선택
- 코드 업로드
- 보관소 저장
- 저장소 안전검사
- app.py 문법검사
- GitHub 자동반영
- 사진 등록 자동반영
- 한글 결과 표시
