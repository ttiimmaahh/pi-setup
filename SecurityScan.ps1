<#
Run the conservative pre-commit/publication security scan.

Usage:
  powershell -ExecutionPolicy Bypass -File .\SecurityScan.ps1
  pwsh -File ./SecurityScan.ps1
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Get-PythonCommand {
  $candidates = @(
    @{ Command = "python"; Args = @() },
    @{ Command = "python3"; Args = @() },
    @{ Command = "py"; Args = @("-3") }
  )

  foreach ($candidate in $candidates) {
    $cmd = Get-Command $candidate.Command -ErrorAction SilentlyContinue
    if ($null -ne $cmd) {
      return $candidate
    }
  }

  throw "Python 3 was not found. Install Python 3 or run: bash scripts/security_scan.py from Git Bash/WSL."
}

$python = Get-PythonCommand
$script = Join-Path $ScriptDir "scripts/security_scan.py"
& $python.Command @($python.Args + @($script))
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
