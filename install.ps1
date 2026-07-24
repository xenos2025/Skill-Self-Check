# Install skill-self-check into Cursor personal skills (default) or a project.
# Usage:
#   ./install.ps1
#   ./install.ps1 -Project .
#   ./install.ps1 -Dest "$HOME\.cursor\skills\skill-self-check"

param(
    [string]$Dest = "",
    [string]$Project = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Src = Join-Path $Root "skills\skill-self-check"

if (-not (Test-Path $Src)) {
    throw "Missing skills/skill-self-check at $Src"
}

if ($Dest -eq "" -and $Project -ne "") {
    $Dest = Join-Path (Resolve-Path $Project) ".cursor\skills\skill-self-check"
}
elseif ($Dest -eq "") {
    $Dest = Join-Path $HOME ".cursor\skills\skill-self-check"
}

$DestParent = Split-Path -Parent $Dest
New-Item -ItemType Directory -Force -Path $DestParent | Out-Null

if ((Test-Path $Dest) -and -not $Force) {
    throw "Destination exists: $Dest (pass -Force to overwrite)"
}

if (Test-Path $Dest) {
    Remove-Item -Recurse -Force $Dest
}

Copy-Item -Recurse $Src $Dest
Write-Host "Installed skill-self-check -> $Dest"
Write-Host "Requires Python 3.10+ (stdlib only). Try:"
Write-Host "  python `"$Dest\scripts\hard_gates.py`" path\to\your-skill --pretty"
