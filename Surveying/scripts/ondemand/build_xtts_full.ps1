# 第5回の全スライドを XTTS（本人の声）で合成する起動スクリプト。
# build_video.py を別プロセス（優先度 低、ウィンドウなし）で動かし、ログを ondemand/work/build_xtts.log に残す。
# Claude Code / Codex のシェルから起動しても、シェルの制限時間やメモリ監視で止められない。
#
# 使い方（PowerShell）:
#   powershell -ExecutionPolicy Bypass -File scripts/ondemand/build_xtts_full.ps1            # 全体（途中で止まっても再実行で続きから）
#   powershell -ExecutionPolicy Bypass -File scripts/ondemand/build_xtts_full.ps1 -Only 3,5  # 指定の枚だけ作り直す
#   powershell -ExecutionPolicy Bypass -File scripts/ondemand/build_xtts_full.ps1 -Force     # 空きメモリが少なくても起動
#
# 進み具合:  (Select-String -Path ondemand/work/build_xtts.log -Pattern '^\[tts\] slide').Count   # 合成済みの枚数（64 枚で約 8〜10 時間）
# 止める:    Stop-Process -Id <pid>（pid は起動時に表示。manifest.json があるので再実行で続きから）
# 終わり:    ログ末尾の "wrote ondemand\work\lecture05_xtts.mp4" と、check_asr.py --work ondemand/work/work_lecture05_xtts で点検
param(
    [string]$Only = "",
    [switch]$Force,
    [string]$Narration = "materials/slides/第05回_トラバース測量I/narration.md",
    [string]$PngDir = "materials/slides/第05回_トラバース測量I/preview",
    [string]$Out = "ondemand/work/lecture05_xtts.mp4"
)
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..\..")
$py = Join-Path $env:USERPROFILE ".venvs\ondemand-tts\Scripts\python.exe"
if (-not (Test-Path $py)) { Write-Error "仮想環境が無い: $py（指南書 1 章）"; exit 1 }
$refs = @("ondemand/voice/reference/xtts_ref_01.wav", "ondemand/voice/reference/xtts_ref_02.wav", "ondemand/voice/reference/xtts_ref_03.wav")
foreach ($r in $refs) { if (-not (Test-Path $r)) { Write-Error "参照音声が無い: $r（指南書 5 章）"; exit 1 } }

$free = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB
if ($free -lt 2.5 -and -not $Force) {
    Write-Host ("空きメモリ {0:N1} GB。XTTS はモデルで約 3 GB 使うので、他のアプリを閉じて 2.5 GB 以上にしてから起動する（-Force で無視）" -f $free)
    exit 1
}

$env:PYTHONUTF8 = "1"
$env:COQUI_TOS_AGREED = "1"
$env:PYTHONIOENCODING = "utf-8"
New-Item -ItemType Directory -Force "ondemand/work" | Out-Null
$log = "ondemand/work/build_xtts.log"
$argList = @("scripts/ondemand/build_video.py", "--narration", $Narration, "--png-dir", $PngDir, "--out", $Out, "--engine", "xtts")
foreach ($r in $refs) { $argList += @("--ref", $r) }
if ($Only) { $argList += @("--only", $Only) }

$p = Start-Process -FilePath $py -ArgumentList $argList -RedirectStandardOutput $log -RedirectStandardError "$log.err" -WindowStyle Hidden -PassThru
$p.PriorityClass = "BelowNormal"
Write-Host ("pid={0} log={1} 開始 {2:s}" -f $p.Id, $log, (Get-Date))
Write-Host "進み具合: (Select-String -Path $log -Pattern '^\[tts\] slide').Count"
