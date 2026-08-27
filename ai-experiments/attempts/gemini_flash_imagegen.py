# filename: flashimage_final.py
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# -----------------------------
# 1) 환경 변수 로드
# -----------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("GEMINI_API_KEY를 찾을 수 없습니다. .env 파일을 확인하세요.")
    raise SystemExit(1)

# -----------------------------
# 2) 파일 저장 함수
# -----------------------------
def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")

# -----------------------------
# 3) 이미지 생성 함수
# -----------------------------
def generate_image_with_input(prompt, input_image_path="test.jpg", output_file="result.jpg"):
    client = genai.Client(api_key=API_KEY)
    model = "gemini-2.0-flash-preview-image-generation"

    # 로컬 이미지 읽기
    with open(input_image_path, "rb") as f:
        image_bytes = f.read()

    # Part 구성 (최신 SDK 방식)
        text_part = types.Part(text=prompt)
    image_part = types.Part(
        image=types.ImageContent(
            data=image_bytes,
            mime_type="image/jpeg"
        )
    )
    contents = [
        types.Content(
            role="user",
            parts=[text_part, image_part]
        )
    ]


    # IMAGE + TEXT 응답 설정
    generate_content_config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"]
    )

    # 스트리밍으로 이미지 생성 및 저장
    file_saved = False
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        candidate = chunk.candidates[0] if chunk.candidates else None
        if candidate and candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, "image") and part.image:
                    save_binary_file(output_file, part.image)
                    file_saved = True
                    break
        if file_saved:
            break

    if not file_saved:
        print("이미지 생성 실패: Gemini에서 데이터를 받지 못했습니다.")

# -----------------------------
# 4) 실행
# -----------------------------
if __name__ == "__main__":
    user_prompt = "고급스러운 배경에 놓인 해당 제품 클로즈업과 로우앵글, 세련된 조명, 질감 강조, 광고 이미지"
    generate_image_with_input(prompt=user_prompt, input_image_path="test.jpg", output_file="result.jpg")
