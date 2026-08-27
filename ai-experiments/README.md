# ai-experiments

`ai-server`의 아웃페인팅 파이프라인을 확정하기 전에, **어떤 조합으로 음식 사진을 광고 이미지로 바꿀 수 있는지** 검증한 습작 모음입니다.

핵심 질문은 하나였습니다 — *피사체(실제 메뉴)를 훼손하지 않으면서 배경만 바꿀 수 있는가?*

## 실행

```bash
cp .env.example .env      # GEMINI_API_KEY 입력
pip install python-dotenv pillow google-generativeai torch diffusers
python gemini_sd_img2img.py
```

`test.jpg`를 입력으로 읽고 `result_natural.jpg`를 만듭니다. 두 경로 모두 스크립트 기준 상대경로입니다.

## `gemini_sd_img2img.py` — 채택된 방식

동작이 확인된 유일한 스크립트입니다.

```
원본 → 16:9 레터박스 → Gemini 1.5 Flash 프롬프트 생성 → SD v1.5 img2img → 저장
```

세 가지가 이 스크립트의 요점입니다.

**1. 크롭 대신 레터박스** — `to_16x9_letterbox()`는 비율을 맞출 때 이미지를 잘라내지 않습니다. 대신 패딩을 넣되, 그 색을 `ImageStat`으로 구한 **원본 평균 RGB**로 채워 검은 띠 없이 자연스럽게 이어지도록 했습니다. 음식이 잘리면 안 된다는 제약에서 나온 선택입니다.

**2. `strength=0.3`** — img2img의 변형 강도를 낮게 잡아 원본 피사체를 최대한 보존합니다. 값을 높이면 배경은 좋아지지만 음식 자체가 다른 음식으로 바뀝니다.

**3. negative prompt로 메뉴 변형 차단**
```
no different product type, no different food, no extra objects,
no text, no logos, no hands, no watermark
```
"소상공인이 올린 실제 메뉴가 다른 음식이 되면 안 된다"는 서비스 제약을 파라미터로 옮긴 부분입니다.

또한 Gemini 호출이 실패하면 원래 사용자 프롬프트로 떨어지도록 `try/except` fallback을 두어 파이프라인이 멈추지 않습니다.

## 이 습작이 `ai-server`로 이어진 지점

로컬 Stable Diffusion은 GPU가 필요해 서버 배포에 부담이 컸습니다. 그래서 `ai-server/openai_seojae.py`에서는 **SD를 DALL·E 2 아웃페인팅으로 교체**하되, 여기서 얻은 두 가지 결론은 그대로 가져갔습니다.

| 여기서 배운 것 | `ai-server`에서의 적용 |
|---|---|
| 배경만 바꾸려면 피사체를 먼저 분리해야 한다 | `rembg`로 배경 제거 후 캔버스 중앙 배치 |
| 부정 지시가 없으면 잡객체(수저·포크)가 생성된다 | DALL·E 2엔 negative prompt가 없어, **Gemini에게 부정 키워드를 프롬프트 본문에 심도록 지시** |

## 파일

| 파일 | 상태 | 설명 |
|---|---|---|
| `gemini_sd_img2img.py` | ✅ 동작 | Gemini 프롬프트 생성 + Stable Diffusion v1.5 img2img |
| `attempts/` | ⚠️ 미완성 | Gemini 단독 이미지 생성 시도들 — [attempts/README.md](./attempts/README.md) |
| `test.jpg` | — | 입력 샘플 |
| `sample_output.png` | — | 결과 예시 |

## 주의

`.env`와 `service-account.json`은 `.gitignore`로 제외됩니다. 커밋 전 `git status`로 반드시 확인하세요.
