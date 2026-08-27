# Build standalone Pixicon for the current OS.
# Output: dist/Pixicon/  and a zip archive for distribution.
#
# Optional env:
#   PIXICON_ARTIFACT  - archive filename (default: Pixicon-windows-x64.zip)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

# Stop a running app so COLLECT/zip can overwrite locked files
Get-Process -Name "Pixicon" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 400

$py = if (Test-Path .\.venv\Scripts\python.exe) { ".\.venv\Scripts\python.exe" } else { "python" }

& $py -m pip install -U pip
& $py -m pip install -e .
& $py -m pip install "pyinstaller>=6.3"
& $py -m PyInstaller --noconfirm --clean packaging\pixicon.spec

$out = "dist\Pixicon"
if (-not (Test-Path "$out\Pixicon.exe")) {
    throw "Build failed: $out\Pixicon.exe not found"
}

$zipName = if ($env:PIXICON_ARTIFACT) { $env:PIXICON_ARTIFACT } else { "Pixicon-windows-x64.zip" }
$zip = "dist\$zipName"
if (Test-Path $zip) { Remove-Item $zip -Force }

try {
    Compress-Archive -Path $out -DestinationPath $zip -Force
    Write-Host "OK  zip:    $zip"
} catch {
    Write-Warning "Zip failed (files may be locked): $_"
}

Write-Host ""
Write-Host "OK  folder: $out"
Write-Host "Run:        $out\Pixicon.exe"
