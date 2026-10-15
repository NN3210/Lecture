# PowerPointで補足スライドを読み取り専用で開き、PDF・確認画像を保存する。
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$folder=Join-Path $root 'materials\slides\第02回_測量の基礎と誤差論\補足_分散の定義と導出_20261015'
$app=New-Object -ComObject PowerPoint.Application
$deck=$app.Presentations.Open((Join-Path $folder '分散の定義と導出_補足スライド.pptx'),$true,$false,$false)
try {
    $preview=Join-Path $folder 'preview'
    New-Item -ItemType Directory -Force -Path $preview | Out-Null
    $deck.Export($preview,'PNG',1600,900)
    $deck.SaveAs((Join-Path $folder '分散の定義と導出_補足スライド.pdf'),32)
    $issues=@()
    foreach($slide in $deck.Slides){
        foreach($shape in $slide.Shapes){
            if($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1){
                $tr=$shape.TextFrame2.TextRange
                if($tr.BoundWidth -gt ($shape.Width+3) -or $tr.BoundHeight -gt ($shape.Height+3)){
                    $issues+=@{slide=$slide.SlideIndex;shape=$shape.Id;text=$tr.Text;boundWidth=$tr.BoundWidth;width=$shape.Width;boundHeight=$tr.BoundHeight;height=$shape.Height}
                }
            }
        }
    }
    @{slides=$deck.Slides.Count;renderer='Microsoft PowerPoint';textBoundsIssues=$issues}|ConvertTo-Json -Depth 5|Set-Content -Encoding utf8 (Join-Path $folder 'build\powerpoint_validation.json')
    Write-Output "PowerPoint出力: $($deck.Slides.Count)枚、文字範囲の指摘 $($issues.Count)件"
} finally {$deck.Close()}
