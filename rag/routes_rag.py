from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Document
import os, json, numpy as np
import faiss
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
GEN_MODEL = "models/gemini-2.5-flash"
EMB_MODEL = "models/text-embedding-004"

INDEX_DIR = os.path.join("instance", "indexes")

rag_bp = Blueprint('rag_bp', __name__)

def get_latest_doc(user_id: int):
    return Document.query.filter_by(user_id=user_id).order_by(Document.id.desc()).first()

def embed_query_gemini(text: str) -> np.ndarray:
    resp = genai.embed_content(model=EMB_MODEL, content=text)
    v = np.array(resp["embedding"], dtype=np.float32)
    n = np.linalg.norm(v) + 1e-12
    return v / n   # normalized

def load_index_and_meta(doc_id: int):
    faiss_path = os.path.join(INDEX_DIR, f"{doc_id}.faiss")
    meta_path  = os.path.join(INDEX_DIR, f"{doc_id}.meta.json")
    if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
        return None, None
    index = faiss.read_index(faiss_path)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    return index, meta

def search_chunks(doc_id: int, query: str, top_k=4):
    index, meta = load_index_and_meta(doc_id)
    if index is None or meta is None:
        return 0.0, []

    qv = embed_query_gemini(query).reshape(1, -1).astype(np.float32)
    scores, idxs = index.search(qv, top_k)  # cosine via IP (normalized)
    scores = scores[0]
    idxs   = idxs[0]

    chunks = meta.get("chunks", [])
    results = []
    for sc, ix in zip(scores, idxs):
        if ix == -1:
            continue
        if ix < len(chunks):
            results.append((float(sc), chunks[ix]))

    top_sim = results[0][0] if results else 0.0
    top_chunks = [c for _, c in results]
    return top_sim, top_chunks

def build_grounded_prompt(context_chunks, question):
    ctx = "\n\n---\n\n".join(context_chunks)
    return f"""
You are a helpful assistant answering a question based on a PDF document.

CONTEXT FROM PDF:
{ctx}

TASK:
- Answer the question using the context above.
- If context contains relevant information → answer normally.
- Reference the context provided.
- If context does NOT contain answer → respond exactly: "I could not find this in the document."

QUESTION: {question}
"""

def build_open_prompt(question):
    return f"""Not found in the PDF.
Answer the following question using your general knowledge, clearly and concisely (4–6 sentences).

QUESTION:
{question}
"""

@rag_bp.route('/doubt_resolver', methods=['GET', 'POST'])
@login_required
def doubt_resolver():
    # latest doc only
    latest = get_latest_doc(current_user.id)
    if not latest:
        flash("Please upload a document first.")
        return redirect(url_for('docs_bp.upload'))

    answer = None
    reference_chunk = None
    retrieved_chunks = []
    found_in_pdf = False
    similarity_top = 0.0

    threshold = 0.25  # >= threshold => treat as "found in PDF"

    if request.method == 'POST':
        question = (request.form.get('question') or "").strip()
        if not question:
            flash("Please type a question.")
            return redirect(url_for('rag_bp.doubt_resolver'))

        similarity_top, retrieved_chunks = search_chunks(latest.id, question, top_k=4)
        model = genai.GenerativeModel(GEN_MODEL)

        if similarity_top >= threshold and retrieved_chunks:
            found_in_pdf = True
            prompt = build_grounded_prompt(retrieved_chunks, question)
            resp = model.generate_content(prompt)
            answer = getattr(resp, "text", str(resp))
            reference_chunk = retrieved_chunks[0]
        else:
            found_in_pdf = False
            prompt = build_open_prompt(question)
            resp = model.generate_content(prompt)
            answer = getattr(resp, "text", str(resp))
            reference_chunk = None

    return render_template(
        'doubt_resolver.html',
        answer=answer,
        retrieved=retrieved_chunks,
        found_in_pdf=found_in_pdf,
        reference_chunk=reference_chunk,
        similarity_top=round(float(similarity_top), 3)
    )
