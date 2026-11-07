$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python environment creation failed.' }
}
$ewbPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $ewbPython -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) { throw 'Build dependencies failed to install.' }
& $ewbPython -m PyInstaller --noconfirm --clean Workbench.spec
if ($LASTEXITCODE -ne 0) { throw 'Executable build failed.' }
Copy-Item README.zh-CN.md dist\EgressWorkbench\README.zh-CN.md -Force
Copy-Item ..\LICENSE dist\EgressWorkbench\LICENSE -Force
Copy-Item THIRD_PARTY_NOTICES.md dist\EgressWorkbench\THIRD_PARTY_NOTICES.md -Force
Compress-Archive -Path dist\EgressWorkbench\* -DestinationPath dist\Egress-Workbench-Windows-x64-0.2.0-Portable.zip -Force
$iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
$ewbIscc = if ($iscc) { $iscc.Source } else { "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe" }
if (-not (Test-Path $ewbIscc)) { throw 'Install Inno Setup 6 to build the setup executable.' }
& $ewbIscc Installer.iss
if ($LASTEXITCODE -ne 0) { throw 'Windows setup build failed.' }
Get-ChildItem dist -File | Where-Object { $_.Extension -in '.zip','.exe' } | ForEach-Object {
    $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower()
    [IO.File]::WriteAllText($_.FullName + '.sha256', "$hash  $($_.Name)`n", [Text.UTF8Encoding]::new($false))
}
