# 🤖 My Personal Assistant — Arena Agent

A ready-to-run personal assistant built on **Arena.ai Agent Mode**.

It already works in **DEMO mode** (no API key needed) with tools for todos, notes, time, and calculator. Add an LLM key to make it super smart.

### ✨ What it can do
- ✅ **Todos & Reminders** — `Add todo: ...`, `Show my todos`, complete/delete
- 🕐 **Knows your timezone** — Asia/Karachi
- 📓 **Long-term memory** — `Remember: ...` saves notes
- 🧮 **Calculator** — math expressions
- 🔍 **Web search & Files** — ready to extend in `tools.py`
- 💬 **Chat UI** — beautiful interface at `http://localhost:3000`

---

### 🚀 Quick Start

**Your agent is already running!** Open the preview.

To run manually:
```bash
cd /home/user/my-agent
pip install -r requirements.txt
python app.py
```

### 🧠 Make it Smarter (Add GPT-4o)

1. Get a key from https://platform.openai.com/api-keys
2. Create `.env`:
```
OPENAI_API_KEY=sk-proj-...
```
3. Restart: `python app.py` — mode will change to `GPT-4o` and it will use tool-calling properly.

You can also swap to Anthropic Claude or Gemini by editing `app.py`.

### ⚙️ Customize

Edit these files:

- **`config.json`** — Change `name`, `system_prompt`, personality, timezone
  - Example: Make it speak Urdu, be formal, or focus on business tasks
- **`tools.py`** — Add new tools:
  ```python
  def my_new_tool(args):
      return {"result": "..."}
  # Then add to TOOL_SCHEMAS
  ```
- **`agent.py`** — Change demo responses and system prompt logic
- **`static/index.html`** — Customize the UI

### 📁 File Structure
```
my-agent/
├── config.json     # Agent name, personality, tools
├── agent.py        # System prompt + demo logic
├── tools.py        # All tool implementations
├── app.py          # Flask server + LLM integration
├── static/index.html # Chat UI
├── requirements.txt
└── memory_*.json   # Auto-created: todos & notes storage
```

### 🔧 Add More Tools (Examples)

- **Email (Gmail API)** — send/read emails
- **Calendar (Google Calendar)** — create events
- **WhatsApp (Twilio)** — send messages
- **Web Search (Tavily/SerpAPI)** — live search
- **Weather API** — forecasts for Utmanzai
- **Voice (ElevenLabs)** — speak responses

Tell me what tools you want and I'll add them for you!

### 📦 Deploy on Arena

Your agent lives in `/home/user/my-agent`. To share:
1. Download the folder
2. Deploy `app.py` to any Python host (Render, Railway, Hugging Face)
3. Or keep running it here in Arena workspace

---

**Need help?** Tell me:
- What should your agent be named?
- What tasks should it do daily?
- Should it speak English, Urdu, or both?

I can update everything for you now!
