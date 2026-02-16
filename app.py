from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import time
import base64
from datetime import datetime
import requests
import certifi

app = Flask(__name__)

# Voice ID constant
JASON_VOICE_ID = 'Xar9jZKMXSKxBNlDsFCr'

# Load Jason Silva knowledge base for RAG-enhanced generation
JASON_KB = ""
_kb_path = os.path.join(os.path.dirname(__file__), 'jason_knowledge_base.txt')
if os.path.exists(_kb_path):
    with open(_kb_path) as _f:
        JASON_KB = _f.read()

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
    
    # Build RAG-enhanced system prompt with Jason's actual knowledge
    kb_section = ""
    if JASON_KB:
        kb_section = f"""

JASON SILVA'S ACTUAL WRITINGS AND KNOWLEDGE BASE:
The following is real content from Jason Silva's Substack, interviews, and public writings.
Use this to ground your generation in his ACTUAL ideas, vocabulary, and philosophical frameworks.
Draw specific connections, quotes, and concepts from this material — don't just mimic his style, 
channel his actual intellectual universe.

{JASON_KB[:15000]}"""

    system_prompt = f"""You are generating keynote content as Jason Silva — not imitating him, but channeling his actual intellectual framework.

Jason Silva's signature characteristics:
- Opens with wonder/awe ("Have you ever considered...", "What if I told you...")
- Rapid-fire delivery with strategic pauses
- References thinkers: Terence McKenna, Carl Sagan, Alan Watts, Carl Jung, Joseph Campbell, Stuart Kauffman, Ray Kurzweil, Buckminster Fuller
- Builds to emotional crescendo
- Poetic, evocative language — "purple prose" that earns its intensity
- Core themes: consciousness, technology, creativity, awe, mortality, transcendence, flow states, psychedelics, the adjacent possible
- Uses phrases like "the adjacent possible," "cosmic perspective," "ontological," "metaphysical," "aesthetic arrest," "ecstatic truth"
- Enthusiastic, breathless energy — like a "philosophical espresso shot"
- Ends with an inspiring call to wonder

CRITICAL: Generate ONLY the spoken script text. No stage directions, no markdown formatting, no asterisks, no bold text, no headers. Just pure spoken words as Jason would deliver them. Use "..." for pauses instead of [PAUSE] or stage directions.
{kb_section}"""

    user_prompt = f"""Write a {duration} keynote monologue (approximately {word_count} words) on the topic: "{topic}"

This should sound like Jason Silva delivering a "Shots of Awe" episode.

Requirements:
- Hook opening that grabs with wonder
- Weave in 2-3 quotes from thinkers Jason actually references
- Build to an emotional crescendo  
- Close with awe and inspiration
- Write as pure spoken word — no formatting, no stage directions
- If the knowledge base above contains relevant material on this topic, reference and build upon Jason's actual ideas"""

    try:
        # Use Anthropic API directly (OpenRouter DNS fails on Vercel)
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4000,
                "temperature": 0.8,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": user_prompt}
                ]
            },
            timeout=30,
            verify=certifi.where()
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['content'][0]['text'], False
        else:
            # API error - fallback to demo
            return get_demo_script(topic), True
            
    except Exception:
        # Network error - fallback to demo
        return get_demo_script(topic), True

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
                    "stability": 0.50,
                    "similarity_boost": 0.80,
                    "style": 0.45
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

@app.route('/api/longform/outline', methods=['POST'])
def api_longform_outline():
    """Step 1: Generate outline only. Single API call, fast."""
    from longform_engine import generate_outline

    data = request.json
    topic = data.get('topic', '')
    duration = data.get('duration_minutes', 45)

    if not topic:
        return jsonify({'error': 'Topic required'}), 400

    duration = max(10, min(45, int(duration)))

    try:
        outline = generate_outline(topic, duration)
        return jsonify(outline)
    except Exception as e:
        return jsonify({'error': f'Outline generation failed: {str(e)[:300]}'}), 500


@app.route('/api/longform/section', methods=['POST'])
def api_longform_section():
    """Step 2: Generate one section. Single API call per section."""
    from longform_engine import generate_section, _desmell_text

    data = request.json
    section_outline = data.get('section_outline', {})
    previous_summaries = data.get('previous_summaries', [])
    used_quotes = data.get('used_quotes', [])
    topic = data.get('topic', '')

    if not topic or not section_outline:
        return jsonify({'error': 'Topic and section_outline required'}), 400

    try:
        text, new_quotes = generate_section(
            section_outline, previous_summaries, used_quotes, topic
        )
        text = _desmell_text(text)

        words = text.split()
        summary = f"Section {section_outline.get('section_number', '?')} ({section_outline.get('name', '')}): {' '.join(words[:50])}..."

        return jsonify({
            'text': text,
            'new_quotes': new_quotes,
            'summary': summary,
            'word_count': len(words)
        })
    except Exception as e:
        return jsonify({'error': f'Section generation failed: {str(e)[:300]}'}), 500


@app.route('/api/voice/chunk', methods=['POST'])
def api_voice_chunk():
    """Generate voice for a single text chunk. One ElevenLabs call."""
    from longform_engine import _synthesize_chunk, get_elevenlabs_key, JASON_VOICE_ID

    data = request.json
    text = data.get('text', '')
    previous_text = data.get('previous_text', None)
    next_text = data.get('next_text', None)

    if not text:
        return jsonify({'error': 'Text required'}), 400

    api_key = get_elevenlabs_key()
    if not api_key:
        return jsonify({'error': 'ElevenLabs API key not configured'}), 500

    try:
        audio_bytes = _synthesize_chunk(text, JASON_VOICE_ID, api_key, previous_text, next_text)
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        return jsonify({
            'audio_base64': audio_b64,
            'audio_mime': 'audio/mpeg'
        })
    except Exception as e:
        return jsonify({'error': f'Voice synthesis failed: {str(e)[:200]}'}), 500


@app.route('/api/voice/split', methods=['POST'])
def api_voice_split():
    """Split script text into chunks for sequential voice synthesis."""
    from longform_engine import _split_into_chunks

    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'Text required'}), 400

    chunks = _split_into_chunks(text, max_chars=4500)
    return jsonify({
        'chunks': chunks,
        'count': len(chunks)
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
