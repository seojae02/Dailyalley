# filename: ad_img_hybrid_natural.py
import os
from dotenv import load_dotenv
from PIL import Image, ImageOps, ImageStat
import google.generativeai as genai
import torch
from diffusers import StableDiffusionImg2ImgPipeline

# -----------------------------
# 0) 유틸: 16:9 캔버스로 맞추기 (원본 최대한 보존)
# -----------------------------
def to_16x9_letterbox(img: Image.Image) -> Image.Image:
    target_ratio = 16 / 9
    w, h = img.size
    src_ratio = w / h
    if abs(src_ratio - target_ratio) < 1e-3:
        return img
    stat = ImageStat.Stat(img.convert("RGB"))
    mean_rgb = tuple(int(v) for v in stat.mean)
    if src_ratio > target_ratio:
        new_h = int(round(w / target_ratio))
        pad_top = (new_h - h) // 2
        pad_bottom = new_h - h - pad_top
        return ImageOps.expand(img, border=(0, pad_top, 0, pad_bottom), fill=mean_rgb)
    else:
        new_w = int(round(h * target_ratio))
        pad_left = (new_w - w) // 2
        pad_right = new_w - w - pad_left
        return ImageOps.expand(img, border=(pad_left, 0, pad_right, 0), fill=mean_rgb)

# -----------------------------
# 1) 환경 변수 로드
# -----------------------------
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("GEMINI_API_KEY를 찾을 수 없습니다. .env 파일을 확인하세요.")
    raise SystemExit(1)
genai.configure(api_key=API_KEY)

# -----------------------------
# 2) 입력/출력 경로
# -----------------------------
INPUT_IMAGE_PATH = "test.jpg"   # 원본 피자 이미지
OUTPUT_IMAGE_PATH = "result_natural.jpg"

# -----------------------------
# 3) 원본 이미지 로드 + 16:9 레터박스
# -----------------------------
try:
    ref_image = Image.open(INPUT_IMAGE_PATH).convert("RGB")
except FileNotFoundError:
    print(f"'{INPUT_IMAGE_PATH}' 파일을 찾을 수 없습니다.")
    raise SystemExit(1)

ref_image_16x9 = to_16x9_letterbox(ref_image)

# -----------------------------
# 4) Gemini 프롬프트 생성 (fallback 포함)
# -----------------------------
user_prompt = (
    "A delicious pizza on a natural wooden table, realistic natural sunlight, "
    "soft shadows, food highlighted, high detail, ultra realistic, "
    "cinematic photography, soft studio lighting, subtle reflections, bokeh background, cozy and warm atmosphere"
)

role_definition = """
You are an advertising marketing director. 
Keep the core subject (pizza) completely intact while optimizing lighting, background, and color to create a luxurious advertisement image.
"""

final_gemini_prompt = f"""
{role_definition}
[User's Request]: {user_prompt}
Provide a detailed English prompt suitable for Stable Diffusion img2img.
"""

try:
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    gemini_response = model.generate_content([final_gemini_prompt, ref_image_16x9])
    generated_prompt = (gemini_response.text or "").strip()
    if not generated_prompt:
        raise ValueError("빈 프롬프트 반환됨")
except Exception as e:
    print("⚠️ Gemini 오류, fallback 프롬프트 사용:", e)
    generated_prompt = user_prompt

# -----------------------------
# 5) Stable Diffusion img2img (GPU 자동)
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Stable Diffusion 로딩 중... (디바이스: {device})")
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if device=="cuda" else torch.float32
)
pipe = pipe.to(device)

# img2img 세팅
strength = 0.3          # 원본 피자 보존
guidance_scale = 7.5     # 프롬프트 반영 강도
num_inference_steps = 35

# 피사체 훼손 방지용 negative prompt
negative_prompt = (
    "do not change the core subject, no extra objects, no text, no logos, "
    "no distortions, no deformations, no different product type, no different food, "
    "no hands, no watermark, low quality, blurry"
)

print("이미지 생성 중...")
with torch.no_grad():
    out = pipe(
        prompt=generated_prompt,
        image=ref_image_16x9,
        strength=strength,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps,
        negative_prompt=negative_prompt
    )
gen_img = out.images[0]

# -----------------------------
# 6) 저장
# -----------------------------
gen_img.save(OUTPUT_IMAGE_PATH, quality=95)
print(f"\n✅ 완료: '{OUTPUT_IMAGE_PATH}' 로 저장되었습니다.")
