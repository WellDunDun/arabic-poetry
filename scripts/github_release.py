"""Validate a plugin version bump; publish its reviewed bilingual notes with --publish."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request

import plugin_version as versions

ROOT = Path(__file__).resolve().parents[1]
SHA = re.compile(r'[0-9a-f]{40}')
REPOSITORY = re.compile(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+')


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f'Cannot read release source: {result.stderr.strip()}')
    return result.stdout


def version_at(root, commit):
    documents = {name: json.loads(git(root, 'show', f'{commit}:{name}'))
                 for name in versions.FILES}
    return versions.validate_declarations(documents)[2]


def bilingual_notes(text):
    sections = {}
    current = None
    fence = None
    for line in text.splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif (marker[1][0] == fence[0] and len(marker[1]) >= len(fence)
                  and not line[marker.end():].strip()):
                fence = None
            continue
        if fence:
            continue
        heading = re.fullmatch(r'##\s+(.+?)\s*', line)
        if heading:
            current = heading[1] if heading[1] in ('English', 'العربية') else None
            if current:
                if current in sections:
                    raise ValueError(f'Duplicate release-notes section: {current}')
                sections[current] = []
        elif current:
            sections[current].append(line)
    for name, alphabet in [('English', r'[A-Za-z]'), ('العربية', r'[\u0621-\u064a]')]:
        if not re.search(alphabet, '\n'.join(sections.get(name, []))):
            raise ValueError(f'Release notes need a nonempty ## {name} section in that language')


def pinned_links(text, repository, commit, notes_path):
    try:
        import mistune
        from mistune.renderers.markdown import MarkdownRenderer
    except ImportError as error:
        raise ValueError('Install release tooling with pip install --require-hashes -r scripts/release-requirements.txt') from error
    base = f'https://github.com/{repository}/blob/{commit}/'
    directory = base + str(Path(notes_path).parent).replace(os.sep, '/') + '/'
    def pin(target):
        if target.startswith('#') or urllib.parse.urlsplit(target).scheme or target.startswith('//'):
            return target
        return base + target.lstrip('/') if target.startswith('/') else urllib.parse.urljoin(directory, target)
    markdown = mistune.create_markdown(renderer='ast', plugins=['table', 'strikethrough', 'task_lists', 'footnotes'])
    tokens, state = markdown.parse(text)
    def rewrite(nodes):
        for token in nodes:
            if token['type'] in ('link', 'image'):
                token['attrs']['url'] = pin(token['attrs']['url'])
            rewrite(token.get('children', []))
    rewrite(tokens)
    for reference in state.env.get('ref_links', {}).values():
        reference['url'] = pin(reference['url'])
    class ReleaseMarkdown(MarkdownRenderer):
        def footnote_ref(self, token, state):
            return '[^' + token['raw'] + ']'

        def footnotes(self, token, state):
            return self.render_children(token, state)

        def footnote_item(self, token, state):
            content = self.render_children(token, state).rstrip().replace('\n', '\n    ')
            return '[^' + token['attrs']['key'] + ']: ' + content + '\n\n'
    return ReleaseMarkdown()(tokens, state)


def plan(root, before, commit, repository):
    if not REPOSITORY.fullmatch(repository):
        raise ValueError('Expected a GitHub OWNER/REPO repository')
    if not SHA.fullmatch(before) or not SHA.fullmatch(commit) or before == '0' * 40:
        raise ValueError('Expected full existing before/commit SHAs')
    previous, version = version_at(root, before), version_at(root, commit)
    if versions.version_tuple(version) < versions.version_tuple(previous):
        raise ValueError('Plugin version must not decrease')
    git(root, 'merge-base', '--is-ancestor', before, commit)
    result = {'publish': version != previous, 'version': version, 'commit': commit}
    if not result['publish']:
        return result
    path = f'docs/releases/{version}.md'
    try:
        body = git(root, 'show', f'{commit}:{path}')
    except ValueError as error:
        raise ValueError(f'Missing version-specific release notes: {path}') from error
    if (git(root, 'ls-tree', '--name-only', before, '--', path).strip()
            and git(root, 'show', f'{before}:{path}') == body):
        raise ValueError('Version-specific release notes must be added or changed with the version bump')
    bilingual_notes(body)
    result.update(tag='v' + version, name='Arabic Poetry v' + version,
                  body=pinned_links(body, repository, commit, path))
    return result


class GitHub:
    def __init__(self, repository, token):
        self.base = f'https://api.github.com/repos/{repository}/'
        self.token = token

    def request(self, method, path, data=None, missing=False):
        headers = {'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json',
                   'X-GitHub-Api-Version': '2026-03-10', 'User-Agent': 'arabic-poetry-release'}
        if self.token:
            headers['Authorization'] = 'Bearer ' + self.token
        request = urllib.request.Request(
            self.base + path, method=method,
            data=json.dumps(data, ensure_ascii=False).encode() if data is not None else None,
            headers=headers,
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if missing and error.code == 404:
                return None
            raise RuntimeError(f'GitHub {method} {path} failed with HTTP {error.code}; inspect the run before retrying') from error


def tag_commit(api, tag):
    record = api.request('GET', 'git/ref/tags/' + tag, missing=True)
    if record is None:
        return None
    obj = record['object']
    seen = set()
    while obj['type'] == 'tag':
        if obj['sha'] in seen:
            raise ValueError('Cannot resolve cyclic release tag')
        seen.add(obj['sha'])
        obj = api.request('GET', 'git/tags/' + obj['sha'])['object']
    if obj['type'] != 'commit':
        raise ValueError('Release tag must point to a commit')
    return obj['sha']


def matching_release(release, proposal):
    if (release['tag_name'] != proposal['tag'] or release['draft'] or release['prerelease']
            or release['name'] != proposal['name']
            or not isinstance(release.get('body'), str)
            or release['body'].rstrip() != proposal['body'].rstrip()):
        raise ValueError('Existing or returned release differs from the reviewed notes; it will not be overwritten')


def publish(proposal, api):
    target = tag_commit(api, proposal['tag'])
    if target is not None and target != proposal['commit']:
        raise ValueError('Existing release tag points to another commit; it will not be moved')
    existing = api.request('GET', 'releases/tags/' + proposal['tag'], missing=True)
    if existing is not None:
        matching_release(existing, proposal)
        if target != proposal['commit']:
            raise ValueError('Existing release has no matching commit tag')
        return existing['html_url']
    api.request('POST', 'releases', {
        'tag_name': proposal['tag'], 'target_commitish': proposal['commit'],
        'name': proposal['name'], 'body': proposal['body'],
        'draft': False, 'prerelease': False, 'make_latest': 'legacy',
    })
    # Inspect what GitHub saved. An uncertain POST is not replayed in this run.
    actual = api.request('GET', 'releases/tags/' + proposal['tag'])
    matching_release(actual, proposal)
    if tag_commit(api, proposal['tag']) != proposal['commit']:
        raise ValueError('Published release tag does not match the reviewed commit')
    return actual['html_url']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before', required=True, help='Full SHA before the merge/push')
    parser.add_argument('--commit', required=True, help='Full SHA to release')
    parser.add_argument('--repository', required=True, help='GitHub OWNER/REPO')
    parser.add_argument('--github-output', type=Path, help='Append validated GitHub Actions outputs')
    parser.add_argument('--publish', action='store_true', help='Publish using GH_TOKEN; default is offline validation')
    args = parser.parse_args()
    try:
        proposal = plan(ROOT, args.before, args.commit, args.repository)
        if args.github_output:
            with args.github_output.open('a', encoding='utf-8') as output:
                output.write(f'publish={str(proposal["publish"]).lower()}\nversion={proposal["version"]}\n')
        print(json.dumps({k: v for k, v in proposal.items() if k != 'body'}, indent=2))
        if args.publish and proposal['publish']:
            token = os.environ.get('GH_TOKEN')
            if not token:
                raise ValueError('GH_TOKEN is required for publication')
            print(publish(proposal, GitHub(args.repository, token)))
    except (ValueError, RuntimeError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'Release stopped: {error}\n')


if __name__ == '__main__':
    main()
