import streamlit as st
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
from google import genai

# ================================
# 🔐 HARD-CODE YOUR API KEY HERE
# ================================
API_KEY = st.secrets["API_KEY"]
# ================================

# ---- SESSION STATE INITIALIZATION ----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Knowledge Base Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title on main page
st.markdown("<h1 style='text-align: center;'>📚 Knowledge Base Assistant</h1>", unsafe_allow_html=True)


# ---- SIDEBAR ----
st.sidebar.header("📄 Document Upload")
st.sidebar.write("Upload a PDF or TXT file to load into the Knowledge Base:")

uploaded_files = st.sidebar.file_uploader("Drag & Drop or Browse", accept_multiple_files=True)

# Sidebar instructions
st.sidebar.markdown("""
### 📝 How to use:
1. Upload a document (PDF / TXT)  
2. I will index it  
3. Ask questions in the chat  
4. I answer using ONLY your document  
""")

# ---- GEMINI CLIENT ----
client = genai.Client(api_key=API_KEY)

# Embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

# Vector DB
client_chroma = chromadb.Client()
collection = client_chroma.get_or_create_collection(
    name="docs",
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
      model_name="all-MiniLM-L6-v2",
      device="cpu"


    )
)

# ---- PROCESS DOCS ----
if uploaded_files:
    docs_text = []
    for f in uploaded_files:
        if f.name.endswith(".pdf"):
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        else:
            text = f.read().decode("utf-8", errors="ignore")

        docs_text.append(text)

    # Store in ChromaDB
    for i, text in enumerate(docs_text):
        collection.add(
            ids=[str(i)],
            documents=[text],
            embeddings=[embedder.encode(text)]
        )

    st.sidebar.success("Documents processed and indexed!")

# ==========================================
#            CHAT INTERFACE
# ==========================================

st.markdown("---")
st.subheader("💬 Chat with your document")

# CSS for chat bubbles
chat_css = """
<style>
.user-msg {
    background-color: #2b6cb0;
    color: white;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
    max-width: 70%;
    margin-left: auto;
    margin-right: 10px;
}
.assistant-msg {
    background-color: #2d2d2d;
    color: white;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
    max-width: 70%;
    margin-right: auto;
    margin-left: 10px;
}
</style>
"""
st.markdown(chat_css, unsafe_allow_html=True)

# ---- DISPLAY CHAT HISTORY ----
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='assistant-msg'>{msg['content']}</div>", unsafe_allow_html=True)

# ---- CHAT INPUT ----
user_input = st.chat_input("Ask a question about your document...")

if user_input:
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Retrieve contextual chunks
    q_embed = embedder.encode(user_input)
    results = collection.query(query_embeddings=[q_embed], n_results=3)
    context = "\n\n".join(results["documents"][0]) if results["documents"] else "No context found."

    # Build prompt
    conversation_text = ""
    for m in st.session_state.chat_history:
        if m["role"] == "user":
            conversation_text += f"User: {m['content']}\n"
        else:
            conversation_text += f"Assistant: {m['content']}\n"

    prompt = f"""
Use ONLY the context below to answer clearly and accurately.

Context:
{context}

Conversation so far:
{conversation_text}

Current Question:
{user_input}

Answer:
"""

    # Gemini response
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    ).text

    # Save assistant reply
    st.session_state.chat_history.append({"role": "assistant", "content": response})

    st.rerun()

