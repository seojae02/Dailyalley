# attempts

**어느 것도 완성되지 않았습니다.** 기록을 위해 남겨둔 시도들입니다.

당시 목표는 Stable Diffusion 없이 **Gemini만으로 이미지 생성까지** 끝내는 것이었습니다. `gemini-2.0-flash-preview-image-generation` 모델을 여러 SDK 방식으로 호출해봤지만, 프롬프트 생성까지는 되어도 이미지 바이너리를 받아오는 단계에서 계속 막혔습니다. 결국 이미지 생성은 Stable Diffusion(습작) → DALL·E 2(운영)으로 갔습니다.

| 파일 | 막힌 지점 |
|---|---|
| `gemini_image_edit.py` | 이미지 생성 단계에서 막힘. 모델명에 REST 메서드가 섞여 있음 (`gemini-2.0-flash:generateContent`) |
| `gemini_flash_imagegen.py` | 32번째 줄 들여쓰기 오류로 `IndentationError` |
| `gemini_imagegen_base64.py` | `types.Part(type=..., inline_data=...)` — 존재하지 않는 시그니처 |
| `gemini_imagegen_stub.py` | `types.Part.from_image_file()` — 존재하지 않는 메서드 |
| `instagram_upload_stub.py` | `instapy-cli` 자리표시자. 인스타그램 자동 업로드는 구현되지 않았고, 실제 발행은 `api-backend`의 네이버 블로그 Selenium으로 대체되었습니다 |

> 원래 파일명이 의미 없는 문자열이라 내용에 맞게 바꿨습니다. API 키도 전부 환경변수로 옮겼습니다.
