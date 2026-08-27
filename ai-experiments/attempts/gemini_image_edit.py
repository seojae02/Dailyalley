#프롬프트는 정상적으로 되는데 이미지생성에서 막힘

import os
import io
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

def edit_image_with_prompt(api_key, image_path, output_path, prompt):
    """
    이미지와 명확한 텍스트 프롬프트를 사용하여 이미지를 편집하고 저장합니다.
    """
    print("✨ 이미지 편집을 시작합니다...")

    # Gemini API 설정
    genai.configure(api_key=api_key)

    # 멀티모달 입력이 가능한 모델 선택
    model = genai.GenerativeModel('gemini-2.0-flash:generateContent')

    try:
        # 원본 이미지 열기
        print(f"📄 원본 이미지 '{image_path}'를 불러옵니다.")
        input_image = Image.open(image_path)

        # 모델에 이미지와 프롬프트를 함께 전달하여 콘텐츠 생성 요청
        print(f"🎨 프롬프트 적용 중: \"{prompt}\"")
        # 'stream=True'를 사용하여 응답을 스트리밍으로 받으면 더 안정적일 수 있습니다.
        response = model.generate_content([prompt, input_image], stream=True)

        print("📡 모델로부터 응답을 기다리는 중...")
        
        # 스트리밍 응답 처리
        image_data = None
        for chunk in response:
            # 응답 'parts'에 blob(binary large object) 데이터가 있는지 확인
            if chunk.parts and hasattr(chunk.parts[0], "blob"):
                image_data = chunk.parts[0].blob.data
                break # 이미지 데이터를 찾았으면 루프 종료
        
        if image_data:
            result_image = Image.open(io.BytesIO(image_data))
            result_image.save(output_path)
            print(f"✅ 성공! 편집된 이미지가 '{output_path}'에 저장되었습니다.")
        else:
            # 이미지 데이터가 없는 경우, 수신된 텍스트 전체를 출력
            full_text_response = "".join(chunk.text for chunk in response)
            print("❌ 오류: 응답에서 이미지 데이터를 찾을 수 없습니다.")
            print("🙋‍♂️ API 텍스트 응답:", full_text_response)

    except FileNotFoundError:
        print(f"❌ 오류: '{image_path}' 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
    except Exception as e:
        print(f"❌ 예상치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    load_dotenv()
    my_api_key = os.getenv('GEMINI_API_KEY')

    if not my_api_key:
        print("🚨 '.env' 파일에서 GEMINI_API_KEY를 찾을 수 없습니다.")
    else:
        INPUT_IMAGE_FILE = "test.jpg"
        OUTPUT_IMAGE_FILE = "result.jpg"

        # --- ‼️ 가장 중요한 부분: 명확하고 구체적인 프롬프트 ---
        # "결과물은 반드시 이미지여야 한다"는 점을 강력하게 지시합니다.
        EDIT_PROMPT = (
            "이 피자 이미지를 기반으로, 구도를 시계 방향으로 15도 기울이고, "
            "오른쪽 위에서 따뜻한 자연광이 비추는 효과를 추가해줘. "
            "다른 모든 요소는 원본과 동일하게 유지해줘. "
            "텍스트 설명은 필요 없고, 결과물로 **오직 편집된 이미지만 생성**해줘."
        )

        edit_image_with_prompt(
            api_key=my_api_key,
            image_path=INPUT_IMAGE_FILE,
            output_path=OUTPUT_IMAGE_FILE,
            prompt=EDIT_PROMPT
        )