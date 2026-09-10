import json
import re
import os
import traceback

from langchain_ollama import ChatOllama
from dotenv import load_dotenv

from src.paddle_ocr import extract_text


load_dotenv()


MODEL = os.getenv(
    "TEXT_MODEL",
    "llama3.2"
)


def get_invoice_llm():
    """
    Creates a fresh Ollama client for each invoice request.

    This avoids keeping a broken connection
    after a previous request.
    """

    return ChatOllama(
        model=MODEL,
        temperature=0,
        keep_alive="30m",
        timeout=120
    )



def extract_invoice_from_image(image_path: str) -> dict:
    """
    Extract invoice information from image.

    Flow:

    Image
      |
      v
    PaddleOCR
      |
      v
    Llama JSON extraction
      |
      v
    Python dictionary
    """

    try:

        # -------------------------------------------------
        # 1. OCR
        # -------------------------------------------------

        raw_ocr_text = extract_text(image_path)


        print(
            "\n" +
            "=" * 20 +
            " DEBUG: RAW OCR TEXT START " +
            "=" * 20
        )

        print(
            raw_ocr_text
            if raw_ocr_text.strip()
            else "[NO TEXT DETECTED]"
        )

        print(
            "=" * 20 +
            " DEBUG: RAW OCR TEXT END " +
            "=" * 20 +
            "\n"
        )


        if not raw_ocr_text.strip():
            return {}



        # -------------------------------------------------
        # 2. Create prompt
        # -------------------------------------------------

        prompt = f"""

You are an invoice extraction engine.

Extract invoice information from the OCR text.

Rules:

- Return ONLY valid JSON.
- Never use markdown.
- Never explain your answer.
- Never invent values.
- Missing values must be null.


ADDRESS RULES

vendor_address must ALWAYS be one string.

Example:

Correct:

"1912 Harvest Lane, New York, NY 12210"


Incorrect:

{{
    "street":"1912 Harvest Lane",
    "city":"New York"
}}


customer_address follows the same rule.


CURRENCY RULES

Detect invoice currency.

Return:

currency

using ISO code.

Examples:

$ -> USD
€ -> EUR
£ -> GBP
¥ -> JPY


Also return:

currency_symbol


Examples:

"$"
"€"


Do NOT remove currency symbols from money fields.


Correct:

"subtotal":"$145.00"


Incorrect:

"subtotal":"145.00"



Return JSON using this structure:


{{
    "invoice_number": null,
    "invoice_date": null,
    "due_date": null,

    "vendor_name": null,
    "vendor_address": null,

    "customer_name": null,
    "customer_address": null,

    "currency": null,
    "currency_symbol": null,

    "subtotal": null,
    "tax": null,
    "total": null,

    "items":[
        {{
            "description":"",
            "quantity":"",
            "unit_price":"",
            "amount":""
        }}
    ]
}}



OCR TEXT:

{raw_ocr_text}

"""


        print(
            "Sending invoice extraction request to Ollama..."
        )



        # -------------------------------------------------
        # 3. LLM extraction
        # -------------------------------------------------

        llm = get_invoice_llm()


        try:

            response = llm.invoke(prompt)

            content = response.content.strip()


        except Exception as e:

            print(
                "\n========== OLLAMA ERROR =========="
            )

            print(str(e))

            traceback.print_exc()

            print(
                "===================================\n"
            )

            return {}



        print(
            "=" * 20 +
            " DEBUG: LLM RESPONSE START " +
            "=" * 20
        )

        print(content)

        print(
            "=" * 20 +
            " DEBUG: LLM RESPONSE END " +
            "=" * 20 +
            "\n"
        )



        # -------------------------------------------------
        # 4. Extract JSON
        # -------------------------------------------------

        match = re.search(
            r"\{[\s\S]*\}",
            content
        )


        if not match:

            print(
                "No JSON object found in LLM response"
            )

            return {}



        json_text = match.group()



        try:

            invoice_json = json.loads(
                json_text
            )

            return invoice_json



        except json.JSONDecodeError:


            print(
                "Invalid JSON returned by model:"
            )

            print(
                json_text
            )

            return {}



    except Exception as e:


        print(
            "\n========== INVOICE ERROR =========="
        )

        print(
            str(e)
        )

        traceback.print_exc()

        print(
            "===================================\n"
        )


        return {}