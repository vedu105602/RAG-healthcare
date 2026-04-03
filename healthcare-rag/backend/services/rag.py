import os
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from services.guardrails import get_rag_prompt, get_medical_disclaimer

from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage

def _mock_invoke(inputs):
    return AIMessage(content="This is a mock response because the ANTHROPIC_API_KEY environment variable was not found. Please set your API key in the .env file to use the real RAG generator.")

def MockLLM():
    """Fallback LLM if OpenAI API key is missing."""
    return RunnableLambda(_mock_invoke)

class RAGPipeline:
    def __init__(self):
        # We use a completely local embedding model!
        print("Initializing Embeddings Model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Local persistent directory for Chroma database
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "chroma_db")
        os.makedirs(db_path, exist_ok=True)
        
        print("Initializing Vector Store...")
        self.vector_store = Chroma(
            collection_name="healthcare_docs",
            embedding_function=self.embeddings,
            persist_directory=db_path
        )
        
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            # similarity search parameters: top 5 chunks
            search_kwargs={"k": 5}
        )
        
        # Generator
        # In a real environment, you'd specify model_name="gpt-4" or similar
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key and api_key.startswith("sk-ant-"):
            print("Using Claude LLM...")
            self.llm = ChatAnthropic(temperature=0.0, model_name="claude-3-haiku-20240307")
        else:
            print("Using Mock LLM...")
            self.llm = MockLLM()
        
        self.prompt = get_rag_prompt()
        self.output_parser = StrOutputParser()
        
    def _format_docs(self, docs):
        # We also want to record citations. For the LLM context, join string.
        # But we also need the raw docs to return source citations.
        return "\n\n".join(f"[{doc.metadata.get('source', 'Unknown')}]\n{doc.page_content}" for doc in docs)

    def generate_response(self, query: str):
        # Retrieve context manually to inspect sources and calculate fake confidence
        docs_with_scores = self.vector_store.similarity_search_with_score(query, k=5)
        
        retrieved_docs = []
        max_cosine_similarity = 0.0
        
        # Chroma returns squared L2 distance by default.
        # Cosine similarity for L2-normalized vectors = 1 - (L2_squared / 2)
        for doc, distance in docs_with_scores:
            cosine_sim = 1.0 - (distance / 2.0)
            max_cosine_similarity = max(max_cosine_similarity, cosine_sim)
            retrieved_docs.append(doc)
            
        confidence_score = max_cosine_similarity
        
        # STRICT GUARDRAIL: Refuse to answer if the best chunk is < 0.75 similarity
        if max_cosine_similarity < 0.75:
            retrieved_docs = [] # Erase context
            answer = "This information is not available in the provided documents."
        else:
            context_string = self._format_docs(retrieved_docs)
            
            # LangChain chain 
            chain = self.prompt | self.llm | self.output_parser
            answer = chain.invoke({"context": context_string, "question": query})
            answer += get_medical_disclaimer()

        sources = [
            {
                "source": doc.metadata.get("source", "Unknown"), 
                "snippet": doc.page_content[:200] + "..."
            } 
            for doc in retrieved_docs
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence_score": confidence_score
        }
