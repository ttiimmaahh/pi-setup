<#
Apply this repo's portable Pi setup to the current machine.
Auth is deliberately not restored. After this runs, use `pi /login` or set
provider-specific API key environment variables as needed.

Usage:
  powershell -ExecutionPolicy Bypass -File .\Apply.ps1
  pwsh -File ./Apply.ps1
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceDir = Join-Path $ScriptDir "config"
$PiDir = if ($env:PI_CODING_AGENT_DIR) { $env:PI_CODING_AGENT_DIR } else { Join-Path $HOME ".pi/agent" }
$BackupDir = Join-Path $PiDir ("backups/" + (Get-Date -Format "yyyyMMdd-HHmmss"))

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

  throw "Python 3 was not found. Install Python 3 or run the bash apply.sh from Git Bash/WSL."
}

function Backup-IfExists {
  param([Parameter(Mandatory = $true)][string]$Path)

  if (Test-Path -LiteralPath $Path) {
    $relative = [System.IO.Path]::GetRelativePath($PiDir, $Path)
    $destination = Join-Path $BackupDir $relative
    $destinationParent = Split-Path -Parent $destination
    New-Item -ItemType Directory -Force -Path $destinationParent | Out-Null
    Copy-Item -LiteralPath $Path -Destination $destination -Recurse -Force
  }
}

function Install-File {
  param([Parameter(Mandatory = $true)][string]$Relative)

  $source = Join-Path $SourceDir $Relative
  $target = Join-Path $PiDir $Relative
  if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
    return
  }

  Backup-IfExists -Path $target
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
  Copy-Item -LiteralPath $source -Destination $target -Force
  Write-Host "  installed $Relative"
}

function Install-Directory {
  param([Parameter(Mandatory = $true)][string]$Relative)

  $source = Join-Path $SourceDir $Relative
  $target = Join-Path $PiDir $Relative
  if (-not (Test-Path -LiteralPath $source -PathType Container)) {
    return
  }

  Backup-IfExists -Path $target
  if (Test-Path -LiteralPath $target) {
    Remove-Item -LiteralPath $target -Recurse -Force
  }
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
  Copy-Item -LiteralPath $source -Destination $target -Recurse -Force
  Write-Host "  installed $Relative/"
}

if (-not (Test-Path -LiteralPath $SourceDir -PathType Container)) {
  throw "No Pi config snapshot found at $SourceDir. Run .\Export.ps1 on a configured machine first."
}

New-Item -ItemType Directory -Force -Path $PiDir | Out-Null
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

Write-Host "Pi setup: applying portable config from $SourceDir"
Write-Host "Target: $PiDir"

Install-File "settings.json"
Install-File "keybindings.json"
Install-File "models.json"
Install-File "mcp.json"
Install-File "pi-handoff-config.json"
Install-File "pi-tool-chrome/config.json"
Install-File "pi-usage-bar/config.json"

Install-Directory "prompts"
Install-Directory "extensions"
Install-Directory "skills"
Install-Directory "themes"

$python = Get-PythonCommand
$localPathChecker = Join-Path $ScriptDir "scripts/check_local_package_paths.py"
$settingsPath = Join-Path $SourceDir "settings.json"
& $python.Command @($python.Args + @($localPathChecker, $settingsPath))

$piCommand = Get-Command pi -ErrorAction SilentlyContinue
if ($null -ne $piCommand) {
  Write-Host ""
  Write-Host "Reconciling Pi package installs from settings.json..."
  & pi list *> $null
  if ($LASTEXITCODE -eq 0) {
    & pi update --extensions
    if ($LASTEXITCODE -ne 0) {
      Write-Warning "pi update --extensions failed. Check local package paths and network access."
    }
  } else {
    Write-Warning "pi is installed but 'pi list' failed. Skipping package reconciliation."
  }
} else {
  Write-Host ""
  Write-Host "Pi CLI not found. Install it first, then run: pi update --extensions"
}

Write-Host ""
Write-Host "Auth not restored by design. Re-run /login or configure API-key environment variables on this machine."
Write-Host "Existing files were backed up under: $BackupDir"
