#!/usr/bin/env bash
set -euo pipefail

for command in curl jq kubectl; do
  command -v "$command" >/dev/null || { echo "$command is required" >&2; exit 1; }
done

find_load_balancer_address() {
  kubectl --namespace nginx-ingress get service \
    --selector=app.kubernetes.io/instance=nginx-ingress \
    -o json | jq -r '
      .items[]
      | select(.spec.type == "LoadBalancer")
      | (.status.loadBalancer.ingress[0].ip // .status.loadBalancer.ingress[0].hostname // empty)
    ' | head -n 1
}

base_url="${BASE_URL:-}"
if [[ -z "$base_url" ]]; then
  for _ in {1..40}; do
    address="$(find_load_balancer_address)"
    if [[ -n "$address" ]]; then
      base_url="http://$address"
      break
    fi
    sleep 15
  done
fi
[[ -n "$base_url" ]] || { echo "The OCI Load Balancer has no public address" >&2; exit 1; }

api_key="$(kubectl --namespace togglemaster get secret evaluation-runtime-secrets \
  -o jsonpath='{.data.SERVICE_API_KEY}' | base64 --decode)"
ingress_host="${INGRESS_HOST:-togglemaster.local}"
headers=(-H "Host: $ingress_host" -H "Authorization: Bearer $api_key" -H 'Content-Type: application/json')
flag_name="${FLAG_NAME:-enable-oke-demo}"
body="$(mktemp)"
trap 'rm -f "$body"' EXIT

request() {
  local method="$1" url="$2" payload="${3:-}" status
  local args=(-sS --connect-timeout 10 --max-time 30 -o "$body" -w '%{http_code}' -X "$method")
  if [[ -n "$payload" ]]; then
    args+=(-d "$payload")
  fi
  status="$(curl "${args[@]}" "${headers[@]}" "$url")"
  printf '%s' "$status"
}

status="$(request GET "$base_url/validate")"
[[ "$status" == "200" ]] || { echo "auth validate failed ($status): $(cat "$body")" >&2; exit 1; }
echo "auth validate: $status"

flag_payload="$(jq -cn --arg name "$flag_name" '{name:$name,description:"OKE smoke test",is_enabled:true}')"
status="$(request POST "$base_url/flags" "$flag_payload")"
if [[ "$status" == "409" ]]; then
  status="$(request PUT "$base_url/flags/$flag_name" '{"description":"OKE smoke test","is_enabled":true}')"
fi
[[ "$status" == "200" || "$status" == "201" ]] || { echo "flag upsert failed ($status): $(cat "$body")" >&2; exit 1; }
echo "flag upsert: $status"

rule_payload="$(jq -cn --arg name "$flag_name" '{flag_name:$name,is_enabled:true,rules:{type:"PERCENTAGE",value:100}}')"
status="$(request POST "$base_url/rules" "$rule_payload")"
if [[ "$status" == "409" ]]; then
  status="$(request PUT "$base_url/rules/$flag_name" '{"is_enabled":true,"rules":{"type":"PERCENTAGE","value":100}}')"
fi
[[ "$status" == "200" || "$status" == "201" ]] || { echo "rule upsert failed ($status): $(cat "$body")" >&2; exit 1; }
echo "rule upsert: $status"

status="$(request GET "$base_url/evaluate?user_id=oke-demo-user&flag_name=$flag_name")"
[[ "$status" == "200" ]] || { echo "evaluation failed ($status): $(cat "$body")" >&2; exit 1; }
jq -e '.result == true' "$body" >/dev/null
echo "evaluation: $status $(jq -c . "$body")"
echo "Smoke test completed through $base_url"
