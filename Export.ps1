<#
Export the portable, auth-free parts of the current Pi setup into this repo.

Usage:
  powershell -ExecutionPolicy Bypass -File .\Export.ps1
  pwsh -File ./Export.ps1
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PiDir = if ($env:PI_CODING_AGENT_DIR) { $env:PI_CODING_AGENT_DIR } else { Join-Path $HOME ".pi/agent" }
$OutDir = Join-Path $ScriptDir "config"

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

  throw "Python 3 was not found. Install Python 3 or run the bash export.sh from Git Bash/WSL."
}

if (-not (Test-Path -LiteralPath $PiDir -PathType Container)) {
  throw "Pi config directory not found: $PiDir"
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$python = Get-PythonCommand
$script = Join-Path $ScriptDir "scripts/export_portable_pi_config.py"
& $python.Command @($python.Args + @($script, $PiDir, $OutDir))
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}
