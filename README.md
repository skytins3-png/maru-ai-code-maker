# MARU V10 무음성 최종 통합 실제 패치 AI

음성지시/OpenAI API 키/요금 발생 요소를 제거하고, 오늘 대화한 기능을 한 파일 `app.py` 중심으로 통합했습니다.

## 핵심
- ZIP 자동 압축해제
- 파일 목록 검사
- 오류 파일 검사
- 문법 검사
- 기존 기능 분석
- 자동 모니터
- 반복 자동테스트
- 로그 분석
- 개선안 추천
- 승인/미승인/추가지시
- 승인 항목 실제 패치
- app.py 실제 수정
- helper 파일 실제 추가
- 새 버전 ZIP 생성
- 구글시트 저장
- GitHub Actions 예약 테스트
- 자동구매/자동결제 차단
- 음성지시 제거
- OpenAI API 키 제거

## 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud Main file path: `app.py`
