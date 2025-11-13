Ask AI – Intelligent Education Platform

An AI-powered education web platform that transforms any uploaded document into an interactive learning system. It provides automatic text extraction, summarization, question generation, chatbot-based doubt solving (RAG), and adaptive MCQ quizzes, making learning efficient and intelligent.

Project Overview

Ask-AI is a Flask-based web application designed to help students and educators learn from documents more effectively.
After uploading a PDF/DOCX/TXT file, the system automatically:

✅ Extracts text
✅ Summarizes the document using BART
✅ Generates MCQ quizzes using Gemini AI
✅ Provides doubt-resolution using Retrieval-Augmented Generation (RAG)
✅ Saves user history with authentication

This platform acts as an AI tutor that personalizes the learning experience using modern NLP models.

Core Features
🔹 1. Document Upload & OCR Extraction
Supports PDF, DOCX, TXT
For scanned PDFs → OCR performed using Tesseract
Extracted text stored in SQLite database
🔹 2. AI Summarization (BART CNN Model)
Uses HuggingFace BART-Large-CNN
Produces concise, meaningful summaries
Adjustable target length based on document
🔹 3. Doubt Resolver using RAG
FAISS vector index built from document chunks
Embeddings generated using Google Gemini Embedding Model
User queries answered contextually using document-based retrieval
🔹 4. Intelligent Quiz Generator
Uses Gemini Flash 2.5 to generate:
High-quality MCQs
Meaningful distractors
Correct answers & explanations
Interactive quiz interface with:
Instant feedback
Colored correctness indicators
Final score report
🔹 5. User Authentication System
Register/Login using username & password
Flask-Login session management
Users can:
Upload documents
Generate summaries
Take quizzes
Solve doubts


           Tech Stack
| Layer           | Technology                                            |
| --------------- | ----------------------------------------------------- |
| Backend         | Flask, Python                                         |
| Frontend        | HTML, CSS, Bootstrap, Glass-morphism UI               |
| AI Models       | Google Gemini 2.5, Gemini Embeddings, BART Summarizer |
| OCR             | Tesseract                                             |
| Vector Database | FAISS                                                 |
| Database        | SQLite                                                |
| Version Control | Git + GitHub                                          |

       Project Structure
       
ai_doc_app/
│── app.py                # Main Flask app
│── config.py             # Configuration
│── models.py             # Database models
│── requirements.txt      # Dependencies
│── users.db              # SQLite database
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


Why This Project Is Important?
  Solves real educational challenges
  Automates study workflows
  Uses industry-standard AI technologies
  Demonstrates end-to-end system integration:
    NLP
    RAG search
    LLM prompting
    Web development
    Databases

This project is a perfect capstone for demonstrating applied AI + software engineering.

