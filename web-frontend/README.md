# web-frontend

사용자 화면입니다. **Next.js 15 App Router** 기반이며, 가게 정보 입력부터 AI 생성 결과 확인·발행까지를 담당합니다.

## 실행

```bash
npm install
npm run dev     # http://localhost:3000
```

## 스택

| 항목 | 선택 |
|---|---|
| 프레임워크 | Next.js 15.4 (App Router), React 19 |
| UI | MUI 7 + Emotion |
| 상태 관리 | jotai |
| HTTP | axios |

## 화면 흐름

```
/            메인
/info        가게 정보 조회
/info/edit   가게 정보 입력 (4단계 마법사)
/create      사진 업로드 → AI 생성 요청
/create/result   생성 결과 확인 → 네이버 블로그 발행
/user        프로필
```

## 파일별 설명

| 파일 | 설명 |
|---|---|
| **`config/axios.ts`** | 백엔드(`api-backend`)용 인스턴스. 타임아웃 120초 |
| **`config/aiAxiosInstance.ts`** | AI 서버(`ai-server`, `:7100`)용 인스턴스. 이미지 생성이 오래 걸려 타임아웃 120초 |
| **`app/create/page.tsx`** | 사진 업로드 후 `/v1/outpaint` → `/v1/generate-promo`를 순차 호출 |
| **`app/create/result/page.tsx`** | 생성 결과 표시. `/ai` 저장, `/api/naver/blog/upload` 발행 호출 |
| **`app/info/edit/`** | `FirstPage` ~ `FourthInfoPage` 4단계 입력 폼 + `useStoreEdit` 훅 |
| **`app/atom/storeId.ts`** | jotai atom — 선택된 가게 ID 전역 공유 |
| **`app/create/atom/creationAtom.ts`** | jotai atom — 생성 진행 상태 |
| **`app/theme/`** | MUI 테마 및 SSR용 `ThemeRegistry` |
| **`app/components/`** | `MainBottomNav`, `UploadHistory`, `UploadPostCard`, `UserProfileHeader` |

## 참고

**서버 주소가 소스에 하드코딩되어 있습니다.** 두 axios 설정 파일의 `baseURL`을 환경에 맞게 바꾸거나, `NEXT_PUBLIC_*` 환경변수로 옮기는 것이 좋습니다.
