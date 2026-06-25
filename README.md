# MARU GitHub 자동반영 패치 AI V11.2.2

패치된 ZIP을 사람이 다시 경마앱 저장소에 올리는 단계를 자동화한 버전입니다.

## 핵심 흐름

```text
경마앱/토토앱 ZIP 등록
→ 자동 압축해제
→ 파일/오류 검사
→ 자동테스트
→ 개선안 추천
→ 승인한 항목 실제 패치
→ 새 ZIP 생성
→ GitHub 대상 저장소에 자동 업로드/커밋
→ Streamlit Cloud 자동 재배포
```

## GitHub 자동반영에 필요한 것

GitHub 토큰이 필요합니다.

권한:
- 대상 저장소 접근
- Contents: Read and write

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud:

```text
Main file path: app.py
```


## V11.2.2 수정

- `zip_bytes` 누락으로 버전 탭에서 발생하던 NameError 수정


## V11.2 수정

- 등록 탭에서 프로젝트 이름이 입력되어 보여도 빈값으로 읽히던 문제 방어
- 이름이 비면 앱 주소/업로드 ZIP명에서 자동 추론
