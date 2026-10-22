# XTTS の合成結果（work_<名前>/audio/slideNN.wav）を点検する起動スクリプト（指南書 6.4）。
# check_asr.py（faster-whisper で聞き直して台本との CER）と voice_similarity.py（本人の参照音声との話者類似度）を
# 別プロセス（優先度 低、ウィンドウなし）で順に動かし、結果を UTF-8 のテキストに残す。
#   ondemand/work/check_xtts_asr.txt   枚ごとの CER と差分、末尾に平均・最大
#   ondemand/work/check_xtts_sim.txt   枚ごとの類似度（0.5 以上なら似ている）
#   ondemand/work/check_xtts.done      両方終わった印（時刻）
# 合成（build_xtts_full.ps1）が終わってから起動する。同時に動かすとメモリが足りない。
#
# 使い方（PowerShell）:
#   powershell -ExecutionPolicy Bypass -File scripts/ondemand/check_xtts_full.ps1              # 全枚（ASR は枚ごとにキャッシュ、再実行で続きから）
#   powershell -ExecutionPolicy Bypass -File scripts/ondemand/check_xtts_full.ps1 -Only 3,5    # 指定の枚だけ
#   powershell -ExecutionPolicy Bypass -File scripts/ondemand/check_xtts_full.ps1 -Force       # 空きメモリが少なくても起動
# 所要: 64 枚（約 45 分の音声）で 15〜30 分。終わりは check_xtts.done ができること。
param(
    [string]$Only = "",
    [string]$Narration = "materials/slides/第05回_トラバース測量I/narration.md",
    [string]$Work = "ondemand/work/work_lecture05_xtts",
    [string]$Ref = "ondemand/voice/reference/xtts_ref_01.wav",
    [string]$OutDir = "ondemand/work",
    [string]$Prefix = "check_xtts",
    [switch]$Force,
    [switch]$Inner
)
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..\..")
$py = Join-Path $env:USERPROFILE ".venvs\ondemand-tts\Scripts\python.exe"
if (-not (Test-Path $py)) { Write-Error "仮想環境が無い: $py（指南書 1 章）"; exit 1 }
if (-not (Test-Path (Join-Path $Work "audio"))) { Write-Error "合成結果が無い: $Work/audio（先に build_xtts_full.ps1）"; exit 1 }
if (-not (Test-Path $Ref)) { Write-Error "参照音声が無い: $Ref（指南書 5 章）"; exit 1 }
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$asrOut = Join-Path $OutDir "$Prefix`_asr.txt"
$simOut = Join-Path $OutDir "$Prefix`_sim.txt"
$done = Join-Path $OutDir "$Prefix.done"

if (-not $Inner) {
    $free = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB
    if ($free -lt 2.0 -and -not $Force) {
        Write-Host ("空きメモリ {0:N1} GB。whisper と speechbrain で約 1.5 GB 使うので、合成が終わり 2 GB 以上空いてから起動する（-Force で無視）" -f $free)
        exit 1
    }
    if (Test-Path $done) { Remove-Item $done }
    $argList = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $PSCommandPath, "-Inner",
                 "-Narration", $Narration, "-Work", $Work, "-Ref", $Ref, "-OutDir", $OutDir, "-Prefix", $Prefix)
    if ($Only) { $argList += @("-Only", $Only) }
    $p = Start-Process -FilePath "powershell.exe" -ArgumentList $argList -WindowStyle Hidden -PassThru
    $p.PriorityClass = "BelowNormal"
    Write-Host ("pid={0} 開始 {1:s}  結果: {2} / {3}  終わり: {4}" -f $p.Id, (Get-Date), $asrOut, $simOut, $done)
    exit 0
}

# ---- ここから別プロセス側 ----
# 1) 聞き直し（CER）。枚ごとの認識結果は <Work>/asr/ にキャッシュされ、再実行で続きから。
$a = @("scripts/ondemand/check_asr.py", "--narration", $Narration, "--work", $Work)
if ($Only) { $a += @("--only", $Only) }
$p = Start-Process -FilePath $py -ArgumentList $a -RedirectStandardOutput $asrOut -RedirectStandardError "$asrOut.err" -NoNewWindow -Wait -PassThru
$asrExit = $p.ExitCode

# 2) 話者類似度。slideNN.wav だけ（末尾無音を足した *_padded.wav は除く）。
$wavs = Get-ChildItem (Join-Path $Work "audio") -Filter "slide??.wav" | Sort-Object Name
if ($Only) {
    $want = @($Only -split "," | ForEach-Object { "slide{0:D2}.wav" -f [int]$_.Trim() })
    $wavs = $wavs | Where-Object { $want -contains $_.Name }
}
$a = @("scripts/ondemand/voice_similarity.py", "--ref", $Ref) + @($wavs | ForEach-Object { $_.FullName })
$p = Start-Process -FilePath $py -ArgumentList $a -RedirectStandardOutput $simOut -RedirectStandardError "$simOut.err" -NoNewWindow -Wait -PassThru
$simExit = $p.ExitCode

("asr exit={0} sim exit={1} {2:s}" -f $asrExit, $simExit, (Get-Date)) | Out-File -FilePath $done -Encoding utf8
