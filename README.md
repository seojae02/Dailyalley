# 오늘의 골목 (Daily Alley)

소상공인이 가게 사진과 기본 정보만 올리면 **SNS 홍보 이미지와 카피를 자동 생성**하고, 네이버 블로그에 **바로 발행**까지 해주는 AI 마케팅 서비스입니다.

> 멋쟁이사자처럼 순천향대학교 13기 해커톤 프로젝트 (2025.07 ~ 2025.08)

---

## 왜 만들었나

인스타그램에서 '핫플' 인증을 받은 가게는 줄을 서지만, 음식이 좋아도 홍보가 약한 가게는 존재감을 잃습니다. 실제 소상공인 대상 조사에서 **사진 품질**과 **홍보 문구 작성**이 가장 큰 장벽으로 나타나, 이 둘을 자동화하는 것을 핵심 과제로 잡았습니다.

---

## 아키텍처

```
┌──────────────┐
│ web-frontend │  Next.js 15 / MUI / jotai
└──────┬───────┘
       │
       ├─────────────────► api-backend    (Spring Boot :8080)
       │                    가게·게시글·SNS 계정 CRUD
       │                    Selenium 네이버 블로그 자동 발행
       │
       └─────────────────► ai-server      (FastAPI :7100)
                            /v1/upload-store-images  가게 사진 업로드
                            /v1/outpaint             음식 사진 배경 재생성
                            /v1/generate-promo       홍보 카피 생성
```

## 폴더 구성

| 폴더 | 역할 | 스택 |
|---|---|---|
| [`web-frontend/`](./web-frontend) | 사용자 화면 | Next.js 15, React 19, MUI 7, jotai |
| [`api-backend/`](./api-backend) | 도메인 API · 블로그 자동 발행 | Spring Boot, JPA, MySQL, MinIO, Selenium |
| [`ai-server/`](./ai-server) | 이미지 생성 · 카피 생성 | FastAPI, Gemini, DALL·E 2, rembg |
| [`ai-experiments/`](./ai-experiments) | 이미지 생성 방식 검증 습작 | Gemini, Stable Diffusion |
| [`docs/`](./docs) | 발표 자료, 결과 예시 | — |

## 파이프라인

사진 한 장이 게시글이 되기까지의 흐름입니다.

```
가게 사진 업로드           → ai-server  /v1/upload-store-images  → N_store_*.jpg
음식 사진 업로드           → ai-server  /v1/outpaint
   ├ rembg 로 피사체 분리
   ├ 1024² 캔버스 중앙에 60% 크기로 배치 (여백 확보)
   ├ Gemini 1.5 Flash: 한국어 요청 → 영문 프롬프트 번역·제약 주입
   └ DALL·E 2 images.edit: 빈 여백을 채움              → N_food_AI.jpg
홍보 카피 생성             → ai-server  /v1/generate-promo
   └ 위 두 이미지를 Gemini 에 멀티모달 입력 → headline / body / tags / cta
네이버 블로그 발행         → api-backend /api/naver/blog/upload
   └ Selenium 으로 로그인 → 에디터 iframe 진입 → 발행
```

이미지는 `N_food.jpg`(원본) / `N_food_AI.jpg`(가공) / `N_store_*.jpg`(가게)로 **번호 N을 기준으로 그룹**을 이루며, 카피 생성 시 가공본과 가게 사진만 본문에 실립니다.

## 실행

각 폴더의 README를 참고하세요. 모든 서비스가 키를 필요로 하므로 `.env.example`을 복사해 채우는 것이 먼저입니다.

```bash
cp ai-server/.env.example       ai-server/.env
cp ai-experiments/.env.example  ai-experiments/.env
cp api-backend/src/main/resources/application-secret.yml.example \
   api-backend/src/main/resources/application-secret.yml
```

## 팀

| 파트 | 담당 |
|---|---|
| AI 이미지 생성 파이프라인 (`/v1/outpaint`) | 서재연 |
| AI 카피 생성 · 서버 | 팀 공동 |
| 백엔드 · 인프라 | 팀 공동 |
| 프론트엔드 | 팀 공동 |
