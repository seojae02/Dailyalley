# api-backend

가게·게시글·SNS 계정을 관리하고, **Selenium으로 네이버 블로그에 글을 자동 발행**하는 Spring Boot 서버입니다.

## 실행

```bash
cp src/main/resources/application-secret.yml.example \
   src/main/resources/application-secret.yml     # DB · MinIO · AES 키 입력
./gradlew bootRun
```

기본 포트는 `8080`, Swagger는 `/swagger-ui.html` 입니다. MySQL과 MinIO가 필요합니다.

## 구조

```
likelionhackathon13.dailyalley
├── Controller/   Store · post · img · sns
├── Service/      비즈니스 로직 + AES256
├── Repository/   Spring Data JPA
├── Entity/       Store · post · img · sns  (BaseEntity 상속)
├── Dto/
├── domain/selenium/   네이버 블로그 자동 발행
└── global/       예외 처리 · 응답 래퍼 · Swagger 설정
```

## 파일별 설명

| 파일 | 설명 |
|---|---|
| **`domain/selenium/service/NaverBlogService.java`** | 네이버 로그인 → 글쓰기 → 발행 전 과정 자동화. 봇 탐지를 피하려 ID/PW를 `JavascriptExecutor`로 주입합니다 |
| **`domain/selenium/util/SeleniumUtil.java`** | 자동화의 핵심 유틸. 아래 별도 설명 |
| **`Service/AES256.java`** | 네이버 계정 비밀번호 암·복호화 (AES/CBC/PKCS5Padding) |
| **`SecurityConfig.java`** | 현재 `anyRequest().permitAll()` + CSRF 비활성 |
| **`MinioConfig.java`** | 이미지 오브젝트 스토리지 설정 |
| **`global/exception/`** | `ErrorCode` 기반 커스텀 예외 + `GlobalExceptionHandler` |

## `SeleniumUtil`이 푸는 문제

네이버 블로그 에디터에는 공개 API가 없고, **중첩 iframe**과 동적 렌더링 때문에 일반적인 Selenium 클릭이 통하지 않습니다. 세 가지로 대응했습니다.

**1. 클릭 4단계 폴백** — `hardClick()`
```
el.click()
  → Actions.moveToElement().click()
    → JS arguments[0].click()
      → MouseEvent(mousedown/mouseup/click) 직접 dispatch
```

**2. 전체 컨텍스트 순회** — `listAllContexts()`
`default` → 최상위 iframe들 → `mainFrame` → `mainFrame` 안의 iframe들을 모두 수집해, 버튼이 어느 프레임에 있든 찾아냅니다.

**3. 발행 버튼 대기 후 클릭** — `clickFinalPublishAnywhere()`
20초 데드라인 안에서 모든 컨텍스트 × 4개 XPath를 돌며, `disabled` / `aria-disabled`가 풀릴 때까지 기다렸다가 클릭합니다.

## 알려진 이슈

해커톤 기간 제약으로 남아 있는 부분입니다.

- **`AES256`의 IV가 키에서 고정 파생됩니다** (`iv = key.substring(0, 16)`). 같은 평문이 항상 같은 암호문이 되므로, 실제 운영이라면 매 암호화마다 랜덤 IV를 생성해 암호문 앞에 붙여야 합니다
- **전 엔드포인트가 무인증**입니다 (`permitAll`). SNS 계정 비밀번호를 다루는 서버이므로 인증이 필요합니다
- 클래스명 표기가 섞여 있습니다 — `StoreDto`(PascalCase)와 `postDto`·`snsService`(camelCase)가 공존합니다
