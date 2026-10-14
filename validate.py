"""Check generated pages, local links/anchors, metadata, and publication coverage."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import hashlib
import json

ROOT = Path(__file__).resolve().parent


class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids = set()
        self.links = []
        self.h1 = 0
        self.mains = 0
        self.publications = []
        self.title = False
        self.meta_description = False
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, (self.path, 'duplicate id', attrs['id'])
            self.ids.add(attrs['id'])
        self.h1 += tag == 'h1'
        self.mains += tag == 'main'
        self.title |= tag == 'title'
        self.meta_description |= tag == 'meta' and attrs.get('name') == 'description' and bool(attrs.get('content'))
        for key in ['href', 'src']:
            if attrs.get(key):
                self.links.append(attrs[key])
        if tag == 'img':
            assert attrs.get('alt'), (self.path, 'image lacks alt')
        if 'data-publication' in attrs:
            self.publications.append(attrs['id'])


pages = {p.name: Document(p) for p in ROOT.glob('*.html')}
assert set(pages) == {'index.html', 'research.html', 'publications.html', 'code.html', 'contact.html', '404.html'}
local_links = external_links = 0
for name, doc in pages.items():
    assert doc.h1 == doc.mains == 1 and doc.title and doc.meta_description
    for url in doc.links:
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            assert parsed.scheme in {'https', 'mailto'}, (name, url)
            external_links += 1
            continue
        target = unquote(parsed.path).lstrip('/') or name
        assert (ROOT / target).is_file(), (name, 'missing asset/page', url)
        if parsed.fragment and target.endswith('.html'):
            assert unquote(parsed.fragment) in pages[target].ids, (name, 'missing anchor', url)
        local_links += 1

papers = json.loads((ROOT / 'data/publications.json').read_text())
assert len(papers) == 11
assert set(pages['publications.html'].publications) == {p['id'] for p in papers}
assert all('Anirban Pal' in p['authors'] for p in papers)
assert all(p['category'] == 'submission' for p in papers if 'Submitted' in p['status'] or 'Submission' in p['status'])
bib = (ROOT / 'publications.bib').read_text()
assert bib.count('@misc{') + bib.count('@article{') == len(papers)
assert bib.count('@article{') == len([p for p in papers if p['category'] == 'journal']) == 2
assert len({p.get('doi') for p in papers if p.get('doi')}) == 2
assert all(p.get('journal') and p.get('volume') and p.get('doi') for p in papers if p['category'] == 'journal')
assert (ROOT / '.nojekyll').exists()
assert (ROOT / 'assets/portrait.png').stat().st_size > 0
for p in papers:
    assert p['title'].replace('&', '&amp;') in (ROOT / 'publications.html').read_text()
    assert p['record_label'] == 'Author profile' or p.get('url') or p['id'] == 'vector-plus'
assert 'vector-plus-manuscript' not in ''.join(p.read_text() for p in ROOT.glob('*.html'))
assert 'github.com/alphago1234/vector-plus' not in ''.join(p.read_text() for p in ROOT.glob('*.html'))
receipt = {'status': 'passed', 'pages': len(pages), 'publication_records': len(papers),
           'local_links_and_anchors_checked': local_links, 'external_links_syntax_checked': external_links,
           'checks': ['all page targets/assets and internal anchors exist', 'one h1 and main per page',
                      'titles and descriptions', 'image alternative text', 'all publication records rendered',
                      'submission statuses retained', 'no private experiment repository links', 'BibTeX record coverage'],
           'limits': 'No graphical-browser preview available in this session. External destinations checked separately where accessible; live OpenReview verification blocked.',
           'page_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in pages}}
(ROOT / 'VALIDATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
