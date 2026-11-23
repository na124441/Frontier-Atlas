param (
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArgs
)

$VenvDir = "C:\Users\nayan\.venv_scraper"
$VenvPy = "$VenvDir\Scripts\python.exe"
$UvPy = "C:\Users\nayan\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\python.exe"

if (Test-Path $VenvPy) {
    try {
        & $VenvPy cli.py @CliArgs
        if ($LASTEXITCODE -eq 0) { exit 0 }
    } catch {}
}

if (Test-Path $UvPy) {
    $env:VIRTUAL_ENV = $VenvDir
    $env:PYTHONPATH = "$PSScriptRoot\src;$VenvDir\Lib\site-packages"
    & $UvPy cli.py @CliArgs
    exit $LASTEXITCODE
}

Write-Error "Python interpreter not found."
exit 1
