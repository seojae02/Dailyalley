# ai-server

이미지 생성과 홍보 카피 생성을 담당하는 **FastAPI** 서버입니다. 프론트엔드가 `:7100`으로 직접 호출합니다.

원본 저장소: [`seojae02/daily`](https://github.com/seojae02/daily)

## 실행

```bash
cp .env.example .env      # 키 입력
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Swagger 문서는 `/docs`, 헬스체크는 `/health` 입니다.

## 엔드포인트

| 메서드 | 경로 | 설명 |
|---|---|---|
| `POST` | `/v1/upload-store-images` | 가게 사진 여러 장 업로드 → `N_store_*.jpg` |
| `POST` | `/v1/outpaint` | 음식 사진 배경 재생성 → `N_food_AI.jpg` (204 반환) |
| `POST` | `/v1/generate-promo` | 홍보 카피 생성 → `{headline, body, tags, cta}` |
| `GET` | `/health` | 모델 ID · 디바이스(cuda/cpu) 확인 |

## 파일별 설명

| 파일 | 설명 |
|---|---|
| **`app.py`** | FastAPI 앱 진입점. 3개 라우터를 등록합니다. **CORS 미들웨어가 주석 처리되어 있어** 프록시 없이 브라우저에서 직접 호출하면 차단됩니다 |
| **`openai_seojae.py`** | `/v1/outpaint`. rembg 배경 제거 → 캔버스 중앙 배치 → Gemini 프롬프트 생성 → **DALL·E 2 `images.edit` 아웃페인팅**. 이 저장소에서 OpenAI를 쓰는 유일한 파일입니다 |
| **`routes_promo.py`** | `/v1/generate-promo`. 최신 이미지 그룹을 찾아 **가게 사진 + 가공 음식 사진을 Gemini에 멀티모달 입력**으로 넣고 카피를 생성합니다. 응답 JSON 파싱 실패 시 `raw`를 그대로 반환합니다 |
| **`routes_upload_store.py`** | `/v1/upload-store-images`. 파일명 규약(`N_store_*.jpg`)을 스캔해 다음 그룹 번호를 부여합니다 |
| **`utils.py`** | 프롬프트 빌더(`build_promo_prompt`), 이미지→inline part 변환, 리사이즈, 텍스트 합성(`draw_text_with_background`), 비율 파싱 등 공용 유틸 |
| **`config.py`** | `.env` 로드 및 Gemini 엔드포인트 구성. 키가 없으면 기동 시점에 `RuntimeError` |
| **`Dockerfile`** | Python 3.13-slim 기반. `requirements.txt`에서 주석 처리된 무거운 패키지(diffusers/rembg/onnxruntime/openai)를 별도 `RUN`으로 설치합니다 |
| **`.github/workflows/docker-image.yml`** | `deploy` 브랜치 push 시 linux/arm64 이미지를 빌드해 tar로 EC2에 SCP 전송 후 교체 |
| **`main.py`** | 실행 파일이 아닙니다. 리팩터링 안내 주석만 남아 있습니다 (진입점은 `app.py`) |
| **`routes_ad_image.py`** | **전체가 주석 처리됨.** Stable Diffusion Inpaint 기반 `/v1/ad-image`를 시도하다 중단된 코드입니다 |
| **`test.py`** | **전체가 주석 처리됨.** 키 로딩 확인용 스크립트 |

## 이미지 저장 규약

`IMAGE_DIR`(기본 `/home/ec2-user/BE/img`) 아래에 번호로 그룹을 묶습니다.

```
img/
├── food/   N_food.jpg      원본 음식 사진
│           N_food_AI.jpg   아웃페인팅 결과 (카피 생성 시 본문에 사용)
└── store/  N_store_1.jpg   가게 사진
```

DB 없이 **파일명 규약만으로** 이미지 세트를 이어 붙이는 구조입니다. `_next_food_index()`, `_latest_group_with_food_ai()`가 정규식으로 최대 N을 찾아 증분합니다.

## 알려진 이슈

- `app.py`의 CORS 미들웨어가 주석 처리되어 있습니다
- `IMAGE_ROOT` 기본값에 EC2 절대경로가 하드코딩되어 있습니다 (`IMAGE_DIR`로 덮어쓰기 가능)
- `__pycache__/`, `.idea/`, `debug_01_opened_image.png`가 원격에 커밋되어 있습니다
