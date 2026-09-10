import re

SQL_KEYWORDS = {
    "employee", "leave", "performance", "department", 
    "remaining leave", "used leave", "annual leave", "position", "employee id"
}

POLICY_KEYWORDS = {
    "policy", "remote", "holiday", "leave policy", 
    "work from home", "guideline", "sick", "ill"
}

# Small talk and general conversation triggers
GENERAL_PHRASES = {
    "hi", "hello", "hey", "how are you", "how can you help me", 
    "bye", "goodbye", "have a nice day", "thanks", "thank you", 
    "thank you very much", "tell me about you", "introduce yourself", 
    "what can you do for me", "who are you", "what is your name"
}

VALID_ROUTES = {
    "SQL", "PINECONE", "BOTH", "IMAGE", "DOCUMENT", "INVOICE", "GENERAL"
}

def route_question(question, has_file=False, file_type=None):
    if has_file:
        if file_type in {".png", ".jpg", ".jpeg", ".webp"}:
            if "invoice" in question.lower():
                return "INVOICE"
            return "IMAGE"
        if file_type in {".pdf", ".docx", ".csv", ".xlsx", ".txt"}:
            return "DOCUMENT"
        
    question_lower = question.strip().lower()
    
    # Check SQL triggers
    needs_sql = any(k in question_lower for k in SQL_KEYWORDS)
    if re.search(r'emp-2026-\d{3}', question_lower):
        needs_sql = True
        
    needs_policy = any(k in question_lower for k in POLICY_KEYWORDS)
    
    if needs_sql and needs_policy:
        return "BOTH"
    if needs_sql:
        return "SQL"
        
    # Clean punctuation (e.g., "hi!" -> "hi", "how are you?" -> "how are you")
    cleaned_q = re.sub(r'[^\w\s]', '', question_lower).strip()
    
    # Check if user message is purely standard small talk
    if cleaned_q in GENERAL_PHRASES:
        return "GENERAL"
        
    # All other non-SQL, non-small-talk queries route to PINECONE
    return "PINECONE"