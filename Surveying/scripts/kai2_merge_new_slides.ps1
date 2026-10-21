# 第3回・改2 の組み立て（その 2）：kai2_build_pptx.py で並べ替えた土台 PPTX に、md2pptx.py で作った新規枚を
# PowerPoint（COM）の InsertFromFile で差し込み、保存する。Windows + PowerPoint が必要。
# 使い方:
#   powershell -ExecutionPolicy Bypass -File scripts/kai2_merge_new_slides.ps1 -Base <土台.pptx> -New <新規.pptx> -Plan <差し込み表.txt> -Out <出力.pptx>
# 差し込み表（タブ区切り、1 行 1 枚）: <最終的な位置（1 始まり）> <TAB> <新規.pptx の中の枚番号（1 始まり）>
#   位置の昇順に処理する（先に差し込んだ枚で後ろがずれるため、順に入れれば最終位置と一致する）。
param(
    [Parameter(Mandatory = $true)][string]$Base,
    [Parameter(Mandatory = $true)][string]$New,
    [Parameter(Mandatory = $true)][string]$Plan,
    [Parameter(Mandatory = $true)][string]$Out
)
$Base = (Resolve-Path $Base).Path
$New = (Resolve-Path $New).Path
$Out = [System.IO.Path]::GetFullPath($Out)
$rows = Get-Content -Encoding UTF8 $Plan | Where-Object { $_ -match '^\s*(\d+)\s+(\d+)\s*$' } | ForEach-Object {
    $m = [regex]::Match($_, '^\s*(\d+)\s+(\d+)\s*$')
    [pscustomobject]@{ Pos = [int]$m.Groups[1].Value; Src = [int]$m.Groups[2].Value }
} | Sort-Object Pos
$app = New-Object -ComObject PowerPoint.Application
try {
    $pres = $app.Presentations.Open($Base, $false, $false, $false)
    foreach ($r in $rows) {
        # InsertFromFile(FileName, Index, SlideStart, SlideEnd): Index の「後ろ」に入る
        $n = $pres.Slides.InsertFromFile($New, $r.Pos - 1, $r.Src, $r.Src)
        Write-Output ("inserted new#{0} at {1} ({2} slide)" -f $r.Src, $r.Pos, $n)
    }
    $pres.SaveAs($Out)
    Write-Output ("saved: {0} ({1} slides)" -f $Out, $pres.Slides.Count)
    $pres.Close()
} finally {
    $app.Quit()
}
