import os
import json
import re
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from quiz import quiz_bp
from models import Document, QuizResult, db
import google.generativeai as genai

# ---- Gemini setup ----
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
GEN_MODEL = "models/gemini-2.5-flash"


# ---------------------- Helpers ----------------------
def get_latest_doc(user_id: int):
    """Return latest uploaded document of a user"""
    return Document.query.filter_by(user_id=user_id).order_by(Document.id.desc()).first()


def clamp(n, lo, hi):
    return max(lo, min(n, hi))


def extract_json_block(text: str) -> str:
    """Extract JSON block from Gemini output"""
    if not isinstance(text, str):
        return ""
    fenced = re.search(r"```(?:json)?(.*?)```", text, re.S | re.I)
    if fenced:
        text = fenced.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    return text[start:end + 1] if start != -1 and end != -1 else text


# =========================================================
#  START QUIZ: generate and store in session
# =========================================================
@quiz_bp.route("/quiz/start", methods=["GET", "POST"])
@login_required
def start_quiz():
    latest = get_latest_doc(current_user.id)
    if not latest or not (latest.extracted_text or "").strip():
        flash("Please upload a document first.", "warning")
        return redirect(url_for("docs_bp.upload"))

    if request.method == "POST":
        try:
            num = int(request.form.get("num_questions", "5"))
        except Exception:
            num = 5
        num = clamp(num, 1, 50)

        difficulty = (request.form.get("difficulty") or "medium").lower()
        if difficulty not in ("easy", "medium", "hard"):
            difficulty = "medium"

        text = latest.extracted_text

        # Enhanced prompt for high-quality, context-aware questions
        prompt = f"""
You are an expert AI educator. Generate {num} high-quality multiple-choice questions (difficulty: {difficulty})
based strictly on the DOCUMENT TEXT below.

For each question:
- Provide a clear question derived from the document.
- Provide 4 complete, distinct options labeled "A)", "B)", "C)", "D)".
- Ensure one correct answer and three plausible distractors.
- Avoid dummy options like "Option 1" or unrelated words.
- Add a one-sentence explanation for the correct answer.
- Output only valid JSON, e.g.:
[
  {{
    "question": "...",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correct": "B",
    "explanation": "..."
  }}
]

DOCUMENT TEXT:
{text}
"""

        try:
            model = genai.GenerativeModel(GEN_MODEL)
            resp = model.generate_content(prompt)
            raw = getattr(resp, "text", "").strip()
        except Exception as e:
            print("GENERATION ERROR:", e)
            flash("Quiz generation failed. Please try again.", "danger")
            return redirect(url_for("quiz_bp.start_quiz"))

        json_str = extract_json_block(raw)
        try:
            data = json.loads(json_str)
            assert isinstance(data, list) and len(data) > 0
        except Exception as e:
            print("PARSE ERROR:", e, "RAW:", raw)
            flash("Quiz generation failed to parse JSON. Try again.", "danger")
            return redirect(url_for("quiz_bp.start_quiz"))

        labels = ["A", "B", "C", "D"]
        clean_data = []

        for q in data:
            opts = q.get("options", [])
            if not isinstance(opts, list):
                if isinstance(opts, str):
                    opts = re.split(r"[\n;|]", opts)
                else:
                    opts = list(opts) if opts else []

            cleaned_opts = []
            for o in opts:
                t = str(o).strip()
                t = re.sub(r"^[A-D][\)\.\-:\s]+", "", t, flags=re.I).strip()
                if len(t.split()) > 1:
                    cleaned_opts.append(t)
                else:
                    cleaned_opts.append(str(o).strip())

            while len(cleaned_opts) < 4:
                cleaned_opts.append(f"Choice {len(cleaned_opts) + 1}")

            final_opts = [
                f"{labels[i]}) {cleaned_opts[i]}" for i in range(4)
            ]

            corr = q.get("correct", "")
            try:
                if isinstance(corr, list):
                    corr = "".join(map(str, corr))
                corr = str(corr).strip().upper()
            except Exception:
                corr = "A"

            corr_match = re.search(r"[A-D]", corr)
            corr_letter = corr_match.group(0) if corr_match else "A"

            explanation = q.get("explanation") or "No explanation provided."

            clean_data.append({
                "question": str(q.get("question", "")),
                "options": final_opts,
                "correct": corr_letter,
                "explanation": str(explanation)
            })

        session["quiz_data"] = clean_data
        session["quiz_index"] = 0
        session["quiz_score"] = 0
        session["quiz_answered_set"] = []

        return redirect(url_for("quiz_bp.play_quiz"))

    return render_template("quiz_start.html")


# =========================================================
#  PLAY QUIZ
# =========================================================
@quiz_bp.route("/quiz/play", methods=["GET"])
@login_required
def play_quiz():
    data = session.get("quiz_data")
    if not data:
        flash("Please generate a quiz first.", "warning")
        return redirect(url_for("quiz_bp.start_quiz"))
    return render_template("quiz_play.html", questions=data)


# =========================================================
#  CHECK single answer (AJAX)
# =========================================================
@quiz_bp.route("/quiz/check", methods=["POST"])
@login_required
def check_answer_ajax():
    payload = request.get_json() or {}
    try:
        qid = int(payload.get("qid", -1))
    except Exception:
        return jsonify({"error": "Invalid qid"}), 400

    chosen_raw = (payload.get("chosen") or "").strip().upper()
    chosen_match = re.search(r"[A-D]", chosen_raw)
    chosen_letter = chosen_match.group(0) if chosen_match else ""

    data = session.get("quiz_data", [])
    if qid < 0 or qid >= len(data):
        return jsonify({"error": "qid out of range"}), 400

    correct_raw = str(data[qid].get("correct") or "A").strip().upper()
    correct_match = re.search(r"[A-D]", correct_raw)
    correct_letter = correct_match.group(0) if correct_match else "A"

    is_correct = (chosen_letter == correct_letter)

    answered = session.get("quiz_answered_set", [])
    score = session.get("quiz_score", 0)

    if qid not in answered:
        if is_correct:
            score += 1
            session["quiz_score"] = score
        answered.append(qid)
        session["quiz_answered_set"] = answered

    explanation = data[qid].get("explanation", "")
    return jsonify({
        "is_correct": is_correct,
        "correct": correct_letter,
        "explanation": explanation,
        "score": session.get("quiz_score", 0)
    })


# =========================================================
#  SUBMIT final quiz (AJAX)
# =========================================================
@quiz_bp.route("/quiz/submit", methods=["POST"])
@login_required
def submit_quiz():
    data = session.get("quiz_data", []) or []
    total = len(data)
    score = int(session.get("quiz_score", 0))
    percent = round((score / total * 100), 2) if total else 0.0

    latest = get_latest_doc(current_user.id)
    doc_id = latest.id if latest else None
    if total > 0:
        rec = QuizResult(
            user_id=current_user.id,
            document_id=doc_id,
            score=score,
            total=total
        )
        try:
            db.session.add(rec)
            db.session.commit()
        except Exception as e:
            print("DB Error:", e)
            db.session.rollback()

    for key in ["quiz_data", "quiz_index", "quiz_score", "quiz_answered_set"]:
        session.pop(key, None)

    return jsonify({"score": score, "total": total, "percent": percent})
