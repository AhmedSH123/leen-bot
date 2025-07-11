from flask import Flask, request, jsonify
from backend.qa_engine import LeenQABot

bot = LeenQABot()
bot.rebuild_index("data/courses.json", "data/faqs.json")

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Leen Bot is running!"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "Missing question"}), 400
    answer = bot.answer_question(question)
    return jsonify({"answer": answer})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # 10000 is a fallback for local testing
    app.run(debug=False, host="0.0.0.0", port=port)

