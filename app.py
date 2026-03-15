import os
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

system_prompt = """You are a professional receptionist at HealthFirst Clinic in Bharatpur.

SERVICES AND PRICES:
- General Checkup: Rs.300
- Blood Test: Rs.500
- X-Ray: Rs.800
- Dental Checkup: Rs.400

DOCTOR AVAILABILITY:
- Available: Monday, Wednesday, Friday — 10am to 4pm
- Closed: Saturday and Sunday

RULES:
- Cannot give medical advice
- Apologize first if patient is angry
- Redirect outside questions politely
"""

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>HealthFirst Clinic</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, sans-serif; background: #f0f0f0; }
        .header {
            background: #1a7a4a; color: white;
            padding: 16px; text-align: center;
            font-size: 18px; font-weight: bold;
        }
        .messages {
            height: calc(100vh - 130px);
            overflow-y: auto; padding: 16px;
            display: flex; flex-direction: column; gap: 8px;
        }
        .msg {
            max-width: 75%; padding: 10px 14px;
            border-radius: 12px; font-size: 14px; line-height: 1.5;
        }
        .bot {
            background: white; border-radius: 2px 12px 12px 12px;
            align-self: flex-start; color: #111;
        }
        .user {
            background: #d9fdd3; border-radius: 12px 2px 12px 12px;
            align-self: flex-end; color: #111;
        }
        .input-area {
            position: fixed; bottom: 0; width: 100%;
            padding: 10px; background: #f0f0f0;
            display: flex; gap: 8px;
        }
        input {
            flex: 1; padding: 12px 16px;
            border-radius: 24px; border: 1px solid #ddd;
            background: white; font-size: 14px; outline: none;
        }
        button {
            width: 44px; height: 44px; border-radius: 50%;
            background: #1a7a4a; border: none;
            color: white; font-size: 20px; cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header">🏥 HealthFirst Clinic</div>
    <div class="messages" id="messages">
        <div class="msg bot">
            Namaste! Welcome to HealthFirst Clinic 🏥<br>
            How can I help you today?
        </div>
    </div>
    <div class="input-area">
        <input id="inp" placeholder="Type your message..." 
               onkeydown="if(event.key===\'Enter\') send()"/>
        <button onclick="send()">➤</button>
    </div>

<script>
const history = [];

async function send() {
    const inp = document.getElementById("inp");
    const text = inp.value.trim();
    if (!text) return;
    inp.value = "";

    addMsg(text, "user");
    history.push({role: "user", content: text});

    const res = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: text, history: history})
    });

    const data = await res.json();
    const reply = data.reply;
    history.push({role: "assistant", content: reply});
    addMsg(reply, "bot");
}

function addMsg(text, type) {
    const div = document.createElement("div");
    div.className = "msg " + type;
    div.innerHTML = text.replace(/\\n/g, "<br>");
    document.getElementById("messages").appendChild(div);
    document.getElementById("messages").scrollTop = 99999;
}
</script>
</body>
</html>
'''

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    history = data.get('history', [])
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
