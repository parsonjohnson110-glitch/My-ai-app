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
.message img { max-width: 100%; border-radius: 8px; margin-top: 8px; }
.preview-bar { display: none; padding: 10px 15px; background-color: #40414f; align-items: center; }
.preview-bar img { height: 50px; border-radius: 6px; margin-right: 10px; }
.input-area { display: flex; padding: 15px; background-color: #40414f; }
.input-area input { flex: 1; padding: 12px; border-radius: 8px; border: none; font-size: 16px; }
.input-area button { margin-left: 10px; padding: 12px 16px; border-radius: 8px; border: none; background-color: #19c37d; color: white; font-size: 16px; }
.attach-btn { background-color: #555 !important; }
</style>
</head>
<body>
<div class="header">My AI Chat</div>
<div class="chat-box" id="chat-box"></div>
<div class="preview-bar" id="preview-bar">
  <img id="preview-img" src="">
  <span>Image attached - ask a question</span>
</div>
<div class="input-area">
<button class="attach-btn" onclick="document.getElementById('file-input').click()">📎</button>
<input type="file" id="file-input" accept="image/*" style="display:none" onchange="handleFile(event)">
<input type="text" id="question" placeholder="Message, or /image a cat surfing">
<button onclick="sendMessage()">Send</button>
</div>
<script>
var uploadedImage = null;

function handleFile(event) {
  var file = event.target.files[0];
  if (!file) return;
  var reader = new FileReader();
  reader.onload = function(e) {
    uploadedImage = e.target.result;
    document.getElementById("preview-img").src = uploadedImage;
    document.getElementById("preview-bar").style.display = "flex";
  };
  reader.readAsDataURL(file);
}

function sendMessage() {
  var input = document.getElementById("question");
  var question = input.value;
  if (question.trim() === "" && !uploadedImage) return;
  var chatBox = document.getElementById("chat-box");

  if (uploadedImage) {
    chatBox.innerHTML += '<div class="message user-message"><img src="' + uploadedImage + '"><br>' + question + '</div>';
    var imgToSend = uploadedImage;
    uploadedImage = null;
    document.getElementById("preview-bar").style.display = "none";
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
    fetch("/vision", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question: question, image: imgToSend})
    })
    .then(response => response.json())
    .then(data => {
      chatBox.innerHTML += '<div class="message ai-message">' + data.answer + '</div>';
      chatBox.scrollTop = chatBox.scrollHeight;
    });
    return;
  }

  if (question.toLowerCase().indexOf("/image ") === 0) {
    var prompt = question.substring(7);
    var imgUrl = "https://gen.pollinations.ai/image/" + encodeURIComponent(prompt);
    chatBox.innerHTML += '<div class="message user-message">' + question + '</div>';
    chatBox.innerHTML += '<div class="message ai-message"><img src="' + imgUrl + '"></div>';
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;
    return;
  }

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

@app.route("/vision", methods=["POST"])
def vision():
    data = request.get_json()
    question = data.get("question") or "What is in this image?"
    image_data = data["image"]
    chat = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": image_data}}
                ]
            }
        ]
    )
    answer = chat.choices[0].message.content
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run()
