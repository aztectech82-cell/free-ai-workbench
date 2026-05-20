# Free AI Workbench

**A local-first AI stack for Windows. Free models. No subscription required.**

Built by Marcos Alvarez | Veteran Fleet Technologies, LLC | Army Veteran | MBA Candidate

---

## What It Is

Free AI Workbench runs powerful AI models directly on your Windows PC using [Ollama](https://ollama.com). You get a clean browser interface with chat, model comparison, screenshot context, file tools, and AI framing presets -- all offline, all private, all free.

Optional paid API keys (OpenAI, Anthropic, DeepSeek, Groq) can be added anytime, but are never required.

---

## One-Command Install

Open PowerShell and run:

```powershell
irm https://raw.githubusercontent.com/aztectech82-cell/free-ai-workbench/main/installer/install-free-ai-workbench.ps1 | iex
```

The installer will:
1. Create `C:\Users\YourName\FreeAIWorkbench` folder
2. Check Python -- install via winget if missing
3. Check Ollama -- install via winget if missing
4. Pull the DeepSeek R1 starter model (free, local, 8B)
5. Create a `.env.local` config file with optional API slots
6. Create a `Start-FreeAIWorkbench.ps1` launcher
7. Add a **desktop shortcut** -- double-click to start

Then open: `http://127.0.0.1:8765`

---

## Manual Start (if already installed)

```powershell
cd C:\Users\YourName\FreeAIWorkbench
powershell -NoProfile -ExecutionPolicy Bypass -File .\Start-FreeAIWorkbench.ps1
```

---

## Local AI Models Included

| Model | Tag | Best For |
|-------|-----|----------|
| DeepSeek R1 | `deepseek-r1:8b` | Reasoning, logic, step-by-step analysis |
| Qwen 3.6 | `qwen3.6:latest` | General purpose, long context |
| Qwen Coder | `qwen2.5-coder:7b` | Code generation and debugging |
| Qwen Vision | `qwen2.5vl:7b` | Screenshot and image analysis |
| Mistral | `mistral:latest` | Fast general chat |
| Moondream | `moondream:latest` | Lightweight vision |

Pull any model with: `ollama pull <model-tag>`

---

## Features

**Chat**
- Select any installed Ollama model with one click
- Ask One -- single model response
- Ask All -- send one prompt to ALL models and compare answers side by side

**AI Framing Presets**
Load a purpose-built context for your task without typing a system prompt every time:
- Business | Finance | Engineering | Marketing | Writing | Data Analytics
- Research | Career | Creative | Custom (paste your own)

**Screenshot Context**
Click Shot or paste a screenshot with `Ctrl+V`. Use a vision model (Qwen Vision or Moondream) to ask what is on screen.

**File Actions**
- Read -- inspect a local file
- Create -- generate a new file with AI content
- Edit -- rewrite an existing file
- Append -- add AI content to the end of a file

**Stack Panopticon**
Right panel with MVP kit generator, installer audit, and Big Checker troubleshooting.

**Customizable Action Buttons**
Replace the default build-path buttons with your own workflow shortcuts. Saved in the browser.

**Desktop Shortcut**
Double-click `Free AI Workbench` on your desktop to launch. No terminal required.

---

## Requirements

- Windows 10 / 11
- Python 3.10+ (installer handles this)
- Ollama (installer handles this)
- ~5 GB free disk space for starter model

---

## Optional API Keys

Add to `.env.local` to unlock cloud models when needed. Free local mode works with no keys at all.

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-...
```

---

## Tech Stack

- Python (local HTTP server)
- HTML / CSS / JavaScript (VS Code-dark browser UI)
- Ollama (free local model engine)
- PowerShell (Windows install and launch scripts)

---

## Who This Is For

- Veterans and military families getting into AI
- Small business owners who want AI without monthly bills
- Students learning to build with AI tools
- Anyone who wants a private, offline AI workspace

---

## License

MIT License -- free to use, share, and build on.

---

*Veteran Fleet Technologies, LLC | Marcos Alvarez | 2026*
