# 강호풍운록 · 江湖风云录

원작 정통 무협 연재 + 중국어 학습 웹페이지. **첫 회 공개 자료**는 `index.html`, `episodes.json`, `assets/`에 있습니다.

## 온라인 공개 시작하기
GitHub 저장소 Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: maru-wuxia-serial /(root) → Save. GitHub Pages가 활성화되어야 공개 주소가 생깁니다. 현재 Pages 공개 여부는 확인하지 못했습니다.

## 새 회차 작성
`episodes.json`의 `episodes` 배열 끝에 매일 한 개를 추가하세요. 날짜 `release_at`은 Asia/Seoul 기준 YYYY-MM-DD; 예정일 전 회차는 사이트에 표시하지 않습니다. 필수: id,release_at,title,teaser,prep,grammar,panels[{image,zh,py,ko,note}],words[{zh,py,ko,usage}],dialects[{region,zh,py,ko,note}].

## 학습 구조
만화는 오로지 중국어 대사; 별도 예습 / 문장 / 단어(등장순, 중복 허용) / 지역말 / 복습. 휴대폰과 맥북에 대응.

## 아직 연결되지 않은 기능
매일 **새 AI 만화와 교재를 무인 생성하는 엔진**, GitHub Pages 설정, 기기간 진도 동기화. 새 회차 작성과 GitHub 게시가 없으면 새 콘텐츠가 늘어나지 않습니다. 
