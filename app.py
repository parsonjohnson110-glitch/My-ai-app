from flask import Flask, request
from groq import Groq
import os
app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
@app.route("/")
def home():
    return """
    <h1>My AI App</h1>
    <form method="POST" action="/ask">
        <input type="text" name="question" placeholder="Ask me anything">
        <button type="submit">Ask AI</button>
    </form>
    """
@app.route("/ask", methods=["POST"])
def ask():
    question = request.form["question"]
    chat = client.chat.completions.create(
        messages=[{"role": "user", "content": question}],
        model="llama-3.3-70b-versatile"
    )
    answer = chat.choices[0].message.content
    return f"<h2>Answer:</h2><p>{answer}</p>"
if __name__ == "__main__":
    app.run()
