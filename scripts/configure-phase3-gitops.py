#!/usr/bin/env python3
"""Fill non-secret GitOps placeholders from core outputs. Never applies or pushes."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('legacy_renderer', ROOT/'scripts/render-oci-manifests.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


def configure(outputs, gitops, tag):
    if not re.fullmatch(r'sha-[0-9a-f]{12}', tag):
        raise ValueError('initial image tag must be sha-<12 hex> and already published for all five services')
    values = renderer.replacements(outputs, tag)
    pending = {}
    for p in list((gitops/'apps').rglob('*.yaml')) + list((gitops/'platform').rglob('*.yaml')):
        text = p.read_text()
        for token, value in values.items():
            # Values are inserted into plain YAML scalars; reject YAML injection.
            if not re.fullmatch(r'[A-Za-z0-9_./:@-]+', value):
                raise ValueError(f'invalid non-secret output for {token}')
            text = text.replace(token, value)
        if p.name == 'kustomization.yaml' and 'overlays' in p.parts and 'apps' in p.parts:
            service = p.parts[p.parts.index('apps')+1]
            image = outputs['ocir_repositories'][service]['image_path']
            text = re.sub(r'newName: .*', 'newName: ' + image, text)
            text = re.sub(r'newTag: .*', 'newTag: ' + tag, text)
        if re.search(r'__[A-Z0-9_]+__|ocir\.invalid|replace-with', text):
            raise ValueError(f'unresolved placeholders in {p.relative_to(gitops)}')
        pending[p] = text
    # Validate all substitutions before writing any file; repeated use preserves non-image settings.
    for p, text in pending.items():
        p.write_text(text)
    print('Configured non-secret GitOps inputs. Review diff and run validator --ready. Nothing applied or pushed.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gitops-root', required=True, type=Path)
    parser.add_argument('--initial-image-tag', required=True)
    parser.add_argument('--outputs-json', type=Path, help='Offline fixture or terraform output -json file; never a state file')
    args = parser.parse_args()
    raw = args.outputs_json.read_text() if args.outputs_json else subprocess.check_output(['terraform', f'-chdir={ROOT}/infra/environments/homolog/core', 'output', '-json'], text=True)
    document = json.loads(raw)
    outputs = {k: v['value'] for k, v in document.items()}
    configure(outputs, args.gitops_root.resolve(), args.initial_image_tag)


if __name__ == '__main__':
    main()
