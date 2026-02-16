"""
Long-form Keynote Generation Engine for Jason Silva AI
Generates 10-45 minute keynotes with structured narrative arc + chunked voice synthesis.
"""

import os
import sys
import json
import time
import base64
import tempfile
import requests
import certifi
from datetime import datetime

# Voice ID constant
JASON_VOICE_ID = 'Xar9jZKMXSKxBNlDsFCr'

# Load knowledge base
JASON_KB = ""
_kb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jason_knowledge_base.txt')
if os.path.exists(_kb_path):
    with open(_kb_path) as _f:
        JASON_KB = _f.read()

def get_anthropic_key():
    return os.getenv('ANTHROPIC_API_KEY', '').strip()

def get_elevenlabs_key():
    return os.getenv('ELEVENLABS_API_KEY', '').strip()

# --- Narrative Arc Definitions ---

# Word targets calibrated at ~210 wpm (Jason's energetic delivery + ElevenLabs pacing)
NARRATIVE_ARCS = {
    10: [
        {"name": "Hook", "minutes": "0-2", "tone": "wonder, awe, grabbing attention", "words": 420},
        {"name": "Context", "minutes": "2-5", "tone": "grounding, intellectual framework", "words": 630},
        {"name": "Crescendo", "minutes": "5-8", "tone": "building intensity, emotional peak", "words": 630},
        {"name": "Landing", "minutes": "8-10", "tone": "resolution, call to wonder, inspiring close", "words": 420},
    ],
    20: [
        {"name": "Hook", "minutes": "0-3", "tone": "wonder, awe, cosmic opening", "words": 630},
        {"name": "Context", "minutes": "3-8", "tone": "grounding the topic, intellectual framework", "words": 1050},
        {"name": "Tension", "minutes": "8-13", "tone": "paradox, challenge, the hard question", "words": 1050},
        {"name": "Synthesis", "minutes": "13-17", "tone": "connecting threads, building toward resolution", "words": 840},
        {"name": "Landing", "minutes": "17-20", "tone": "emotional crescendo into inspiring close", "words": 630},
    ],
    30: [
        {"name": "Hook", "minutes": "0-4", "tone": "wonder, awe, set the cosmic stage", "words": 840},
        {"name": "Context", "minutes": "4-10", "tone": "ground the topic, introduce intellectual framework", "words": 1260},
        {"name": "Tension", "minutes": "10-16", "tone": "present the paradox, the challenge, the question", "words": 1260},
        {"name": "Exploration", "minutes": "16-22", "tone": "deep dive, multiple perspectives", "words": 1260},
        {"name": "Crescendo", "minutes": "22-27", "tone": "emotional peak, the big aha moment", "words": 1050},
        {"name": "Landing", "minutes": "27-30", "tone": "call to wonder, closing inspiration", "words": 630},
    ],
    45: [
        {"name": "Hook", "minutes": "0-5", "tone": "wonder, awe, set the cosmic stage", "words": 1050},
        {"name": "Context", "minutes": "5-12", "tone": "ground the topic, introduce the intellectual framework", "words": 1470},
        {"name": "Tension", "minutes": "12-20", "tone": "present the paradox, challenge, the hard question", "words": 1680},
        {"name": "Exploration", "minutes": "20-28", "tone": "deep dive, multiple perspectives, rich examples", "words": 1680},
        {"name": "Synthesis", "minutes": "28-35", "tone": "connect the threads, build toward resolution", "words": 1470},
        {"name": "Crescendo", "minutes": "35-42", "tone": "emotional peak, the big aha moment, breathless intensity", "words": 1470},
        {"name": "Landing", "minutes": "42-45", "tone": "call to wonder, closing inspiration, stay curious", "words": 630},
    ],
}

# Thinker pool — each section draws from different thinkers
THINKER_POOL = [
    "Terence McKenna", "Carl Sagan", "Alan Watts", "Carl Jung", "Joseph Campbell",
    "Stuart Kauffman", "Ray Kurzweil", "Buckminster Fuller", "Aldous Huxley",
    "Pierre Teilhard de Chardin", "Rupert Sheldrake", "Douglas Hofstadter",
    "William James", "Albert Einstein", "Marshall McLuhan", "Nikola Tesla",
    "Werner Heisenberg", "David Bohm", "Ilya Prigogine", "Freeman Dyson"
]

def _call_anthropic(system_prompt, user_prompt, max_tokens=4000, temperature=0.8):
    """Make a single Anthropic API call. Returns text or raises."""
    api_key = get_anthropic_key()
    if not api_key:
        raise ValueError("No ANTHROPIC_API_KEY set")

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}]
        },
        timeout=90,
        verify=certifi.where()
    )

    if response.status_code != 200:
        raise Exception(f"Anthropic API error {response.status_code}: {response.text[:300]}")

    return response.json()['content'][0]['text']


def generate_outline(topic, duration_minutes=45):
    """Generate a structured outline with narrative arc."""

    # Find closest arc
    arc_key = min(NARRATIVE_ARCS.keys(), key=lambda k: abs(k - duration_minutes))
    arc = NARRATIVE_ARCS[arc_key]

    system_prompt = """You are a keynote architect for Jason Silva. You design the structural outline of keynotes that follow his signature style.

Return ONLY valid JSON. No markdown, no code blocks, no explanation."""

    # Distribute thinkers across sections (no repeats)
    import random
    shuffled = THINKER_POOL.copy()
    random.shuffle(shuffled)

    sections_desc = []
    thinker_idx = 0
    for i, section in enumerate(arc):
        # Assign 2-3 unique thinkers per section
        n_thinkers = 3 if section["words"] > 700 else 2
        assigned = shuffled[thinker_idx:thinker_idx + n_thinkers]
        thinker_idx += n_thinkers
        sections_desc.append({
            "section_number": i + 1,
            "name": section["name"],
            "minutes": section["minutes"],
            "tone": section["tone"],
            "target_words": section["words"],
            "assigned_thinkers": assigned
        })

    user_prompt = f"""Design a {duration_minutes}-minute keynote outline on the topic: "{topic}"

The keynote must follow this narrative arc structure:
{json.dumps(sections_desc, indent=2)}

For each section, provide:
- "section_number": (int)
- "name": section name
- "theme": specific sub-theme for this section (2-3 sentences)
- "key_points": list of 3-4 specific points to hit
- "thinkers": which thinkers to quote (use ONLY the assigned ones)
- "opening_hook": the first line of this section
- "target_words": word count target
- "tone": emotional tone

Return a JSON object: {{"topic": "...", "sections": [...]}}"""

    result = _call_anthropic(system_prompt, user_prompt, max_tokens=3000, temperature=0.7)

    # Parse JSON (handle potential markdown wrapping)
    result = result.strip()
    if result.startswith("```"):
        result = result.split("\n", 1)[1]
        if result.endswith("```"):
            result = result[:-3]

    outline = json.loads(result)
    outline["arc_key"] = arc_key
    outline["duration_minutes"] = duration_minutes
    outline["total_target_words"] = sum(s["words"] for s in arc)

    return outline


def generate_section(section_outline, previous_summaries, used_quotes, topic):
    """Generate one section of the keynote."""

    kb_excerpt = JASON_KB[:8000] if JASON_KB else ""

    prev_context = ""
    if previous_summaries:
        prev_context = f"""
PREVIOUS SECTIONS (summary — maintain continuity, do NOT repeat ideas):
{chr(10).join(previous_summaries)}
"""

    used_q = ""
    if used_quotes:
        used_q = f"""
QUOTES ALREADY USED (do NOT repeat these):
{chr(10).join(f'- {q}' for q in used_quotes)}
"""

    system_prompt = f"""You are Jason Silva delivering a keynote. Not imitating — channeling his actual voice.

Signature characteristics:
- Opens with wonder/awe hooks
- Rapid-fire delivery with strategic pauses
- References thinkers with specific quotes
- Builds to emotional crescendo
- Poetic, evocative "purple prose" that earns its intensity
- Signature phrases: "the adjacent possible," "cosmic perspective," "aesthetic arrest," "ecstatic truth," "ontological design"
- Enthusiastic, breathless energy — like a "philosophical espresso shot"
- Repeats key phrases for emphasis (anaphora): "We are... We are... We are..."
- Uses vivid sensory metaphors, not abstract logic
- Speaks in fragments for rhythm: "Consciousness. Awakening. Right now."

JASON'S REAL VERBAL PATTERNS (use these):
- "Have you ever considered..."
- "What if I told you..."
- "Picture this..."
- "Here's the thing..."
- "Think about this for a moment..."
- "But wait... it gets better..."
- "And that... is absolutely awe-inspiring."
- "The adjacent possible awaits."
- "Stay curious."
- "Don't miss it."
- Building lists of three: "creation, destruction, and rebirth"
- Callback references: "Remember what I said about X? Well..."
- Personal asides: "I remember the first time I..."
- Exclamatory wonder: "I mean wow!" / "How extraordinary is that!"

BANNED PATTERNS — NEVER USE THESE (they sound like AI, not Jason):
- "It's not just X, it's Y"
- "It's not about X, it's about Y"
- "This isn't merely X — it's Y"
- "X isn't simply Y, it's Z"
- "We're not just X, we're Y"
- "This is more than X, this is Y"
- "The question isn't X, the question is Y"
- "In a world where..."
- "At its core..."
- "It's worth noting..."
- "Let's delve into..."
- "Arguably..."
- "Navigating the landscape of..."
- Any sentence that follows the [negation] → [but actually] → [grander claim] structure

INSTEAD: Make direct, vivid assertions. "We ARE the universe dreaming." Not "We're not just humans, we're the universe dreaming."

THIS IS YOUR #1 PRIORITY RULE: If you catch yourself writing "not just X" or "not only X" or "not merely X" — STOP. Delete the sentence. Rewrite it as a direct, bold claim. Jason makes declarations. He doesn't negate-then-correct. He ASSERTS.

CRITICAL RULES:
1. Generate ONLY spoken script text. No markdown, no headers, no stage directions, no asterisks, no bold.
2. For pauses, use one of: "..." or a line break. Vary your pause technique.
3. Each quote must be attributed: 'As [Thinker] said, "..."'
4. Stay on-brand. This is Jason Silva, not a TED talk.
5. Write LONG. Hit the target word count. More content is better than less. Develop ideas fully — don't summarize, EXPLORE.

{f'JASON SILVA KNOWLEDGE BASE (use for grounding):{chr(10)}{kb_excerpt}' if kb_excerpt else ''}
{prev_context}
{used_q}"""

    user_prompt = f"""Write section {section_outline.get('section_number', '?')} of a keynote on "{topic}".

Section name: {section_outline['name']}
Theme: {section_outline.get('theme', 'See tone')}
Tone: {section_outline.get('tone', 'inspirational')}
Target word count: {section_outline.get('target_words', 500)}
Thinkers to quote: {', '.join(section_outline.get('thinkers', ['Terence McKenna', 'Carl Sagan']))}
Key points to hit: {json.dumps(section_outline.get('key_points', []))}
Opening hook: {section_outline.get('opening_hook', 'Start with wonder')}

Write approximately {section_outline.get('target_words', 500)} words. Pure spoken word only."""

    text = _call_anthropic(system_prompt, user_prompt, max_tokens=3000, temperature=0.8)

    # Extract any new quotes used
    new_quotes = []
    for line in text.split('\n'):
        for thinker in THINKER_POOL:
            if thinker.lower() in line.lower() and '"' in line:
                new_quotes.append(line.strip()[:200])
                break

    return text.strip(), new_quotes


def _desmell_text(text):
    """Post-process to remove common AI rhetorical patterns."""
    import re

    replacements = [
        # "X isn't just Y — it's Z" → "X is Z"
        (r"(\w+) (?:isn't|is not|aren't|are not) (?:just|only|merely|simply) [^—,;.!?]+?[—,;]\s*(?:it'?s|they'?re|this is|that'?s)\s+", r"\1 is "),
        # "not just X, we're Y" → "We are Y"
        (r"[Ww]e'?re not (?:just|only|merely|simply) [^.!?]+?[,;—]\s*we'?re\s+", "We are "),
        # "not just X. We're Y" → "We are Y"
        (r"[Ww]e'?re not (?:just|only|merely|simply) [^.!?]+\.\s*[Ww]e'?re\s+", "We are "),
        # "It's not just/only about X, it's about Y" → "It's about Y"
        (r"[Ii]t'?s not (?:just|only|merely|simply) (?:about )?[^,;—]+?[,;—]\s*it'?s (?:about )?", "It's about "),
        # "This isn't merely X — it's Y" → "This is Y"
        (r"[Tt]his (?:isn't|is not) (?:just|merely|simply) [^—,;]+?[—,;]\s*(?:it'?s|this is)\s+", "This is "),
        # "not just the X, not just the Y" → "the X, the Y" (list patterns)
        (r"[Nn]ot just (the [^,]+), not just (the [^,]+)", r"\1, \2"),
        # "creativity isn't just about X — it's about Y" → "creativity is about Y"
        (r"(\w+) (?:isn't|is not) (?:just|only|merely) about [^—,;]+?[—,;]\s*(?:it'?s|that'?s) (?:about )?", r"\1 is about "),
        # Catch remaining "not just" with dash/comma patterns
        (r"(?:isn't|is not|aren't|are not) (?:just|only|merely) ([^—,;.!?]+?)\s*[—]\s*(?:it'?s|they'?re|we'?re)\s+", r"is \1. It is "),
    ]

    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)

    return text


def generate_full_keynote(topic, duration_minutes=45, progress_callback=None):
    """
    Full pipeline: outline → sections → assembly.
    Returns dict with script, metadata, outline.
    """

    if progress_callback:
        progress_callback("generating_outline", 0)

    # Step 1: Generate outline
    outline = generate_outline(topic, duration_minutes)

    sections_text = []
    previous_summaries = []
    all_used_quotes = []
    total_words = 0

    # Step 2: Generate each section
    for i, section in enumerate(outline["sections"]):
        if progress_callback:
            progress_callback("generating_section", i + 1)

        try:
            text, new_quotes = generate_section(
                section, previous_summaries, all_used_quotes, topic
            )
        except Exception as e:
            # Retry once
            try:
                time.sleep(2)
                text, new_quotes = generate_section(
                    section, previous_summaries, all_used_quotes, topic
                )
            except Exception:
                text = f"[Section {i+1} generation failed: {str(e)[:100]}]"
                new_quotes = []

        # Post-process to remove AI smell
        text = _desmell_text(text)

        sections_text.append(text)
        all_used_quotes.extend(new_quotes)

        # Create summary of this section for context
        words = text.split()
        summary = f"Section {i+1} ({section['name']}): {' '.join(words[:50])}..."
        previous_summaries.append(summary)
        total_words += len(words)

    # Step 3: Assemble full script with section breaks
    full_script = "\n\n".join(sections_text)

    return {
        "script": full_script,
        "topic": topic,
        "duration_minutes": duration_minutes,
        "word_count": total_words,
        "estimated_duration": round(total_words / 130, 1),
        "sections_count": len(sections_text),
        "sections": [
            {
                "name": outline["sections"][i].get("name", f"Section {i+1}"),
                "word_count": len(sections_text[i].split()),
                "preview": sections_text[i][:200] + "..."
            }
            for i in range(len(sections_text))
        ],
        "quotes_used": len(all_used_quotes),
        "outline": outline,
        "generated_at": datetime.now().isoformat()
    }


# --- Voice Synthesis Pipeline ---

def _synthesize_chunk(text, voice_id, api_key, previous_text=None, next_text=None):
    """Synthesize a single text chunk to audio bytes with context for prosody continuity."""
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.50,
            "similarity_boost": 0.80,
            "style": 0.45
        }
    }

    # Add context for smoother transitions between chunks
    if previous_text:
        payload["previous_text"] = previous_text[-200:]
    if next_text:
        payload["next_text"] = next_text[:200]

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=120,
        verify=certifi.where()
    )

    if response.status_code != 200:
        raise Exception(f"ElevenLabs error {response.status_code}: {response.text[:200]}")

    return response.content


def _split_into_chunks(text, max_chars=4500):
    """Split text at paragraph boundaries, respecting max char limit."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) + 2 > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # If single paragraph exceeds max, split at sentence boundaries
            if len(para) > max_chars:
                sentences = para.replace('. ', '.\n').replace('? ', '?\n').replace('! ', '!\n').split('\n')
                sub_chunk = ""
                for sent in sentences:
                    if len(sub_chunk) + len(sent) + 1 > max_chars:
                        if sub_chunk:
                            chunks.append(sub_chunk.strip())
                        sub_chunk = sent
                    else:
                        sub_chunk += " " + sent
                current_chunk = sub_chunk
            else:
                current_chunk = para
        else:
            current_chunk += "\n\n" + para if current_chunk else para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def _stitch_audio(chunk_paths, output_path):
    """Stitch audio chunks by direct MP3 byte concatenation.
    
    Works without ffmpeg. ElevenLabs outputs same-format MP3s,
    so raw concatenation produces valid playback.
    """
    with open(output_path, 'wb') as out_f:
        for chunk_path in chunk_paths:
            with open(chunk_path, 'rb') as chunk_f:
                out_f.write(chunk_f.read())


def synthesize_long_audio(script_text, voice_id=None, progress_callback=None):
    """
    Full voice pipeline: chunk → synthesize → stitch → return base64.
    """
    api_key = get_elevenlabs_key()
    if not api_key:
        return None, "ElevenLabs API key required"

    voice_id = voice_id or JASON_VOICE_ID

    # Split into chunks
    chunks = _split_into_chunks(script_text, max_chars=4500)

    if progress_callback:
        progress_callback("voice_chunking", len(chunks))

    # Create temp directory
    tmp_dir = tempfile.mkdtemp(prefix='jason_audio_')
    chunk_paths = []

    try:
        # Synthesize each chunk with context for prosody continuity
        for i, chunk_text in enumerate(chunks):
            if progress_callback:
                progress_callback("voice_synthesizing", i + 1)

            # Provide surrounding context for smoother transitions
            prev_text = chunks[i - 1] if i > 0 else None
            next_text = chunks[i + 1] if i < len(chunks) - 1 else None

            try:
                audio_bytes = _synthesize_chunk(chunk_text, voice_id, api_key, prev_text, next_text)
            except Exception as e:
                # Retry once
                time.sleep(3)
                try:
                    audio_bytes = _synthesize_chunk(chunk_text, voice_id, api_key, prev_text, next_text)
                except Exception:
                    return None, f"Voice synthesis failed on chunk {i+1}: {str(e)[:200]}"

            chunk_path = os.path.join(tmp_dir, f'chunk_{i:03d}.mp3')
            with open(chunk_path, 'wb') as f:
                f.write(audio_bytes)
            chunk_paths.append(chunk_path)

            # Rate limiting (ElevenLabs)
            if i < len(chunks) - 1:
                time.sleep(0.5)

        # Stitch chunks
        if progress_callback:
            progress_callback("voice_stitching", 0)

        output_path = os.path.join(tmp_dir, 'final_keynote.mp3')
        _stitch_audio(chunk_paths, output_path)

        # Read and encode
        with open(output_path, 'rb') as f:
            audio_base64 = base64.b64encode(f.read()).decode('utf-8')

        return {
            "audio_base64": audio_base64,
            "audio_mime": "audio/mpeg",
            "chunks_count": len(chunks),
            "total_duration_estimate": round(len(script_text.split()) / 130, 1)
        }, None

    finally:
        # Cleanup temp files
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)


# --- CLI Mode ---

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Jason Silva AI — Long-form Keynote Generator')
    parser.add_argument('topic', help='Keynote topic')
    parser.add_argument('--duration', type=int, default=45, help='Duration in minutes (10-45)')
    parser.add_argument('--output', default=None, help='Output file for script (.md)')
    parser.add_argument('--voice', default=None, help='Output file for audio (.mp3)')
    parser.add_argument('--json', action='store_true', help='Output metadata as JSON')

    args = parser.parse_args()

    def progress(stage, value):
        stages = {
            "generating_outline": "📋 Generating outline...",
            "generating_section": f"✍️  Writing section {value}...",
            "voice_chunking": f"🔪 Split into {value} chunks",
            "voice_synthesizing": f"🎙️  Synthesizing chunk {value}...",
            "voice_stitching": "🎵 Stitching audio..."
        }
        print(stages.get(stage, f"{stage}: {value}"), flush=True)

    print(f"\n⚡ Jason Silva AI — Generating {args.duration}-min keynote")
    print(f"📝 Topic: {args.topic}\n")

    result = generate_full_keynote(args.topic, args.duration, progress_callback=progress)

    print(f"\n✅ Generated: {result['word_count']} words, ~{result['estimated_duration']} min")
    print(f"📊 Sections: {result['sections_count']}, Quotes: {result['quotes_used']}")

    if args.output:
        with open(args.output, 'w') as f:
            f.write(f"# {result['topic']}\n")
            f.write(f"*{result['estimated_duration']} min | {result['word_count']} words*\n\n")
            f.write(result['script'])
        print(f"💾 Script saved to {args.output}")

    if args.json:
        meta = {k: v for k, v in result.items() if k != 'script'}
        print(json.dumps(meta, indent=2))

    if args.voice:
        print("\n🎙️  Starting voice synthesis...")
        audio_result, error = synthesize_long_audio(result['script'], progress_callback=progress)
        if error:
            print(f"❌ Voice error: {error}")
        else:
            audio_bytes = base64.b64decode(audio_result['audio_base64'])
            with open(args.voice, 'wb') as f:
                f.write(audio_bytes)
            print(f"🔊 Audio saved to {args.voice} ({audio_result['chunks_count']} chunks)")

    if not args.output and not args.json:
        print("\n--- SCRIPT PREVIEW (first 1000 chars) ---")
        print(result['script'][:1000])
        print("...")
