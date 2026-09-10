import traceback
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple


from src.conversation_memory import (
    format_history,
    save_message
)

from src.conversation_manager import (
    user_owns_conversation,
    update_conversation_timestamp,
    save_database_message
)

from src.question_rewriter import rewrite_question

from src.router import route_question

from src.sql_context import get_sql_context

from pinecone_scripts.pinecone_retriever import (
    get_pinecone_context
)

from src.answer_chain import answer_chain

from src.document_processor import extract_text

from src.invoice_extractor import (
    extract_invoice_from_image
)

from src.export_service import (
    export_invoice_csv,
    export_invoice_pdf
)

from src.paddle_ocr import (
    extract_text as extract_image_text_paddle
)



IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp"
}


DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".csv",
    ".xlsx",
    ".txt"
}




def process_chat_message(
        user,
        conversation_id,
        question,
        uploaded_file=None
):


    print(
        "\n========== NEW CHAT REQUEST =========="
    )

    print(
        question
    )

    print(
        uploaded_file
    )



    try:


        # -------------------------------------------------
        # Permission check
        # -------------------------------------------------

        if not user_owns_conversation(
            conversation_id,
            user.id
        ):

            return {
                "success": False,
                "status_code": 403,
                "answer": "Conversation not found."
            }



        history = format_history(
            user.id,
            conversation_id
        )


        standalone_question = rewrite_question(
            question,
            history
        )



        generated_files = []


        file_path = None
        file_ext = None



        if uploaded_file:


            file_path = uploaded_file.get(
                "path"
            )

            file_ext = uploaded_file.get(
                "extension",
                ""
            ).lower()



        if uploaded_file and not file_path:


            return {

                "success": False,
                "status_code":400,
                "answer":
                "Uploaded file path missing."

            }



        # -------------------------------------------------
        # Invoice detection
        # -------------------------------------------------

        q_lower = standalone_question.lower()


        is_invoice_request = uploaded_file and (

            any(
                keyword in q_lower
                for keyword in [
                    "invoice",
                    "bill",
                    "receipt"
                ]
            )

            or

            (
                "extract" in q_lower
                and
                "pdf" in q_lower
            )

        )



        # =================================================
        # INVOICE ROUTE
        # =================================================

        if is_invoice_request:


            route = "INVOICE"


            print(
                "STARTING INVOICE PIPELINE"
            )



            try:


                invoice_data = extract_invoice_from_image(
                    file_path
                )



                print(
                    "INVOICE EXTRACTION FINISHED"
                )

                print(
                    invoice_data
                )



                if (
                    invoice_data
                    and
                    isinstance(
                        invoice_data,
                        dict
                    )
                ):


                    csv_filename = export_invoice_csv(
                        invoice_data
                    )


                    print(
                        "CSV CREATED:",
                        csv_filename
                    )



                    pdf_filename = export_invoice_pdf(
                        invoice_data
                    )


                    print(
                        "PDF CREATED:",
                        pdf_filename
                    )



                    generated_files = [

                        {
                            "type":"csv",
                            "filename":csv_filename,
                            "url":
                            f"/generated/{csv_filename}"
                        },


                        {
                            "type":"pdf",
                            "filename":pdf_filename,
                            "url":
                            f"/generated/{pdf_filename}"
                        }

                    ]



                    answer = (
                        "I have successfully extracted "
                        "the invoice details and generated "
                        "your requested PDF and CSV files below."
                    )



                else:


                    answer = (
                        "Could not extract valid invoice "
                        "information from the image."
                    )



            except Exception as e:


                print(
                    "INVOICE PIPELINE ERROR"
                )

                traceback.print_exc()


                answer = (
                    "Invoice processing failed."
                )




        # =================================================
        # DOCUMENT / IMAGE HR ROUTE
        # =================================================

        elif uploaded_file:


            route = (
                "DOCUMENT_OR_IMAGE_RAG"
            )


            try:


                if file_ext in IMAGE_EXTENSIONS:


                    extracted_file_text = (
                        extract_image_text_paddle(
                            file_path
                        )
                    )


                    print(
                        "\nOCR TEXT:"
                    )

                    print(
                        extracted_file_text
                    )



                else:


                    extracted_file_text = (
                        extract_text(
                            file_path
                        )
                    )



                combined_query = (
                    f"{standalone_question}\n"
                    f"{ extracted_file_text }"
                ).strip()



                pinecone_context = (
                    get_pinecone_context(
                        combined_query
                    )
                )



                response = answer_chain.invoke(

                    {

                        "input":
                        combined_query,

                        "context":
                        pinecone_context

                    }

                )


                answer = (
                    response.content.strip()
                )



            except Exception:


                traceback.print_exc()


                answer = (
                    "Error processing uploaded file."
                )




        # =================================================
        # TEXT ONLY ROUTE
        # =================================================

        else:


            route = route_question(
                standalone_question,
                has_file=False
            )



            context_parts = []



            if route in (
                "SQL",
                "BOTH",
                "PINECONE"
            ):


                SafeUser = namedtuple(
                    "SafeUser",
                    [
                        "id",
                        "role",
                        "department",
                        "employee_id"
                    ]
                )



                thread_safe_user = SafeUser(

                    id=user.id,

                    role=getattr(
                        user,
                        "role",
                        None
                    ),

                    department=getattr(
                        user,
                        "department",
                        None
                    ),

                    employee_id=getattr(
                        user,
                        "employee_id",
                        None
                    )

                )



                with ThreadPoolExecutor() as executor:


                    futures = []



                    if route in (
                        "SQL",
                        "BOTH"
                    ):


                        futures.append(

                            executor.submit(
                                get_sql_context,
                                standalone_question,
                                thread_safe_user
                            )

                        )



                    if route in (
                        "PINECONE",
                        "BOTH"
                    ):


                        futures.append(

                            executor.submit(
                                get_pinecone_context,
                                standalone_question
                            )

                        )



                    for future in futures:

                        result = future.result()


                        if isinstance(
                            result,
                            dict
                        ):


                            if not result["allowed"]:

                                return {

                                    "success":False,
                                    "status_code":403,
                                    "answer":
                                    "Unauthorized SQL access."

                                }


                            context_parts.append(
                                result["context"]
                            )


                        else:

                            context_parts.append(
                                result
                            )



            context = (

                "No HR context required."

                if not context_parts

                else

                "\n\n".join(
                    context_parts
                )

            )



            response = answer_chain.invoke(

                {

                    "input":
                    standalone_question,

                    "context":
                    context

                }

            )


            answer = (
                response.content.strip()
            )



        # -------------------------------------------------
        # Save history
        # -------------------------------------------------

        save_message(
            user.id,
            conversation_id,
            "user",
            question
        )


        save_database_message(
            conversation_id,
            "user",
            question
        )



        save_message(
            user.id,
            conversation_id,
            "assistant",
            answer
        )


        save_database_message(
            conversation_id,
            "assistant",
            answer
        )


        update_conversation_timestamp(
            conversation_id
        )



        return {

            "success":True,

            "status_code":200,

            "answer":answer,

            "question":
            standalone_question,

            "route":route,

            "generated_files":
            generated_files

        }



    except Exception as e:


        print(
            "\n========== CHAT SERVER ERROR =========="
        )

        print(
            str(e)
        )

        traceback.print_exc()

        print(
            "========================================\n"
        )


        return {

            "success":False,

            "status_code":500,

            "answer":
            "Internal chatbot error."

        }