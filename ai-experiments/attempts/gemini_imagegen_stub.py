import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    print(f"File saved to: {file_name}")

def generate(input_image_path="test.jpg"):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    model = "gemini-2.0-flash-preview-image-generation"

    # 이미지 Part 생성 (최신 SDK 방식)
    image_part = types.Part.from_image_file(input_image_path)

    # 텍스트 프롬프트 + 이미지
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text("replace background on wood table"),
                image_part
            ]
        )
    ]

    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"]
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=config
    ):
        if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
            part = chunk.candidates[0].content.parts[0]
            if part.data:
                save_binary_file("result.jpg", part.data)

if __name__ == "__main__":
    generate("test.jpg")
