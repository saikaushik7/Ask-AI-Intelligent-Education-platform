Ask AI – Intelligent Education Platform

A complete AI-powered learning assistant built using Flask, Google Gemini, FAISS, BART Summarizer, OCR, and interactive tools such as Document Upload, Summarization, Quiz Generator, and AI Doubt Resolver.

🚀 Project Overview

Ask-AI is an intelligent educational platform that allows students to upload study materials and receive:

✓ Smart summaries

✓ Auto-generated MCQ quizzes from the document

✓ A RAG-based doubt resolver powered by semantic search

✓ Clean UI with glass-morphism

✓ Secure login & register authentication

✓ Full document history & deletion

Everything is processed locally except AI models, which use Google Gemini APIs.

🧠 Key Features
1️⃣ Document Upload & OCR

Upload PDF, TXT, DOCX

Extract text using:

PDF text extraction

OCR using Tesseract for scanned documents

DOCX text extraction

Automatically indexes document text using FAISS & Gemini embeddings.

2️⃣ AI-Powered Summarization

Uses Facebook BART Large CNN model

Generates a summary of ~35% of document length

Clean UI showing summary stats (ratio, word count)

3️⃣ RAG-Enabled Doubt Resolver

Ask any question related to the uploaded document

Uses:

Google text-embedding-004

FAISS vector search

Gemini generative model

Produces accurate, context-aware answers

4️⃣ MCQ Quiz Generator

Generates high-quality AI-generated quizzes directly from your document

Each question includes:

4 options

Correct answer

Explanation

Interactive quiz player with:

Correct/wrong highlighting

Score tracking

Final results screen

5️⃣ Secure User Login System

Authentication via:

Username

Email

Password

Flask-Login used for session management

User-specific document history & quiz results

🛠️ Tech Stack
Layer	Technology
Backend	Flask, Python
Frontend	HTML, CSS, Bootstrap, Glass-morphism UI
AI Models	Google Gemini 2.5, Gemini Embeddings, BART Summarizer
OCR	Tesseract
Vector Database	FAISS
Database	SQLite
Version Control	Git + GitHub
📂 Project Structure
ai_doc_app/
│
├── auth/                 → Login/Register routes
├── docs/                 → Uploading, OCR, Summarization, FAISS
├── quiz/                 → MCQ quiz generator & routes
├── rag/                  → Doubt resolver (RAG pipeline)
│
├── templates/            → HTML pages (UI)
├── static/               → Background images, CSS, JS
├── uploads/              → User uploaded documents
│
├── models.py             → Database models (User, Document, QuizResult)
├── app.py                → Main Flask app entry
├── config.py             → App configuration
├── users.db              → SQLite database
├── requirements.txt      → Python dependencies
└── README.md

⚙️ How to Run the Project
1️⃣ Create Virtual Environment
conda create -n ai-doc-app python=3.10
conda activate ai-doc-app

2️⃣ Install Requirements
pip install -r requirements.txt

3️⃣ Add Your Gemini API Key

Create a .env file:

GEMINI_API_KEY=your_api_key_here

4️⃣ Run Flask
python app.py

5️⃣ Open in Browser
http://127.0.0.1:5000

🎯 Screenshots (Add your own)

Login Page

Register Page

Dashboard

Summarizer

Quiz Interface

Final Results

Doubt Resolver

(You can upload these images on GitHub and embed them here)

🏁 Conclusion

This project demonstrates a complete AI-driven educational assistant with:

File processing

AI summarization

Interactive learning tools

RAG-based doubt solving

Full-stack Flask + AI integration

Perfect for academic evaluation, portfolios, and real-world learning platforms.
