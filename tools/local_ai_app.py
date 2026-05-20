"""
Local AI Workbench

Browser-based UI for your local Ollama models. This is intentionally
click-first: model buttons, voice button, ask-one/ask-all, and file actions.

Run:
    python tools/local_ai_app.py
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import subprocess
import sys
import threading
import urllib.error
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

MODEL_ALIASES = {
    "DeepSeek R1": ("deepseek-r1:8b", "strong"),
    "Big Qwen": ("qwen3.6:latest", "slow"),
    "Qwen Coder": ("qwen2.5-coder:7b", "fast"),
    "Qwen Vision": ("qwen2.5vl:7b", "vision"),
    "Mistral": ("mistral:latest", "fast"),
    "Moondream": ("moondream:latest", "vision"),
}

BASE_SYSTEM_PROMPT = """You are a free-first local AI workbench assistant.
You help AI learners, families, veterans, builders, and small teams use local AI
without subscriptions. Be clear, practical, and safe. Explain steps simply when
teaching beginners, but provide expert-level detail when asked. When creating
files, produce complete usable content. When editing, preserve the user's tone
unless asked otherwise. Be concise unless asked to expand."""

QUICK_CONTEXTS = {
    "none": "",
    "general": """GENERAL AI FRAMING:
Be a practical assistant. Clarify the goal, summarize the situation, identify options, recommend next steps, and keep the answer useful for a normal person.""",
    "business": """BUSINESS AI FRAMING:
Think like a practical operator. Focus on customers, offer, pricing, process, sales, risk, execution, and the next measurable action.""",
    "finance": """FINANCE AI FRAMING:
Help with budgeting, comparisons, simple financial reasoning, and decision support. Be clear about assumptions and do not pretend to be a licensed financial advisor.""",
    "engineering": """ENGINEERING AI FRAMING:
Think in systems. Focus on requirements, constraints, architecture, tradeoffs, safety, testing, maintainability, and step-by-step implementation.""",
    "marketing": """MARKETING AI FRAMING:
Focus on audience, positioning, channel, message, offer, creative, funnel, metrics, experimentation, and what to test next.""",
    "writing": """WRITING AI FRAMING:
Help shape clear, human writing. Preserve the user's intent and voice, improve structure and flow, and make the result specific instead of generic.""",
    "data_analytics": """DATA ANALYTICS AI FRAMING:
Focus on the question, dataset, definitions, cleaning steps, metrics, patterns, caveats, and what decision the analysis should support.""",
    "research": """RESEARCH AI FRAMING:
Separate facts from assumptions. Create source-aware summaries, identify uncertainty, ask what evidence is missing, and avoid overclaiming.""",
    "career": """CAREER AI FRAMING:
Help with resumes, portfolios, job search, interview preparation, networking, and translating experience into credible proof of ability.""",
    "creative": """CREATIVE AI FRAMING:
Generate original concepts, names, stories, visuals, scripts, and variations. Keep ideas bold but usable, and offer options with different tones.""",
    "astrology": """ASTROLOGY / REFLECTION AI FRAMING:
Use astrology as a reflective or creative lens, not as factual prediction. Keep it grounded, optional, and useful for journaling, storytelling, or self-reflection.""",
    "ai_stack_mvp": """FREE AI WORKBENCH MVP FRAMING:
The product is an installable Windows app that starts with a small optional API budget for setup, then runs day-to-day on free local Ollama models. It should teach the build journey: install tools, pull models, chat, use screenshot context, work with files, create automations, package the app, and publish a showcase.""",
}

HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Free AI Workbench</title>
  <style>
    :root {
      --bg: #1e1e1e;
      --panel: #252526;
      --panel2: #2d2d30;
      --ink: #e7e7e7;
      --muted: #a6a6a6;
      --line: #3c3c3c;
      --blue: #007acc;
      --blue2: #0e639c;
      --green: #89d185;
      --red: #f48771;
      --orange: #dcdcaa;
      --dark: #181818;
      --soft: #1f2933;
      --left-w: 248px;
      --right-w: 340px;
      --accent: #4fc1ff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", system-ui, sans-serif;
      color: var(--ink);
      background: var(--bg);
      height: 100vh;
      width: 100vw;
      display: grid;
      grid-template-columns: var(--left-w) 6px minmax(0, 1fr) 6px var(--right-w);
      gap: 0;
      padding: 8px;
      overflow: hidden;
    }
    aside, main, section { min-width: 0; }
    aside {
      background: var(--dark);
      color: white;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      overflow-y: auto;
      height: calc(100vh - 16px);
      border: 1px solid var(--line);
      border-radius: 8px 0 0 8px;
    }
    h1, h2, h3 { margin: 0; }
    h1 { font-size: 19px; line-height: 1.2; }
    h2 { font-size: 16px; margin-bottom: 8px; }
    h3 { font-size: 13px; margin-bottom: 6px; color: var(--muted); }
    .subtitle { color: #adbad0; font-size: 12px; line-height: 1.35; }
    .brand { display:grid; gap:8px; padding-bottom:6px; }
    .brand-row { display:flex; align-items:center; gap:10px; }
    .brand-row > div:last-child { min-width: 0; }
    .brand-mark {
      width:34px; height:34px; border-radius:8px;
      display:grid; place-items:center; font-weight:800;
      color:#07111c; background:linear-gradient(135deg,#4fc1ff,#89d185);
      box-shadow:0 0 24px rgba(79,193,255,.22);
    }
    .pill-row { display:flex; flex-wrap:wrap; gap:6px; }
    .pill {
      border:1px solid #344963; background:#202734; color:#c8d7ea;
      border-radius:999px; padding:3px 8px; font-size:10px;
    }
    .models { display: grid; gap: 6px; }
    .build-steps {
      border: 1px solid #334155;
      background: #151f2e;
      border-radius: 8px;
      padding: 10px;
      display: grid;
      gap: 7px;
    }
    .build-steps h3 { color: #dbeafe; margin-bottom: 2px; }
    .action-tools { display:grid; grid-template-columns:1fr 1fr; gap:7px; }
    .action-tools button { min-height:34px; font-size:12px; }
    .step-btn {
      width: 100%;
      text-align: left;
      background: #223149;
      border-color: #3d4f6d;
      color: #f8fbff;
      min-height: 34px;
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }
    .step-btn small {
      color: #89d185;
      font-size: 10px;
      flex: 0 0 auto;
    }
    button, input, textarea, select { font: inherit; }
    button {
      border: 1px solid var(--line);
      background: #2d2d30;
      color: var(--ink);
      min-height: 38px;
      border-radius: 6px;
      padding: 7px 11px;
      cursor: pointer;
    }
    button:hover { border-color: #6a9955; background: #333337; }
    .model-btn {
      text-align: left;
      background: #202734;
      color: white;
      border-color: #35445a;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 6px;
      font-size: 13px;
    }
    .model-btn span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .model-btn.active { background: var(--blue); border-color: #58adf2; }
    .speed-fast { color: #7fde9f; font-size: 10px; }
    .speed-slow { color: #f5a623; font-size: 10px; }
    .toggle {
      display: flex; gap: 6px;
      background: #182232; padding: 6px; border-radius: 7px;
    }
    .toggle button {
      flex: 1; background: transparent; color: white; border-color: transparent; font-size: 13px;
    }
    .toggle button.active { background: white; color: #101722; }
    .gutter {
      height: calc(100vh - 16px);
      background: #151515;
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
      cursor: col-resize;
      position: relative;
    }
    .gutter::after {
      content: "";
      position: absolute;
      left: 2px;
      top: 45%;
      width: 2px;
      height: 44px;
      border-radius: 4px;
      background: #4b4b4b;
    }
    .gutter:hover::after { background: var(--blue); }
    main {
      display: grid;
      grid-template-rows: auto minmax(0, 1fr) auto;
      height: calc(100vh - 16px);
      background: #1e1e1e;
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
    }
    header {
      background: var(--panel);
      border-bottom: 1px solid var(--line);
      padding: 16px 22px;
      display: flex; align-items: center;
      justify-content: space-between; gap: 12px;
    }
    .status { color: var(--muted); font-size: 12px; text-align: right; }
    .chat {
      overflow-y: auto; padding: 26px;
      display: flex; flex-direction: column; gap: 12px;
    }
    .welcome {
      border: 1px solid var(--line);
      background: linear-gradient(135deg, #252526 0%, #202a33 100%);
      border-radius: 8px;
      padding: 20px;
      max-width: 960px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.03);
    }
    .welcome h2 { font-size: 24px; margin-bottom: 6px; }
    .welcome-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin-top: 12px;
    }
    .welcome-tile {
      border: 1px solid var(--line);
      border-radius: 7px;
      padding: 12px;
      background: rgba(30,30,30,.72);
      font-size: 12px;
      line-height: 1.35;
    }
    .msg {
      max-width: 900px; padding: 11px 13px; border-radius: 8px;
      line-height: 1.5; white-space: pre-wrap;
      border: 1px solid var(--line); background: var(--panel);
      box-shadow: 0 4px 14px rgba(0,0,0,0.04);
      font-size: 14px;
    }
    .msg.user { align-self: flex-end; background: #0e3a5a; border-color: #1f6aa5; }
    .msg.ai strong { color: var(--blue2); display: block; margin-bottom: 4px; font-size: 12px; }
    .msg.thinking { opacity: 0.7; font-style: italic; }
    .composer {
      background: var(--panel); border-top: 1px solid var(--line);
      padding: 12px;
      display: grid; grid-template-columns: auto auto minmax(0,1fr) auto auto;
      gap: 8px; align-items: end;
    }
    .shot-btn.has-image { border-color: var(--green); color: var(--green); }
    .image-preview {
      grid-column: 1 / -1;
      display: none;
      align-items: center;
      gap: 10px;
      border: 1px solid var(--line);
      background: #181818;
      border-radius: 7px;
      padding: 8px;
    }
    .image-preview.visible { display: flex; }
    .image-preview img {
      width: 92px;
      height: 54px;
      object-fit: cover;
      border-radius: 5px;
      border: 1px solid var(--line);
    }
    .image-preview span { color: var(--muted); font-size: 12px; }
    textarea {
      width: 100%; min-height: 50px; max-height: 160px; resize: vertical;
      border: 1px solid var(--line); border-radius: 7px; padding: 10px;
      font-size: 14px;
      background: #1e1e1e;
      color: var(--ink);
    }
    .primary { background: var(--blue); color: white; border-color: var(--blue); font-weight: 650; }
    .primary:hover { background: var(--blue2); }
    .voice.recording { background: #ffecec; border-color: #ffaaa7; color: var(--red); }
    .right {
      background: #1e1e1e; padding: 18px;
      overflow-y: auto; height: calc(100vh - 16px);
      border: 1px solid var(--line);
      border-radius: 0 8px 8px 0;
    }
    .card {
      border: 1px solid var(--line); border-radius: 8px; padding: 13px;
      margin-bottom: 14px; background: var(--panel);
    }
    .metric-row {
      display: grid;
      grid-template-columns: repeat(3, minmax(0,1fr));
      gap: 7px;
      margin: 8px 0 10px;
    }
    .metric {
      border: 1px solid var(--line);
      background: #1e1e1e;
      border-radius: 7px;
      padding: 8px;
      min-height: 54px;
    }
    .metric b { display:block; font-size:15px; }
    .metric span { display:block; color:var(--muted); font-size:10px; margin-top:2px; }
    label {
      display: block; font-size: 11px; color: var(--muted);
      margin: 9px 0 4px; font-weight: 650; text-transform: uppercase; letter-spacing: 0.4px;
    }
    input, select {
      width: 100%; border: 1px solid var(--line); border-radius: 6px;
      min-height: 36px; padding: 7px 9px; font-size: 13px;
      background: #1e1e1e;
      color: var(--ink);
    }
    .row { display: flex; gap: 7px; }
    .row button { flex: 1; font-size: 13px; }
    .small { color: var(--muted); font-size: 12px; line-height: 1.35; }
    .ok { color: var(--green); }
    .bad { color: var(--red); }
    .warn { color: var(--orange); }
    .file-output {
      max-height: 240px; overflow: auto;
      background: #f6f8fb; border: 1px solid var(--line);
      border-radius: 6px; padding: 9px; white-space: pre-wrap;
      font-family: Consolas, monospace; font-size: 12px;
      background: #1e1e1e;
      color: #d4d4d4;
    }
    .ctx-badge {
      display: inline-block; background: #e6f4ea; color: #186a3b;
      border: 1px solid #b7dfc5; border-radius: 12px;
      font-size: 11px; padding: 2px 9px; margin-top: 6px;
    }
    select { cursor: pointer; }
    @media (max-width: 1100px) {
      body { grid-template-columns: 220px 6px minmax(0, 1fr); overflow:auto; }
      .right { display:none; }
      #rightGutter { display:none; }
    }
  </style>
</head>
<body>
<aside>
  <div class="brand">
    <div class="brand-row">
      <div class="brand-mark">AI</div>
      <div>
        <h1>Free AI Workbench</h1>
        <p class="subtitle">Local models. Adjustable panes. No subscription required.</p>
      </div>
    </div>
    <div class="pill-row">
      <span class="pill">Ollama</span>
      <span class="pill">Local</span>
      <span class="pill">Private</span>
    </div>
  </div>
  <div class="toggle">
    <button id="oneMode" class="active">Ask One</button>
    <button id="allMode">Ask All</button>
  </div>
  <div class="build-steps">
    <h3>Actions</h3>
    <div class="action-tools">
      <button id="bigCheckerBtn" class="primary">Big Checker</button>
      <button id="customizeActionsBtn">Customize Actions</button>
    </div>
    <div id="actionButtons" class="models"></div>
  </div>
  <div>
    <h3>Models</h3>
    <div id="modelButtons" class="models"></div>
  </div>
  <div style="background:#182232;border:1px solid #2c3b51;border-radius:8px;padding:12px">
    <h3 style="color:#c7d2e3">Voice</h3>
    <p class="small" style="color:#adbad0">Mic button below, or click text box and press <b>Win+H</b>.</p>
  </div>
</aside>
<div id="leftGutter" class="gutter" title="Drag to resize sidebar"></div>

<main>
  <header>
    <div>
      <h2 id="title">Chat</h2>
      <div class="small" id="ctxLabel"></div>
    </div>
    <div id="status" class="status">Connecting...</div>
  </header>
  <div id="chat" class="chat"></div>
  <div class="composer">
    <div id="imagePreview" class="image-preview">
      <img id="previewImg" alt="Screenshot preview" />
      <span id="previewText">Screenshot attached. Ask what you want to understand.</span>
      <button id="removeImageBtn" title="Remove screenshot">Remove</button>
    </div>
    <button id="voiceBtn" class="voice" title="Speak">Mic</button>
    <button id="shotBtn" class="shot-btn" title="Capture or paste a screenshot">Shot</button>
    <textarea id="prompt" placeholder="Say or type anything. Example: help me set up a Google Ads campaign for Buhi backpacks."></textarea>
    <button id="sendBtn" class="primary">Send</button>
    <button id="clearBtn">Clear</button>
  </div>
</main>
<div id="rightGutter" class="gutter" title="Drag to resize tools panel"></div>

<section class="right">
  <div class="card">
    <h2>Stack Panopticon</h2>
    <p class="small">See the local AI setup, generate the installer kit, and audit what should be improved or removed.</p>
    <div class="metric-row">
      <div class="metric"><b>$100</b><span>bootstrap API budget</span></div>
      <div class="metric"><b>Free</b><span>daily local models</span></div>
      <div class="metric"><b>MVP</b><span>showcase package</span></div>
    </div>
    <label>MVP Folder</label>
    <input id="setupFolder" value="AI-Stack-MVP" />
    <div class="row" style="margin-top:8px">
      <button id="setupBtn" class="primary" style="font-size:12px">Create MVP Kit</button>
      <button id="openMvpBtn" style="font-size:12px">Open Folder</button>
    </div>
    <div class="row" style="margin-top:6px">
      <button id="auditBtn" style="font-size:12px">Audit Stack</button>
      <button id="checkerBtn" style="font-size:12px">Run Checker</button>
    </div>
    <div class="row" style="margin-top:6px">
      <button id="openRepoTopBtn" style="font-size:12px">Open App</button>
      <button id="openMvpTopBtn" style="font-size:12px">Open MVP</button>
    </div>
    <p class="small" style="margin-top:8px">Creates placeholders only. Real API keys stay private in your local env file.</p>
  </div>

  <div class="card">
    <h2>AI Framing</h2>
    <p class="small">Choose the lens the AI should use, or write your own. The AI reads this with every message.</p>
    <label>Quick Load</label>
    <select id="quickCtx">
      <option value="none">No context</option>
      <option value="general">General Problem Solving</option>
      <option value="business">Business</option>
      <option value="finance">Finance</option>
      <option value="engineering">Engineering</option>
      <option value="marketing">Marketing</option>
      <option value="writing">Writing</option>
      <option value="data_analytics">Data Analytics</option>
      <option value="research">Research</option>
      <option value="career">Career</option>
      <option value="creative">Creative</option>
      <option value="astrology">Astrology / Reflection</option>
      <option value="ai_stack_mvp">Build This AI Tool</option>
      <option value="custom">Custom (type below)</option>
    </select>
    <label>Framing text (AI sees this)</label>
    <textarea id="ctxText" style="min-height:80px;max-height:140px;font-size:12px" placeholder="Paste your report, notes, or situation here..."></textarea>
    <div class="row" style="margin-top:8px">
      <button id="setCtxBtn" class="primary" style="font-size:12px">Set Framing</button>
      <button id="clearCtxBtn" style="font-size:12px">Clear</button>
    </div>
    <div id="ctxStatus" class="small" style="margin-top:6px"></div>
  </div>

  <div class="card">
    <h2>File Actions</h2>
    <p class="small">The app writes only after you click the exact action.</p>
    <label>Path</label>
    <input id="filePath" placeholder="Generated-Content/notes.md" />
    <label>Instruction / content</label>
    <textarea id="fileInstruction" placeholder="Describe the edit or paste content." style="min-height:60px;max-height:120px;font-size:12px"></textarea>
    <div class="row" style="margin-top:8px">
      <button id="readBtn" style="font-size:12px">Read</button>
      <button id="createBtn" style="font-size:12px">Create</button>
    </div>
    <div class="row" style="margin-top:6px">
      <button id="editBtn" style="font-size:12px">Edit</button>
      <button id="appendBtn" style="font-size:12px">Append</button>
    </div>
  </div>

  <div class="card">
    <h2>Workspace</h2>
    <label>Folder</label>
    <input id="listPath" value="." />
    <div class="row" style="margin-top:8px">
      <button id="listBtn" style="font-size:12px">List Files</button>
      <button id="gitBtn" style="font-size:12px">Git Status</button>
    </div>
  </div>

  <div class="card">
    <h2>Windows Tools</h2>
    <p class="small">One-click helpers for the local machine.</p>
    <div class="row" style="margin-top:8px">
      <button id="openRepoBtn" style="font-size:12px">Open Repo</button>
      <button id="shortcutBtn" style="font-size:12px">Desktop Shortcut</button>
    </div>
    <div class="row" style="margin-top:6px">
      <button id="ollamaBtn" style="font-size:12px">List Ollama</button>
      <button id="openMvpWinBtn" style="font-size:12px">Open MVP</button>
    </div>
  </div>

  <div class="card">
    <h2>Output</h2>
    <div id="fileOutput" class="file-output">Ready.</div>
  </div>
</section>

<script>
const QUICK_CONTEXTS = {
  none: "",
  general: "GENERAL AI FRAMING: Be a practical assistant. Clarify the goal, summarize the situation, identify options, recommend next steps, and keep the answer useful for a normal person.",
  business: "BUSINESS AI FRAMING: Think like a practical operator. Focus on customers, offer, pricing, process, sales, risk, execution, and the next measurable action.",
  finance: "FINANCE AI FRAMING: Help with budgeting, comparisons, simple financial reasoning, and decision support. Be clear about assumptions and do not pretend to be a licensed financial advisor.",
  engineering: "ENGINEERING AI FRAMING: Think in systems. Focus on requirements, constraints, architecture, tradeoffs, safety, testing, maintainability, and step-by-step implementation.",
  marketing: "MARKETING AI FRAMING: Focus on audience, positioning, channel, message, offer, creative, funnel, metrics, experimentation, and what to test next.",
  writing: "WRITING AI FRAMING: Help shape clear, human writing. Preserve the user's intent and voice, improve structure and flow, and make the result specific instead of generic.",
  data_analytics: "DATA ANALYTICS AI FRAMING: Focus on the question, dataset, definitions, cleaning steps, metrics, patterns, caveats, and what decision the analysis should support.",
  research: "RESEARCH AI FRAMING: Separate facts from assumptions. Create source-aware summaries, identify uncertainty, ask what evidence is missing, and avoid overclaiming.",
  career: "CAREER AI FRAMING: Help with resumes, portfolios, job search, interview preparation, networking, and translating experience into credible proof of ability.",
  creative: "CREATIVE AI FRAMING: Generate original concepts, names, stories, visuals, scripts, and variations. Keep ideas bold but usable, and offer options with different tones.",
  astrology: "ASTROLOGY / REFLECTION AI FRAMING: Use astrology as a reflective or creative lens, not as factual prediction. Keep it grounded, optional, and useful for journaling, storytelling, or self-reflection.",
  ai_stack_mvp: "FREE AI WORKBENCH MVP FRAMING: Installable Windows app. Start with optional paid API setup, then run day-to-day on free local Ollama models. Teach the build journey: install tools, pull models, chat, screenshot context, files, automations, package, and publish showcase.",
  custom: ""
};

const DEFAULT_ACTIONS = [
  {label: "1. Install free stack", tag: "setup", prompt: "Walk me through installing this free AI stack on a Windows computer. Give the exact beginner-friendly steps, what each tool does, and how to verify it worked."},
  {label: "2. Pull local models", tag: "Ollama", prompt: "Help me choose and pull the best free local Ollama models for this computer. Explain fast model, code model, vision model, and fallback model."},
  {label: "3. Ask first question", tag: "chat", prompt: "Guide me through my first local AI chat test. Tell me what to ask, what a good response looks like, and what to troubleshoot if it fails."},
  {label: "4. Screenshot context", tag: "vision", prompt: "I want to use screenshots as context. Explain how to capture or paste a screenshot, what model should read it, and how to ask good questions about the image."},
  {label: "5. Work with files", tag: "local", prompt: "Teach me how this app should read, create, edit, and append local files safely. Include rules for previewing before overwrite and keeping private files local."},
  {label: "6. Build automation", tag: "code", prompt: "Help me design one useful free local automation for this workbench. Keep it MVP: input, action, output file, and safety checks."},
  {label: "7. Audit and cut clutter", tag: "clean", prompt: "Audit this Free AI Workbench MVP like a product reviewer. Identify what is powerful, what is confusing, what is stale or personal clutter, what should be cut, and the next 10 fixes in priority order."},
  {label: "8. Package app", tag: "Windows", prompt: "Create the packaging checklist for giving this app to another Windows user: installer, shortcut, Ollama check, model pulls, env file, workspace, uninstall, and troubleshooting."},
  {label: "9. Publish showcase", tag: "MVP", prompt: "Help me write the MVP showcase for this Free AI Workbench: problem, users, features, screenshots to capture, demo flow, and next improvements."},
];

const state = {
  model: "deepseek-r1:8b",
  askAll: false,
  messages: [],
  context: "",
  attachedImage: null,
  attachedImageName: ""
};

const chat = document.getElementById("chat");
const promptBox = document.getElementById("prompt");
const statusEl = document.getElementById("status");
const out = document.getElementById("fileOutput");
const ctxLabel = document.getElementById("ctxLabel");

chat.innerHTML = `
  <div class="welcome">
    <h2>Free AI Workbench</h2>
    <div class="small">A free-first AI control room: install local models, learn the stack, capture screenshots for context, audit what is installed, and package an MVP others can use.</div>
    <div class="welcome-grid">
      <div class="welcome-tile"><b>Learn</b><br>Follow the build path from install to showcase.</div>
      <div class="welcome-tile"><b>Inspect</b><br>Audit models, files, workspace, and stale pieces to cut.</div>
      <div class="welcome-tile"><b>Build</b><br>Package a Windows MVP for AI learners, families, and veterans.</div>
    </div>
    <div style="margin-top:14px;padding:12px 14px;background:#1a1208;border:1px solid #5a3e00;border-radius:8px;font-size:12px;line-height:1.6;color:#e3c97a;">
      <b style="color:#f5a623;">Safety Rules</b> &mdash; Read before sharing this app with anyone:<br>
      <b>1.</b> Never enter SSNs, passwords, bank numbers, or credentials into the chat.<br>
      <b>2.</b> By default all messages stay on your computer. Adding a cloud API key sends messages to that provider.<br>
      <b>3.</b> Do not paste your employer's confidential or proprietary data. You may be under NDA.<br>
      <b>4.</b> AI output is not legal, medical, or financial advice. Verify before acting on anything important.<br>
      <b>5.</b> Do not use this app to generate content that harms, deceives, or impersonates others.<br>
      <span style="color:#aaa;">Full guardrails: <code style="color:#89d185;">docs/SAFETY_AND_GUARDRAILS.md</code></span>
    </div>
  </div>`;

function esc(s) {
  return String(s).replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
}

function isVisionModel(model) {
  return /moondream|qwen2\.5vl/i.test(model || "");
}

function addMessage(role, label, initial="") {
  const div = document.createElement("div");
  div.className = "msg " + (role === "user" ? "user" : "ai");
  if (role !== "user") {
    const strong = document.createElement("strong");
    strong.textContent = label;
    div.appendChild(strong);
  }
  const span = document.createElement("span");
  span.textContent = initial;
  div.appendChild(span);
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return span;
}

async function apiPost(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error(await res.text());
  return await res.json();
}

async function loadModels() {
  try {
    const data = await (await fetch("/api/models")).json();
    const wrap = document.getElementById("modelButtons");
    wrap.innerHTML = "";
    data.aliases.forEach(item => {
      const btn = document.createElement("button");
      btn.className = "model-btn" + (item.model === state.model ? " active" : "");
      const speedClass = item.speed === "slow" ? "speed-slow" : "speed-fast";
      const speedLabel = item.speed === "slow" ? "slow (36B)" : (item.speed === "vision" ? "vision" : (item.speed === "strong" ? "strong" : "fast"));
      btn.innerHTML = `<span>${esc(item.label)}</span><small class="${speedClass}">${item.installed ? speedLabel : "missing"}</small>`;
      btn.onclick = () => {
        state.model = item.model;
        state.messages = [];
        document.querySelectorAll(".model-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById("title").textContent = "Chat - " + item.label;
        statusEl.innerHTML = `<span class="ok">Ready</span><br>${esc(item.model)}`;
      };
      wrap.appendChild(btn);
    });
    statusEl.innerHTML = data.ollama
      ? `<span class="ok">Ollama online</span><br>${esc(state.model)}`
      : `<span class="bad">Ollama not reachable</span>`;
  } catch (e) {
    statusEl.innerHTML = `<span class="bad">Error: ${esc(e.message)}</span>`;
  }
}

async function send() {
  const text = promptBox.value.trim();
  if (!text && !state.attachedImage) return;
  if (isVisionModel(state.model) && !state.attachedImage) {
    addMessage("ai", "System", "This model is best for screenshots/images. Attach a screenshot with Shot or Ctrl+V, or choose DeepSeek R1 / Qwen Coder / Mistral for normal text chat.");
    return;
  }
  promptBox.value = "";
  const displayText = text || "What should I understand from this screenshot?";
  addMessage("user", "", state.attachedImage ? `${displayText}\n\n[Screen image attached]` : displayText);
  statusEl.textContent = "Generating...";
  const userMessage = {role: "user", content: displayText};
  if (state.attachedImage) {
    userMessage.images = [state.attachedImage];
  }
  state.messages.push(userMessage);

  if (state.askAll) {
    try {
      const data = await apiPost("/api/panel", {prompt: displayText, context: state.context});
      data.results.forEach(r => addMessage("ai", r.model, r.response));
    } catch (e) {
      addMessage("ai", "System", "Error: " + e.message);
    }
    statusEl.innerHTML = `<span class="ok">Ready</span>`;
    clearAttachedImage();
    return;
  }

  const span = addMessage("ai", state.model, "");
  let full = "";
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({model: state.model, messages: state.messages, context: state.context})
    });
    if (!res.ok) {
      throw new Error(await res.text());
    }
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    let buf = "";
    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      buf += dec.decode(value, {stream: true});
      const lines = buf.split("\n");
      buf = lines.pop();
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const raw = line.slice(6).trim();
        if (raw === "[DONE]") break;
        try {
          const parsed = JSON.parse(raw);
          if (parsed.token) {
            full += parsed.token;
            span.textContent = full;
            chat.scrollTop = chat.scrollHeight;
          }
          if (parsed.error) {
            span.textContent = "Error: " + parsed.error;
          }
        } catch {}
      }
    }
    state.messages.push({role: "assistant", content: full});
  } catch (e) {
    span.textContent = "Error: " + friendlyError(e);
  }
  clearAttachedImage();
  statusEl.innerHTML = `<span class="ok">Ready</span><br>${esc(state.model)}`;
}

function friendlyError(e) {
  const msg = String(e && e.message ? e.message : e);
  if (/network|fetch/i.test(msg)) {
    return "connection dropped. Check that Ollama is running, then try a text model like DeepSeek R1. If you selected Moondream or Qwen Vision, attach a screenshot first.";
  }
  return msg;
}

function getActions() {
  try {
    const saved = JSON.parse(localStorage.getItem("freeAiWorkbenchActions") || "null");
    if (Array.isArray(saved) && saved.length) return saved.slice(0, 12);
  } catch {}
  return DEFAULT_ACTIONS;
}

function saveActions(actions) {
  localStorage.setItem("freeAiWorkbenchActions", JSON.stringify(actions.slice(0, 12)));
}

function renderActions() {
  const wrap = document.getElementById("actionButtons");
  wrap.innerHTML = "";
  getActions().forEach(action => {
    const btn = document.createElement("button");
    btn.className = "step-btn";
    btn.innerHTML = `<span>${esc(action.label || "Untitled action")}</span><small>${esc(action.tag || "custom")}</small>`;
    btn.onclick = () => {
      promptBox.value = action.prompt || "";
      promptBox.focus();
    };
    wrap.appendChild(btn);
  });
}

function customizeActions() {
  const current = JSON.stringify(getActions(), null, 2);
  const edited = window.prompt(
    "Customize action buttons. Edit labels/tags/prompts as JSON. Keep 1-12 actions.",
    current
  );
  if (edited === null) return;
  try {
    const parsed = JSON.parse(edited);
    if (!Array.isArray(parsed)) throw new Error("Use a JSON array.");
    const cleaned = parsed.slice(0, 12).map((item, i) => ({
      label: String(item.label || `Action ${i + 1}`),
      tag: String(item.tag || "custom"),
      prompt: String(item.prompt || ""),
    }));
    saveActions(cleaned);
    renderActions();
    out.textContent = "Custom actions saved in this browser.";
  } catch (e) {
    out.textContent = "Could not save actions: " + e.message;
  }
}

function attachImageData(dataUrl, name="screenshot") {
  const base64 = dataUrl.includes(",") ? dataUrl.split(",").pop() : dataUrl;
  state.attachedImage = base64;
  state.attachedImageName = name;
  document.getElementById("previewImg").src = dataUrl;
  document.getElementById("previewText").textContent = `${name} attached. Ask what you want to understand.`;
  document.getElementById("imagePreview").classList.add("visible");
  document.getElementById("shotBtn").classList.add("has-image");
  if (!promptBox.value.trim()) {
    promptBox.value = "Explain what is on this screen and what I should do next.";
  }
}

function clearAttachedImage() {
  state.attachedImage = null;
  state.attachedImageName = "";
  document.getElementById("imagePreview").classList.remove("visible");
  document.getElementById("previewImg").removeAttribute("src");
  document.getElementById("shotBtn").classList.remove("has-image");
}

async function captureScreen() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
    out.textContent = "Screen capture is not available in this browser. Use Print Screen or Snipping Tool, then paste here with Ctrl+V.";
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getDisplayMedia({video: true});
    const video = document.createElement("video");
    video.srcObject = stream;
    await video.play();
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    stream.getTracks().forEach(track => track.stop());
    attachImageData(canvas.toDataURL("image/png"), "screen capture");
  } catch (e) {
    out.textContent = "Screen capture canceled. You can still use Snipping Tool, copy the image, then paste it into the app.";
  }
}

async function fileAction(action) {
  const path = document.getElementById("filePath").value.trim();
  const instruction = document.getElementById("fileInstruction").value;
  if (!path) { out.textContent = "Add a path first."; return; }
  out.textContent = "Working...";
  try {
    const data = await apiPost("/api/file", {action, path, instruction, model: state.model});
    out.textContent = data.output || data.message || "Done.";
  } catch (e) {
    out.textContent = "Error: " + e.message;
  }
}

async function listFiles() {
  out.textContent = "Loading...";
  try {
    const data = await apiPost("/api/list", {path: document.getElementById("listPath").value || "."});
    out.textContent = data.items.join("\n");
  } catch (e) {
    out.textContent = "Error: " + e.message;
  }
}

async function gitStatus() {
  out.textContent = "Checking...";
  try {
    const data = await apiPost("/api/run", {command: "git status --short"});
    out.textContent = data.output || "(clean)";
  } catch (e) {
    out.textContent = "Error: " + e.message;
  }
}

async function windowsAction(action) {
  out.textContent = "Running " + action + "...";
  try {
    const data = await apiPost("/api/windows", {action});
    out.textContent = data.output || data.message || "Done.";
  } catch (e) {
    out.textContent = "Error: " + e.message;
  }
}

async function runSetup(openOnly=false) {
  const folder = document.getElementById("setupFolder").value.trim() || "AI-Stack-MVP";
  out.textContent = openOnly ? "Opening MVP folder..." : "Creating MVP kit...";
  try {
    const data = await apiPost(openOnly ? "/api/open-folder" : "/api/setup", {folder});
    out.textContent = data.output || data.message || "Done.";
  } catch (e) {
    out.textContent = "Error: " + e.message;
  }
}

function setContext() {
  const ctx = document.getElementById("ctxText").value.trim();
  state.context = ctx;
  state.messages = [];
  const label = ctx ? `Framing active (${ctx.length} chars) - conversation reset` : "No framing";
  document.getElementById("ctxStatus").innerHTML = ctx
    ? `<span class="ok">${esc(label)}</span>`
    : `<span class="warn">Framing cleared</span>`;
  ctxLabel.innerHTML = ctx ? `<span class="ctx-badge">Framing loaded</span>` : "";
}

document.getElementById("quickCtx").onchange = function() {
  const val = this.value;
  if (val !== "custom") {
    document.getElementById("ctxText").value = QUICK_CONTEXTS[val] || "";
  }
};
document.getElementById("setCtxBtn").onclick = setContext;
document.getElementById("clearCtxBtn").onclick = () => {
  document.getElementById("ctxText").value = "";
  document.getElementById("quickCtx").value = "none";
  state.context = "";
  state.messages = [];
  document.getElementById("ctxStatus").innerHTML = `<span class="warn">Framing cleared</span>`;
  ctxLabel.innerHTML = "";
};

document.getElementById("sendBtn").onclick = send;
document.getElementById("clearBtn").onclick = () => { state.messages = []; chat.innerHTML = ""; };
promptBox.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
document.getElementById("oneMode").onclick = () => {
  state.askAll = false;
  document.getElementById("oneMode").classList.add("active");
  document.getElementById("allMode").classList.remove("active");
};
document.getElementById("allMode").onclick = () => {
  state.askAll = true;
  document.getElementById("allMode").classList.add("active");
  document.getElementById("oneMode").classList.remove("active");
};
document.getElementById("readBtn").onclick = () => fileAction("read");
document.getElementById("createBtn").onclick = () => fileAction("create");
document.getElementById("editBtn").onclick = () => fileAction("edit");
document.getElementById("appendBtn").onclick = () => fileAction("append");
document.getElementById("listBtn").onclick = listFiles;
document.getElementById("gitBtn").onclick = gitStatus;
document.getElementById("setupBtn").onclick = () => runSetup(false);
document.getElementById("openMvpBtn").onclick = () => runSetup(true);
document.getElementById("auditBtn").onclick = () => windowsAction("audit_stack");
document.getElementById("checkerBtn").onclick = () => windowsAction("run_checker");
document.getElementById("openRepoTopBtn").onclick = () => windowsAction("open_repo");
document.getElementById("openMvpTopBtn").onclick = () => windowsAction("open_mvp");
document.getElementById("openRepoBtn").onclick = () => windowsAction("open_repo");
document.getElementById("shortcutBtn").onclick = () => windowsAction("create_shortcut");
document.getElementById("ollamaBtn").onclick = () => windowsAction("ollama_list");
document.getElementById("openMvpWinBtn").onclick = () => windowsAction("open_mvp");
document.getElementById("shotBtn").onclick = captureScreen;
document.getElementById("removeImageBtn").onclick = clearAttachedImage;
document.getElementById("bigCheckerBtn").onclick = () => windowsAction("run_checker");
document.getElementById("customizeActionsBtn").onclick = customizeActions;
renderActions();

window.addEventListener("paste", e => {
  const items = e.clipboardData && e.clipboardData.items ? Array.from(e.clipboardData.items) : [];
  const imageItem = items.find(item => item.type && item.type.startsWith("image/"));
  if (!imageItem) return;
  const file = imageItem.getAsFile();
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => attachImageData(reader.result, file.name || "pasted screenshot");
  reader.readAsDataURL(file);
});

function setupResizer(gutterId, side) {
  const gutter = document.getElementById(gutterId);
  if (!gutter) return;
  gutter.addEventListener("pointerdown", e => {
    gutter.setPointerCapture(e.pointerId);
    const startX = e.clientX;
    const styles = getComputedStyle(document.documentElement);
    const startLeft = parseInt(styles.getPropertyValue("--left-w")) || 248;
    const startRight = parseInt(styles.getPropertyValue("--right-w")) || 340;
    function move(ev) {
      const dx = ev.clientX - startX;
      if (side === "left") {
        const next = Math.max(220, Math.min(420, startLeft + dx));
        document.documentElement.style.setProperty("--left-w", next + "px");
      } else {
        const next = Math.max(300, Math.min(560, startRight - dx));
        document.documentElement.style.setProperty("--right-w", next + "px");
      }
    }
    function up() {
      gutter.removeEventListener("pointermove", move);
      gutter.removeEventListener("pointerup", up);
    }
    gutter.addEventListener("pointermove", move);
    gutter.addEventListener("pointerup", up);
  });
}
setupResizer("leftGutter", "left");
setupResizer("rightGutter", "right");

let recognition = null;
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const voiceBtn = document.getElementById("voiceBtn");
if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = true;
  recognition.continuous = false;
  recognition.onstart = () => voiceBtn.classList.add("recording");
  recognition.onend = () => voiceBtn.classList.remove("recording");
  recognition.onresult = event => {
    let text = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      text += event.results[i][0].transcript;
    }
    promptBox.value = text;
  };
  voiceBtn.onclick = () => recognition.start();
} else {
  voiceBtn.onclick = () => alert("Browser speech not available. Click the text box and press Win+H.");
}

loadModels();
document.getElementById("title").textContent = "Chat - DeepSeek R1";
</script>
</body>
</html>
"""


def json_bytes(data: object) -> bytes:
    return json.dumps(data, indent=2).encode("utf-8")


def read_body(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0"))
    if not length:
        return {}
    return json.loads(handler.rfile.read(length).decode("utf-8"))


def installed_models() -> list[str]:
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
    except Exception:
        return []


def safe_path(raw: str) -> Path:
    raw = raw.strip() or "."
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def build_system_prompt(context: str) -> str:
    if context and context.strip():
        return BASE_SYSTEM_PROMPT + "\n\nCONTEXT PROVIDED BY USER:\n" + context.strip()
    return BASE_SYSTEM_PROMPT


def call_model_sync(model: str, messages: list[dict], context: str = "") -> str:
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": build_system_prompt(context)}] + messages,
        "stream": False,
        "options": {"num_predict": 900},
    }
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=600) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("message", {}).get("content", "").strip()


def create_or_edit_with_model(model: str, path: Path, instruction: str, existing: str | None) -> str:
    if existing is None:
        prompt = (
            "Create the full file content for this request. "
            "Return only the file content, no markdown fence.\n\n"
            f"Path: {path.name}\nInstruction: {instruction}"
        )
    else:
        prompt = (
            "Rewrite this file according to the instruction. "
            "Return only the full replacement file content, no markdown fence.\n\n"
            f"Path: {path.name}\nInstruction: {instruction}\n\nCurrent file:\n{existing}"
        )
    return call_model_sync(model, [{"role": "user", "content": prompt}])


def write_if_missing_or_update(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def build_mvp_kit(folder_name: str) -> dict:
    safe_name = "".join(c for c in (folder_name or "AI-Stack-MVP") if c.isalnum() or c in ("-", "_", " ")).strip()
    if not safe_name:
        safe_name = "AI-Stack-MVP"
    root = (REPO_ROOT / safe_name).resolve()
    if REPO_ROOT not in root.parents and root != REPO_ROOT:
        raise ValueError("MVP folder must stay inside the AI-TOOL workspace.")

    today = _dt.date.today().isoformat()
    files: dict[str, str] = {
        "README.md": f"""# AI Stack MVP

Prepared: {today}

This is a free-first local AI workbench MVP. The idea is simple:

1. Use a small paid API budget only for setup, testing, or cloud-only tasks.
2. Run daily work on local Ollama models for free.
3. Keep API keys private in local env files.
4. Give users click-first workflows for chat, files, and starter automations.

## What It Does

- Local chat with Ollama models such as DeepSeek, Qwen, Mistral, and Moondream.
- Optional API key slots for OpenAI, Anthropic, Gemini, Groq, OpenRouter, DeepSeek, and xAI.
- Starter automations for notes, summaries, job packets, learning plans, and business playbooks.
- Safe file workspace with generated content stored locally.

## Quick Start

```powershell
cd "{root}"
copy .env.example .env.local
notepad .env.local
.\\scripts\\start-free-stack.ps1
```

## Handshake Pitch

I built a local AI workbench that starts with a small optional API budget for setup but runs day-to-day on free local models. It gives AI learners, families, veterans, and builders a practical AI stack for chat, screenshot context, file work, business planning, and starter automations without needing to memorize terminal commands.
""",
        ".env.example": """# AI Stack MVP environment template
# Copy this file to .env.local and fill only the services you use.

# Free/local first
OLLAMA_URL=http://localhost:11434
DEFAULT_LOCAL_MODEL=deepseek-r1:8b
WORKSPACE_DIR=./workspace

# Optional paid/cloud APIs. Leave blank if unused.
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=
DEEPSEEK_API_KEY=
XAI_API_KEY=

# Optional app integrations
GITHUB_TOKEN=
NOTION_TOKEN=
SLACK_BOT_TOKEN=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Safety defaults
ALLOW_SHELL_COMMANDS=false
ALLOW_FILE_OVERWRITE=false
""",
        ".env.local": """# Local secrets live here. Do not commit this file.
OLLAMA_URL=http://localhost:11434
DEFAULT_LOCAL_MODEL=deepseek-r1:8b
WORKSPACE_DIR=./workspace

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=
DEEPSEEK_API_KEY=
XAI_API_KEY=

ALLOW_SHELL_COMMANDS=false
ALLOW_FILE_OVERWRITE=false
""",
        ".gitignore": """.env
.env.local
*.log
workspace/private/
__pycache__/
.venv/
""",
        "scripts/start-free-stack.ps1": """Set-Location -LiteralPath $PSScriptRoot\\..
Write-Host "AI Stack MVP - free/local mode"
Write-Host "Checking Ollama..."
try {
  $models = ollama list
  Write-Host $models
} catch {
  Write-Host "Ollama is not available. Install Ollama, then run: ollama pull deepseek-r1:8b"
}
Write-Host ""
Write-Host "Suggested starter models:"
Write-Host "  ollama pull deepseek-r1:8b"
Write-Host "  ollama pull qwen2.5-coder:7b"
Write-Host "  ollama pull mistral:latest"
Write-Host ""
Write-Host "Open the main workbench from the parent AI-TOOL repo:"
Write-Host "  ..\\local-ai-workbench.ps1"
""",
        "automations/starter_automations.py": '''"""
Starter automations for AI Stack MVP.

These are intentionally simple and local. They do not require paid APIs.
"""

from pathlib import Path
import datetime as dt

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workspace"


def ensure_workspace() -> None:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    (WORKSPACE / "notes").mkdir(exist_ok=True)
    (WORKSPACE / "outputs").mkdir(exist_ok=True)


def daily_note(topic: str = "AI stack progress") -> Path:
    ensure_workspace()
    path = WORKSPACE / "notes" / f"{dt.date.today().isoformat()}-daily-note.md"
    if not path.exists():
        path.write_text(f"# Daily Note - {dt.date.today().isoformat()}\\n\\n## Topic\\n{topic}\\n\\n## Wins\\n- \\n\\n## Next Actions\\n- \\n", encoding="utf-8")
    return path


def business_playbook(name: str) -> Path:
    ensure_workspace()
    slug = "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    path = WORKSPACE / "outputs" / f"{slug}-playbook.md"
    path.write_text(f"""# {name} Playbook

## Goal

## Audience

## Offer

## Workflow

## Automations

## Metrics

## Next 7 Days
- 
""", encoding="utf-8")
    return path


if __name__ == "__main__":
    ensure_workspace()
    print("Created:", daily_note())
    print("Created:", business_playbook("AI Stack MVP"))
''',
        "showcase/HANDSHAKE_SHOWCASE.md": """# AI Stack MVP - Handshake Showcase Draft

## Project Title

Free-First Local AI Workbench

## One-Liner

A local AI stack that starts with a small API budget for setup, then runs daily work on free local models with a clean click-first interface.

## Problem

Most AI learners and small builders either pay for every AI interaction or get stuck in terminal-heavy local AI workflows. I wanted a human-friendly bridge: local/private/free for daily use, with optional API keys when a cloud model is worth it.

## What I Built

- Browser-based local AI workbench.
- Ollama model selector for DeepSeek, Qwen, Mistral, and vision models.
- Ask one model or compare all local models.
- AI framing presets for business, finance, engineering, marketing, writing, data analytics, research, career, creative work, astrology/reflection, and custom projects.
- File actions for reading, creating, editing, and appending local files.
- Starter MVP generator that creates env files, scripts, automations, and showcase copy.

## Why It Matters

This gives people a practical AI operating system without requiring a subscription for every task. Paid APIs become optional accelerators, not the foundation.

## Stack

- Python
- Local HTTP server
- Ollama
- PowerShell launch scripts
- Local Markdown/JSON workspace

## Next Steps

- Safer file preview before overwrite.
- Drag-and-drop files.
- Screenshot/image input for vision models.
- Stack audit tools to cut stale files, confusing flows, and personal clutter before sharing.
- GitHub publishing flow.
- More starter automations for school, job search, and small business.
""",
        "workspace/README.md": """# Workspace

Generated notes, drafts, playbooks, and automation outputs go here.

Keep private files in `workspace/private/`.
""",
    }

    created = []
    for rel, content in files.items():
        path = root / rel
        write_if_missing_or_update(path, content)
        created.append(str(path.relative_to(REPO_ROOT)))
    return {"root": str(root), "created": created}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        return

    def send_json(self, data: object, status: int = 200) -> None:
        body = json_bytes(data)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text: str, status: int = 200, content_type: str = "text/html; charset=utf-8") -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self.send_text(HTML)
        elif parsed.path == "/api/models":
            models = installed_models()
            aliases = [
                {
                    "label": label,
                    "model": model,
                    "speed": speed,
                    "installed": model in models,
                }
                for label, (model, speed) in MODEL_ALIASES.items()
            ]
            self.send_json({"ollama": bool(models), "aliases": aliases, "models": models})
        else:
            self.send_json({"error": "not found"}, status=404)

    def do_POST(self) -> None:
        try:
            body = read_body(self)
            path = urlparse(self.path).path
            if path == "/api/chat":
                self.stream_chat(body)
            elif path == "/api/panel":
                self.panel_chat(body)
            elif path == "/api/file":
                self.handle_file(body)
            elif path == "/api/setup":
                result = build_mvp_kit(body.get("folder", "AI-Stack-MVP"))
                output = "Created AI Stack MVP kit:\n" + result["root"] + "\n\nFiles:\n" + "\n".join(result["created"])
                self.send_json({"message": "MVP kit created.", "output": output, "root": result["root"]})
            elif path == "/api/open-folder":
                folder = safe_path(body.get("folder", "AI-Stack-MVP"))
                folder.mkdir(parents=True, exist_ok=True)
                if os.name == "nt":
                    subprocess.Popen(["explorer", str(folder)])
                else:
                    subprocess.Popen(["open", str(folder)])
                self.send_json({"message": f"Opened {folder}", "output": f"Opened {folder}"})
            elif path == "/api/windows":
                self.handle_windows(body)
            elif path == "/api/list":
                folder = safe_path(body.get("path", "."))
                if not folder.exists() or not folder.is_dir():
                    self.send_json({"error": f"Not a folder: {folder}"}, status=400)
                    return
                items = []
                for p in sorted(folder.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))[:300]:
                    marker = "[dir] " if p.is_dir() else "      "
                    items.append(f"{marker}{p.name}")
                self.send_json({"items": items})
            elif path == "/api/run":
                command = body.get("command", "")
                allowed = {"git status --short", "git diff --stat", "ollama list"}
                if command not in allowed:
                    self.send_json({"error": "Only safe preset commands are enabled."}, status=400)
                    return
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", command],
                    cwd=str(REPO_ROOT),
                    text=True,
                    capture_output=True,
                    timeout=60,
                )
                self.send_json({"output": (result.stdout + result.stderr).strip(), "code": result.returncode})
            else:
                self.send_json({"error": "not found"}, status=404)
        except Exception as exc:
            self.send_json({"error": str(exc)}, status=500)

    def stream_chat(self, body: dict) -> None:
        model = body.get("model") or "deepseek-r1:8b"
        messages = body.get("messages") or []
        context = body.get("context") or ""

        payload = {
            "model": model,
            "messages": [{"role": "system", "content": build_system_prompt(context)}] + messages,
            "stream": True,
            "options": {"num_predict": 900},
        }

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        try:
            self.wfile.write(
                b'data: {"token": "Loading local model... if this is the first run, it can take a minute on CPU.\\n\\n"}\n\n'
            )
            self.wfile.flush()
            req = urllib.request.Request(
                f"{OLLAMA_URL}/api/chat",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=600) as resp:
                for raw_line in resp:
                    raw_line = raw_line.strip()
                    if not raw_line:
                        continue
                    try:
                        chunk = json.loads(raw_line.decode("utf-8"))
                    except Exception:
                        continue
                    token = chunk.get("message", {}).get("content", "")
                    done = chunk.get("done", False)
                    if token:
                        data = json.dumps({"token": token})
                        self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
                        self.wfile.flush()
                    if done:
                        self.wfile.write(b"data: [DONE]\n\n")
                        self.wfile.flush()
                        return
        except Exception as exc:
            try:
                err = json.dumps({"error": str(exc)})
                self.wfile.write(f"data: {err}\n\n".encode("utf-8"))
                self.wfile.write(b"data: [DONE]\n\n")
                self.wfile.flush()
            except Exception:
                pass

    def panel_chat(self, body: dict) -> None:
        prompt = body.get("prompt", "")
        context = body.get("context") or ""
        results = []
        for model in installed_models():
            try:
                response = call_model_sync(model, [{"role": "user", "content": prompt}], context)
            except Exception as e:
                response = f"Error: {e}"
            results.append({"model": model, "response": response})
        self.send_json({"results": results})

    def handle_file(self, body: dict) -> None:
        action = body.get("action", "")
        path = safe_path(body.get("path", ""))
        instruction = body.get("instruction", "")
        model = body.get("model") or "deepseek-r1:8b"

        if action == "read":
            if not path.exists() or not path.is_file():
                self.send_json({"error": f"Missing file: {path}"}, status=400)
                return
            self.send_json({"output": path.read_text(encoding="utf-8", errors="ignore")})
            return

        if action == "append":
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(instruction.rstrip() + "\n")
            self.send_json({"message": f"Appended to {path}", "output": path.read_text(encoding="utf-8", errors="ignore")[-4000:]})
            return

        if action == "create":
            if not instruction.strip():
                self.send_json({"error": "Add an instruction/content first."}, status=400)
                return
            content = create_or_edit_with_model(model, path, instruction, existing=None)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content.rstrip() + "\n", encoding="utf-8")
            self.send_json({"message": f"Created {path}", "output": content})
            return

        if action == "edit":
            if not path.exists() or not path.is_file():
                self.send_json({"error": f"Missing file: {path}"}, status=400)
                return
            existing = path.read_text(encoding="utf-8", errors="ignore")
            content = create_or_edit_with_model(model, path, instruction, existing=existing)
            path.write_text(content.rstrip() + "\n", encoding="utf-8")
            self.send_json({"message": f"Edited {path}", "output": content})
            return

        self.send_json({"error": f"Unknown action: {action}"}, status=400)

    def handle_windows(self, body: dict) -> None:
        action = body.get("action", "")
        if action == "open_repo":
            subprocess.Popen(["explorer", str(REPO_ROOT)])
            self.send_json({"output": f"Opened repo folder:\n{REPO_ROOT}"})
            return
        if action == "open_mvp":
            folder = REPO_ROOT / "AI-Stack-MVP"
            folder.mkdir(exist_ok=True)
            subprocess.Popen(["explorer", str(folder)])
            self.send_json({"output": f"Opened MVP folder:\n{folder}"})
            return
        if action == "create_shortcut":
            script = REPO_ROOT / "create-local-ai-workbench-shortcut.ps1"
            if not script.exists():
                self.send_json({"error": f"Missing shortcut script: {script}"}, status=400)
                return
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
                cwd=str(REPO_ROOT),
                text=True,
                capture_output=True,
                timeout=60,
            )
            self.send_json({"output": (result.stdout + result.stderr).strip(), "code": result.returncode})
            return
        if action == "audit_stack":
            sections = ["FREE AI WORKBENCH AUDIT\n", f"Root: {REPO_ROOT}\n"]
            for name, command in {
                "Git status": "git status --short",
                "Git diff summary": "git diff --stat",
                "Ollama models": "ollama list",
            }.items():
                try:
                    result = subprocess.run(
                        ["powershell", "-NoProfile", "-Command", command],
                        cwd=str(REPO_ROOT),
                        text=True,
                        capture_output=True,
                        timeout=60,
                    )
                    content = (result.stdout + result.stderr).strip() or "(no output)"
                except Exception as exc:
                    content = f"Error: {exc}"
                sections.append(f"\n## {name}\n{content}\n")

            key_paths = [
                "tools/local_ai_app.py",
                "local-ai-workbench.ps1",
                "installer/install-free-ai-workbench.ps1",
                "installer/README_INSTALLER.md",
                "AI-Stack-MVP/README.md",
                "AI-Stack-MVP/docs/SOP_LOCAL_AI_WORKBENCH.md",
                "AI-Stack-MVP/docs/CAPABILITY_INVENTORY.md",
                "AI-Stack-MVP/showcase/HANDSHAKE_SHOWCASE.md",
            ]
            sections.append("\n## Key MVP files")
            for rel in key_paths:
                p = REPO_ROOT / rel
                if p.exists():
                    sections.append(f"[ok] {rel} ({p.stat().st_size} bytes)")
                else:
                    sections.append(f"[missing] {rel}")
            sections.append(
                "\nPaste this audit into chat and ask: "
                "'What should I improve, cut, or package before sharing this MVP?'"
            )
            self.send_json({"output": "\n".join(sections)})
            return
        if action == "run_checker":
            checker = REPO_ROOT / "tools" / "free_ai_workbench_checker.py"
            if not checker.exists():
                self.send_json({"error": f"Missing checker: {checker}"}, status=400)
                return
            result = subprocess.run(
                [sys.executable, str(checker)],
                cwd=str(REPO_ROOT),
                text=True,
                capture_output=True,
                timeout=120,
            )
            output = (result.stdout + result.stderr).strip() or "No checker output."
            self.send_json({"output": output, "code": result.returncode})
            return
        if action == "ollama_list":
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", "ollama list"],
                cwd=str(REPO_ROOT),
                text=True,
                capture_output=True,
                timeout=60,
            )
            self.send_json({"output": (result.stdout + result.stderr).strip() or "No output.", "code": result.returncode})
            return
        self.send_json({"error": f"Unknown Windows action: {action}"}, status=400)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}"
    if not args.no_open:
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    print(f"Local AI Workbench running at {url}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
