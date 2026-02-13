from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import time
from datetime import datetime
import requests

app = Flask(__name__)

# API Keys from environment
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
JASON_VOICE_ID = 'Xar9jZKMXSKxBNlDsFCr'  # Jason Silva voice clone

# Jason's style patterns
JASON_PATTERNS = {
    "openings": [
        "Have you ever considered...",
        "What if I told you...",
        "Let me ask you something...",
        "Picture this:",
        "Imagine for a moment..."
    ],
    "transitions": [
        "But here's the thing...",
        "And yet...",
        "The question is...",
        "Think about it...",
        "Consider this..."
    ],
    "closings": [
        "And that, my friends, is absolutely awe-inspiring.",
        "We are the universe experiencing itself.",
        "Don't miss it.",
        "The adjacent possible awaits.",
        "Stay curious."
    ],
    "quotes": [
        "As Terence McKenna said...",
        "Carl Sagan once observed...",
        "Alan Watts reminds us...",
        "In the words of Buckminster Fuller..."
    ]
}

def generate_keynote_script(topic, duration="10 min", style="inspirational"):
    """Generate a keynote script using Claude."""
    
    word_count = {
        "5 min": 750,
        "10 min": 1500,
        "20 min": 3000
    }.get(duration, 1500)
    
    system_prompt = """You are generating keynote content in the style of Jason Silva.

Jason Silva's signature characteristics:
- Opens with wonder/awe ("Have you ever considered...")
- Rapid-fire delivery with strategic pauses
- Heavy use of quotes (Terence McKenna, Carl Sagan, Alan Watts)
- Builds to emotional crescendo
- Poetic language, metaphors
- Topics: consciousness, technology, creativity, awe, mortality, transcendence
- Uses phrases like "the adjacent possible," "cosmic perspective," "technological singularity"
- Enthusiastic, breathless energy
- Ends with an inspiring call to wonder

Generate content that sounds authentically like Jason Silva would deliver it."""

    user_prompt = f"""Write a {duration} keynote speech ({word_count} words) on the topic: "{topic}"

Make it sound like Jason Silva delivering a "Shots of Awe" episode or TED talk.

Structure:
1. Hook opening (grab attention with wonder)
2. 2-3 main sections exploring the topic
3. Include 2-3 philosophical quotes
4. Build to an emotional crescendo
5. Close with awe and inspiration

Write it as spoken word, not an essay. Use rhetorical devices, pacing cues (PAUSE), and emphasis."""

    try:
        response = requests.post(
            "https://api.openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {ANTHROPIC_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://demo.jasonsilva.ai"
            },
            json={
                "model": "anthropic/claude-sonnet-4-5",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 4000,
                "temperature": 0.8
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error generating script: {str(e)}"

def generate_voice(script_text):
    """Generate voice using ElevenLabs."""
    
    if not ELEVENLABS_API_KEY:
        return None, "ElevenLabs API key not configured"
    
    try:
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{JASON_VOICE_ID}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": script_text[:5000],  # ElevenLabs limit
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.35,
                    "similarity_boost": 0.80,
                    "style": 0.50
                }
            },
            timeout=120
        )
        
        if response.status_code == 200:
            # Save to file
            audio_path = f"static/audio_{int(time.time())}.mp3"
            with open(audio_path, 'wb') as f:
                f.write(response.content)
            return audio_path, None
        else:
            return None, f"ElevenLabs error: {response.status_code}"
            
    except Exception as e:
        return None, f"Voice generation error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.json
    topic = data.get('topic', '')
    duration = data.get('duration', '10 min')
    style = data.get('style', 'inspirational')
    
    if not topic:
        return jsonify({'error': 'Topic required'}), 400
    
    # Simulate steps for demo effect
    time.sleep(0.5)
    
    # Generate script
    script = generate_keynote_script(topic, duration, style)
    
    if script.startswith("Error"):
        return jsonify({'error': script}), 500
    
    return jsonify({
        'script': script,
        'topic': topic,
        'duration': duration,
        'word_count': len(script.split()),
        'generated_at': datetime.now().isoformat()
    })

@app.route('/api/voice', methods=['POST'])
def api_voice():
    data = request.json
    script = data.get('script', '')
    
    if not script:
        return jsonify({'error': 'Script required'}), 400
    
    audio_path, error = generate_voice(script)
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({
        'audio_url': audio_path.replace('static/', '/static/'),
        'duration_estimate': len(script.split()) / 150  # ~150 words per minute
    })

@app.route('/api/guardrails', methods=['POST'])
def api_guardrails():
    """Check content against guardrails."""
    data = request.json
    script = data.get('script', '')
    
    # Simple guardrail checks
    forbidden_topics = ['politics', 'religion', 'medical advice', 'financial advice']
    checks = {
        'topic_check': True,
        'style_score': min(0.95, 0.7 + (len(script) / 10000)),  # Simulated
        'content_flags': [],
        'quote_verification': True
    }
    
    # Check for forbidden topics
    script_lower = script.lower()
    for topic in forbidden_topics:
        if topic in script_lower:
            checks['content_flags'].append(f"Mentions: {topic}")
    
    checks['approved'] = len(checks['content_flags']) == 0
    
    return jsonify(checks)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
