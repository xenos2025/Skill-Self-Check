# Install skill-self-check + skill-ship-safety into Cursor personal skills
# (default) or a project.
# Usage:
#   ./install.ps1
#   ./install.ps1 -Project .
#   ./install.ps1 -Dest "$HOME\.cursor\skills\skill-self-check"   # single skill, legacy
#   ./install.ps1 -Skills skill-self-check                        # pick skills

param(
    [string]$Dest = "",
    [string]$Project = "",
    [string[]]$Skills = @("skill-self-check", "skill-ship-safety"),
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Dest -ne "") {
    # Legacy single-destination mode: install the first requested skill only.
    $Skills = @($Skills[0])
}

if ($Dest -eq "" -and $Project -ne "") {
    $Base = Join-Path (Resolve-Path $Project) ".cursor\skills"
}
elseif ($Dest -eq "") {
    $Base = Join-Path $HOME ".cursor\skills"
}

foreach ($Skill in $Skills) {
    $Src = Join-Path $Root "skills\$Skill"
    if (-not (Test-Path $Src)) {
        throw "Missing skills/$Skill at $Src"
    }

    $Target = if ($Dest -ne "") { $Dest } else { Join-Path $Base $Skill }

    $TargetParent = Split-Path -Parent $Target
    New-Item -ItemType Directory -Force -Path $TargetParent | Out-Null

    if ((Test-Path $Target) -and -not $Force) {
        throw "Destination exists: $Target (pass -Force to overwrite)"
    }

    if (Test-Path $Target) {
        Remove-Item -Recurse -Force $Target
    }

    Copy-Item -Recurse $Src $Target
    Write-Host "Installed $Skill -> $Target"
}

Write-Host "Requires Python 3.10+ (stdlib only). Try:"
Write-Host "  python `"$HOME\.cursor\skills\skill-self-check\scripts\hard_gates.py`" path\to\your-skill --pretty"
Write-Host "  python `"$HOME\.cursor\skills\skill-ship-safety\scripts\ship_safety.py`" path\to\your-skill --pretty"
