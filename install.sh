#!/usr/bin/env bash
set -euo pipefail

CLEAN_OLD_SKILLS=false
MERGE=false
NON_INTERACTIVE=false
SKIP_BACKUP=false
WORKSPACE=""
WORKSPACE_ONLY=false
CLEAN_WORKSPACE=""
CONFIG_ROOT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --clean-old-skills)
      CLEAN_OLD_SKILLS=true
      shift
      ;;
    --merge)
      MERGE=true
      shift
      ;;
    --non-interactive)
      NON_INTERACTIVE=true
      shift
      ;;
    --skip-backup)
      SKIP_BACKUP=true
      shift
      ;;
    --workspace)
      WORKSPACE="${2:-}"
      [[ -z "$WORKSPACE" ]] && { echo "Error: --workspace requires a path" >&2; exit 1; }
      shift 2
      ;;
    --workspace-only)
      WORKSPACE_ONLY=true
      shift
      ;;
    --clean-workspace)
      CLEAN_WORKSPACE="${2:-}"
      [[ -z "$CLEAN_WORKSPACE" ]] && { echo "Error: --clean-workspace requires a path" >&2; exit 1; }
      shift 2
      ;;
    --config-root)
      CONFIG_ROOT="${2:-}"
      [[ -z "$CONFIG_ROOT" ]] && { echo "Error: --config-root requires a path" >&2; exit 1; }
      shift 2
      ;;
    -h|--help)
      cat <<'EOF'
Usage: ./install.sh [OPTIONS]

Options:
  --clean-old-skills       Clear old skills in ~/.gemini/config/skills, remotion-* in
                           ~/.agents/skills, and superseded pre-rename subagent files first
  --merge                  Keep unrelated custom skills and overwrite packaged items only
  --non-interactive        Never prompt for input (safe for automated agents)
  --skip-backup            Skip creating config-backup-<timestamp>
  --workspace PATH         Also deploy skills/ into PATH/.agents/skills
  --workspace-only         Only deploy into --workspace/.agents/ (requires --workspace)
  --clean-workspace PATH   Back up and remove PATH/.agents/skills
  --config-root PATH       Override global target directory (default: ~/.gemini/config)
EOF
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

if [[ "$WORKSPACE_ONLY" == true ]] && [[ -z "$WORKSPACE" ]]; then
  echo "Error: --workspace-only requires --workspace PATH" >&2
  exit 1
fi

PACKAGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${CONFIG_ROOT:-${HOME}/.gemini/config}"
TARGET_SKILLS_DIR="${CONFIG_DIR}/skills"
TARGET_AGENTS_DIR="${CONFIG_DIR}/agents"
TARGET_PLUGINS_DIR="${CONFIG_DIR}/plugins"
TARGET_GEMINI_MD="${CONFIG_DIR}/GEMINI.md"
LEGACY_AGENTS_SKILLS_DIR="${HOME}/.agents/skills"

LEGACY_AGENT_FILES=(
  "software-architect.md"
  "backend-systems-engineer.md"
  "desktop-app-engineer.md"
  "ui-ux-designer.md"
  "motion-design-engineer.md"
  "deep-debugger.md"
  "code-reviewer.md"
  "qa-automation-engineer.md"
  "security-auditor.md"
  "video-production-engineer.md"
  "skill-architect.md"
)

echo "=== Antigravity Engineering OS Portable Installer ==="
echo "Package source : ${PACKAGE_DIR}"
[[ "$WORKSPACE_ONLY" == false ]] && echo "Global target  : ${CONFIG_DIR}"
[[ -n "$WORKSPACE" ]] && echo "Workspace      : ${WORKSPACE}"

if [[ "$WORKSPACE_ONLY" == false ]] && [[ "$CLEAN_OLD_SKILLS" == false ]] && [[ "$MERGE" == false ]] && [[ "$NON_INTERACTIVE" == false ]] && [[ -t 0 ]]; then
  read -r -p "Clean old global skills and legacy subagent filenames before installing? [y/N] " reply
  if [[ "$reply" =~ ^[Yy]([Ee][Ss])?$ ]]; then
    CLEAN_OLD_SKILLS=true
  fi
fi

if [[ "$WORKSPACE_ONLY" == false ]]; then
  if [[ "$SKIP_BACKUP" == false ]] && [[ -d "$CONFIG_DIR" ]]; then
    TS="$(date +%Y%m%d-%H%M%S)"
    BACKUP_DIR="$(dirname "$CONFIG_DIR")/$(basename "$CONFIG_DIR")-backup-${TS}"
    echo "Creating global backup at ${BACKUP_DIR} ..."
    mkdir -p "$BACKUP_DIR"
    [[ -f "$TARGET_GEMINI_MD" ]] && cp "$TARGET_GEMINI_MD" "${BACKUP_DIR}/GEMINI.md"
    [[ -d "$TARGET_AGENTS_DIR" ]] && cp -R "$TARGET_AGENTS_DIR" "${BACKUP_DIR}/agents"
    [[ -d "$TARGET_SKILLS_DIR" ]] && cp -R "$TARGET_SKILLS_DIR" "${BACKUP_DIR}/skills"
    [[ -d "$TARGET_PLUGINS_DIR" ]] && cp -R "$TARGET_PLUGINS_DIR" "${BACKUP_DIR}/plugins"
  fi

  mkdir -p "$CONFIG_DIR" "$TARGET_SKILLS_DIR" "$TARGET_AGENTS_DIR"

  if [[ "$CLEAN_OLD_SKILLS" == true ]]; then
    echo "Cleaning old global skills and legacy subagent files ..."
    rm -rf "${TARGET_SKILLS_DIR:?}"/*
    for legacy in "${LEGACY_AGENT_FILES[@]}"; do
      rm -f "${TARGET_AGENTS_DIR}/${legacy}"
    done
    if [[ -d "$LEGACY_AGENTS_SKILLS_DIR" ]]; then
      rm -rf "${LEGACY_AGENTS_SKILLS_DIR}"/remotion-*
    fi
  fi

  cp "${PACKAGE_DIR}/GEMINI.md" "$TARGET_GEMINI_MD"
  cp -R "${PACKAGE_DIR}/agents/." "$TARGET_AGENTS_DIR/"

  for skill_path in "${PACKAGE_DIR}/skills/"*; do
    [[ -d "$skill_path" ]] || continue
    skill_name="$(basename "$skill_path")"
    rm -rf "${TARGET_SKILLS_DIR}/${skill_name}"
    cp -R "$skill_path" "${TARGET_SKILLS_DIR}/${skill_name}"
  done

  if [[ -d "${PACKAGE_DIR}/plugins" ]]; then
    mkdir -p "$TARGET_PLUGINS_DIR"
    for plugin_path in "${PACKAGE_DIR}/plugins/"*; do
      [[ -d "$plugin_path" ]] || continue
      plugin_name="$(basename "$plugin_path")"
      rm -rf "${TARGET_PLUGINS_DIR}/${plugin_name}"
      cp -R "$plugin_path" "${TARGET_PLUGINS_DIR}/${plugin_name}"
    done
  fi
fi

if [[ -n "$WORKSPACE" ]]; then
  WS_AGENTS_ROOT="${WORKSPACE}/.agents"
  WS_SKILLS_DIR="${WS_AGENTS_ROOT}/skills"
  WS_PLUGINS_DIR="${WS_AGENTS_ROOT}/plugins"
  if [[ "$SKIP_BACKUP" == false ]] && [[ -d "$WS_AGENTS_ROOT" ]]; then
    WS_BACKUP="${WS_AGENTS_ROOT}/backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$WS_BACKUP"
    [[ -d "$WS_SKILLS_DIR" ]] && cp -R "$WS_SKILLS_DIR" "${WS_BACKUP}/skills"
    [[ -d "$WS_PLUGINS_DIR" ]] && cp -R "$WS_PLUGINS_DIR" "${WS_BACKUP}/plugins"
  fi
  mkdir -p "$WS_SKILLS_DIR"

  for skill_path in "${PACKAGE_DIR}/skills/"*; do
    [[ -d "$skill_path" ]] || continue
    skill_name="$(basename "$skill_path")"
    rm -rf "${WS_SKILLS_DIR}/${skill_name}"
    cp -R "$skill_path" "${WS_SKILLS_DIR}/${skill_name}"
  done

  if [[ -d "${PACKAGE_DIR}/plugins" ]]; then
    mkdir -p "$WS_PLUGINS_DIR"
    for plugin_path in "${PACKAGE_DIR}/plugins/"*; do
      [[ -d "$plugin_path" ]] || continue
      plugin_name="$(basename "$plugin_path")"
      rm -rf "${WS_PLUGINS_DIR}/${plugin_name}"
      cp -R "$plugin_path" "${WS_PLUGINS_DIR}/${plugin_name}"
    done
  fi
fi

if [[ -n "$CLEAN_WORKSPACE" ]]; then
  CLEAN_WS_SKILLS="${CLEAN_WORKSPACE}/.agents/skills"
  if [[ -d "$CLEAN_WS_SKILLS" ]]; then
    WS_BACKUP="${CLEAN_WORKSPACE}/.agents/skills-backup-$(date +%Y%m%d-%H%M%S)"
    cp -R "$CLEAN_WS_SKILLS" "$WS_BACKUP"
    rm -rf "$CLEAN_WS_SKILLS"
    echo "Backed up workspace skills to ${WS_BACKUP} and removed ${CLEAN_WS_SKILLS}"
  fi
fi

echo ""
echo "=== Installation Verified ==="

if [[ "$WORKSPACE_ONLY" == false ]]; then
  SKILL_COUNT="$(find "$TARGET_SKILLS_DIR" -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')"
  AGENT_COUNT="$(find "$TARGET_AGENTS_DIR" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')"
  GEMINI_BYTES="$(wc -c < "$TARGET_GEMINI_MD" | tr -d ' ')"

  [[ "$SKILL_COUNT" -ge 38 ]] || { echo "Error: expected >= 38 global skills, found $SKILL_COUNT" >&2; exit 1; }
  [[ "$AGENT_COUNT" -ge 11 ]] || { echo "Error: expected >= 11 subagents, found $AGENT_COUNT" >&2; exit 1; }
  [[ "$GEMINI_BYTES" -lt 24000 ]] || { echo "Error: GEMINI.md exceeds 24000 bytes ($GEMINI_BYTES)" >&2; exit 1; }

  echo "Global skills (SKILL.md) : ${SKILL_COUNT}"
  echo "Global subagents (.md)   : ${AGENT_COUNT}"
  echo "GEMINI.md size           : ${GEMINI_BYTES} / 24000 bytes"
fi

if [[ -n "$WORKSPACE" ]]; then
  WS_SKILL_COUNT="$(find "${WORKSPACE}/.agents/skills" -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')"
  [[ "$WS_SKILL_COUNT" -ge 38 ]] || { echo "Error: expected >= 38 workspace skills, found $WS_SKILL_COUNT" >&2; exit 1; }
  echo "Workspace skills         : ${WS_SKILL_COUNT}"
fi

echo "Open a new Antigravity conversation to load the updated configuration."
echo "Optional (for diagram-design PDF/PNG export): pip install playwright && playwright install chromium"
