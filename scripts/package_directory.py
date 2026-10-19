"""Preflight and build a reproducible skills-only directory submission ZIP.

This local check does not submit, publish, or replace OpenAI's portal scans.
"""
import argparse
import hashlib
import io
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

from plugin_version import declarations

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = ('LICENSE', 'README.md', 'PRIVACY.md', 'SUPPORT.md', 'INSTALL.md', 'CHANGELOG.md', 'AGENTS.md')


def git_env():
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull, GIT_TERMINAL_PROMPT='0')
    return env


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, env=git_env())


def package_files(root):
    documents, _, version = declarations(root)
    manifest = documents['plugin.json']
    interface = manifest['extensions']['com.openai']['interface']
    limits = {'displayName': 30, 'shortDescription': 30, 'longDescription': 4000, 'developerName': 80}
    for key, limit in limits.items():
        value = interface.get(key)
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise ValueError(f'{key} must contain 1 to {limit} characters')
    if interface.get('category') != 'Productivity':
        raise ValueError('Confirm the intended Productivity category in the portal')
    prompts = interface.get('defaultPrompt', [])
    if isinstance(prompts, str):
        prompts = [prompts]
    if not isinstance(prompts, list) or len(prompts) > 3 or any(
            not isinstance(p, str) or not p.strip() or len(p) > 128 or '@' in p for p in prompts):
        raise ValueError('Use at most three distinct starter prompts of 1 to 128 characters without @mentions')
    if len(set(prompts)) != len(prompts):
        raise ValueError('Starter prompts must be distinct')
    for key in ('websiteURL', 'supportURL', 'privacyPolicyURL'):
        value = interface.get(key, '')
        url = urlsplit(value)
        base = '/WellDunDun/arabic-poetry'
        if (len(value) > 1024 or url.scheme != 'https' or url.netloc != 'github.com'
                or not (url.path == base or url.path.startswith(base + '/'))):
            raise ValueError(f'{key} must identify this repository over HTTPS')
    files = {'plugin.json', '.claude-plugin/plugin.json', *DOCUMENTS}
    for key in ('logo', 'composerIcon'):
        value = interface.get(key, '')
        path = PurePosixPath(value)
        if not value.startswith('./assets/plugin/') or '..' in path.parts or path.suffix != '.svg':
            raise ValueError(f'{key} must reference a bundled SVG under ./assets/plugin/')
        icon = root / path
        if icon.is_symlink() or icon.stat().st_size > 5 * 1024 * 1024:
            raise ValueError('Listing icons must be real files of at most 5 MiB')
        svg = ET.fromstring(icon.read_bytes())
        box = [float(v) for v in svg.attrib.get('viewBox', '').split()]
        if len(box) != 4 or box[2] != box[3] or box[2] < 48:
            raise ValueError('Listing icons need a square viewBox of at least 48 units')
        files.add(path.as_posix())
    tracked = git(root, 'ls-files', '-z', '--', 'skills/arabic-poetry').decode().split('\0')
    files.update(name for name in tracked if name)
    if 'skills/arabic-poetry/SKILL.md' not in files:
        raise ValueError('The tracked arabic-poetry skill is missing')
    for name in files:
        path = root / name
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError(f'Not a real package file inside the repository: {name}')
    return version, sorted(files)


def build(root, output):
    if output.suffix != '.zip':
        raise ValueError('The output filename must end in .zip')
    if output.resolve().is_relative_to(root.resolve()):
        raise ValueError('Write generated archives outside the Git checkout')
    version, names = package_files(root)
    if git(root, 'status', '--porcelain', '--untracked-files=all', '--', *names).strip():
        raise ValueError('Commit package inputs before building the submission archive')
    commit = git(root, 'rev-parse', 'HEAD').decode().strip()
    content = {name: git(root, 'show', f'{commit}:{name}') for name in names}
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in content.items():
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    data = buffer.getvalue()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)
    return {'version': version, 'source_commit': commit,
            'archive_sha256': hashlib.sha256(data).hexdigest(),
            'files': {name: hashlib.sha256(value).hexdigest() for name, value in content.items()},
            'limits': 'Local preflight only; no portal scan, browser activation, submission or publication.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='ZIP path outside the checkout; omit for preflight only')
    args = parser.parse_args()
    try:
        if args.output:
            report = build(ROOT, args.output)
            args.output.with_suffix('.json').write_text(json.dumps(report, indent=2) + '\n')
            print(f'Built {args.output} with {len(report["files"])} files, version {report["version"]}')
        else:
            version, names = package_files(ROOT)
            print(f'PASS local directory preflight: version {version}, {len(names)} package files')
    except (ValueError, OSError, KeyError, TypeError, ET.ParseError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
