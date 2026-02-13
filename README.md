# 🎤 Jason Silva AI Demo — Quick Start

## Prerequisites

- Python 3.8+
- Anthropic API key (in OpenRouter)
- ElevenLabs API key with Jason voice clone

## Setup (2 minutes)

```bash
# 1. Navigate to demo folder
cd demo-web

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export ANTHROPIC_API_KEY="your-key-here"
export ELEVENLABS_API_KEY="your-key-here"

# 5. Run the app
python app.py
```

## Access the Demo

Open browser to: **http://localhost:5000**

## Deploy to Production

### Option 1: Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

Add environment variables in Vercel dashboard:
- `ANTHROPIC_API_KEY`
- `ELEVENLABS_API_KEY`

### Option 2: Render

1. Push code to GitHub
2. Connect repo to Render
3. Add environment variables
4. Deploy

### Option 3: Localtunnel (For Demo Meeting)

```bash
# Install localtunnel
npm install -g localtunnel

# Run app
python app.py &

# Expose to internet
lt --port 5000
```

Share the URL with Jordan.

## Demo Flow

1. **Open the app** — Shows "Jason Silva AI" interface
2. **Enter topic** — "The future of human creativity in an AI world"
3. **Click Generate** — Shows progress steps
4. **View script** — Full keynote appears
5. **Click Generate Voice** — Jason's AI voice plays
6. **Close the deal**

## Features

- ✅ AI script generation (Claude)
- ✅ Voice synthesis (ElevenLabs)
- ✅ Progress visualization
- ✅ Guardrails display
- ✅ Audio playback
- ✅ Copy/regenerate functions

## Troubleshooting

**Voice not generating?**
- Check ElevenLabs API key
- Verify voice ID `Xar9jZKMXSKxBNlDsFCr` exists
- Check API quota

**Scripts not generating?**
- Check OpenRouter API key
- Verify Anthropic credits

## Cost Per Demo

- Script generation: ~$0.02
- Voice synthesis: ~$0.05
- **Total: ~$0.07 per keynote**

---

**Built for the Jordan Silva meeting — February 13, 2026**
