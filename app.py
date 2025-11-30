import streamlit as st
import chromadb
from pypdf import PdfReader
from google import genai

# ================================
# 🔐 LOAD API KEY FROM SECRETS
# ================================
API_KEY = st.secrets["API_KEY"]

# Initialize Gemini client
client = genai.Client(api_key=API_KEY)

# ================================
# 🔥 EMBEDDING FUNCTION (NO TORCH)
# ================================
def embed_text(text: str):
    response = client.models.embed_content(
        model="models/text-embedding-004",
        content=text
    )
    return response.embedding


# ================================
# STREAMLIT UI
# ================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.set_page_config(page_title="Knowledge Base Assistant", layout="wide")

st.markdown("<h1 style='text-align: center;'>📚 Knowledge Base Assistant</h1>", 
            unsafe_allow_html=True)

# Sidebar for uploads
st.sidebar.header("📄 Upload PDF or TXT")
uploaded_files = st.sidebar.file_uploader("Upload multiple files", accept_multiple_files=True)

st.sidebar.markdown("""
### 📝 Usage:
1. Upload your documents  
2. They will be indexed  
3. Ask questions  
4. Answers ONLY from your documents  
""")

# ================================
# ChromaDB Setup
# ================================
client_chroma = chromadb.Client()
collection = client_chroma.get_or_create_collection(name="docs")


# ================================
# PROCESS UPLOADED DOCUMENTS
# ================================
if uploaded_files:
    for idx, f in enumerate(uploaded_files):
        if f.name.endswith(".pdf"):
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        else:
            text = f.read().decode("utf-8")

        embedding = embed_text(text)

        collection.add(
            ids=[str(idx)],
            documents=[text],
            embeddings=[embedding]
        )

    st.sidebar.success("Documents successfully indexed!")


# ================================
# CHAT UI
# ================================
st.markdown("---")
st.subheader("💬 Chat with your Document")

# Chat bubbles CSS
st.markdown("""
<style>
.user-msg {
    background-color: #2b6cb0;
    color: white;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
    max-width: 70%;
    margin-left: auto;
}
.assistant-msg {
    background-color: #2d2d2d;
    color: white;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
    max-width: 70%;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)

# Display previous chat
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='assistant-msg'>{msg['content']}</div>", unsafe_allow_html=True)

# ================================
# USER INPUT
# ================================
user_msg = st.chat_input("Ask a question…")

if user_msg:
    st.session_state.chat_history.append({"role": "user", "content": user_msg})

    # Embed query
    q_embed = embed_text(user_msg)

    # Retrieve top matches
    results = collection.query(query_embeddings=[q_embed], n_results=3)
    context = "\n\n".join(results["documents"][0]) if results["documents"] else "No context found."

    # Build prompt
    prompt = f"""
Use ONLY the context below to answer.

Context:
{context}

Question:
{user_msg}

Answer clearly:
"""

    # Generate LLM answer
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    ).text

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()



