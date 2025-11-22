"""
Web Scraper for Content Gap Analysis
Collects data from OpenProject and competitors (Asana, Trello, Monday.com)
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta
import re
import hashlib

class ContentScraper:
    """Scrapes content from project management tool websites"""
    
    def __init__(self, deduplicate: bool = True, refresh_days: int = 30, force: bool = False, index_path: str = 'data/scrape_index.json'):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.deduplicate = deduplicate
        self.refresh_days = refresh_days
        self.force = force
        self.index_path = index_path
        self.index = self._load_index()

    # ----------------------------------------------------------------------------------
    # Index Management
    # ----------------------------------------------------------------------------------
    def _load_index(self):
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {'entries': []}
        return {'entries': []}

    def _save_index(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)

    def _find_by_url(self, url):
        for e in self.index['entries']:
            if e['url'] == url:
                return e
        return None

    def _find_by_hash(self, content_hash):
        for e in self.index['entries']:
            if e['content_hash'] == content_hash:
                return e
        return None

    def _add_index_entry(self, url, title, content_hash, word_count):
        entry = self._find_by_url(url)
        now = datetime.utcnow().isoformat()
        if entry:
            entry.update({'title': title, 'content_hash': content_hash, 'word_count': word_count, 'last_scraped': now})
        else:
            self.index['entries'].append({
                'url': url,
                'title': title,
                'content_hash': content_hash,
                'word_count': word_count,
                'first_scraped': now,
                'last_scraped': now
            })
        self._save_index()

    def _is_fresh(self, entry):
        if not entry:
            return False
        try:
            last = datetime.fromisoformat(entry['last_scraped'].replace('Z', ''))
        except Exception:
            return False
        return datetime.utcnow() - last < timedelta(days=self.refresh_days)
    
    def scrape_page(self, url, max_retries=3):
        """Scrape a single page"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            except Exception as e:
                print(f"  ⚠ Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    return None
    
    def extract_content(self, html, url):
        """Extract structured content from HTML"""
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract title
        title = soup.find('title')
        title = title.get_text().strip() if title else urlparse(url).path.strip('/')
        
        # Extract main content
        content_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li'])
        content = ' '.join([tag.get_text().strip() for tag in content_tags if tag.get_text().strip()])
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc and 'content' in meta_desc.attrs else ''
        
        # Extract keywords from meta or generate from content
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and 'content' in meta_keywords.attrs:
            keywords = [k.strip() for k in meta_keywords['content'].split(',')]
        else:
            # Extract common words as keywords
            words = re.findall(r'\b[a-z]{4,}\b', content.lower())
            from collections import Counter
            keywords = [word for word, count in Counter(words).most_common(10)]
        
        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = urljoin(url, link['href'])
            if urlparse(href).netloc == urlparse(url).netloc:
                links.append(href)
        
        # Count words
        word_count = len(content.split())

        # Content hash (normalized)
        normalized = re.sub(r'\s+', ' ', content.strip().lower())
        content_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
        
        return {
            'title': title,
            'url': url,
            'published_at': None,
            'updated_at': datetime.now().isoformat(),
            'author': None,
            'tags': keywords[:10],
            'content_type': 'webpage',
            'word_count': word_count,
            'content': content[:5000],  # Limit content length
            'description': description,
            'links': links[:20],  # Limit links
            'entities': [],
            'language': 'en',
            'content_hash': content_hash
        }
    
    def save_content(self, content_data, output_dir, filename):
        """Save content as JSON"""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Remove hash before persisting if not needed externally (keep for now)
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def scrape_openproject(self, max_pages=20):
        """Scrape OpenProject website"""
        print("\n🔍 Scraping OpenProject...")
        
        urls = [
            'https://www.openproject.org/docs/',
            'https://www.openproject.org/docs/user-guide/',
            'https://www.openproject.org/docs/user-guide/gantt-chart/',
            'https://www.openproject.org/docs/user-guide/wiki/',
            'https://www.openproject.org/docs/user-guide/time-and-costs/',
            'https://www.openproject.org/docs/user-guide/agile-boards/',
            'https://www.openproject.org/docs/installation-and-operations/',
            'https://www.openproject.org/blog/',
            'https://www.openproject.org/collaboration-software/',
            'https://www.openproject.org/project-management/',
            'https://www.openproject.org/features/',
            'https://www.openproject.org/pricing/',
            'https://www.openproject.org/download-and-installation/',
            'https://www.openproject.org/security/',
            'https://www.openproject.org/integrations/',
            'https://www.openproject.org/api/',
            'https://www.openproject.org/roadmap/',
            'https://www.openproject.org/cloud-edition/',
            'https://www.openproject.org/on-premises/',
            'https://www.openproject.org/enterprise/',
        ]
        
        scraped = 0
        for url in urls[:max_pages]:
            print(f"  📄 Scraping: {url}")
            if self.deduplicate:
                existing = self._find_by_url(url)
                if existing and (self.force is False) and self._is_fresh(existing):
                    print("    ↷ Skipped (fresh in index, deduplicate ON)")
                    continue
            html = self.scrape_page(url)
            if html:
                content = self.extract_content(html, url)
                if content and content['word_count'] > 100:
                    if self.deduplicate:
                        duplicate = self._find_by_hash(content['content_hash'])
                        if duplicate and duplicate['url'] != url:
                            print(f"    ↷ Skipped (duplicate content of {duplicate['url']})")
                            continue
                    filename = f"openproject_{urlparse(url).path.strip('/').replace('/', '_')[:50]}.json"
                    filepath = self.save_content(content, 'data/your_content', filename)
                    print(f"    ✓ Saved: {filename} ({content['word_count']} words)")
                    if self.deduplicate:
                        self._add_index_entry(url, content['title'], content['content_hash'], content['word_count'])
                    scraped += 1
                    time.sleep(1)  # Be polite
        
        print(f"✅ OpenProject: {scraped} pages scraped")
        return scraped
    
    def scrape_asana(self, max_pages=20):
        """Scrape Asana website"""
        print("\n🔍 Scraping Asana...")
        
        urls = [
            'https://asana.com/guide',
            'https://asana.com/guide/team/project-management',
            'https://asana.com/guide/examples/project-management/project-plan',
            'https://asana.com/resources',
            'https://asana.com/resources/gantt-chart-basics',
            'https://asana.com/resources/raci-chart',
            'https://asana.com/resources/work-breakdown-structure',
            'https://asana.com/resources/project-roadmap',
            'https://asana.com/resources/agile-methodology',
            'https://asana.com/resources/scrum-sprint',
            'https://asana.com/product',
            'https://asana.com/pricing',
            'https://asana.com/features',
            'https://asana.com/templates',
            'https://asana.com/uses/project-management',
            'https://asana.com/uses/work-management',
            'https://asana.com/uses/goal-management',
            'https://asana.com/enterprise',
            'https://asana.com/developers',
            'https://asana.com/apps',
        ]
        
        scraped = 0
        for url in urls[:max_pages]:
            print(f"  📄 Scraping: {url}")
            if self.deduplicate:
                existing = self._find_by_url(url)
                if existing and (self.force is False) and self._is_fresh(existing):
                    print("    ↷ Skipped (fresh in index, deduplicate ON)")
                    continue
            html = self.scrape_page(url)
            if html:
                content = self.extract_content(html, url)
                if content and content['word_count'] > 100:
                    if self.deduplicate:
                        duplicate = self._find_by_hash(content['content_hash'])
                        if duplicate and duplicate['url'] != url:
                            print(f"    ↷ Skipped (duplicate content of {duplicate['url']})")
                            continue
                    filename = f"asana_{urlparse(url).path.strip('/').replace('/', '_')[:50]}.json"
                    filepath = self.save_content(content, 'data/competitor_content', filename)
                    print(f"    ✓ Saved: {filename} ({content['word_count']} words)")
                    if self.deduplicate:
                        self._add_index_entry(url, content['title'], content['content_hash'], content['word_count'])
                    scraped += 1
                    time.sleep(1)
        
        print(f"✅ Asana: {scraped} pages scraped")
        return scraped
    
    def scrape_trello(self, max_pages=15):
        """Scrape Trello website"""
        print("\n🔍 Scraping Trello...")
        
        urls = [
            'https://trello.com/guide',
            'https://trello.com/en/tour',
            'https://trello.com/templates',
            'https://trello.com/pricing',
            'https://trello.com/enterprise',
            'https://trello.com/power-ups',
            'https://trello.com/use-cases/project-management',
            'https://trello.com/use-cases/remote-work',
            'https://trello.com/use-cases/agile-sprint-board',
            'https://trello.com/use-cases/kanban-board',
            'https://trello.com/platforms',
            'https://trello.com/integrations',
            'https://blog.trello.com/',
            'https://trello.com/about',
            'https://trello.com/teams',
        ]
        
        scraped = 0
        for url in urls[:max_pages]:
            print(f"  📄 Scraping: {url}")
            if self.deduplicate:
                existing = self._find_by_url(url)
                if existing and (self.force is False) and self._is_fresh(existing):
                    print("    ↷ Skipped (fresh in index, deduplicate ON)")
                    continue
            html = self.scrape_page(url)
            if html:
                content = self.extract_content(html, url)
                if content and content['word_count'] > 100:
                    if self.deduplicate:
                        duplicate = self._find_by_hash(content['content_hash'])
                        if duplicate and duplicate['url'] != url:
                            print(f"    ↷ Skipped (duplicate content of {duplicate['url']})")
                            continue
                    filename = f"trello_{urlparse(url).path.strip('/').replace('/', '_')[:50]}.json"
                    filepath = self.save_content(content, 'data/competitor_content', filename)
                    print(f"    ✓ Saved: {filename} ({content['word_count']} words)")
                    if self.deduplicate:
                        self._add_index_entry(url, content['title'], content['content_hash'], content['word_count'])
                    scraped += 1
                    time.sleep(1)
        
        print(f"✅ Trello: {scraped} pages scraped")
        return scraped
    
    def scrape_monday(self, max_pages=15):
        """Scrape Monday.com website"""
        print("\n🔍 Scraping Monday.com...")
        
        urls = [
            'https://monday.com/product',
            'https://monday.com/pricing',
            'https://monday.com/templates',
            'https://monday.com/use-cases/project-management',
            'https://monday.com/use-cases/portfolio-management',
            'https://monday.com/features',
            'https://monday.com/integrations',
            'https://monday.com/marketplace',
            'https://monday.com/enterprise',
            'https://monday.com/developers',
            'https://monday.com/lang/resources',
            'https://monday.com/blog',
            'https://monday.com/automations',
            'https://monday.com/gantt',
            'https://monday.com/kanban',
        ]
        
        scraped = 0
        for url in urls[:max_pages]:
            print(f"  📄 Scraping: {url}")
            if self.deduplicate:
                existing = self._find_by_url(url)
                if existing and (self.force is False) and self._is_fresh(existing):
                    print("    ↷ Skipped (fresh in index, deduplicate ON)")
                    continue
            html = self.scrape_page(url)
            if html:
                content = self.extract_content(html, url)
                if content and content['word_count'] > 100:
                    if self.deduplicate:
                        duplicate = self._find_by_hash(content['content_hash'])
                        if duplicate and duplicate['url'] != url:
                            print(f"    ↷ Skipped (duplicate content of {duplicate['url']})")
                            continue
                    filename = f"monday_{urlparse(url).path.strip('/').replace('/', '_')[:50]}.json"
                    filepath = self.save_content(content, 'data/competitor_content', filename)
                    print(f"    ✓ Saved: {filename} ({content['word_count']} words)")
                    if self.deduplicate:
                        self._add_index_entry(url, content['title'], content['content_hash'], content['word_count'])
                    scraped += 1
                    time.sleep(1)
        
        print(f"✅ Monday.com: {scraped} pages scraped")
        return scraped
    
    def run_full_scrape(self, openproject_pages=20, competitor_pages=15):
        """Run complete scraping operation"""
        print("=" * 80)
        print("CONTENT SCRAPER FOR GAP ANALYSIS")
        print("=" * 80)
        
        total = 0
        
        # Scrape your company
        total += self.scrape_openproject(openproject_pages)
        
        # Scrape competitors
        total += self.scrape_asana(competitor_pages)
        total += self.scrape_trello(competitor_pages)
        total += self.scrape_monday(competitor_pages)
        
        print("\n" + "=" * 80)
        print(f"✅ SCRAPING COMPLETE - {total} pages collected")
        print("=" * 80)
        print("\n📊 Next steps:")
        print("  1. Review scraped data in data/your_content and data/competitor_content")
        print("  2. Run: python main.py")
        print("  3. Analyze updated gaps and recommendations")
        
        return total


def main():
    scraper = ContentScraper(
        deduplicate=True,
        refresh_days=30,
        force=False
    )
    
    # Configuration
    OPENPROJECT_PAGES = 20
    COMPETITOR_PAGES_EACH = 15
    
    print("\n🚀 Starting web scraper...")
    print(f"   OpenProject pages: {OPENPROJECT_PAGES}")
    print(f"   Competitor pages each: {COMPETITOR_PAGES_EACH}")
    print("\n⚠ Note: This respects robots.txt and includes delays between requests")
    print("⚙ Deduplication: ON (content hash + URL index)")
    print(f"⚙ Refresh window: {scraper.refresh_days} days (older pages will be re-scraped)")
    if scraper.force:
        print("⚙ Force mode: ON (all pages will be re-scraped regardless of freshness)")
    print(f"📇 Index file: {scraper.index_path} (entries: {len(scraper.index['entries'])})")
    
    input("\nPress Enter to start scraping...")
    
    total = scraper.run_full_scrape(
        openproject_pages=OPENPROJECT_PAGES,
        competitor_pages=COMPETITOR_PAGES_EACH
    )
    
    print(f"\n🎯 Total pages scraped: {total}")


if __name__ == '__main__':
    main()
