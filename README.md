📚 Knowledge Base AI Assistant

An intelligent document-question answering system powered by Gemini 2.5 Flash & ChromaDB.

This project was built for the AI Agent Development Challenge where participants are required to build a fully functional AI Agent within 48 hours.
My agent belongs to Category 2 — Business Operations → Knowledge Base Agent.

The system allows users to upload documents (PDF/TXT), and then chat with the document using an AI-powered conversational interface.

It works exactly like an internal AI assistant that answers questions based only on your document — not the internet.📚 Knowledge Base AI Assistant

An intelligent document-question answering system powered by Gemini 2.5 Flash & ChromaDB.

This project was built for the AI Agent Development Challenge where participants are required to build a fully functional AI Agent within 48 hours.
My agent belongs to Category 2 — Business Operations → Knowledge Base Agent.

The system allows users to upload documents (PDF/TXT), and then chat with the document using an AI-powered conversational interface.

It works exactly like an internal AI assistant that answers questions based only on your document — not the internet.

🌟 Features (Detailed)
📥 1. Upload Documents

Users can upload:

PDF files

TXT files

These documents become the "knowledge base" of the assistant.

🔍 2. Intelligent Document Parsing

The system:

Reads the document

Extracts text from all pages

Cleans and prepares the text

For PDFs, it extracts each page using PyPDF.

🧠 3. Convert Text to Embeddings

The text is split into small chunks and converted into numerical vectors using:

SentenceTransformer (all-MiniLM-L6-v2)

This allows semantic meaning to be captured.

🗃 4. Store in Vector Database (ChromaDB)

All the embeddings are stored inside ChromaDB, allowing:

Fast semantic search

Retrieval of the most relevant chunks per question

🤖 5. Understanding Your Question

When the user asks a question:

The question is also converted into an embedding

ChromaDB finds the 3 most relevant document chunks

This ensures the AI only uses information from your uploaded file.

🔥 6. Gemini 2.5 Flash Provides the Answer

The system builds a prompt that includes:

Top retrieved document chunks

The full chat history

The user’s latest question

Then it sends the prompt to the Gemini 2.5 Flash model.

Gemini produces a natural, conversational, accurate answer strictly based on document context.

💬 7. Continuous Chat Memory

The agent:

Remembers previous questions

Remembers all answers

Maintains a flowing conversation

This creates a true chatbot experience.

🎨 8. Beautiful Chat UI with Message Bubbles

User messages appear in blue bubbles aligned right

AI messages appear in dark bubbles aligned left

Clean, modern look similar to top-tier AI apps


📊 Features & Limitations
✔ Strengths

  *Fast, accurate document-based answers

  *Secure: only uses your uploaded content

  *No hallucination (constrained by retrieval)

  *Clean conversational interface

  *Scalable for bigger documents

  *Reusable architecture for other agents

❌ Limitations

  *Cannot read DOCX unless added

  *Large PDFs may take longer to embed

  *No multi-user login

  *Memory resets on page refresh

🔮 Future Improvements

  *Support for DOCX, PPTX

  *Multi-document tagging + search

  *Chat history persistence

  *Better chunking strategies

  *Support for images inside PDFs

  *Admin dashboard

  *Multi-language support



  Installation & Running Locally
1. Clone the repository:
      git clone https://github.com/ummehani0531/knowledge-base-agent.git
      cd knowledge-base-agent


2. Create a virtual environment :
      python3 -m venv env
      source env/bin/activate

3.Install dependencies:
      pip install -r requirements.txt

4.Add your Gemini API key :
       API_KEY = "YOUR_API_KEY"

5.Run the app:
       streamlit run app.py       
