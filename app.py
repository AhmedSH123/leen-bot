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
    app.run(debug=True)
