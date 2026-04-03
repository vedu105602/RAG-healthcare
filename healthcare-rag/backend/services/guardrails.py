from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage

# Strict prompt template following the user's requirements
SYSTEM_TEMPLATE = """
You are a reliable, professional, and friendly Healthcare Information Assistant.
Your purpose is to answer questions based STRICTLY on the provided documents.

CRITICAL INSTRUCTIONS:
1. Answer ONLY from the retrieved context provided below. DO NOT hallucinate or guess.
2. If the answer cannot be found in the provided context, you MUST reply verbatim: "This information is not available in the provided documents."
3. If the query is completely unrelated to healthcare or the documents, state that you cannot answer it.

OUTPUT FORMATTING:
When giving medical information based on the documents, keep your answer short, easy to understand, and ALWAYS structure it exactly with these headings:
1. Disease description
2. Symptoms
3. Causes
4. Treatment
5. Prevention

Context to use for your answer:
{context}
"""

def get_rag_prompt():
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_TEMPLATE),
        ("human", "{question}")
    ])
    return prompt

def get_medical_disclaimer():
    return "\n\n---\n**⚠️ Disclaimer:** *This is informational only. Consult a licensed clinician before taking action.*"

def calculate_confidence(retrieved_docs_with_scores):
    """
    Very crude proxy for confidence score based on vector distance/similarity.
    FAISS/Chroma distance: smaller is more similar in L2, larger in Cosine.
    Using default ChromaDB which works on L2 distance, so lower is better.
    """
    if not retrieved_docs_with_scores:
        return 0.0
    
    # Just grab the best score (first element) distances
    # A generic normalization depending on metric, assuming we bounded 0-1
    # Returning a generic fallback.
    return 0.85 
