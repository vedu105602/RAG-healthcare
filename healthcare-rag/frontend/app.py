import streamlit as st
import requests
import os
import time
from dotenv import load_dotenv

# Load env variables (for display purposes mostly, backend holds actual logic)
load_dotenv()

# Constants
BACKEND_URL = "http://127.0.0.1:8000/api"

# Configure standard Streamlit page
st.set_page_config(
    page_title="Healthcare Info Assistant",
    page_icon="⚕️",
    layout="wide"
)

# Custom CSS for animations and styling
st.markdown("""
<style>
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(-20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideUp {
        0% { opacity: 0; transform: translateY(30px) scale(0.98); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }
    
    .fade-in-content {
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Animate every chat message dynamically */
    .stChatMessage {
        animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    
    /* Prettier styling for profile card */
    .user-profile {
        background: linear-gradient(145deg, #ffffff, #f0f2f6);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        border-left: 5px solid #0066cc;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        color: #333;
        transition: transform 0.3s ease;
    }
    .user-profile:hover {
        transform: translateY(-2px);
    }
    
    /* Source Chips styling */
    .source-chip {
        display: inline-block;
        background-color: #e2e8f0;
        border-radius: 16px;
        padding: 4px 12px;
        margin: 4px 4px 4px 0;
        font-size: 0.85em;
        font-weight: 600;
        color: #334155;
        border: 1px solid #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# Initialize chat history and session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_details" not in st.session_state:
    st.session_state.user_details = {}

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am a Healthcare Information Assistant. Please upload your documents in the sidebar, and I will answer questions purely based on them. How can I help you today?"}
    ]

def login_page():
    st.markdown('<div class="fade-in-content">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("⚕️ Healthcare Assistant")
        st.markdown("### User Authentication")
        st.markdown("Please enter your details to access the secure portal.")
        
        with st.form("login_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            role = st.selectbox("Role", ["Patient", "Doctor", "Healthcare Professional", "Researcher"])
            department = st.text_input("Department / Specialization (Optional)")
            
            submitted = st.form_submit_button("Access Portal ✨", use_container_width=True)
            
            if submitted:
                if name and email:
                    with st.spinner("Authenticating credentials and preparing workspace..."):
                        time.sleep(1.5) # Simulate login transition animation
                    st.session_state.user_details = {
                        "Name": name,
                        "Email": email,
                        "Role": role,
                        "Department": department if department else "N/A"
                    }
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("⚠️ Please provide at least your Name and Email Address.")
                    
    st.markdown('</div>', unsafe_allow_html=True)

def main_app():
    # Sidebar for document ingestion and profile
    with st.sidebar:
        st.markdown('<div class="fade-in-content">', unsafe_allow_html=True)
        st.header("👤 User Profile")
        
        # Display entered details to the user
        st.markdown(f"""
        <div class="user-profile">
            <b>Name:</b> {st.session_state.user_details.get('Name', '')}<br>
            <b>Role:</b> {st.session_state.user_details.get('Role', '')}<br>
            <b>Email:</b> {st.session_state.user_details.get('Email', '')}<br>
            <b>Dept:</b> {st.session_state.user_details.get('Department', '')}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()
            
        st.markdown("---")
        
        st.header("1. Upload Documents 📚")
        st.info("Supported formats: PDF, DOCX, TXT, Web URLs")
        
        uploaded_files = st.file_uploader(
            "Upload healthcare-related documents", 
            accept_multiple_files=True,
            type=["pdf", "docx", "txt"]
        )
        
        web_url = st.text_input("Or enter a Web URL:")
        
        if st.button("Submit Documents & URLs"):
            if not uploaded_files and not web_url:
                st.warning("Please upload at least one file or enter a URL.")
            else:
                with st.spinner("Processing and analyzing content..."):
                    all_successful = True
                    
                    # File Uploads
                    if uploaded_files:
                        for uploaded_file in uploaded_files:
                            try:
                                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                                response = requests.post(f"{BACKEND_URL}/upload", files=files)
                                
                                if response.status_code == 200:
                                    st.success(f"Ingested {uploaded_file.name}")
                                else:
                                    st.error(f"Error processing {uploaded_file.name}: {response.text}")
                                    all_successful = False
                            except requests.exceptions.ConnectionError:
                                st.error("Cannot connect to backend server.")
                                all_successful = False
                                break
                                
                    # URL Ingestion
                    if web_url:
                        try:
                            response = requests.post(f"{BACKEND_URL}/upload-url", json={"url": web_url})
                            if response.status_code == 200:
                                st.success(f"Ingested content from {web_url}")
                            else:
                                st.error(f"Error processing URL: {response.text}")
                                all_successful = False
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to backend server. Make sure FastAPI is running on port 8000.")
                            all_successful = False
                    
                    if all_successful:
                        st.success("All source material processed successfully! You can now start asking questions.")

        st.markdown("---")
        st.markdown("### 🛡️ Guardrails Active")
        st.markdown("- **No Hallucination**: Answers strictly from documents.")
        st.markdown("- **Citations Required**: Displays source snippets.")
        st.markdown("- **Uncertainty Handled**: Responds gracefully when data is missing.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Main Chat Interface
    st.markdown('<div class="fade-in-content">', unsafe_allow_html=True)
    st.title("⚕️ Healthcare Info Assistant")
    st.markdown("*A Retrieval-Augmented Generation (RAG) System for patient histories and medical knowledge.*")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources if assistant provided them
            if "sources" in message and message["sources"]:
                st.markdown(f"**Retrieval Confidence:** `{message.get('confidence_score', 0):.2f}` (Cosine Similarity)")
                
                # Show chips
                chip_html = ""
                for idx, source in enumerate(message["sources"]):
                    filename = source.get('source', 'Unknown')
                    chip_html += f'<span class="source-chip">📄 {filename} (Snippet {idx+1})</span>'
                st.markdown(chip_html, unsafe_allow_html=True)
                
                with st.expander("View Source Content"):
                    for idx, source in enumerate(message["sources"]):
                        st.markdown(f"**{source['source']}**")
                        st.text(source['snippet'])

    # Chat Input
    if prompt := st.chat_input("Ask about the uploaded healthcare guidelines or patient records..."):
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Searching documents & generating answer..."):
                try:
                    response = requests.post(f"{BACKEND_URL}/chat", json={"query": prompt})
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "")
                        sources = data.get("sources", [])
                        confidence_score = data.get("confidence_score", 0)
                        
                        st.markdown(answer)
                        
                        if sources:
                            st.markdown(f"**Retrieval Confidence:** `{confidence_score:.2f}` (Cosine Similarity)")
                            
                            # Show chips
                            chip_html = ""
                            for idx, source in enumerate(sources):
                                filename = source.get('source', 'Unknown')
                                chip_html += f'<span class="source-chip">📄 {filename} (Snippet {idx+1})</span>'
                            st.markdown(chip_html, unsafe_allow_html=True)
                            
                            with st.expander("View Source Content"):
                                for idx, source in enumerate(sources):
                                    st.markdown(f"**{source['source']}**")
                                    st.text(source['snippet'])
                                    
                        # Add strictly to memory
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources,
                            "confidence_score": confidence_score
                        })
                    else:
                        st.error(f"Error from server: {response.text}")
                except requests.exceptions.ConnectionError:
                    error_msg = "⚠️ Cannot connect to backend server. Ensure FastAPI is running on http://127.0.0.1:8000."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()
