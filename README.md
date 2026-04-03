Healthcare Information RAG Assistant ⚕️
A production-ready Retrieval-Augmented Generation (RAG) assistant designed specifically for healthcare environments, focusing on Responsible AI principles.

Features
Document Ingestion System: Securely upload PDF, DOCX, and TXT files.
Semantic Retrieval: Uses ChromaDB and HuggingFace embeddings for localized similarity search.
Strict Guardrails: Enforces a strict 0.75 cosine similarity threshold. If query semantics fail to meet this match limit with context chunks, generation is abruptly blocked.
Transparent Citations: End users see exactly which document and snippet generated the text via Source Chips, alongside native Cosine Similarity confidence arrays.
Modular Architecture: Built with FastAPI for the backend and Streamlit for the user interface.
Quickstart Guide
1. Requirements
Ensure you have Python 3.9+ installed. You will need two terminal tabs to run the backend and frontend simultaneously.

2. Set Up the Backend
Navigate to the backend folder:

cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
Note on LLM Provision: By default, the system will use a local Mock LLM if no API key is provided, returning hardcoded responses. For full capabilities, copy the placeholder .env file to .env in the root folder and add your ANTHROPIC_API_KEY:

ANTHROPIC_API_KEY="sk-ant-..."
Start the FastAPI backend:

uvicorn main:app --reload
The server will start at http://localhost:8000.

3. Set Up the Frontend
Open a new terminal tab and navigate to the frontend folder:

cd frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Run the Streamlit app:

streamlit run app.py
The chat interface will open in your default browser at http://localhost:8501.

Evaluation & Testing
Launch both the backend and frontend.
Observe the sidebar and upload the file from data/sample_medical_guidelines.txt using the file uploader. Uploading triggers backend processing with tiktoken limit chunking (500 tokens).
Try asking an in-scope question: "What should I eat after an appendectomy?"
Try asking an out-of-scope question: "How do I treat a broken arm?"
Notice the strict AI guardrails kick in if the vector distance exceeds the math cutoff barrier (< 0.75 similarity).
Notice the strict AI guardrails kicking in to prevent dangerous medical hallucination.
