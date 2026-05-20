# Capability Inventory - AI Stack MVP

This inventory lists what exists now, what is partially present, and what should be built next.

## Exists Now

| Capability | Status | Where |
|---|---|---|
| Local browser UI | Working | `tools/local_ai_app.py` |
| Ollama model detection | Working | `/api/models` |
| One-model chat | Working | `/api/chat` |
| Ask All model comparison | Working | `/api/panel` |
| AI framing presets | Working | UI + `QUICK_CONTEXTS` |
| Custom action buttons | Working | left panel + browser localStorage |
| Big Checker button | Working | left panel + `/api/windows` |
| Screenshot capture/paste | Working, model-dependent | composer |
| Voice input | Browser dependent | Web Speech API |
| Read file | Working | `/api/file` |
| Create file | Working, direct write | `/api/file` |
| Edit file | Working, direct write | `/api/file` |
| Append file | Working | `/api/file` |
| List workspace files | Working | `/api/list` |
| Git status | Working | `/api/run` |
| Safe preset shell commands | Working | allowlist only |
| Stack Panopticon / installer builder | Working | right panel |
| MVP kit generator | Working | `/api/setup` |
| Open folder helper | Working | `/api/open-folder` |
| Windows tools | Working | `/api/windows` |
| Desktop shortcut script | Working | `create-local-ai-workbench-shortcut.ps1` |
| Starter automations | Working | `AI-Stack-MVP/automations/starter_automations.py` |
| Handshake showcase draft | Working | `AI-Stack-MVP/showcase/HANDSHAKE_SHOWCASE.md` |

## Partially Present

| Capability | Current State | Next Improvement |
|---|---|---|
| API keys | `.env` placeholders exist | Add UI validator and provider routing |
| Vision models | Screenshot UI exists | Test Qwen Vision/Moondream and add clearer model guidance |
| File safety | Path resolver exists | Add preview/confirm before overwrite |
| Windows integration | Helper buttons exist | Add open current file, copy path, launch VS Code |
| Demo readiness | Showcase draft exists | Add screenshots, GIF, and short video script |
| Automations | Simple templates exist | Add job packet, learning plan, audit, and email brief automations |

## Not Built Yet

- Cloud API model routing.
- GitHub publish flow.
- Broader installer testing.
- Settings page.
- Recent files list.
- Conversation export.
- File diff preview.
- Multi-workspace profiles.
- Authentication or remote deployment.

## Best Current MVP Claim

The MVP is not a complete AI platform yet. The accurate claim is:

> A local-first AI workbench that combines Ollama chat, model comparison, reusable context, screenshot capture, file actions, Windows helpers, stack audit prompts, and an MVP kit generator in one browser interface.

## Strongest Demo Use Cases

1. Use the build-path guide to explain how the free stack is made.
2. Capture or paste a screenshot and ask a vision model for context.
3. Ask All models for critique.
4. Create a business playbook or learning-plan file.
5. Generate the AI-Stack-MVP package.
6. Open the Handshake showcase draft.
7. Show local `.env` placeholders for optional APIs.

## Weakest Areas To Fix Before Public Posting

1. File writes need preview/confirm.
2. The UI needs screenshots and a stronger landing narrative.
3. The project needs a clean README at repo root or MVP root.
4. The cloud API story is currently only configuration slots, not working routing.
5. The app should clearly say local-only/private by default.
