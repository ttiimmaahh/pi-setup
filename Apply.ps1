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
$PiLensConfigPath = if ($env:PI_LENS_CONFIG_PATH) { $env:PI_LENS_CONFIG_PATH } else { Join-Path $HOME ".pi-lens/config.json" }
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

function Install-PiLensConfig {
  $source = Join-Path $SourceDir "pi-lens/config.json"
  if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
    return
  }

  if (Test-Path -LiteralPath $PiLensConfigPath) {
    $backup = Join-Path $BackupDir "pi-lens/config.json"
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backup) | Out-Null
    Copy-Item -LiteralPath $PiLensConfigPath -Destination $backup -Force
  }

  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $PiLensConfigPath) | Out-Null
  Copy-Item -LiteralPath $source -Destination $PiLensConfigPath -Force
  Write-Host "  installed Pi Lens config -> $PiLensConfigPath"
}

function Install-WebToolsDependencies {
  $extensionDir = Join-Path $PiDir "extensions/web-tools"
  $lockfile = Join-Path $extensionDir "package-lock.json"
  if (-not (Test-Path -LiteralPath $lockfile -PathType Leaf)) {
    return
  }

  $npmCommand = Get-Command npm -ErrorAction SilentlyContinue
  if ($null -eq $npmCommand) {
    throw "npm is required to install the web-tools extension dependencies."
  }

  Write-Host "  installing extensions/web-tools dependencies"
  & $npmCommand.Source ci --omit=dev --omit=peer --ignore-scripts --prefix $extensionDir
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to install the web-tools extension dependencies."
  }
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
Install-File "pi-usage-bar/config.json"

Install-Directory "prompts"
Install-Directory "extensions"
Install-Directory "skills"
Install-Directory "themes"
Install-PiLensConfig
Install-WebToolsDependencies

$macropadSource = Join-Path $SourceDir "macropad"
$macropadTarget = Join-Path $HOME ".config/ch57x-keyboard-tool"
if (Test-Path -LiteralPath $macropadSource -PathType Container) {
  New-Item -ItemType Directory -Force -Path $macropadTarget | Out-Null
  foreach ($filename in @("coding-voice.yaml", "coding-voice-ctrl-only-fallback.yaml", "CHEATSHEET.md")) {
    $source = Join-Path $macropadSource $filename
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { continue }
    $target = Join-Path $macropadTarget $filename
    if (Test-Path -LiteralPath $target -PathType Leaf) {
      $backupTarget = Join-Path $BackupDir "external/ch57x-keyboard-tool/$filename"
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupTarget) | Out-Null
      Copy-Item -LiteralPath $target -Destination $backupTarget -Force
    }
    Copy-Item -LiteralPath $source -Destination $target -Force
    Write-Host "  installed ~/.config/ch57x-keyboard-tool/$filename"
  }
}

$alacrittyAdapterSource = Join-Path $macropadSource "alacritty-f13-adapter.toml"
$alacrittyInstaller = Join-Path $ScriptDir "scripts/install_alacritty_macropad_adapter.js"
if (
  (Test-Path -LiteralPath $alacrittyAdapterSource -PathType Leaf) -and
  (Test-Path -LiteralPath $alacrittyInstaller -PathType Leaf)
) {
  $nodeCommand = Get-Command node -ErrorAction SilentlyContinue
  if ($null -eq $nodeCommand) {
    Write-Warning "Node.js is required to install the Alacritty macropad adapter."
  } else {
    $appDataDir = if ($env:APPDATA) { $env:APPDATA } else { Join-Path $HOME "AppData/Roaming" }
    $alacrittyDir = Join-Path $appDataDir "alacritty"
    & $nodeCommand.Source $alacrittyInstaller `
      --source $alacrittyAdapterSource `
      --adapter (Join-Path $alacrittyDir "macropad-f13-adapter.toml") `
      --config (Join-Path $alacrittyDir "alacritty.toml") `
      --backup-dir (Join-Path $BackupDir "external/alacritty")
    if ($LASTEXITCODE -ne 0) {
      throw "Failed to install the Alacritty macropad adapter."
    }
  }
}

$claudeKeybindingsSource = Join-Path $macropadSource "claude-keybindings.json"
if (Test-Path -LiteralPath $claudeKeybindingsSource -PathType Leaf) {
  $claudeDir = Join-Path $HOME ".claude"
  $claudeKeybindingsTarget = Join-Path $claudeDir "keybindings.json"
  New-Item -ItemType Directory -Force -Path $claudeDir | Out-Null
  if (Test-Path -LiteralPath $claudeKeybindingsTarget -PathType Leaf) {
    $backupTarget = Join-Path $BackupDir "external/claude/keybindings.json"
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $backupTarget) | Out-Null
    Copy-Item -LiteralPath $claudeKeybindingsTarget -Destination $backupTarget -Force
  }
  Copy-Item -LiteralPath $claudeKeybindingsSource -Destination $claudeKeybindingsTarget -Force
  Write-Host "  installed Claude Code macropad bindings"
}

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
