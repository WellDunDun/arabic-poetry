"""Prepare a private Diwan HTML file with the current poem ready to review.

This writes a local file, not a hosted artifact. Open the returned path with the
current host's local HTML viewer or browser capability after preparation.
"""
import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
MARKER = '<!--DIWAN_INITIAL_POEM-->'
POEM_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}')


def prepare(poem_file, workspace, identity, title, mode='auto'):
    """Reuse the built editor and embed text as data without touching the skill."""
    workspace = Path(workspace).resolve()
    if workspace == SKILL or SKILL in workspace.parents:
        raise ValueError('Choose a writable poem workspace outside the installed skill')
    if not POEM_ID.fullmatch(identity):
        raise ValueError('Poem id must contain 1–64 letters, digits, hyphens or underscores')
    if mode not in ('auto', 'classical', 'free', 'pairs'):
        raise ValueError('Unknown poem layout')
    private = workspace / '.diwan'
    output = private / f'diwan-{identity}.html'
    if Path(poem_file).resolve() == output:
        raise ValueError('The poem input and prepared HTML must be different files')
    text = Path(poem_file).read_text(encoding='utf-8')
    if not text.strip() or not title.strip():
        raise ValueError('Supply a nonempty poem and title')
    source_id = hashlib.sha256((str(workspace) + '\0' + identity).encode()).hexdigest()[:24]
    revision = hashlib.sha256(json.dumps([title, text, mode], ensure_ascii=False).encode()).hexdigest()[:16]
    poem_id = f'local-{source_id}-{revision}'
    poem = {'id': poem_id, 'source_id': source_id, 'title': title, 'text': text, 'choices': [],
            'suggestions': {}, 'status': 'review', 'meter': '', 'mode': mode}
    encoded = json.dumps(poem, ensure_ascii=False)
    for char in ('<', '>', '&', '\u2028', '\u2029'):
        encoded = encoded.replace(char, f'\\u{ord(char):04x}')
    page = (SKILL / 'assets/workbench/diwan.html').read_text(encoding='utf-8')
    if page.count(MARKER) != 1:
        raise ValueError('Installed Diwan template lacks its launch marker; update the skill')
    page = page.replace(MARKER, '<script>window.DiwanInitialPoem=' + encoded + ';</script>')
    private.mkdir(parents=True, exist_ok=True)
    try:
        with (private / '.gitignore').open('x', encoding='utf-8') as ignore:
            ignore.write('*\n')
    except FileExistsError:
        pass
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=private,
                                         prefix='.diwan-', suffix='.tmp', delete=False) as stream:
            temp = Path(stream.name)
            stream.write(page)
        os.replace(temp, output)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
    return {'path': str(output), 'url': output.as_uri(), 'poem_id': poem_id,
            'status': 'prepared', 'opened': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--poem', required=True, type=Path, help='UTF-8 current poem file')
    parser.add_argument('--workspace', required=True, type=Path, help='Writable poem workspace')
    parser.add_argument('--id', required=True, help='Stable id; reuse it when reopening this poem')
    parser.add_argument('--title', required=True)
    parser.add_argument('--mode', default='auto', choices=('auto', 'classical', 'free', 'pairs'))
    args = parser.parse_args()
    try:
        result = prepare(args.poem, args.workspace, args.id, args.title, args.mode)
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
