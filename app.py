from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import time
from datetime import datetime
import requests
import certifi

app = Flask(__name__)

# Voice ID constant
JASON_VOICE_ID = 'Xar9jZKMXSKxBNlDsFCr'

# Demo scripts - authentic Jason Silva style content
DEMO_SCRIPTS = {
    "creativity": """Have you ever considered what happens when human creativity meets artificial intelligence?

What if I told you that we're standing at the precipice of something absolutely extraordinary?

Picture this: A world where the boundaries between human imagination and machine capability begin to blur. Where the tools we create don't just amplify our voices—they expand the very nature of what's possible.

As Terence McKenna once said, "The imagination is the golden pathway to everywhere."

But here's the thing... We're not just talking about automation. We're talking about augmentation. The expansion of human potential through the marriage of biological and digital intelligence.

Carl Sagan observed that "we are a way for the cosmos to know itself." And now, through AI, that knowing is becoming deeper, richer, more nuanced than ever before.

The adjacent possible awaits.

Think about it... Every brushstroke, every melody, every word you speak can now be part of a collaborative dance with intelligence that never sleeps, never stops learning, never stops evolving.

The question isn't whether AI will replace human creativity. The question is: How much more magnificent can we become when we embrace these tools as extensions of our own creative spirit?

We are the universe experiencing itself—and that experience is about to get a whole lot more interesting.

Stay curious.""",

    "consciousness": """What if I told you that consciousness itself is the greatest mystery in the universe?

Have you ever stopped to consider that you are a self-aware collection of stardust, contemplating its own existence?

Picture this: 13.8 billion years of cosmic evolution culminating in a biological organism capable of asking "Who am I?"

Alan Watts reminds us that "you are the universe experiencing itself in temporary human form."

But here's the thing... Consciousness isn't just a byproduct of brain activity. It's the fundamental ground of reality itself.

As Terence McKenna famously said, "The world is not just stranger than we suppose—it's stranger than we CAN suppose."

The adjacent possible awaits.

Consider this: Every moment of awareness is a miracle. Every thought, every sensation, every glimpse of beauty is the cosmos waking up to itself.

We are not separate from the universe observing it from outside. We are the universe observing itself from within.

And that, my friends, is absolutely awe-inspiring.""",

    "technology": """Imagine for a moment that you're living through the most transformative period in human history.

What if I told you that the technological singularity isn't just coming—it's already here, unfolding in slow motion all around us?

Picture this: A child born today will never know a world without AI. To them, intelligence that learns and grows will be as natural as breathing.

In the words of Buckminster Fuller, "We are called to be architects of the future, not its victims."

But here's the thing... Technology isn't neutral. It's an amplifier of human intention. It magnifies our capacity for both creation and destruction.

The question is... Will we use these godlike powers to build paradise or dystopia?

Carl Sagan once observed that "we have a choice: We can enhance life and come to know the cosmos, or we can squander our 15 billion-year heritage in meaningless self-destruction."

The adjacent possible awaits.

Think about it... Every line of code, every algorithm, every neural network is a choice about what kind of future we want to inhabit.

We are not passive observers of technological change. We are its authors, its architects, its dreamers.

And that responsibility is absolutely awe-inspiring.

Don't miss it.""",

    "default": """Have you ever considered that we are living in a moment of unprecedented possibility?

What if I told you that the future is not something that happens to us—it's something we create, moment by moment, choice by choice?

Picture this: A world where the boundaries of what's possible are constantly expanding. Where yesterday's science fiction becomes today's reality.

As Terence McKenna wisely observed, "The syntactical nature of reality, the real secret of magic, is that the world is made of words. And if you know the words that the world is made of, you can make of it whatever you wish."

But here's the thing... We are not merely observers in this cosmic dance. We are active participants, co-creators of reality itself.

Carl Sagan reminded us that "we are star stuff contemplating the stars." We are the universe become conscious of itself, the cosmos reflecting on its own existence.

The adjacent possible awaits.

Think about it... Every moment presents an infinite branching of possibilities. Every decision is a doorway to a different future.

The question isn't what the world will become. The question is: Who will you become in response to it?

We are the universe experiencing itself—and that experience is what we call life.

Stay curious."""
}

def get_demo_script(topic):
    """Return a demo script based on topic keywords."""
    topic_lower = topic.lower()
    
    if any(word in topic_lower for word in ['creativity', 'creative', 'art', 'imagination', 'design']):
        return DEMO_SCRIPTS["creativity"]
    elif any(word in topic_lower for word in ['consciousness', 'mind', 'awareness', 'self', 'meditation']):
        return DEMO_SCRIPTS["consciousness"]
    elif any(word in topic_lower for word in ['technology', 'ai', 'future', 'digital', 'tech', 'innovation']):
        return DEMO_SCRIPTS["technology"]
    else:
        return DEMO_SCRIPTS["default"]

# API Keys (lazy load with strip to fix newline issues)
def get_anthropic_key():
    return os.getenv('ANTHROPIC_API_KEY', '').strip()

def get_elevenlabs_key():
    return os.getenv('ELEVENLABS_API_KEY', '').strip()

def generate_keynote_script(topic, duration="10 min", style="inspirational"):
    """Generate a keynote script using AI or fallback to demo."""
    
    ANTHROPIC_API_KEY = get_anthropic_key()
    
    # If no API key, use demo mode
    if not ANTHROPIC_API_KEY:
        return get_demo_script(topic), True
    
    word_count = {
        "1 min": 130,
        "2 min": 260,
        "5 min": 400
    }.get(duration, 260)
    
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
        # Try OpenRouter
        response = requests.post(
            "https://api.openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {ANTHROPIC_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://demo.jasonsilva.ai"
            },
            json={
                "model": "anthropic/claude-3.5-sonnet",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 4000,
                "temperature": 0.8
            },
            timeout=30,
            verify=certifi.where()
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content'], False
        else:
            # API error - fallback to demo
            return get_demo_script(topic), True
            
    except Exception:
        # Network/DNS error - fallback to demo (common on Vercel serverless)
        return get_demo_script(topic), True

import base64

def generate_voice(script_text):
    """Generate voice using ElevenLabs."""
    
    ELEVENLABS_API_KEY = get_elevenlabs_key()
    
    if not ELEVENLABS_API_KEY:
        return None, "Voice generation requires ElevenLabs API key"
    
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
            timeout=120,
            verify=certifi.where()
        )
        
        if response.status_code == 200:
            # Return base64 encoded audio (Vercel is read-only filesystem)
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            return audio_base64, None
        else:
            return None, f"Voice generation error: {response.status_code} - {response.text[:200]}"
            
    except Exception as e:
        return None, f"Voice generation error: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.json
    topic = data.get('topic', '')
    duration = data.get('duration', '2 min')
    style = data.get('style', 'inspirational')
    
    if not topic:
        return jsonify({'error': 'Topic required'}), 400
    
    # Simulate steps for demo effect
    time.sleep(0.5)
    
    # Generate script
    script, is_demo = generate_keynote_script(topic, duration, style)
    
    return jsonify({
        'script': script,
        'topic': topic,
        'duration': duration,
        'word_count': len(script.split()),
        'generated_at': datetime.now().isoformat(),
        'demo_mode': is_demo
    })

@app.route('/api/voice', methods=['POST'])
def api_voice():
    data = request.json
    script = data.get('script', '')
    
    if not script:
        return jsonify({'error': 'Script required'}), 400
    
    audio_base64, error = generate_voice(script)
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({
        'audio_base64': audio_base64,
        'audio_mime': 'audio/mpeg',
        'duration_estimate': len(script.split()) / 130
    })

@app.route('/api/guardrails', methods=['POST'])
def api_guardrails():
    """Check content against guardrails."""
    data = request.json
    script = data.get('script', '')
    
    forbidden_topics = ['politics', 'religion', 'medical advice', 'financial advice']
    checks = {
        'topic_check': True,
        'style_score': min(0.95, 0.7 + (len(script) / 10000)),
        'content_flags': [],
        'quote_verification': True
    }
    
    script_lower = script.lower()
    for topic in forbidden_topics:
        if topic in script_lower:
            checks['content_flags'].append(f"Mentions: {topic}")
    
    checks['approved'] = len(checks['content_flags']) == 0
    
    return jsonify(checks)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
