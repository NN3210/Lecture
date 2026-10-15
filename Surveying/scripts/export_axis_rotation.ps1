# 対象の補足資料だけを読み取り専用で開き、PDFと全ページのPNGを保存する。
param([Parameter(Mandatory=$true)][string]$Pptx)
$ErrorActionPreference = 'Stop'
$Pptx = (Resolve-Path -LiteralPath $Pptx).Path
$folder = Split-Path -LiteralPath $Pptx
$pdf = [System.IO.Path]::ChangeExtension($Pptx,'.pdf')
$pngDir = Join-Path $folder 'preview'
$app = $null
$pres = $null
$createdApp = $false
try {
    try { $app = [Runtime.InteropServices.Marshal]::GetActiveObject('PowerPoint.Application') }
    catch { $app = New-Object -ComObject PowerPoint.Application; $createdApp = $true }
    $pres = $app.Presentations.Open($Pptx,$true,$false,$false)
    $pres.SaveAs($pdf,32)
    New-Item -ItemType Directory -Force -Path $pngDir | Out-Null
    $pres.Export($pngDir,'PNG',1280,720)
    Write-Output "Slides: $($pres.Slides.Count)"
} finally {
    if ($null -ne $pres) { $pres.Close() }
    if ($createdApp -and $null -ne $app -and $app.Presentations.Count -eq 0) { $app.Quit() }
}
if (-not (Test-Path -LiteralPath $pdf)) { throw 'PDF export failed' }
