from flask import Flask, request, jsonify
from groq import Groq
import os

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

conversation_history = []
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>My AI Chat</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: Arial; background: #343541; color: white; display: flex; flex-direction: column; height: 100vh; }
.header { background: #202123; padding: 15px; text-align: center; font-size: 20px; font-weight: bold; }
.chat-box { flex: 1; overflow-y: auto; padding: 20px; }
.message { max-width: 700px; margin: 10px auto; padding: 12px 18px; border-radius: 10px; line-height: 1.6; }
.user-msg { background: #19c37d; margin-left: auto; }
.ai-msg { background: #444654; }
.input-area { padding: 15px; background: #40414f; display: flex; gap: 10px; }
.input-area input { flex: 1; padding: 14px; border-radius: 8px; border: none; font-size: 16px; background: #343541; color: white; }
.input-area button { padding: 14px 20px; border-radius: 8px; border: none; background: #19c37d; color: white; font-size: 16px; cursor: pointer; }
.personality-bar { background: #202123; padding: 10px; display: flex; gap: 10px; justify-content: center; }
.personality-bar button { padding: 8px 16px; border-radius: 20px; border: none; background: #444654; color: white; cursor: pointer; }
.personality-bar button.active { background: #19c37d; }
</style>
</head>
<body>
<div class="header">My AI Chat</div>
<div class="personality-bar">
<button onclick="setPersonality('assistant')" class="active">Assistant</button>
<button onclick="setPersonality('teacher')">Teacher</button>
<button onclick="setPersonality('coder')">Coder</button>
<button onclick="setPersonality('creative')">Creative</button>
</div>
<div class="chat-box" id="chat-box">
<div class="message ai-msg">Hello! I am your AI assistant. How can I help you today?</div>
</div>
<div class="input-area">
<input type="text" id="question" placeholder="Message AI..." onkeypress="if(event.key==='Enter')sendMessage()">
<button onclick="sendMessage()">Send</button>
</div>
<script>
var currentPersonality = "assistant";
function setPersonality(p) {
currentPersonality = p;
document.querySelectorAll(".personality-bar button").forEach(b => b.classList.remove("active"));
event.target.classList.add("active");
}
function sendMessage() {
var input = document.getElementById("question");
var question = input.value.trim();
if (!question) return;
var chatBox = document.getElementById("chat-box");
chatBox.innerHTML += '<div class="message user-msg">' + question + '</div>';
input.value = "";
chatBox.scrollTop = chatBox.scrollHeight;
fetch("/ask", {
method: "POST",
headers: {"Content-Type": "application/json"},
body: JSON.stringify({question: question, personality: currentPersonality})
})
.then(r => r.json())
.then(data => {
chatBox.innerHTML += '<div class="message ai-msg">' + data.answer + '</div>';
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
    personality = data.get("personality", "assistant")

    personalities = {
        "assistant": "You are a helpful AI assistant.",
        "teacher": "You are a patient teacher who explains things simply.",
        "coder": "You are an expert programmer who helps with code.",
        "creative": "You are a creative writer with imaginative responses."
    }

    system_message = personalities[personality]
    conversation_history.append({"role": "user", "content": question})

    messages = [{"role": "system", "content": system_message}] + conversation_history

    chat = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile"
    )

    answer = chat.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": answer})

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run()
