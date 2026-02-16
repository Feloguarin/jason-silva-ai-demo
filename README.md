# Jason Silva AI — Keynote Generator

AI-powered keynote generator that creates content in Jason Silva's voice and style, with voice synthesis using his cloned voice.

**Live:** [jason-silva-ai-demo.vercel.app](https://jason-silva-ai-demo.vercel.app)

## Features

- **AI Script Generation** — Claude (Anthropic) generates keynote scripts grounded in Jason's actual writings and philosophical frameworks
- **RAG Knowledge Base** — Scripts informed by Jason's Substack articles, interviews, and public content (~48K chars)
- **Voice Synthesis** — ElevenLabs voice clone produces audio in Jason's voice
- **Long-Form Engine** — Structured narrative arcs for 10–45 minute keynotes (Hook → Context → Tension → Exploration → Synthesis → Crescendo → Landing)
- **Chunked Pipeline** — Split architecture for Vercel Hobby (60s timeout): each API call is one Anthropic or ElevenLabs request, orchestrated by the frontend
- **AI Smell Removal** — Banned patterns in prompt + regex post-processor catches "not just X, it's Y" and similar AI tells
- **Guardrails** — Content filtering for approved topics and style consistency
- **Duration Options** — 1 min to 45 min keynotes

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
    ┌────┴────────────┐
    │                 │
    ▼                 ▼
Short-form        Long-form (10-45 min)
(1-5 min)         ┌──────────────────┐
Single call       │ Frontend orchestrates:
                  │ 1. POST /api/longform/outline (Haiku)
                  │ 2. POST /api/longform/section × N (Sonnet)
                  │ 3. POST /api/voice/split
                  │ 4. POST /api/voice/chunk × N (ElevenLabs)
                  │ 5. Browser-side MP3 stitching
                  └──────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask (Python) |
| AI Generation | Anthropic Claude (Haiku for outlines, Sonnet for sections) |
| Voice Synthesis | ElevenLabs Multilingual v2 |
| Voice ID | `Xar9jZKMXSKxBNlDsFCr` (Jason Silva clone) |
| Knowledge Base | Embedded RAG (~48K chars) |
| Deployment | Vercel Serverless (Hobby plan, 60s timeout) |
| Frontend | Vanilla HTML/CSS/JS |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/api/generate` | POST | Generate short-form script (1–5 min) |
| `/api/voice` | POST | Synthesize voice from short script |
| `/api/guardrails` | POST | Content guardrails check |
| `/api/longform/outline` | POST | Generate narrative outline (Haiku, ~8s) |
| `/api/longform/section` | POST | Generate one section (Sonnet, ~14–23s) |
| `/api/voice/split` | POST | Split text into voice chunks |
| `/api/voice/chunk` | POST | Synthesize one voice chunk |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude |
| `ELEVENLABS_API_KEY` | ElevenLabs API key for voice synthesis |

## Project Structure

```
jason-silva-ai-demo/
├── app.py                      # Flask routes (short-form + split long-form endpoints)
├── longform_engine.py          # Long-form generation engine (narrative arcs, desmell, chunked voice)
├── jason_knowledge_base.txt    # RAG knowledge base (Jason's writings, ~48K chars)
├── templates/
│   └── index.html              # Frontend with multi-step orchestration
├── requirements.txt            # Python dependencies
├── vercel.json                 # Vercel deployment config
└── README.md
```

## Cost Per Keynote

| Length | Script | Voice | Total |
|--------|--------|-------|-------|
| 1–5 min | ~$0.01 | ~$0.50–1.50 | ~$1–2 |
| 10 min | ~$0.09 | ~$2.56 | ~$2.65 |
| 20 min | ~$0.12 | ~$5.12 | ~$5.24 |
| 45 min | ~$0.15 | ~$11.51 | ~$11.66 |

## Local Development

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key
export ELEVENLABS_API_KEY=your_key
python app.py
# → http://localhost:5000
```

## Deployment

Deploys automatically via Vercel Git integration, or manually:

```bash
vercel --prod
```
