from flask import Flask, render_template, request, jsonify
import json
from difflib import get_close_matches
import os

app = Flask(__name__, static_folder="static", template_folder="templates")


# Load chatbot data
with open("chatbot_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def find_best_match(query, keys, cutoff=0.6):
    matches = get_close_matches(query, keys, n=1, cutoff=cutoff)
    return matches[0] if matches else None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    raw_q = request.json.get("sanskrit", "").lower()

    roman_hint_map = {
        "bharat": "भारतस्य राजधानी का",
        "rajdhani": "भारतस्य राजधानी का",
        "capital": "भारतस्य राजधानी का",
        "namaste": "नमस्ते",
        "who are you": "त्वं कः असि",
        "sanskrit": "संस्कृतम् किम्",
        "dhanyavad": "धन्यवादः"
    }

    canonical = None
    for hint, value in roman_hint_map.items():
        if hint in raw_q:
            canonical = value
            break

    if not canonical:
        canonical = find_best_match(raw_q, data.keys())

    if canonical and canonical in data:
        result = data[canonical]
    else:
        canonical = raw_q
        result = {
            "en_q": "Unknown question",
            "sa_ans": "क्षम्यताम्। अहं न अवगच्छामि।",
            "en_ans": "Sorry, I did not understand."
        }

    return jsonify({
        "sa_question": canonical,
        "en_question": result["en_q"],
        "sa_answer": result["sa_ans"],
        "en_answer": result["en_ans"]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
