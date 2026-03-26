#!/usr/bin/env python3
"""
Find additional Finnish fence companies using free web scraping
Searches Finnish business directories and websites for fence-related companies
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import csv
import logging
from urllib.parse import urljoin, quote

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Finnish fence-related keywords
FINNISH_KEYWORDS = [
    'aita',           # fence
    'aidat',          # fences
    'aitaus',         # fencing
    'verkkoaita',     # wire fence
    'puuaita',        # wooden fence
    'metalliportti',  # metal gate
    'portti',         # gate
]

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

class FinnishCompanyFinder:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        self.found_companies = set()  # Track unique companies by website

    def extract_emails(self, text):
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = set(re.findall(email_pattern, text))

        # Filter out common false positives
        filtered = set()
        for email in emails:
            email_lower = email.lower()
            if not any(skip in email_lower for skip in ['example.', 'test.', 'dummy.', '@sentry.']):
                filtered.add(email)
        return filtered

    def normalize_url(self, url):
        """Normalize URL"""
        if not url:
            return None
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url

    def search_finder_fi(self, keyword, max_pages=3):
        """
        Search Finder.fi - Finnish business directory
        Free public directory
        """
        companies = []
        logging.info(f"Searching Finder.fi for: {keyword}")

        for page in range(1, max_pages + 1):
            try:
                # Finder.fi search URL
                url = f"https://www.finder.fi/search?what={quote(keyword)}&page={page}"

                response = self.session.get(url, timeout=10)
                if response.status_code != 200:
                    break

                soup = BeautifulSoup(response.content, 'html.parser')

                # Find company listings
                listings = soup.find_all('div', class_='search-result')

                if not listings:
                    break

                for listing in listings:
                    try:
                        # Extract company name
                        name_tag = listing.find('h3')
                        if not name_tag:
                            continue
                        company_name = name_tag.get_text(strip=True)

                        # Extract website
                        website = None
                        link_tag = listing.find('a', href=True)
                        if link_tag and 'http' in link_tag['href']:
                            website = link_tag['href']

                        # Extract email if visible
                        email = None
                        email_tag = listing.find('a', href=lambda x: x and 'mailto:' in x)
                        if email_tag:
                            email = email_tag['href'].replace('mailto:', '').split('?')[0]

                        if website and website not in self.found_companies:
                            self.found_companies.add(website)
                            companies.append({
                                'name': company_name,
                                'website': website,
                                'email': email or '',
                                'source': 'Finder.fi'
                            })
                            logging.info(f"  Found: {company_name}")
                    except Exception as e:
                        continue

                time.sleep(2)  # Be respectful

            except Exception as e:
                logging.error(f"Error searching Finder.fi: {e}")
                break

        return companies

    def search_yellow_pages(self, keyword, max_results=20):
        """
        Search Finnish yellow pages / directories
        Public business listings
        """
        companies = []
        logging.info(f"Searching for: {keyword}")

        # This is a placeholder - you would implement specific directory searches
        # For now, we'll use a generic search approach

        return companies

    def scrape_company_website(self, url):
        """Scrape a company website for email addresses"""
        try:
            response = self.session.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Remove scripts
                for script in soup(['script', 'style']):
                    script.decompose()

                text = soup.get_text()
                emails = self.extract_emails(text)

                # Also check mailto links
                for a_tag in soup.find_all('a', href=True):
                    if a_tag['href'].startswith('mailto:'):
                        email = a_tag['href'].replace('mailto:', '').split('?')[0]
                        emails.add(email)

                return emails
        except:
            pass
        return set()


def main():
    OUTPUT_FILE = 'ADDITIONAL_FINNISH_FENCE_COMPANIES.csv'

    logging.info("=" * 80)
    logging.info("Searching for Additional Finnish Fence Companies")
    logging.info("Using FREE public sources")
    logging.info("=" * 80)

    finder = FinnishCompanyFinder()
    all_companies = []

    # Search for each Finnish keyword
    for keyword in FINNISH_KEYWORDS[:3]:  # Start with first 3 to be respectful
        companies = finder.search_finder_fi(keyword, max_pages=2)
        all_companies.extend(companies)
        time.sleep(3)  # Be respectful between searches

    logging.info(f"\nFound {len(all_companies)} companies from directories")

    # Try to scrape emails for companies without them
    logging.info("\nScraping websites for email addresses...")
    for i, company in enumerate(all_companies):
        if not company['email'] and company['website']:
            logging.info(f"[{i+1}/{len(all_companies)}] Scraping {company['name']}")
            emails = finder.scrape_company_website(company['website'])
            if emails:
                company['email'] = ', '.join(emails)
            time.sleep(2)  # Be respectful

    # Filter out companies without emails
    companies_with_emails = [c for c in all_companies if c['email']]

    # Save results
    logging.info(f"\nSaving {len(companies_with_emails)} companies with emails to: {OUTPUT_FILE}")

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['country', 'website', 'email'])

        for company in companies_with_emails:
            writer.writerow(['Finland', company['website'], company['email']])

    logging.info("=" * 80)
    logging.info(f"COMPLETE: Found {len(companies_with_emails)} Finnish companies with emails")
    logging.info(f"Output: {OUTPUT_FILE}")
    logging.info("=" * 80)


if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
