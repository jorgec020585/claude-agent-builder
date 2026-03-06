# Claude Agent Builder — Windows Install Script
# Usage: .\install.ps1 [-Project]

param(
    [switch]$Project
)

$ErrorActionPreference = "Stop"
$SkillDir = "agent-builder"

if ($Project) {
    $Target = ".claude\skills"
    Write-Host "Installing to project-level: $Target\$SkillDir" -ForegroundColor Cyan
} else {
    $Target = "$env:USERPROFILE\.claude\skills"
    Write-Host "Installing to user-level: $Target\$SkillDir" -ForegroundColor Cyan
}

# Create target directory
if (-not (Test-Path $Target)) {
    New-Item -ItemType Directory -Path $Target -Force | Out-Null
}

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourcePath = Join-Path $ScriptDir $SkillDir

if (Test-Path $SourcePath) {
    # Remove existing install if present
    $DestPath = Join-Path $Target $SkillDir
    if (Test-Path $DestPath) {
        Remove-Item -Recurse -Force $DestPath
    }
    Copy-Item -Recurse -Force $SourcePath $Target
    Write-Host ""
    Write-Host "Installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Open Claude Code and try:"
    Write-Host '  > Build me an agent that [describe your use case]' -ForegroundColor Yellow
} else {
    Write-Host "Error: $SkillDir directory not found. Run this from the repo root." -ForegroundColor Red
    exit 1
}
