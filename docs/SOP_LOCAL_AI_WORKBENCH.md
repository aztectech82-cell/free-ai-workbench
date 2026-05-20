# SOP - Local AI Workbench MVP

Version: 0.1  
Prepared: 2026-05-10  
System: AI-TOOL Local AI Workbench + AI-Stack-MVP kit

## 1. Purpose

This SOP explains how to use and demonstrate the Local AI Workbench MVP.

The project is a **free-first AI stack**:

- Use local Ollama models for daily work.
- Use optional paid API keys only when cloud models are needed.
- Keep secrets in local `.env` files.
- Give the user buttons, build-path steps, screenshot context, and file actions instead of terminal commands.

The core story:

> Start with a small bootstrap API budget, then run the daily AI workflow on a free local stack.

## 2. What The System Can Do Today

### Chat And Model Work

- Chat with one selected Ollama model.
- Compare responses across installed local models with **Ask All**.
- Use model buttons instead of typing model names.
- Show whether Ollama is online.
- Stream responses into the browser.

Current model aliases:

- DeepSeek R1: `deepseek-r1:8b`
- Big Qwen: `qwen3.6:latest`
- Qwen Coder: `qwen2.5-coder:7b`
- Qwen Vision: `qwen2.5vl:7b`
- Mistral: `mistral:latest`
- Moondream: `moondream:latest`

### AI Framing Presets

The AI can load reusable framing so the same question can be answered through a useful lens:

- No context
- General Problem Solving
- Business
- Finance
- Engineering
- Marketing
- Writing
- Data Analytics
- Research
- Career
- Creative
- Astrology / Reflection
- Build This AI Tool
- Custom pasted context

### Custom Action Buttons

The left panel starts by guiding the user through how the stack was made:

- Install free stack
- Pull local models
- Ask first question
- Screenshot context
- Work with files
- Build automation
- Audit and cut clutter
- Package app
- Publish showcase

After setup, the user can click **Customize Actions** and replace these with their own command buttons. The custom buttons are stored in the browser with `localStorage`, so a user can turn the setup panel into a personal workflow panel.

The **Big Checker** button runs the cross-reference checker for troubleshooting.

### Screenshot Context

The composer includes a **Shot** button. Users can capture the screen, or use Windows Snipping Tool and paste an image into the app with `Ctrl+V`. Vision-capable models such as Qwen Vision or Moondream should be used for image questions.

### File Actions

The app can:

- Read a file.
- Create a file with AI-generated content.
- Edit an existing file using the selected model.
- Append text to a file.

Current safety note: create/edit writes directly after clicking the action. A preview-before-save flow is a priority improvement.

### Workspace Tools

The app can:

- List files in a folder.
- Show `git status --short`.
- Run safe preset commands only.

Allowed preset commands today:

- `git status --short`
- `git diff --stat`
- `ollama list`

### Windows Tools

The interface includes local Windows helpers:

- Open the repo folder in File Explorer.
- Create a desktop shortcut for the workbench.
- List Ollama models.
- Open the MVP folder.

### MVP Kit Generator

The **Stack Panopticon** can generate:

- `README.md`
- `.env.example`
- `.env.local`
- `.gitignore`
- `scripts/start-free-stack.ps1`
- `automations/starter_automations.py`
- `showcase/HANDSHAKE_SHOWCASE.md`
- `workspace/README.md`

### Starter Automations

The starter automation script can:

- Create a dated daily note.
- Create a business playbook template.
- Create workspace folders for notes and outputs.

## 3. How To Launch

From PowerShell:

```powershell
cd C:\Users\aztec\AI-TOOL
.\local-ai-workbench.ps1
```

Local URL:

```text
http://127.0.0.1:8765
```

To launch without opening a browser:

```powershell
.\local-ai-workbench.ps1 --no-open
```

## 4. How To Use The Interface

### Basic Chat

1. Confirm the top-right status says Ollama is online.
2. Pick a model on the left.
3. Leave **Ask One** selected.
4. Type your request.
5. Click **Send**.

### Compare Models

1. Click **Ask All**.
2. Type one prompt.
3. Click **Send**.
4. Review responses from installed local models.

Use this when you want critique, second opinions, or multiple writing options.

### Use AI Framing

1. Go to the AI Framing panel.
2. Choose a preset or paste custom framing.
3. Click **Set Framing**.
4. Ask your question.

The conversation resets when framing changes so the AI starts clean.

### Use File Actions

1. Enter a relative path, such as:

```text
Generated-Content/notes.md
```

2. Add the instruction or content.
3. Choose:

- **Read** to inspect a file.
- **Create** to generate a new file.
- **Edit** to rewrite an existing file.
- **Append** to add content to the end.

### Generate The MVP Kit

1. Go to **Stack Panopticon**.
2. Keep folder as:

```text
AI-Stack-MVP
```

3. Click **Create MVP Kit**.
4. Open the folder and review the generated files.

## 5. Demo Script For Handshake

Use this flow:

1. Open Local AI Workbench.
2. Show the model list and explain local/free-first Ollama.
3. Click build-path steps to show the process from install to showcase.
4. Ask DeepSeek for a project plan.
5. Switch to **Ask All** and ask for critique.
6. Show the file actions panel.
7. Generate or open the MVP kit.
8. Open `HANDSHAKE_SHOWCASE.md`.
9. Explain the value:

> This lets AI learners, families, veterans, and builders use local AI models for everyday work, keep optional API keys private, audit their stack, and turn repeated tasks into local automations.

## 6. Safety Rules

- Do not paste real API keys into screenshots.
- Keep `.env.local` out of Git.
- Do not enable arbitrary shell commands by default.
- Keep file writes inside the workspace.
- Add preview-before-save before presenting this as a production file editor.

## 7. Known Gaps

- File create/edit does not yet show a preview before writing.
- No drag-and-drop file upload yet.
- Screenshot paste/capture is present, but model support depends on having a vision model installed.
- No cloud API routing yet, only local Ollama.
- No authentication because this is local-only.
- Installer exists, but needs broader Windows testing.
- No automated tests yet.

## 8. Recommended Next Build Order

1. Add file preview before create/edit overwrite.
2. Add recent files and open folder buttons.
3. Add drag-and-drop file read.
4. Test screenshot flow with Qwen Vision/Moondream.
5. Add cloud model adapter using `.env.local`.
6. Add project templates for learning, job search, small business, family use, and veteran support.
7. Add screenshots and a 60-second demo recording.
