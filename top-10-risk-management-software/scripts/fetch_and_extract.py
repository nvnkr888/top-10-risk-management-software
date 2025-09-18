#!/usr/bin/env python3
"""
Simple fetch-and-extract script.
Usage: python scripts/fetch_and_extract.py --sources sources.csv
"""
import csv, json, os, argparse, requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {"User-Agent": "top-10-risk-corpus-bot/1.0 (+https://github.com/yourorg/top-10-risk-management-citations)"}


def extract_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    article = soup.find('article')
    if article:
        paragraphs = article.find_all('p')
    else:
        paragraphs = soup.body.find_all('p') if soup.body else []
    text = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
    if not text:
        text = ' '.join(t.strip() for t in soup.stripped_strings)
    return text[:100000]


def main(sources_path):
    out = []
    os.makedirs('data/md', exist_ok=True)
    with open(sources_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            id = row['id']
            url = row['canonical_url']
            print(f'Fetching {id}: {url}')
            text = ''
            try:
                r = requests.get(url, headers=HEADERS, timeout=20)
                if r.status_code == 200:
                    text = extract_text(r.text)
                else:
                    print('WARN', r.status_code)
            except Exception as e:
                print('ERROR', e)
            md_path = row.get('content_path') or f"data/md/{id}.md"
            with open(md_path, 'w', encoding='utf-8') as mdout:
                mdout.write(f"# {id} — {row.get('title')}\n\n")
                mdout.write(f"Canonical URL: {url}\n\n")
                mdout.write(text[:20000])
            obj = {
                'id': id,
                'title': row.get('title'),
                'authors': [a.strip() for a in (row.get('authors') or '').split(';') if a.strip()],
                'publisher': row.get('publisher'),
                'published_date': row.get('published_date'),
                'canonical_url': url,
                'archived_url': row.get('archived_url'),
                'license': row.get('license'),
                'language': row.get('language') or 'en',
                'short_summary': row.get('short_summary'),
                'text': text,
                'metadata': {'topic': row.get('topic')},
                'crawler_date': datetime.utcnow().strftime('%Y-%m-%d')
            }
            out.append(obj)
    with open('data/jsonl/all.jsonl', 'w', encoding='utf-8') as jf:
        for o in out:
            jf.write(json.dumps(o, ensure_ascii=False) + '\n')
    print('Wrote', len(out), 'records')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--sources', default='sources.csv')
    args = p.parse_args()
    main(args.sources)
