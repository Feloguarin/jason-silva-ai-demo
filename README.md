# Jason Silva AI — Keynote Generator

AI-powered keynote generator that creates content in Jason Silva's voice and style, with voice synthesis using his cloned voice.

**Live Demo:** [demo-web-alpha-six.vercel.app](https://demo-web-alpha-six.vercel.app)

## Features

- **AI Script Generation** — Claude (Anthropic) generates keynote scripts grounded in Jason's actual writings and philosophical frameworks
- **RAG Knowledge Base** — Scripts are informed by Jason's Substack articles, interviews, and public content (~48k chars of real material)
- **Voice Synthesis** — ElevenLabs voice clone produces audio in Jason's voice
- **Guardrails** — Content filtering for approved topics and style consistency
- **Duration Options** — 1 min, 2 min, or 5 min keynotes

## Architecture

```
User Input (topic, duration, style)
        │
        ▼
  ┌─────────────┐
  │  Flask App   │
  │  (app.py)    │
  └──────┬──────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│Anthropic│ │ElevenLabs│
│  API    │ │  API     │
│(Claude) │ │(Voice)   │
└────┬────┘ └────┬─────┘
     │           │
     ▼           ▼
  Script      Audio
  (text)      (MP3)
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask (Python) |
| AI Generation | Anthropic Claude Sonnet |
| Voice Synthesis | ElevenLabs v2 |
| Knowledge Base | Embedded RAG (text file) |
| Deployment | Vercel Serverless |
| Frontend | Vanilla HTML/CSS/JS |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude |
| `ELEVENLABS_API_KEY` | ElevenLabs API key for voice synthesis |

## Project Structure

```
demo-web/
├── app.py                      # Flask app (routes + generation logic)
├── jason_knowledge_base.txt    # RAG knowledge base (Jason's writings)
├── templates/
│   └── index.html              # Frontend UI
├── requirements.txt            # Python dependencies
├── vercel.json                 # Vercel deployment config
└── README.md
```

## Local Development

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
export ELEVENLABS_API_KEY=your_key
python app.py
# → http://localhost:5000
```

## Deployment

```bash
vercel --prod
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/api/generate` | POST | Generate keynote script |
| `/api/voice` | POST | Synthesize voice from script |
| `/api/guardrails` | POST | Check content against guardrails |
