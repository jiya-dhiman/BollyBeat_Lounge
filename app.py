import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load hidden variables from our .env file
load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("GEMINI_API_KEY")

print("DEBUG CHECK - API Key Loaded:", "YES (Starts with " + API_KEY[:6] + ")" if API_KEY else "NO (None)")

def load_songs():
    with open('bollywood_db.json', 'r') as file:
        return json.load(file)

@app.route('/')
def home():
    return "AI BollyBeat Recs is Live!"

@app.route('/recommend', methods=['GET'])
def recommend():
    user_prompt = request.args.get('prompt', '')
    
    if not user_prompt:
        return jsonify({"error": "Please provide a search prompt."}), 400
    
    # We no longer load from bollywood_db.json!
    ai_instructions = f"""
    You are a Bollywood Music Expert AI. 
    A user is looking for a song recommendation based on this request: "{user_prompt}"
    
    Think of ANY real Bollywood song from history that best fits their vibe, mood, tempo, or dance needs.
    You must respond ONLY with a raw JSON object containing the song details. Do not add any conversational text or markdown code blocks.
    
    Use this exact JSON structure for your response:
    {{
        "id": 1,
        "title": "Song Title",
        "movie": "Movie Name",
        "vibe": "e.g., Romantic, Energetic, Melancholic",
        "tempo": "e.g., Fast, Medium, Slow",
        "energy": "e.g., High, Medium, Low",
        "dance_difficulty": "e.g., Easy, Medium, Hard"
    }}
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": ai_instructions}]}]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response_data = response.json()
        
        ai_text = response_data['candidates'][0]['content']['parts'][0]['text'].strip()
        recommended_song = json.loads(ai_text)
        return jsonify(recommended_song)
        
    except Exception as e:
        return jsonify({
            "error": "AI could not process the request", 
            "details": str(e)
        }), 500
    
if __name__ == '__main__':
    app.run(debug=True)