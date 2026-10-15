# 元ファイルと数式整形版を読み取り専用で開き、表示確認用PNGを保存する。
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$folder=Join-Path $root 'materials\slides\第02回_測量の基礎と誤差論\補足_平均の誤差伝播_20261014'
$app=New-Object -ComObject PowerPoint.Application
$targets=@(
    @{Name='平均の誤差伝播_現場例追加_20261015.pptx'; Preview='before'},
    @{Name='平均の誤差伝播_現場例追加_数式整形_20261015.pptx'; Preview='after'}
)
foreach($t in $targets){
    $dest=Join-Path $root ('notes\mean_math_typesetting\'+$t.Preview)
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    $p=$app.Presentations.Open((Join-Path $folder $t.Name),$true,$false,$false)
    try {
        $p.Export($dest,'PNG',1280,720)
        Write-Output "$($t.Preview): $($p.Slides.Count)枚"
    } finally {$p.Close()}
}
