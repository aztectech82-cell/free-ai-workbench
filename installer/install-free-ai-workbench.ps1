param(
    [string]$InstallDir = "$env:USERPROFILE\FreeAIWorkbench",
    [switch]$SkipOllamaInstall,
    [switch]$SkipModelPull,
    [string]$StarterModel = "deepseek-r1:8b"
)

$ErrorActionPreference = "Stop"

function Write-Step($message) {
    Write-Host ""
    Write-Host "==> $message" -ForegroundColor Cyan
}

function Test-Command($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

$SourceRoot = Split-Path -Parent $PSScriptRoot
$SourceApp = Join-Path $SourceRoot "tools\local_ai_app.py"
if (-not (Test-Path -LiteralPath $SourceApp)) {
    throw "Could not find source app at $SourceApp. Run this installer from inside the AI-TOOL repo."
}

Write-Step "Creating install folder"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $InstallDir "tools") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $InstallDir "workspace") | Out-Null

Write-Step "Copying app files"
Copy-Item -LiteralPath $SourceApp -Destination (Join-Path $InstallDir "tools\local_ai_app.py") -Force

@"
# Free AI Workbench local config
OLLAMA_URL=http://localhost:11434
DEFAULT_LOCAL_MODEL=$StarterModel
WORKSPACE_DIR=./workspace

# Optional paid API slots. Leave blank for free/local mode.
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=
DEEPSEEK_API_KEY=
XAI_API_KEY=
"@ | Set-Content -LiteralPath (Join-Path $InstallDir ".env.example") -Encoding UTF8

if (-not (Test-Path -LiteralPath (Join-Path $InstallDir ".env.local"))) {
    Copy-Item -LiteralPath (Join-Path $InstallDir ".env.example") -Destination (Join-Path $InstallDir ".env.local")
}

@"
# Free AI Workbench

This folder contains a local free-first AI interface.

## Start

Double-click:

`Start-FreeAIWorkbench.ps1`

Then open:

`http://127.0.0.1:8765`

## Free AI Engine

This app uses Ollama models on your computer.

Recommended starter model:

`$StarterModel`

## Notes

- No cloud API key is required for local mode.
- Optional API slots are in `.env.local`.
- Your work is saved locally in `workspace/`.
"@ | Set-Content -LiteralPath (Join-Path $InstallDir "README.md") -Encoding UTF8

@"
Set-Location -LiteralPath `$PSScriptRoot
`$port = 8765
`$existing = Get-NetTCPConnection -LocalPort `$port -ErrorAction SilentlyContinue
if (`$existing) {
    `$existing | ForEach-Object { Stop-Process -Id `$_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Milliseconds 500
}
python .\tools\local_ai_app.py
"@ | Set-Content -LiteralPath (Join-Path $InstallDir "Start-FreeAIWorkbench.ps1") -Encoding UTF8

Write-Step "Checking Python"
if (-not (Test-Command python)) {
    Write-Host "Python was not found on PATH." -ForegroundColor Yellow
    if (Test-Command winget) {
        Write-Host "Installing Python with winget..."
        winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements
    } else {
        Write-Host "Install Python from https://python.org, then run this installer again." -ForegroundColor Yellow
    }
} else {
    python --version
}

Write-Step "Checking Ollama"
if (-not (Test-Command ollama)) {
    if ($SkipOllamaInstall) {
        Write-Host "Ollama not found. Skipping install because -SkipOllamaInstall was used." -ForegroundColor Yellow
    } elseif (Test-Command winget) {
        Write-Host "Installing Ollama with winget..."
        winget install --id Ollama.Ollama -e --accept-package-agreements --accept-source-agreements
    } else {
        Write-Host "Ollama not found and winget is unavailable. Install from https://ollama.com/download" -ForegroundColor Yellow
    }
} else {
    ollama --version
}

if (-not $SkipModelPull -and (Test-Command ollama)) {
    Write-Step "Pulling starter model: $StarterModel"
    ollama pull $StarterModel
}

Write-Step "Creating desktop shortcut"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Free AI Workbench.lnk"
$target = Join-Path $InstallDir "Start-FreeAIWorkbench.ps1"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$target`""
$shortcut.WorkingDirectory = $InstallDir
$shortcut.Description = "Launch Free AI Workbench"
$shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,13"
$shortcut.Save()

Write-Step "Done"
Write-Host "Installed to: $InstallDir" -ForegroundColor Green
Write-Host "Shortcut: $shortcutPath" -ForegroundColor Green
Write-Host ""
Write-Host "Launch now:"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File `"$target`""
Write-Host ""
Write-Host "Then open:"
Write-Host "  http://127.0.0.1:8765"
