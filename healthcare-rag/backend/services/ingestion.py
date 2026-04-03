import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def ingest_document(file_path: str, vector_store) -> int:
    """
    Load a document, chunk it, and add embeddings to the vector store.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
    
    documents = loader.load()
    
    # Semantic + Fixed Size chunking using tokens
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=500,
        chunk_overlap=50,
    )
    
    chunks = text_splitter.split_documents(documents)
    
    # Add metadata to chunks, keep the original filename for source
    filename = os.path.basename(file_path)
    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = filename
        chunk.metadata["chunk_id"] = i
    
    # Store in VectorDB
    if chunks:
        vector_store.add_documents(chunks)
        if hasattr(vector_store, 'persist'):
            vector_store.persist()
    
    return len(chunks)

def ingest_url(url: str, vector_store) -> int:
    """
    Load content from a URL, chunk it, and add embeddings to the vector store.
    """
    loader = WebBaseLoader(url)
    documents = loader.load()
    
    # Semantic + Fixed Size chunking using tokens
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=500,
        chunk_overlap=50,
    )
    
    chunks = text_splitter.split_documents(documents)
    
    # Add metadata to chunks, setting source as the URL
    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = url
        chunk.metadata["chunk_id"] = i
        
    # Store in VectorDB
    if chunks:
        vector_store.add_documents(chunks)
        if hasattr(vector_store, 'persist'):
            vector_store.persist()
            
    return len(chunks)
