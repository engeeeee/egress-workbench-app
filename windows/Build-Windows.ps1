$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python virtual environment creation failed.' }
}
$ewbPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $ewbPython -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw 'Build dependencies failed to install.' }
& $ewbPython -m PyInstaller --noconfirm --clean --onedir --windowed --name EgressWorkbench --add-data 'containers;containers' --collect-all tzdata entry.py
if ($LASTEXITCODE -ne 0) { throw 'GUI executable build failed.' }
& $ewbPython -m PyInstaller --noconfirm --clean --onedir --console --name ewb --add-data 'containers;containers' --collect-all tzdata entry.py
if ($LASTEXITCODE -ne 0) { throw 'CLI executable build failed.' }
Copy-Item README.zh-CN.md dist\README.zh-CN.md -Force
Copy-Item ..\LICENSE dist\LICENSE -Force
Copy-Item THIRD_PARTY_NOTICES.md dist\THIRD_PARTY_NOTICES.md -Force
Compress-Archive -Path dist\EgressWorkbench,dist\ewb,dist\README.zh-CN.md,dist\LICENSE,dist\THIRD_PARTY_NOTICES.md -DestinationPath dist\Egress-Workbench-Windows-x64-0.1.0.zip -Force
Write-Output (Join-Path $PSScriptRoot 'dist\Egress-Workbench-Windows-x64-0.1.0.zip')
