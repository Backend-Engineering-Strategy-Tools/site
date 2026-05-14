#!/usr/bin/env bash
set -e

# ─── Config ───────────────────────────────────────────────────────────────────
IMAGE="pi-agent:latest"
PI_CONFIG="$HOME/.pi/agent"
REPO="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# ─── Build ────────────────────────────────────────────────────────────────────
build_image() {
  echo "🔨 Building $IMAGE..."
  docker build --platform linux/arm64 --tag "$IMAGE" - <<'DOCKERFILE'
FROM node:22-slim

# Install fd and ripgrep so Pi doesn't try to download them at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    fd-find \
    ripgrep \
    git \
    && ln -s /usr/bin/fdfind /usr/local/bin/fd \
    && rm -rf /var/lib/apt/lists/*

# Install Pi globally
RUN npm install -g @earendil-works/pi-coding-agent

# Pi writes config/sessions here
RUN mkdir -p /root/.pi/agent

WORKDIR /app
ENTRYPOINT ["pi"]
DOCKERFILE
  echo "✅ Image built: $IMAGE"
}

ensure_image() {
  if ! docker image inspect "$IMAGE" &>/dev/null; then
    echo "⚠️  Image not found. Building now (one-time, ~2 min)..."
    build_image
  fi
}

ensure_pi_config() {
  mkdir -p "$PI_CONFIG"
}

# ─── Worktree ─────────────────────────────────────────────────────────────────
cmd_worktree() {
  local name="${1:-}"
  local branch="${2:-}"

  # Show usage if no name given
  if [ -z "$name" ]; then
    echo "Usage: $(basename "$0") worktree <name> [branch]"
    echo ""
    echo "  name     Short label for this worktree (e.g. 'review', 'feature-x')"
    echo "  branch   Branch to check out (default: current branch)"
    echo ""
    echo "Examples:"
    echo "  $(basename "$0") worktree review          # new worktree on current branch"
    echo "  $(basename "$0") worktree feature main    # new worktree on main"
    echo ""
    echo "Existing worktrees:"
    git worktree list
    return 0
  fi

  # Worktree lives as a sibling of the repo root
  local worktree_path
  worktree_path="$(dirname "$REPO")/${REPO##*/}-${name}"

  if [ -d "$worktree_path" ]; then
    echo "✅ Worktree already exists: $worktree_path"
  else
    echo "🌿 Creating worktree: $worktree_path"
    if [ -n "$branch" ]; then
      # Check if branch exists; if not, create it
      if git -C "$REPO" show-ref --verify --quiet "refs/heads/$branch"; then
        git -C "$REPO" worktree add "$worktree_path" "$branch"
      else
        echo "   Branch '$branch' not found — creating it from current HEAD"
        git -C "$REPO" worktree add -b "$branch" "$worktree_path"
      fi
    else
      # No branch specified — use current branch name with worktree suffix
      local current_branch
      current_branch=$(git -C "$REPO" rev-parse --abbrev-ref HEAD)
      local wt_branch="${current_branch}-${name}"
      echo "   Creating branch '$wt_branch' from '$current_branch'"
      git -C "$REPO" worktree add -b "$wt_branch" "$worktree_path"
    fi
    echo "✅ Worktree ready: $worktree_path"
  fi

  # Each worktree gets its own Pi config/session dir
  local wt_pi_config="$HOME/.pi/agent-${name}"
  mkdir -p "$wt_pi_config"

  echo "🚀 Starting Pi in worktree '$name'..."
  echo "📁 Project: $worktree_path"
  echo "🗂  Sessions: $wt_pi_config"
  echo "🤖 Switch models anytime with /model or Ctrl+L"
  echo ""

  ensure_image

  docker run -it --rm \
    --cap-drop=ALL \
    --security-opt=no-new-privileges \
    --volume "$worktree_path:$worktree_path" \
    --volume "$REPO/.git:$REPO/.git:ro" \
    --volume "$wt_pi_config:/root/.pi/agent" \
    --workdir "$worktree_path" \
    --env NPM_CONFIG_CACHE=/tmp/.npm \
    --env GEMINI_API_KEY="${GEMINI_API_KEY:-}" \
    --env ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
    --env OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
    "$IMAGE"
}

cmd_worktree_list() {
  echo "🌿 Git worktrees:"
  git -C "$REPO" worktree list
  echo ""
  echo "🗂  Pi session dirs:"
  ls -d "$HOME/.pi/agent"* 2>/dev/null || echo "  (none yet)"
}

cmd_worktree_remove() {
  local name="${1:-}"
  if [ -z "$name" ]; then
    echo "Usage: $(basename "$0") worktree-rm <name>"
    return 1
  fi
  local worktree_path
  worktree_path="$(dirname "$REPO")/${REPO##*/}-${name}"
  echo "🗑  Removing worktree: $worktree_path"
  git -C "$REPO" worktree remove "$worktree_path" --force
  echo "🗑  Removing Pi sessions: $HOME/.pi/agent-${name}"
  rm -rf "$HOME/.pi/agent-${name}"
  echo "✅ Done"
}

# ─── Commands ─────────────────────────────────────────────────────────────────
usage() {
  cat <<EOF
Usage: $(basename "$0") [command]

Commands:
  (none)              Start Pi in the current project
  build               (Re)build the Docker image
  worktree <n> [br]   Create a git worktree and launch Pi in it
  worktrees           List all worktrees and Pi session dirs
  worktree-rm <n>     Remove a worktree and its Pi sessions
  shell               Open a bash shell inside the container
  health              Check prerequisites
  help                Show this message

Worktree examples:
  $(basename "$0") worktree review          # branch: main-review
  $(basename "$0") worktree fix bug-123     # branch: bug-123 (existing or new)
  $(basename "$0") worktree feature feat/x  # branch: feat/x

API keys: GEMINI_API_KEY, ANTHROPIC_API_KEY, OPENAI_API_KEY
EOF
}

run_pi() {
  ensure_image
  ensure_pi_config

  echo "🚀 Starting Pi in Docker..."
  echo "📁 Project: $REPO"
  echo "🤖 Switch models anytime with /model or Ctrl+L"
  echo ""

  docker run -it --rm \
    --cap-drop=ALL \
    --security-opt=no-new-privileges \
    --volume "$REPO:$REPO" \
    --volume "$PI_CONFIG:/root/.pi/agent" \
    --workdir "$REPO" \
    --env NPM_CONFIG_CACHE=/tmp/.npm \
    --env GEMINI_API_KEY="${GEMINI_API_KEY:-}" \
    --env ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
    --env OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
    "$IMAGE" "$@"
}

health() {
  echo "🏥 Health check"
  echo ""
  if docker info &>/dev/null; then
    echo "✅ Docker running"
  else
    echo "❌ Docker not running"
  fi
  if docker image inspect "$IMAGE" &>/dev/null; then
    echo "✅ Image $IMAGE exists"
  else
    echo "⚠️  Image not built yet — run: $(basename "$0") build"
  fi
  if [ -d "$PI_CONFIG" ]; then
    echo "✅ Pi config dir: $PI_CONFIG"
  else
    echo "⚠️  Pi config dir missing (will be created on first run)"
  fi
  for key in GEMINI_API_KEY ANTHROPIC_API_KEY OPENAI_API_KEY; do
    if [ -n "${!key:-}" ]; then
      echo "✅ $key is set"
    else
      echo "⚠️  $key not set"
    fi
  done
}

# ─── Main ─────────────────────────────────────────────────────────────────────
case "${1:-}" in
  build)        build_image ;;
  worktree)     shift; cmd_worktree "$@" ;;
  worktrees)    cmd_worktree_list ;;
  worktree-rm)  shift; cmd_worktree_remove "$@" ;;
  shell)
    ensure_image
    ensure_pi_config
    docker run -it --rm \
      --cap-drop=ALL \
      --security-opt=no-new-privileges \
      --volume "$REPO:$REPO" \
      --volume "$PI_CONFIG:/root/.pi/agent" \
      --workdir "$REPO" \
      --env NPM_CONFIG_CACHE=/tmp/.npm \
      --entrypoint bash \
      "$IMAGE"
    ;;
  health)       health ;;
  help|-h|--help) usage ;;
  *)            run_pi "$@" ;;
esac