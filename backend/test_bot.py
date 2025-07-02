import os
from qa_engine import LeenQABot

# ✅ Set Groq API key (make sure you already have it)
os.environ["GROQ_API_KEY"] = "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" 
# ✅ Initialize the bot
bot = LeenQABot()
bot.rebuild_index("data/courses.json", "data/faqs.json")

# ✅ Start Q&A loop
while True:
    question = input("\n❓ Ask a question (or type 'exit'): ")
    if question.strip().lower() == "exit":
        break
    answer = bot.answer_question(question)
    print(f"\n🤖 Answer:\n{answer}")
