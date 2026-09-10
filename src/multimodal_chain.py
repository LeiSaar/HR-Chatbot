import os
import tempfile
import ollama
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
VISION_MODEL = os.getenv("VISION_MODEL").strip().strip('"').strip("'")

def resize_for_fast_vision(image_path: str, max_dim: int = 2048) -> str:
    """
    Safely downscales extremely high-res images to max 2048px while keeping 
    text sharp. Preserves original if already under limits.
    """
    try:
        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            width, height = img.size
            
            # Only resize if the image is larger than 2048px on its longest edge
            if max(width, height) > max_dim:
                img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                img.save(temp_file.name, "JPEG", quality=95)
                return temp_file.name
        return image_path
    except Exception:
        return image_path

def analyze_image_text(image_path: str, custom_prompt: str = None) -> str:

    optimized_path = resize_for_fast_vision(image_path)
    prompt = custom_prompt or "Describe this image in detail and transcribe any visible text."

    try:
        response = ollama.chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [optimized_path]
                }
            ],
            options={
                "temperature": 0.0,
                "num_ctx": 4096,
                "num_predict": 1024
            }
        )
        return response["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Vision processing failed ({VISION_MODEL}): {str(e)}")
    finally:
        if optimized_path != image_path and os.path.exists(optimized_path):
            try:
                os.remove(optimized_path)
            except OSError:
                pass