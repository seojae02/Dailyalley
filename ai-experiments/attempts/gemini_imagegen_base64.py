# pip install google-genai

import os
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def save_binary_file(file_name, data):
    """바이너리 데이터를 파일로 저장"""
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")

def generate(input_image_path, output_file, prompt_text):
    """
    입력 이미지 + 텍스트 프롬프트로 이미지 생성 후 저장

    input_image_path : str, 입력 이미지 파일 경로
    output_file      : str, 생성된 이미지 저장 경로
    prompt_text      : str, 이미지 생성/변환에 사용할 텍스트 프롬프트
    """
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    model = "gemini-2.0-flash-preview-image-generation"

    # 입력 이미지 읽기
    with open(input_image_path, "rb") as f:
        image_bytes = f.read()

    # base64로 변환
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    # 이미지 Part 생성
    image_part = types.Part(
        type="image",
        inline_data=types.InlineData(
            data=image_base64,
            mime_type="image/jpeg"
        )
    )

    # 텍스트 프롬프트 + 이미지 Part
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(prompt_text),
                image_part
            ]
        )
    ]

    # IMAGE만 출력
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"]
    )

    # 스트리밍으로 결과 받기
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=config
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue

        part = chunk.candidates[0].content.parts[0]
        if part.inline_data and part.inline_data.data:
            data_buffer = part.inline_data.data
            save_binary_file(output_file, data_buffer)

if __name__ == "__main__":
    # 사용자가 원하는 이미지 파일과 프롬프트를 입력
    input_path = "test.jpg"             # 변환할 입력 이미지
    output_path = "result.jpg"          # 생성 이미지 저장 경로
    prompt = "Apply a cinematic low-angle view"  # 원하는 프롬프트

    generate(input_path, output_path, prompt)
