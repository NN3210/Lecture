# pptx を PowerPoint（COM）で PDF と PNG に書き出す。Windows + PowerPoint が必要。
# 使い方: powershell -ExecutionPolicy Bypass -File scripts/pptx_export.ps1 -Pptx <path.pptx> [-PngDir <dir>] [-NoPng]
param(
    [Parameter(Mandatory = $true)][string]$Pptx,
    [string]$Pdf = "",
    [string]$PngDir = "",
    [switch]$NoPng
)
$Pptx = (Resolve-Path $Pptx).Path
if ($Pdf -eq "") { $Pdf = [System.IO.Path]::ChangeExtension($Pptx, ".pdf") }
$app = New-Object -ComObject PowerPoint.Application
try {
    $pres = $app.Presentations.Open($Pptx, $true, $false, $false)
    $pres.SaveAs($Pdf, 32)   # 32 = ppSaveAsPDF
    Write-Output "PDF: $Pdf ($($pres.Slides.Count) slides)"
    if (-not $NoPng) {
        if ($PngDir -eq "") { $PngDir = Join-Path (Split-Path $Pptx) "preview" }
        New-Item -ItemType Directory -Force $PngDir | Out-Null
        $pres.Export($PngDir, "PNG", 1280, 720)
        Write-Output "PNG: $PngDir"
    }
    $pres.Close()
} finally {
    $app.Quit()
}
