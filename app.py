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
    return "HealthFirst Clinic Agent is running!"

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
