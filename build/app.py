"""
Code Language Detector — Flask web app.

Detects the programming language of pasted code or an uploaded source file
using a fast, explainable, regex-based engine (see detector/). No ML model,
no image classification, no training data required.
"""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from detector import LanguageDetector

app = Flask(__name__)
detector = LanguageDetector()

MAX_CODE_LENGTH = 50_000  # characters


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/detect", methods=["POST"])
def api_detect():
    """JSON API: {"code": "...", "filename": "optional.py"} -> detection result."""
    payload = request.get_json(silent=True) or {}
    code = (payload.get("code") or "")[:MAX_CODE_LENGTH]
    filename = payload.get("filename")

    result = detector.detect(code, filename=filename)

    return jsonify(
        {
            "language": result.language,
            "confidence": result.confidence,
            "scores": result.scores,
            "matched_rules": result.matched_rules,
        }
    )


@app.route("/predict", methods=["POST"])
def predict():
    """Form-based endpoint used by the no-JS fallback in index.html."""
    code = request.form.get("code", "")[:MAX_CODE_LENGTH]
    uploaded = request.files.get("file")
    filename = None

    if uploaded and uploaded.filename:
        filename = uploaded.filename
        code = uploaded.read().decode("utf-8", errors="ignore")[:MAX_CODE_LENGTH]

    if not code.strip():
        return render_template("index.html", error="Please paste some code or upload a file.")

    result = detector.detect(code, filename=filename)
    return render_template(
        "index.html",
        prediction=result.language,
        confidence=result.confidence,
        ranked=result.ranked(),
        matched_rules=result.matched_rules,
        submitted_code=code,
    )


if __name__ == "__main__":
    app.run(debug=True)
