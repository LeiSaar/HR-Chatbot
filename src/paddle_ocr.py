import logging
import traceback
import gc
import threading

import numpy as np
from PIL import Image
from paddleocr import PaddleOCR


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.getLogger("ppocr").setLevel(logging.ERROR)


# ---------------------------------------------------------
# Global OCR instance
# Loaded once when server starts
# ---------------------------------------------------------

ocr = PaddleOCR(
    use_angle_cls=False,
    enable_mkldnn=False,
    lang="en"
)


# ---------------------------------------------------------
# Thread safety
# Prevent simultaneous OCR calls from corrupting OCR state
# ---------------------------------------------------------

ocr_lock = threading.Lock()



def extract_text(image_path: str) -> str:
    """
    Extract text from image using PaddleOCR.

    Supports:
    - PNG transparency
    - JPG
    - JPEG
    - WebP

    Returns:
        OCR text as a single string
    """

    img_np = None


    try:

        # -------------------------------------------------
        # Load image safely
        # -------------------------------------------------

        with Image.open(image_path) as img:


            # Handle transparent PNG
            if (
                img.mode in ("RGBA", "LA")
                or (
                    img.mode == "P"
                    and "transparency" in img.info
                )
            ):

                img = img.convert("RGBA")


                background = Image.new(
                    "RGBA",
                    img.size,
                    (255, 255, 255, 255)
                )


                img = Image.alpha_composite(
                    background,
                    img
                ).convert("RGB")


            else:

                img = img.convert("RGB")



            # Convert PIL image -> numpy array

            img_np = np.array(
                img
            )



        print(
            "Starting PaddleOCR..."
        )



        # -------------------------------------------------
        # Run OCR
        # -------------------------------------------------

        with ocr_lock:

            result = ocr.predict(
                img_np
            )



        # -------------------------------------------------
        # Cleanup image memory
        # -------------------------------------------------

        del img_np
        img_np = None

        gc.collect()



        if not result:

            print(
                "PaddleOCR returned no result"
            )

            return ""



        page = result[0]



        texts = page.get(
            "rec_texts",
            []
        )



        if not texts:

            return ""



        return "\n".join(
            str(t)
            for t in texts
        )



    except Exception as e:


        print(
            "\n========== PADDLE OCR ERROR =========="
        )

        print(
            str(e)
        )

        traceback.print_exc()

        print(
            "=======================================\n"
        )


        return ""



    finally:


        # Extra cleanup protection

        if img_np is not None:

            del img_np


        gc.collect()