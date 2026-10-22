# Codex (gpt-6-astra) を切り離して実行する起動スクリプト。
# 使い方: powershell -NoProfile -File run_codex_job.ps1 -PromptFile <指示.md> -LastMessage <報告.md>
# 標準入力で指示文を渡すため、$OutputEncoding を UTF-8 にする（PowerShell 5.1 の既定は ASCII）。
param(
  [Parameter(Mandatory=$true)][string]$PromptFile,
  [Parameter(Mandatory=$true)][string]$LastMessage,
  [string]$Effort = 'high'
)
$ErrorActionPreference = 'Continue'
$root = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path   # scripts/codex の 2 つ上 = AgrTechno
Set-Location $root
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
"__START__ " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + " prompt=" + $PromptFile
$prompt = Get-Content -Raw -Encoding UTF8 $PromptFile
$prompt | codex exec -m gpt-6-astra -c model_reasoning_effort=$Effort -s workspace-write -C $root --skip-git-repo-check -o $LastMessage -
"__CODEX_DONE__ exit=$LASTEXITCODE " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
