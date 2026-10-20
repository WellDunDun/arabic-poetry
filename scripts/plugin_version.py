"""Check plugin versions, or advance all version declarations together."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)')
FILES = ('plugin.json', '.claude-plugin/plugin.json', '.claude-plugin/marketplace.json')


def version_tuple(value):
    if not isinstance(value, str) or not VERSION.fullmatch(value):
        raise ValueError(f'Expected a release version MAJOR.MINOR.PATCH, got {value!r}')
    return tuple(map(int, value.split('.')))


def declarations(root):
    documents = {name: json.loads((root / name).read_text(encoding='utf-8')) for name in FILES}
    return validate_declarations(documents)


def validate_declarations(documents):
    """Check the same release declarations from files or pinned Git objects."""
    catalog = documents[FILES[2]]
    if len(catalog['plugins']) != 1 or catalog['plugins'][0]['name'] != 'arabic-poetry':
        raise ValueError('Expected one arabic-poetry plugin in the Claude marketplace')
    entries = [documents[FILES[0]], documents[FILES[1]], catalog['plugins'][0]]
    if any(entry.get('name') != 'arabic-poetry' for entry in entries):
        raise ValueError('Expected arabic-poetry in every plugin declaration')
    versions = [entry.get('version') for entry in entries]
    for value in versions:
        version_tuple(value)
    if len(set(versions)) != 1:
        raise ValueError(f'Plugin versions differ: {dict(zip(FILES, versions))}')
    return documents, entries, versions[0]


def set_version(root, target):
    documents, entries, current = declarations(root)
    if version_tuple(target) < version_tuple(current):
        raise ValueError('Version must not decrease; release a new patch for a rollback')
    if target != current:
        for entry in entries:
            entry['version'] = target
        for name, document in documents.items():
            (root / name).write_text(json.dumps(document, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('version', nargs='?', help='New release version; omit to check consistency')
    args = parser.parse_args()
    try:
        version = set_version(ROOT, args.version) if args.version else declarations(ROOT)[2]
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'{error}\n')
    print(f'Plugin versions agree: {version}')


if __name__ == '__main__':
    main()
