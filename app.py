from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from backend.qa_engine import LeenQABot
import os

# Initialize bot and rebuild index
bot = LeenQABot()
bot.rebuild_index("data/courses.json", "data/faqs.json")

# Create Flask app
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

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "")
    print(f"Incoming from {from_number}: {incoming_msg}")

    resp = MessagingResponse()
    if incoming_msg:
        answer = bot.answer_question(incoming_msg)
        resp.message(answer)
    else:
        resp.message("Sorry, I didn't understand that.")
    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # 10000 fallback for local dev
    app.run(debug=False, host="0.0.0.0", port=port)
