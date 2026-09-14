# Vendored NGINX chart

`nginx-ingress-2.6.1.tgz` retains the upstream chart templates and values. Only `values.schema.json` changes: external Kubernetes schema references are bundled into local definitions. The Terraform Helm provider rejected the upstream remote references with `invalid file url`; schema validation remains enabled.

Upstream: `oci://ghcr.io/nginx/charts/nginx-ingress:2.6.1` (application5.5.1), OCI manifest digest `sha256:fe6899d4087de3cdd809b5928b7373b0a97a58312f40733938dda84f4d571516`.

Rebuild with `scripts/vendor-nginx-chart.py --chart <upstream.tgz> --schema <_definitions.json> --output infra/environments/homolog/platform/charts/nginx-ingress-2.6.1.tgz`. The script verifies exact SHA256 checksums for both inputs. Schema source: https://raw.githubusercontent.com/nginxinc/kubernetes-json-schema/master/v1.36.1/_definitions.json.

Validated with Helm rendering: valid values succeed, a nonnumeric controller.replicaCount fails. The bundled chart also installed successfully through Terraform with validation enabled.
