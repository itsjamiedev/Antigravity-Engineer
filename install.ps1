<#
.SYNOPSIS
  Installs the portable Antigravity Engineering OS bundle globally (~/.gemini/config)
  and/or into any target project workspace (.agents/).

.PARAMETER CleanOldSkills
  Removes existing folders in <ConfigRoot>/skills, legacy remotion-* duplicates in
  ~/.agents/skills, and the 11 superseded pre-rename subagent files in <ConfigRoot>/agents
  before installing.

.PARAMETER Merge
  Non-interactive merge install: keeps unrelated custom skills and overwrites only
  packaged skills, agents, GEMINI.md, and optional plugins.

.PARAMETER NonInteractive
  Suppresses interactive Read-Host prompts (automatically enabled when stdin is redirected).

.PARAMETER SkipBackup
  Skips creating a timestamped backup before modifying existing files.

.PARAMETER Workspace
  Optional path to a project workspace directory. When set, deploys all 38 unified skills
  into <Workspace>\.agents\skills (and any optional bundled plugins if present).

.PARAMETER WorkspaceOnly
  Installs only into -Workspace\.agents\ (requires -Workspace) without modifying global config.

.PARAMETER CleanWorkspacePath
  Optional project workspace path whose <Path>\.agents\skills folder will be backed up
  and removed so the workspace inherits global skills cleanly.

.PARAMETER ConfigRoot
  Optional override for the global config root (defaults to "$HOME\.gemini\config").
#>
[CmdletBinding()]
param(
  [switch]$CleanOldSkills,
  [switch]$Merge,
  [switch]$NonInteractive,
  [switch]$SkipBackup,
  [string]$Workspace = "",
  [switch]$WorkspaceOnly,
  [string]$CleanWorkspacePath = "",
  [string]$ConfigRoot = ""
)

$ErrorActionPreference = 'Stop'
$PackageDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($WorkspaceOnly -and [string]::IsNullOrWhiteSpace($Workspace)) {
  throw "-WorkspaceOnly requires -Workspace <path>."
}

$ConfigDir = if ([string]::IsNullOrWhiteSpace($ConfigRoot)) {
  Join-Path $HOME '.gemini\config'
} else {
  $ConfigRoot
}

$TargetSkillsDir = Join-Path $ConfigDir 'skills'
$TargetAgentsDir = Join-Path $ConfigDir 'agents'
$TargetPluginsDir = Join-Path $ConfigDir 'plugins'
$TargetGeminiMd = Join-Path $ConfigDir 'GEMINI.md'
$LegacyAgentsSkillsDir = Join-Path $HOME '.agents\skills'

$LegacyAgentFiles = @(
  'software-architect.md',
  'backend-systems-engineer.md',
  'desktop-app-engineer.md',
  'ui-ux-designer.md',
  'motion-design-engineer.md',
  'deep-debugger.md',
  'code-reviewer.md',
  'qa-automation-engineer.md',
  'security-auditor.md',
  'video-production-engineer.md',
  'skill-architect.md'
)

Write-Host "=== Antigravity Engineering OS Portable Installer ===" -ForegroundColor Cyan
Write-Host "Package source : $PackageDir"
if (-not $WorkspaceOnly) {
  Write-Host "Global target  : $ConfigDir"
}
if (-not [string]::IsNullOrWhiteSpace($Workspace)) {
  Write-Host "Workspace      : $Workspace"
}

$isRedirected = $false
try { $isRedirected = [Console]::IsInputRedirected } catch { $isRedirected = $false }

if (-not $WorkspaceOnly -and -not $CleanOldSkills -and -not $Merge -and -not $NonInteractive -and -not $isRedirected) {
  $reply = Read-Host "Clean old global skills and legacy subagent filenames before installing? [y/N]"
  if ($reply -match '^(y|yes)$') {
    $CleanOldSkills = $true
  }
}

# 1. Global installation (~/.gemini/config or -ConfigRoot)
if (-not $WorkspaceOnly) {
  if (-not $SkipBackup -and (Test-Path $ConfigDir)) {
    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $backupParent = Split-Path -Parent $ConfigDir
    $backupName = "$(Split-Path -Leaf $ConfigDir)-backup-$timestamp"
    $backupDir = Join-Path $backupParent $backupName
    Write-Host "Creating global backup at $backupDir ..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    if (Test-Path $TargetGeminiMd) { Copy-Item $TargetGeminiMd -Destination $backupDir -Force }
    if (Test-Path $TargetAgentsDir) { Copy-Item $TargetAgentsDir -Destination (Join-Path $backupDir 'agents') -Recurse -Force }
    if (Test-Path $TargetSkillsDir) { Copy-Item $TargetSkillsDir -Destination (Join-Path $backupDir 'skills') -Recurse -Force }
    if (Test-Path $TargetPluginsDir) { Copy-Item $TargetPluginsDir -Destination (Join-Path $backupDir 'plugins') -Recurse -Force }
  }

  New-Item -ItemType Directory -Force -Path $ConfigDir, $TargetSkillsDir, $TargetAgentsDir | Out-Null

  if ($CleanOldSkills) {
    Write-Host "Cleaning old global skills and legacy subagent files ..." -ForegroundColor Yellow
    Get-ChildItem -Path $TargetSkillsDir -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

    foreach ($legacy in $LegacyAgentFiles) {
      $lp = Join-Path $TargetAgentsDir $legacy
      if (Test-Path $lp) { Remove-Item -Path $lp -Force }
    }

    if (Test-Path $LegacyAgentsSkillsDir) {
      $remotionDups = Get-ChildItem -Path $LegacyAgentsSkillsDir -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'remotion-*' }
      foreach ($dup in $remotionDups) {
        Remove-Item -Path $dup.FullName -Recurse -Force
      }
    }
  }

  Copy-Item -Path (Join-Path $PackageDir 'GEMINI.md') -Destination $TargetGeminiMd -Force

  Get-ChildItem -Path (Join-Path $PackageDir 'agents') -Filter '*.md' -File | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination (Join-Path $TargetAgentsDir $_.Name) -Force
  }

  Get-ChildItem -Path (Join-Path $PackageDir 'skills') -Directory | ForEach-Object {
    $dest = Join-Path $TargetSkillsDir $_.Name
    if (Test-Path $dest) { Remove-Item -Path $dest -Recurse -Force }
    Copy-Item -Path $_.FullName -Destination $dest -Recurse -Force
  }

  $PkgPluginsDir = Join-Path $PackageDir 'plugins'
  if (Test-Path $PkgPluginsDir) {
    New-Item -ItemType Directory -Force -Path $TargetPluginsDir | Out-Null
    Get-ChildItem -Path $PkgPluginsDir -Directory | ForEach-Object {
      $dest = Join-Path $TargetPluginsDir $_.Name
      if (Test-Path $dest) { Remove-Item -Path $dest -Recurse -Force }
      Copy-Item -Path $_.FullName -Destination $dest -Recurse -Force
    }
  }
}

# 2. Optional workspace installation (<Workspace>\.agents\)
if (-not [string]::IsNullOrWhiteSpace($Workspace)) {
  if (-not (Test-Path $Workspace)) {
    New-Item -ItemType Directory -Force -Path $Workspace | Out-Null
  }
  $wsAgentsRoot = Join-Path $Workspace '.agents'
  $wsSkillsDir = Join-Path $wsAgentsRoot 'skills'
  $wsPluginsDir = Join-Path $wsAgentsRoot 'plugins'

  if (-not $SkipBackup -and (Test-Path $wsAgentsRoot)) {
    $wsBackup = Join-Path $wsAgentsRoot ("backup-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    New-Item -ItemType Directory -Force -Path $wsBackup | Out-Null
    if (Test-Path $wsSkillsDir) { Copy-Item $wsSkillsDir -Destination (Join-Path $wsBackup 'skills') -Recurse -Force }
    if (Test-Path $wsPluginsDir) { Copy-Item $wsPluginsDir -Destination (Join-Path $wsBackup 'plugins') -Recurse -Force }
  }

  New-Item -ItemType Directory -Force -Path $wsSkillsDir | Out-Null

  Get-ChildItem -Path (Join-Path $PackageDir 'skills') -Directory | ForEach-Object {
    $dest = Join-Path $wsSkillsDir $_.Name
    if (Test-Path $dest) { Remove-Item -Path $dest -Recurse -Force }
    Copy-Item -Path $_.FullName -Destination $dest -Recurse -Force
  }

  $PkgPluginsDir = Join-Path $PackageDir 'plugins'
  if (Test-Path $PkgPluginsDir) {
    New-Item -ItemType Directory -Force -Path $wsPluginsDir | Out-Null
    Get-ChildItem -Path $PkgPluginsDir -Directory | ForEach-Object {
      $dest = Join-Path $wsPluginsDir $_.Name
      if (Test-Path $dest) { Remove-Item -Path $dest -Recurse -Force }
      Copy-Item -Path $_.FullName -Destination $dest -Recurse -Force
    }
  }
}

# 3. Optional cleanup of legacy per-project .agents\skills
if (-not [string]::IsNullOrWhiteSpace($CleanWorkspacePath)) {
  $cleanWsSkills = Join-Path $CleanWorkspacePath '.agents\skills'
  if (Test-Path $cleanWsSkills) {
    $wsBackup = Join-Path $CleanWorkspacePath (".agents\skills-backup-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    Copy-Item -Path $cleanWsSkills -Destination $wsBackup -Recurse -Force
    Remove-Item -Path $cleanWsSkills -Recurse -Force
    Write-Host "Backed up workspace skills to $wsBackup and removed $cleanWsSkills" -ForegroundColor Green
  }
}

# 4. Verification
Write-Host ""
Write-Host "=== Installation Verified ===" -ForegroundColor Green

if (-not $WorkspaceOnly) {
  $installedSkills = (Get-ChildItem -Path $TargetSkillsDir -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }).Count
  $installedAgents = (Get-ChildItem -Path $TargetAgentsDir -Filter '*.md' -File).Count
  $geminiBytes = (Get-Item $TargetGeminiMd).Length

  if ($installedSkills -lt 38) { throw "Verification failed: expected >= 38 global skills, found $installedSkills" }
  if ($installedAgents -lt 11) { throw "Verification failed: expected >= 11 subagents, found $installedAgents" }
  if ($geminiBytes -ge 24000) { throw "Verification failed: GEMINI.md exceeds 24000 bytes ($geminiBytes)" }

  Write-Host "Global skills (SKILL.md) : $installedSkills"
  Write-Host "Global subagents (.md)   : $installedAgents"
  Write-Host "GEMINI.md size           : $geminiBytes / 24000 bytes"
}

if (-not [string]::IsNullOrWhiteSpace($Workspace)) {
  $wsSkillCount = (Get-ChildItem -Path (Join-Path $Workspace '.agents\skills') -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }).Count
  if ($wsSkillCount -lt 38) { throw "Workspace verification failed: expected >= 38 skills, found $wsSkillCount" }
  Write-Host "Workspace skills         : $wsSkillCount"
}

Write-Host "Open a new Antigravity conversation to load the updated configuration."
Write-Host "Optional (for diagram-design PDF/PNG export): pip install playwright && playwright install chromium" -ForegroundColor DarkGray
