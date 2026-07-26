# Install the four stable workflow, audit, safety, and scorecard skills
# (default) or a project.
# Usage:
#   ./install.ps1
#   ./install.ps1 -Project .
#   ./install.ps1 -Dest "$HOME\.cursor\skills\skill-self-check"   # single skill, legacy
#   ./install.ps1 -Skills skill-self-check                        # pick skills

param(
    [string]$Dest = "",
    [string]$Project = "",
    [string[]]$Skills = @(
        "skill-self-check",
        "skill-ship-safety",
        "agent-work-readiness",
        "skill-growth-scorecard"
    ),
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Assert-SafeTarget {
    param(
        [string]$Path,
        [string]$SkillName
    )

    $Full = [System.IO.Path]::GetFullPath($Path)
    $Comparable = $Full.TrimEnd([char[]]@('\', '/'))
    $RootPath = [System.IO.Path]::GetPathRoot($Full).TrimEnd([char[]]@('\', '/'))
    $HomePath = [System.IO.Path]::GetFullPath($HOME).TrimEnd([char[]]@('\', '/'))
    $RepoPath = [System.IO.Path]::GetFullPath($Root).TrimEnd([char[]]@('\', '/'))
    $ParentPath = [System.IO.Path]::GetFullPath((Split-Path -Parent $Full)).TrimEnd([char[]]@('\', '/'))

    foreach ($Blocked in @($RootPath, $HomePath, $RepoPath)) {
        if ($Comparable.Equals($Blocked, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Unsafe install target: $Full"
        }
    }
    if ($ParentPath.Equals($RootPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to install directly under a drive root: $Full"
    }
    if ((Split-Path -Leaf $Comparable) -ne $SkillName) {
        throw "Install target must end with the skill name '$SkillName': $Full"
    }
    return $Full
}

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
    $Target = Assert-SafeTarget -Path $Target -SkillName $Skill

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
Write-Host "  python `"$HOME\.cursor\skills\skill-self-check\scripts\run_full_audit.py`" path\to\your-skill --out-dir path\outside\the\repo --pretty"
Write-Host "  python `"$HOME\.cursor\skills\skill-self-check\scripts\hard_gates.py`" path\to\your-skill --pretty"
Write-Host "  python `"$HOME\.cursor\skills\skill-ship-safety\scripts\ship_safety.py`" path\to\your-skill --pretty"
Write-Host "  python `"$HOME\.cursor\skills\agent-work-readiness\scripts\readiness_gates.py`" path\to\work-package --pretty"
Write-Host "  python `"$HOME\.cursor\skills\skill-growth-scorecard\scripts\profile_engine.py`" --readiness readiness.json --out-html scorecard.html"
