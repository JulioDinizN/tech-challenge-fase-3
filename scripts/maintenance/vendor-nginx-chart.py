#!/usr/bin/env python3
"""Bundle pinned schemas and scope ingress secret access to its namespace."""
import argparse
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

CHART_SHA = "ae204b34975085dacd23bfbfce54371392432daa29edb49819a59b9efc9611a7"
SCHEMA_SHA = "a9e98cdc6ab09980f23b5e987a5f11d0ec1fc838187efb92f347ccf38ed8fd65"
SCHEMA_URL = "https://raw.githubusercontent.com/nginxinc/kubernetes-json-schema/master/v1.36.1/_definitions.json"


def bundle(chart_path, schema_path, output):
    chart_bytes = chart_path.read_bytes()
    schema_bytes = schema_path.read_bytes()
    if hashlib.sha256(chart_bytes).hexdigest() != CHART_SHA:
        raise ValueError("Upstream chart checksum mismatch")
    if hashlib.sha256(schema_bytes).hexdigest() != SCHEMA_SHA:
        raise ValueError("Upstream schema checksum mismatch")
    upstream = json.loads(schema_bytes)["definitions"]
    definitions = {}

    def rewrite(value):
        if isinstance(value, list):
            return [rewrite(item) for item in value]
        if not isinstance(value, dict):
            return value
        result = {}
        for key, item in value.items():
            if key == "$ref":
                ref = item.removeprefix(SCHEMA_URL)
                if not ref.startswith("#/definitions/"):
                    raise ValueError("Unexpected schema reference: " + item)
                name = ref.split("/")[2]
                if name not in definitions:
                    definitions[name] = {}
                    definitions[name] = rewrite(copy.deepcopy(upstream[name]))
                result[key] = ref
            else:
                result[key] = rewrite(item)
        return result

    with tarfile.open(fileobj=io.BytesIO(chart_bytes)) as source:
        original = json.load(source.extractfile("nginx-ingress/values.schema.json"))
        modified = rewrite(original)
        if "definitions" in modified:
            raise ValueError("Unexpected upstream definitions collision")
        modified["definitions"] = definitions
        payload = (json.dumps(modified, sort_keys=True, separators=(",", ":")) + "\n").encode()
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as target:
                for member in source.getmembers():
                    if not member.isfile() or ".." in Path(member.name).parts:
                        raise ValueError("Unexpected archive member")
                    data = payload if member.name == "nginx-ingress/values.schema.json" else source.extractfile(member).read()
                    if member.name == "nginx-ingress/templates/clusterrole.yaml":
                        if data.count(b"  - secrets\n") != 1:
                            raise ValueError("Unexpected upstream secret RBAC")
                        data = data.replace(b"  - secrets\n", b"")
                    if member.name == "nginx-ingress/values.yaml":
                        data = data.replace(b'watchSecretNamespace: ""', b'watchSecretNamespace: "nginx-ingress"')
                    info = tarfile.TarInfo(member.name)
                    info.size = len(data)
                    info.mode = member.mode
                    target.addfile(info, io.BytesIO(data))
                role = b'''{{- if .Values.rbac.create }}
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {{ include "nginx-ingress.fullname" . }}-secrets
  namespace: {{ .Release.Namespace }}
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {{ include "nginx-ingress.fullname" . }}-secrets
  namespace: {{ .Release.Namespace }}
subjects:
- kind: ServiceAccount
  name: {{ include "nginx-ingress.serviceAccountName" . }}
  namespace: {{ .Release.Namespace }}
roleRef:
  kind: Role
  name: {{ include "nginx-ingress.fullname" . }}-secrets
  apiGroup: rbac.authorization.k8s.io
{{- end }}
'''
                info = tarfile.TarInfo("nginx-ingress/templates/secret-role.yaml")
                info.size = len(role)
                info.mode = 0o644
                target.addfile(info, io.BytesIO(role))
    print(f"Bundled {len(definitions)} upstream definitions; validation remains enabled.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chart", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    bundle(args.chart, args.schema, args.output)
