#!/usr/bin/env bash
# Manage Gardener shoot clusters on Cleura via their REST API.
# Requires: curl, jq
#
# Usage:
#   cleura-shoot.sh create  <cluster-name>
#   cleura-shoot.sh status  <cluster-name>
#   cleura-shoot.sh kubeconfig <cluster-name> [output-file] [expiry-seconds]
#   cleura-shoot.sh delete  <cluster-name>
#   cleura-shoot.sh spec
#   cleura-shoot.sh list
#
# Required env vars:
#   CLEURA_LOGIN     — Cleura account email
#   CLEURA_PASSWORD  — Cleura account password
#
# Optional env vars:
#   CLEURA_PROJECT   — Cleura project ID (auto-resolved from region if unset)
#   CLEURA_REGION    — default: kna1
#   CLEURA_K8S       — Kubernetes version, default: 1.35.5
#   CLEURA_MACHINE   — machine type, default: b.4c8gb (see /gardener/v1/public/cloudprofile)
#   CLEURA_NODES_MIN — worker minimum, default: 1
#   CLEURA_NODES_MAX — worker maximum, default: 3

set -euox pipefail

BASE_URL="https://rest.cleura.cloud"
REGION="${CLEURA_REGION:-kna1}"
K8S_VERSION="${CLEURA_K8S:-1.35.5}"
MACHINE_TYPE="${CLEURA_MACHINE:-b.4c8gb}"
NODES_MIN="${CLEURA_NODES_MIN:-1}"
NODES_MAX="${CLEURA_NODES_MAX:-3}"

: "${CLEURA_LOGIN:?CLEURA_LOGIN is required}"
: "${CLEURA_PASSWORD:?CLEURA_PASSWORD is required}"

# ── auth ──────────────────────────────────────────────────────────────────────

_auth() {
  local response
  response=$(curl -s -X POST "$BASE_URL/auth/v1/tokens" \
    -H "Content-Type: application/json" \
    -d "{\"auth\": {\"login\": \"$CLEURA_LOGIN\", \"password\": \"$CLEURA_PASSWORD\"}}")
  TOKEN=$(echo "$response" | jq -r '.token')
  if [[ -z "$TOKEN" || "$TOKEN" == "null" ]]; then
    echo "Authentication failed" >&2
    exit 1
  fi
}

_resolve_project() {
  if [[ -n "${CLEURA_PROJECT:-}" ]]; then
    return
  fi
  local domain_id
  domain_id=$(curl -s "$BASE_URL/accesscontrol/v1/openstack/domains" \
    -H "X-AUTH-LOGIN: $CLEURA_LOGIN" -H "X-AUTH-TOKEN: $TOKEN" \
    | jq -r --arg r "$REGION" \
      '.[] | select(.area.regions[].region | ascii_downcase == ($r | ascii_downcase)) | .id' \
    | head -1)
  if [[ -z "$domain_id" ]]; then
    echo "No domain found for region $REGION" >&2; exit 1
  fi
  CLEURA_PROJECT=$(curl -s "$BASE_URL/accesscontrol/v1/openstack/$domain_id/projects" \
    -H "X-AUTH-LOGIN: $CLEURA_LOGIN" -H "X-AUTH-TOKEN: $TOKEN" \
    | jq -r '.[0].id')
  if [[ -z "$CLEURA_PROJECT" || "$CLEURA_PROJECT" == "null" ]]; then
    echo "No project found in domain $domain_id" >&2; exit 1
  fi
  echo "Resolved project: $CLEURA_PROJECT"
}

_headers() {
  echo "-H" "X-AUTH-LOGIN: $CLEURA_LOGIN" "-H" "X-AUTH-TOKEN: $TOKEN"
}

# ── commands ──────────────────────────────────────────────────────────────────

cmd_list() {
  _auth; _resolve_project
  curl -s "$BASE_URL/gardener/v1/public/shoot/$REGION/$CLEURA_PROJECT" \
    -H "X-AUTH-LOGIN: $CLEURA_LOGIN" -H "X-AUTH-TOKEN: $TOKEN" \
    | jq -r '.[]? | "\(.metadata.name)  \(.status.lastOperation.state // "unknown")"'
}

cmd_create() {
  local name="$1"
  _auth; _resolve_project

  echo "Bootstrapping project (safe to run repeatedly)..."
  curl -s -X POST "$BASE_URL/gardener/v1/public/secret/$REGION/$CLEURA_PROJECT/bootstrap" \
    -H "X-AUTH-LOGIN: $CLEURA_LOGIN" -H "X-AUTH-TOKEN: $TOKEN" | jq . || true

  echo "Creating shoot cluster: $name"
  curl -s -X POST "$BASE_URL/gardener/v1/public/shoot/$REGION/$CLEURA_PROJECT" \
    -H "X-AUTH-LOGIN: $CLEURA_LOGIN" -H "X-AUTH-TOKEN: $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"shoot\": {
        \"name\": \"$name\",
        \"kubernetes\": {\"version\": \"$K8S_VERSION\"},
        \"provider\": {
          \"infrastructureConfig\": {\"floatingPoolName\": \"ext-net\"},
          \"workers\": [{
            \"machine\": {
              \"type\": \"$MACHINE_TYPE\",
              \"image\": {\"name\": \"gardenlinux\", \"version\": \"1877.17.0\"}
            },
            \"minimum\": $NODES_MIN,
            \"maximum\": $NODES_MAX,
            \"volume\": {\"size\": \"50Gi\"}
          }]
        }
      }
    }" | jq .

  echo ""
  echo "Cluster creation started. Poll status with:"
  echo "  $0 status $name"
}

cmd_status() {
  local name="$1"
  _auth; _resolve_project
  curl -s "$BASE_URL/gardener/v1/public/shoot/$REGION/$CLEURA_PROJECT/$name" \
    -H "X-AUTH-LOGIN: $CLEURA_LOGIN" -H "X-AUTH-TOKEN: $TOKEN" \
    | jq '.status.lastOperation | {state, description, progress}'
}

cmd_wait() {
  local name="$1"
  echo "Waiting for $name to reach Succeeded state..."
  _auth; _resolve_project
  while true; do
    _auth
    STATE=$(curl -sf "$BASE_URL/gardener/v1/public/shoot/$REGION/$CLEURA_PROJECT/$name" \
      -H "X-AUTH-LOGIN: $CLEURA_LOGIN" -H "X-AUTH-TOKEN: $TOKEN" \
      | jq -r '.status.lastOperation.state // "unknown"')
    echo "  $(date '+%H:%M:%S')  $STATE"
    [[ "$STATE" == "Succeeded" ]] && break
    [[ "$STATE" == "Failed" ]] && echo "Cluster reached Failed state" >&2 && exit 1
    sleep 30
  done
  echo "Ready."
}

cmd_kubeconfig() {
  local name="$1"
  local outfile="${2:-$name-kubeconfig.yaml}"
  local expiry="${3:-3600}"
  _auth; _resolve_project

  echo "Generating kubeconfig for $name..."
  local gen
  gen=$(curl -s -X POST "$BASE_URL/gardener/v1/public/shoot/$REGION/$CLEURA_PROJECT/$name/adminkubeconfig" \
    -H "X-AUTH-LOGIN: $CLEURA_LOGIN" -H "X-AUTH-TOKEN: $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"config\": {\"expirationSeconds\": $expiry}}")
  if echo "$gen" | jq -e '.error' > /dev/null 2>&1; then
    echo "$gen" | jq . >&2; exit 1
  fi

#  local response
#  response=$(curl -s "$BASE_URL/gardener/v1/public/shoot/$REGION/$CLEURA_PROJECT/$name/kubeconfig" \
#    -H "X-AUTH-LOGIN: $CLEURA_LOGIN" -H "X-AUTH-TOKEN: $TOKEN")
#  if echo "$response" | jq -e '.error' > /dev/null 2>&1; then
#    echo "$response" | jq . >&2; exit 1
#  fi
#  echo "$response" > "$outfile"
  echo "$gen" | jq -r > "$outfile"
  echo "Kubeconfig written to $outfile"
}

cmd_spec() {
  _auth
  curl -s "$BASE_URL/gardener/v1/public/cloudprofile" \
    -H "X-AUTH-LOGIN: $CLEURA_LOGIN" -H "X-AUTH-TOKEN: $TOKEN" \
    | jq '.[0].spec | {
        kubernetes: [.kubernetes.versions[] | select(.classification == "supported") | .version],
        images: [.machineImages[] | {name, versions: [.versions[] | select(.classification == "supported") | .version]}],
        machine_types: [.machineTypes[] | select(.usable) | .name]
      }'
}

cmd_delete() {
  local name="$1"
  _auth; _resolve_project
  curl -s -X DELETE "$BASE_URL/gardener/v1/public/shoot/$REGION/$CLEURA_PROJECT/$name" \
    -H "X-AUTH-LOGIN: $CLEURA_LOGIN" -H "X-AUTH-TOKEN: $TOKEN"
  echo "Delete requested for $name"
}

# ── dispatch ──────────────────────────────────────────────────────────────────

COMMAND="${1:-}"
shift || true

case "$COMMAND" in
  spec)       cmd_spec ;;
  list)       cmd_list ;;
  create)     cmd_create "${1:?cluster name required}" ;;
  status)     cmd_status "${1:?cluster name required}" ;;
  wait)       cmd_wait "${1:?cluster name required}" ;;
  kubeconfig) cmd_kubeconfig "${1:?cluster name required}" "${2:-}" ;;
  delete)     cmd_delete "${1:?cluster name required}" ;;
  *)
    echo "Usage: $0 {spec|list|create|status|wait|kubeconfig|delete} [cluster-name]" >&2
    exit 1
    ;;
esac
