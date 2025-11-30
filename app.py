import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
from google import genai

# ================================
# API KEY
# ================================
API_KEY = st.secrets["API_KEY"]

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Knowledge Base Assistant", layout="wide")

# ---- INITIAL STATE ----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---- TITLE ----
st.markdown("<h1 style='text-align:center;'>📚 Knowledge Base Assistant</h1>", unsafe_allow_html=True)

# ---- SIDEBAR ----
st.sidebar.header("📄 Upload Documents")
uploaded_files = st.sidebar.file_uploader("Upload PDF or TXT", accept_multiple_files=True)

# ---- GEMINI CLIENT ----
client = genai.Client(api_key=API_KEY)

# ---- GEMINI EMBEDDINGS ----
def embed_text(text):
    emb = client.models.embed_content(
        model="models/text-embedding-004",
        content=text
    )
    return emb.embedding

# ---- VECTOR DB ----
client_chroma = chromadb.Client()
collection = client_chroma.get_or_create_collection(name="docs")

# ---- READ & INDEX FILES ----
if uploaded_files:
    for idx, f in enumerate(uploaded_files):
        if f.name.endswith(".pdf"):
            reader = PdfReader(f)
            full_text = "".join([page.extract_text() or "" for page in reader.pages])
        else:
            full_text = f.read().decode("utf-8", errors="ignore")

        vec = embed_text(full_text)

        collection.add(
            ids=[f"doc_{idx}"],
            documents=[full_text],
            embeddings=[vec]
        )

    st.sidebar.success("📌 Documents indexed successfully!")

# ---- CHAT UI ----
st.markdown("---")
st.subheader("💬 Chat with your document")

user_input = st.chat_input("Ask a question...")

# Display conversation
for msg in st.session_state.chat_history:
    role = "user-msg" if msg["role"] == "user" else "assistant-msg"
    st.markdown(f"<div class='{role}'>{msg['content']}</div>", unsafe_allow_html=True)

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    q_emb = embed_text(user_input)

    results = collection.query(
        query_embeddings=[q_emb],
        n_results=3
    )

    context = "\n\n".join(results["documents"][0]) if results["documents"] else "No context found."

    prompt = f"""
Use ONLY this context to answer:

Context:
{context}

Question: {user_input}

Answer:
"""

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    ).text

    st.session_state.chat_history.append({"role": "assistant", "content": response})

    st.rerun()


