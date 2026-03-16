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
    <title>HealthFirst Clinic — AI Receptionist</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: "Inter", sans-serif; background: #f7f8fc; height: 100vh; display: flex; flex-direction: column; }
        .header {
            background: white;
            border-bottom: 1px solid #e8ecf0;
            padding: 14px 20px;
            display: flex; align-items: center; gap: 12px;
        }
        .avatar {
            width: 42px; height: 42px; border-radius: 50%;
            background: #e8f5ee;
            display: flex; align-items: center; justify-content: center;
            font-size: 20px;
        }
        .header-info { flex: 1; }
        .header-name { font-size: 15px; font-weight: 600; color: #1a1a2e; }
        .header-sub { font-size: 12px; color: #27ae60; margin-top: 1px; }
        .header-badge {
            font-size: 11px; background: #e8f5ee; color: #27ae60;
            padding: 4px 10px; border-radius: 20px; font-weight: 500;
        }
        .messages {
            flex: 1; overflow-y: auto;
            padding: 20px; display: flex;
            flex-direction: column; gap: 12px;
        }
        .msg-wrap { display: flex; align-items: flex-end; gap: 8px; }
        .msg-wrap.user { flex-direction: row-reverse; }
        .bot-avatar {
            width: 28px; height: 28px; border-radius: 50%;
            background: #e8f5ee; display: flex;
            align-items: center; justify-content: center;
            font-size: 14px; flex-shrink: 0;
        }
        .msg {
            max-width: 70%; padding: 10px 14px;
            font-size: 14px; line-height: 1.6;
        }
        .bot .msg {
            background: white; border-radius: 2px 12px 12px 12px;
            color: #2d3436; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }
        .user .msg {
            background: #1a7a4a; border-radius: 12px 2px 12px 12px;
            color: white;
        }
        .msg-time { font-size: 10px; color: #aaa; margin-top: 4px; text-align: right; }
        .input-area {
            background: white; border-top: 1px solid #e8ecf0;
            padding: 12px 16px; display: flex; gap: 10px; align-items: center;
        }
        .input-wrap { flex: 1; position: relative; }
        input {
            width: 100%; padding: 11px 16px;
            border: 1.5px solid #e8ecf0; border-radius: 24px;
            font-size: 14px; outline: none;
            font-family: "Inter", sans-serif;
            transition: border 0.2s;
        }
        input:focus { border-color: #1a7a4a; }
        button {
            width: 42px; height: 42px; border-radius: 50%;
            background: #1a7a4a; border: none;
            color: white; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            transition: background 0.2s; flex-shrink: 0;
        }
        button:hover { background: #156040; }
        .footer {
            text-align: center; font-size: 11px;
            color: #aaa; padding: 6px;
            background: white;
        }
        .typing { display: flex; gap: 4px; padding: 10px 14px; }
        .dot {
            width: 7px; height: 7px; background: #ccc;
            border-radius: 50%; animation: bounce 1.2s infinite;
        }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-5px); }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="avatar">🏥</div>
        <div class="header-info">
            <div class="header-name">HealthFirst Clinic</div>
            <div class="header-sub">● Online — AI Receptionist</div>
        </div>
        <div class="header-badge">Available 24/7</div>
    </div>

    <div class="messages" id="messages">
        <div class="msg-wrap bot">
            <div class="bot-avatar">🏥</div>
            <div>
                <div class="msg">
                    Namaste! Welcome to HealthFirst Clinic. I am your AI receptionist.<br><br>
                    I can help you with:<br>
                    • Service information and pricing<br>
                    • Booking appointments<br>
                    • Doctor availability<br><br>
                    How can I assist you today?
                </div>
                <div class="msg-time" id="start-time"></div>
            </div>
        </div>
    </div>

    <div class="input-area">
        <div class="input-wrap">
            <input id="inp" placeholder="Type your message here..." 
                   onkeydown="if(event.key===\'Enter\') send()"/>
        </div>
        <button onclick="send()">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
        </button>
    </div>
    <div class="footer">Built by bharatpurai • Powered by AI</div>

<script>
const history = [];

document.getElementById("start-time").textContent = new Date().toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"});

async function send() {
    const inp = document.getElementById("inp");
    const text = inp.value.trim();
    if (!text) return;
    inp.value = "";

    addMsg(text, "user");
    history.push({role: "user", content: text});

    showTyping();

    const res = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: text, history: history})
    });

    removeTyping();
    const data = await res.json();
    const reply = data.reply;
    history.push({role: "assistant", content: reply});
    addMsg(reply, "bot");
}

function addMsg(text, type) {
    const msgs = document.getElementById("messages");
    const wrap = document.createElement("div");
    wrap.className = "msg-wrap " + type;

    const time = new Date().toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"});

    if (type === "bot") {
        wrap.innerHTML = `
            <div class="bot-avatar">🏥</div>
            <div>
                <div class="msg">${text.replace(/\\n/g,"<br>")}</div>
                <div class="msg-time">${time}</div>
            </div>`;
    } else {
        wrap.innerHTML = `
            <div>
                <div class="msg">${text.replace(/\\n/g,"<br>")}</div>
                <div class="msg-time">${time}</div>
            </div>`;
    }
    msgs.appendChild(wrap);
    msgs.scrollTop = msgs.scrollHeight;
}

function showTyping() {
    const msgs = document.getElementById("messages");
    const wrap = document.createElement("div");
    wrap.className = "msg-wrap bot";
    wrap.id = "typing";
    wrap.innerHTML = `<div class="bot-avatar">🏥</div><div class="msg"><div class="typing"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div>`;
    msgs.appendChild(wrap);
    msgs.scrollTop = msgs.scrollHeight;
}

function removeTyping() {
    const t = document.getElementById("typing");
    if(t) t.remove();
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
