from flask import Flask, request, jsonify
from groq import Groq
import os

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>My AI Chat</title>
<style>
body { margin: 0; font-family: Arial; background-color: #343541; color: white; display: flex; flex-direction: column; height: 100vh; }
.header { text-align: center; padding: 15px; font-size: 20px; font-weight: bold; background-color: #202123; }
.chat-box { flex: 1; overflow-y: auto; padding: 20px; }
.message { max-width: 700px; margin: 10px auto; padding: 12px 16px; border-radius: 10px; line-height: 1.5; }
.user-message { background-color: #19c37d; }
.ai-message { background-color: #444654; }
.input-area { display: flex; padding: 15px; background-color: #40414f; }
.input-area input { flex: 1; padding: 12px; border-radius: 8px; border: none; font-size: 16px; }
.input-area button { margin-left: 10px; padding: 12px 20px; border-radius: 8px; border: none; background-color: #19c37d; color: white; font-size: 16px; }
</style>
</head>
<body>
<div class="header">My AI Chat</div>
<div class="chat-box" id="chat-box"></div>
<div class="input-area">
<input type="text" id="question" placeholder="Message AI...">
<button onclick="sendMessage()">Send</button>
</div>
<script>
function sendMessage() {
  var input = document.getElementById("question");
  var question = input.value;
  if (question.trim() === "") return;
  var chatBox = document.getElementById("chat-box");
  chatBox.innerHTML += '<div class="message user-message">' + question + '</div>';
  input.value = "";
  chatBox.scrollTop = chatBox.scrollHeight;
  fetch("/ask", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({question: question})
  })
  .then(response => response.json())
  .then(data => {
    chatBox.innerHTML += '<div class="message ai-message">' + data.answer + '</div>';
    chatBox.scrollTop = chatBox.scrollHeight;
  });
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return HTML_PAGE

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data["question"]
    chat = client.chat.completions.create(
        messages=[{"role": "user", "content": question}],
        model="llama-3.3-70b-versatile"
    )
    answer = chat.choices[0].message.content
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run()

