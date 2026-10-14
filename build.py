"""Render the academic website from explicit, editable publication metadata.

Uses only the Python standard library. Generated HTML is committed for GitHub Pages.
"""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parent
PROFILE = json.loads((ROOT / 'data/profile.json').read_text())
PAPERS = json.loads((ROOT / 'data/publications.json').read_text())
BY_ID = {p['id']: p for p in PAPERS}
BASE = PROFILE['site_url']
NAV = [('index.html', 'Home'), ('research.html', 'Research'), ('publications.html', 'Publications'),
       ('code.html', 'Code'), ('contact.html', 'Contact')]


def link(url, text, **attrs):
    attributes = ''.join(f' {escape(k)}="{escape(str(v), quote=True)}"' for k, v in attrs.items())
    return f'<a href="{escape(url, quote=True)}"{attributes}>{escape(text)}</a>'


def authors(p):
    return ', '.join('<strong>Anirban Pal</strong>' if a == 'Anirban Pal' else escape(a) for a in p['authors'])


def paper(p, summary=None):
    title = link(p['record_url'], p['title']) if p.get('url') or p['id'] == 'vector-plus' else escape(p['title'])
    links = [link(p['record_url'], p['record_label'] + ' ↗')]
    for key, text in [('pdf_url', 'PDF ↗'), ('code_url', 'Code ↗'), ('acceptance_source', 'Conference listing ↗')]:
        if p.get(key):
            links.append(link(p[key], text))
    category = p['category']
    status = p['status']
    if status == 'CAISc 2026':
        status = 'CAISc 2026 · accepted paper'
    description = f'<p class="abstract-line">{escape(summary)}</p>' if summary else ''
    citation = str(p['year'])
    if p.get('journal'):
        locator = p.get('article_number') or p.get('pages', '').replace('-', '–')
        citation = f"{p['journal']} · {p['year']}, {p['volume']}({p['issue']}), {locator}"
    date_note = f'<p class="note">{escape(p["date_note"])}</p>' if p.get('date_note') else ''
    return f'''<article class="pub" id="{escape(p['id'])}" data-publication data-category="{category}">
      <h3>{title}</h3><p class="authors">{authors(p)}</p>
      <div class="pub-meta"><span class="status {category}">{escape(status)}</span> {escape(citation)}</div>
      {date_note}{description}<div class="pub-links">{' '.join(links)}</div></article>'''


def related(ids):
    return '<div class="related"><strong>Related work</strong>' + ''.join(
        link('publications.html#' + id_, BY_ID[id_]['title']) for id_ in ids) + '</div>'


def page(file, title, body, description):
    nav = ''.join(f'<a href="{path}"' + (' aria-current="page"' if path == file else '') + f'>{label}</a>' for path, label in NAV)
    canonical = BASE + '/' + ('' if file == 'index.html' else file)
    schema = {'@context': 'https://schema.org', '@type': 'Person', 'name': PROFILE['name'],
              'url': BASE, 'jobTitle': PROFILE['role'], 'image': BASE + '/assets/portrait.png',
              'sameAs': [PROFILE['github'], PROFILE['openreview'], PROFILE['linkedin'], PROFILE['researchgate']],
              'knowsAbout': ['Representation learning', 'Continual learning', 'Self-supervised learning', 'Foundation models',
                             'Machine learning for biology', 'Molecular design', 'Catalysis']}
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · Anirban Pal</title><meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{canonical}"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website"><meta property="og:title" content="{escape(title, quote=True)} · Anirban Pal">
<meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE}/assets/portrait.png"><meta name="theme-color" content="#fcfbf8">
<link rel="stylesheet" href="assets/style.css"><script src="assets/site.js" defer></script>
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False).replace('<', '&lt;')}</script></head>
<body id="top"><a class="skip" href="#main">Skip to content</a><div class="layout">
<aside class="sidebar" aria-label="Profile and site navigation">
  <img class="portrait" src="assets/portrait.png" alt="Anirban Pal" width="144" height="144">
  <a class="identity" href="index.html">Anirban Pal</a>
  <p class="affiliation">PhD researcher at<br>{escape(PROFILE['affiliation'])}<br>Mumbai, India</p>
  <nav class="nav" aria-label="Main navigation">{nav}</nav>
  <div class="socials">{link(PROFILE['github'], 'GitHub ↗')}{link(PROFILE['openreview'], 'OpenReview ↗')}{link('mailto:' + PROFILE['email'], 'Email ↗')}</div>
  <p class="sidebar-note">Representation learning<br>Machine learning for science</p>
</aside>
<main id="main">{body}<footer class="footer"><span>© 2026 Anirban Pal · Updated {PROFILE['updated']}</span>
<a class="back-top" href="#top">Back to top ↑</a></footer></main></div></body></html>
'''
    if file == '404.html':
        # GitHub can serve the 404 page at nested addresses; use root-relative resources.
        html = html.replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/')
        for path, _ in NAV:
            html = html.replace(f'href="{path}"', f'href="/{path}"')
    (ROOT / file).write_text(html)


bio = PROFILE['bio'].split(' My research spans', 1)
home = '''<p class="eyebrow">MACHINE LEARNING · BIOLOGY · DRUG DISCOVERY</p>
<h1>Learning representations<br>that remain useful.</h1>
<div class="intro"><p>''' + escape(bio[0]) + '''</p><p>My research spans''' + escape(bio[1]) + '''</p></div>
<p class="home-cta">''' + link('research.html', 'Explore my research →') + '''</p>
<section class="section" aria-labelledby="directions"><div class="section-head"><h2 id="directions">Research directions</h2></div>
<div class="themes">
<article class="theme"><span class="number">01</span><h3>Representations &amp; continual learning</h3><p>Representation drift, feature alignment, and knowledge retention as models and data change.</p></article>
<article class="theme"><span class="number">02</span><h3>Foundation models &amp; world models</h3><p>Self-supervised features, latent prediction, and adaptation of pretrained representations.</p></article>
<article class="theme"><span class="number">03</span><h3>Biological and Molecular Representation Learning</h3><p>Learning from biological and chemical data for cancer research, drug discovery, and catalysis.</p></article>
</div></section>
<section class="section" aria-labelledby="selected"><div class="section-head"><h2 id="selected">Selected work</h2>''' + link('publications.html', 'All publications →') + '</div>'
home += '''<article class="pub" id="foundation-model-work"><h3>Foundation-model representations</h3>
<div class="pub-meta"><span class="status">Ongoing research</span></div>
<p class="abstract-line">Studying what pretrained representations retain, how they change during adaptation, and how they transfer to downstream tasks. This work connects self-supervised learning and JEPA-based world models with continual learning and biological and molecular applications.</p>
<div class="pub-links">''' + link('research.html#foundation-models', 'Research direction →') + '</div></article>'
for id_ in ['repairable-geometry', 'pixel-reconstruction', 'latent-planning', 'vector-plus', 'pyridines-from-nitroarenes', 'picolinamide-chalcogenation']:
    home += paper(BY_ID[id_])
home += '''</section><section class="section" aria-labelledby="news"><div class="section-head"><h2 id="news">Recent work</h2></div>
<ul class="news"><li><time>2026</time><span>Two papers with Aarav Gupta on latent prediction and latent-space planning appear in the ''' + link('https://caisc2026.github.io/accepted_papers.html', 'CAISc accepted-paper list') + '''.</span></li>
<li><time>2026</time><span>Work with Atharva Airen examines representation drift, test-time feature alignment, gradient reuse, and retrieval compatibility. ''' + link('publications.html', 'Publication records →') + '''</span></li>
<li><time>2025</time><span>''' + link('https://arxiv.org/abs/2509.00684', 'VECTOR+') + ''' introduces property-guided contrastive learning and latent-space sampling for molecular design.</span></li></ul></section>'''
page('index.html', 'Home', home, 'Anirban Pal, PhD researcher at IIT Bombay Monash. Machine learning, biology, and drug discovery; representation and continual learning, foundation models, and biological and molecular representation learning.')

research = '''<p class="eyebrow">Research</p><h1>Representations, adaptation,<br>and scientific discovery.</h1>
<p class="page-lead">I study what learned representations preserve, how they change, and whether that information remains useful for downstream tasks.</p>
<section class="research-block" aria-labelledby="continual"><p class="eyebrow">01 · Representation &amp; continual learning</p>
<h2 id="continual">When a model changes, what stays compatible?</h2>
<p>My work with Atharva Airen examines representation drift in continual learning, feature alignment under uncertain correspondence, and compatibility in retrieval. These questions concern the relationship between a changing encoder and the systems that consume its features.</p>
<p class="question">How can we distinguish a change in representation geometry from a loss of information needed by a downstream task?</p>''' + related(['repairable-geometry', 'interface-contract', 'uncertain-correspondence', 'beyond-marginals', 'retrieval-compatibility', 'gradient-reuse']) + '''</section>
<section class="research-block" aria-labelledby="world-models"><p class="eyebrow">02 · Foundation models, self-supervision &amp; world models</p>
<h2 id="world-models">Learning through prediction in latent space.</h2>
<p id="foundation-models">My ongoing foundation-model research focuses on learned representations: the information they retain, their behavior during adaptation, and their usefulness under distribution shift. I am interested in connecting self-supervised pretraining with continual learning, so that adapting a model to a new task does not discard information needed by other tasks.</p>
<p>I am interested in self-supervised learning and JEPA-based world models. My work with Aarav Gupta studies the distinction between pixel reconstruction and latent prediction, alongside action-conditioned sparsity for latent-space planning.</p>
<p class="question">What does a training objective encourage a representation to retain, and which parts are useful for planning?</p>''' + related(['pixel-reconstruction', 'latent-planning']) + '''</section>
<section class="research-block" aria-labelledby="scientific-ml"><p class="eyebrow">03 · Biology &amp; molecular design</p>
<h2 id="scientific-ml">Biological and Molecular Representation Learning</h2>
<p>I study how biological and molecular data can be represented to capture information relevant to disease, molecular properties, and chemical function. My interests include representations learned through self-supervision and pretrained foundation models, with applications in cancer research, drug discovery, and catalysis. A central question is how to adapt these representations when task-specific labels are scarce and assess their usefulness beyond the training data.</p>
<p>In molecular design, VECTOR+ combines a pretrained ChemBERTa encoder with property-guided contrastive learning, latent-space sampling, and molecular decoding. This provides a setting for examining how representation choice and adaptation affect generation from limited target-specific data.</p>
<p>In catalysis, my chemical ML work uses molecular descriptors, predictive models, and fragment recombination to prioritize phosphine-ligand candidates for cross-electrophile coupling.</p>
<p>My collaborative chemistry publications include methods for accessing pharmaceutically relevant pyridines from nitroarenes and for palladium-catalyzed distal C–H chalcogenation of aliphatic picolinamides.</p>
<p class="question">Which information in a learned representation remains useful for new molecules or biological conditions when labelled data are limited?</p>''' + related(['vector-plus', 'pyridines-from-nitroarenes', 'picolinamide-chalcogenation']) + '<p class="related">' + link('code.html', 'Explore the molecular-design and catalysis code →') + '</p></section>'
page('research.html', 'Research', research, 'Research by Anirban Pal on foundation-model representations, continual learning, latent prediction, JEPA-based world models, and biological and molecular representation learning.')

pubs = '''<p class="eyebrow">Publications</p><h1>Papers &amp; research records.</h1>
<p class="page-lead">Journal articles, conference and workshop papers, preprints, and submissions. Submission status is listed explicitly.</p>
<p class="note">''' + link(PROFILE['openreview'], 'OpenReview profile ↗') + ''' · ''' + link('publications.bib', 'Download BibTeX', download='publications.bib') + '''</p>
<div class="tools"><div class="filters" role="group" aria-label="Filter publication status">
<button type="button" data-filter="all" aria-pressed="true">All</button><button type="button" data-filter="journal" aria-pressed="false">Journal articles</button><button type="button" data-filter="accepted" aria-pressed="false">Conference / workshop</button>
<button type="button" data-filter="submission" aria-pressed="false">Submissions</button><button type="button" data-filter="preprint" aria-pressed="false">Preprints</button></div>
<label class="note" for="publication-search">Search publications</label><input class="search" id="publication-search" type="search" placeholder="Title, author, or venue…" autocomplete="off">
<span class="note" id="result-count" role="status" aria-live="polite"></span></div>
<p class="empty" id="empty-results" hidden>No publications match this search.</p>'''
for year in sorted({p['year'] for p in PAPERS}, reverse=True):
    pubs += f'<section data-year-group aria-labelledby="year-{year}"><h2 class="year" id="year-{year}">{year}</h2>'
    for p in sorted([p for p in PAPERS if p['year'] == year], key=lambda x: x.get('posted_date', ''), reverse=True):
        pubs += paper(p)
    pubs += '</section>'
pubs += '<p class="note section">Where an individual paper link is unavailable, “Author profile” opens the corresponding author’s OpenReview publication list.</p>'
page('publications.html', 'Publications', pubs, 'Journal articles, conference and workshop papers, preprints, and submissions by Anirban Pal, with authors, publication status, DOI links, and public code.')

code = '''<p class="eyebrow">Code &amp; projects</p><h1>Research you can explore.</h1>
<p class="page-lead">Public implementations and project resources for molecular generation and chemical machine learning.</p>
<article class="project"><p class="project-label">Molecular generation · Author implementation</p><h2>VECTOR+</h2>
<p>Property-guided contrastive representation learning combined with latent sampling and a molecular decoder. The public author repository accompanies our paper on low-data molecular design.</p>
<div class="project-links">''' + link('https://github.com/amartya21/vector-drug-design', 'Author code ↗') + ' ' + link('https://arxiv.org/abs/2509.00684', 'Paper ↗') + '''</div></article>
<article class="project"><p class="project-label">Catalysis · Molecular descriptors &amp; ligand design</p><h2>Cross-electrophile coupling</h2>
<p>Research notebooks, descriptor tables, and candidate structures for phosphine-ligand discovery. The workflow includes descriptor regression, fragment recombination, and descriptor-based filtering.</p>
<figure class="workflow"><a href="assets/ligand_workflow.svg" aria-label="Open the cross-electrophile-coupling workflow at full size"><img src="assets/ligand_workflow.svg" alt="Ligand-design workflow from descriptor data and predictive models through fragment recombination and candidate filtering" loading="lazy"></a>
<figcaption>Workflow overview. Open the figure to view it at full size.</figcaption></figure>
<div class="project-links">''' + link('https://github.com/alphago1234/Cross-Electrophile-Coupling', 'Repository ↗') + ' ' + link('https://github.com/alphago1234/Cross-Electrophile-Coupling/blob/main/docs/REPRODUCIBILITY.md', 'Workflow & data ↗') + '''</div></article>
<p class="home-cta">''' + link(PROFILE['github'], 'View my GitHub profile →') + '</p>'
page('code.html', 'Code', code, 'Public code and research resources for VECTOR+ molecular generation and descriptor-based phosphine-ligand discovery for cross-electrophile coupling.')

contact = '''<p class="eyebrow">Contact</p><h1>Get in touch.</h1>
<p class="page-lead">For research discussions across representation learning, continual learning, and machine learning for biology and chemistry.</p>
<p>I’m a PhD researcher at IIT Bombay Monash, based in Mumbai, India.</p>
<dl class="contact-list">'''
for label, url, text in [('Email', 'mailto:' + PROFILE['email'], PROFILE['email']), ('GitHub', PROFILE['github'], 'alphago1234'),
                          ('OpenReview', PROFILE['openreview'], 'Anirban Pal'), ('ResearchGate', PROFILE['researchgate'], 'Anirban Pal'), ('LinkedIn', PROFILE['linkedin'], 'Anirban Pal')]:
    contact += f'<div class="contact-row"><dt>{label}</dt><dd>{link(url, text)}</dd></div>'
contact += '</dl>'
page('contact.html', 'Contact', contact, 'Contact Anirban Pal, PhD researcher at IIT Bombay Monash, for research discussions in machine learning, biology, drug discovery, and catalysis.')

# Only known metadata is included. No DOI, acceptance, or paper-specific URL is invented.
bib = []
for p in PAPERS:
    author = (' and '.join(a['family'] + ', ' + a['given'] for a in p['author_metadata'])
              if p.get('author_metadata') else ' and '.join(' '.join(a.split()[1:]) + ', ' + a.split()[0] for a in p['authors']))
    title = p['title'].replace('&', r'\&').replace('δ', r'$\delta$').replace('–', '--')
    kind = 'article' if p['category'] == 'journal' else 'misc'
    fields = {'title': title, 'author': author, 'year': str(p['year']), 'note': p['status'], 'url': p['record_url']}
    if kind == 'article':
        fields.update(journal=p['journal'], volume=p['volume'], number=p['issue'], doi=p['doi'])
        fields['pages'] = p.get('pages', p.get('article_number', '')).replace('-', '--')
        if p.get('online_date'):
            fields['note'] += '; ' + p['date_note']
    bib.append('@' + kind + '{' + f"pal_{p['id'].replace('-', '_')}_{p['year']},\n" +
               ',\n'.join('  ' + key + ' = {' + value + '}' for key, value in fields.items()) + '\n}')
(ROOT / 'publications.bib').write_text('\n\n'.join(bib) + '\n')
(ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + BASE + '/sitemap.xml\n')
urls = [BASE + '/' + ('' if file == 'index.html' else file) for file, _ in NAV]
(ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join('<url><loc>' + u + '</loc></url>\n' for u in urls) + '</urlset>\n')
page('404.html', 'Page not found', '<p class="eyebrow">404</p><h1>Page not found.</h1><p>This address does not point to a page on my website.</p><p>' + link('/index.html', 'Return to the homepage →') + '</p>', 'The requested page could not be found.')
print(json.dumps({'rendered_pages': 6, 'publication_records': len(PAPERS), 'output': str(ROOT)}, indent=2))
