#!/usr/bin/env python3
"""
Find Finnish fence companies WITHOUT API
Scrapes multiple Finnish sources:
1. Google search results (public HTML)
2. Finnish business directories
3. Company websites for emails

100% FREE - No API required
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import csv
import logging
from urllib.parse import quote, urljoin
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

# Finnish fence-related search terms
SEARCH_TERMS = [
    "aita yritys suomi yhteystiedot",
    "aidat myynti finland email",
    "verkkoaita helsinki yhteystiedot",
    "puuaita yritys suomi",
    "metalliportti finland contact",
    "aitaus palvelu yhteystiedot",
    "rakennusaita vuokraus suomi",
    "betoniaita myynti finland",
]

class FinnishCompanyScraper:
    def __init__(self):
        self.session = requests.Session()
        self.found_companies = {}  # website -> company info

    def get_random_user_agent(self):
        return random.choice(USER_AGENTS)

    def extract_emails(self, text):
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = set(re.findall(email_pattern, text))

        # Filter out fake emails
        filtered = set()
        for email in emails:
            email_lower = email.lower()
            if not any(skip in email_lower for skip in [
                'example.', 'test.', 'dummy.', '@sentry.', 'noreply@',
                'no-reply@', 'privacy@', 'webmaster@'
            ]):
                filtered.add(email)
        return filtered

    def is_finnish_fence_company(self, text):
        """Check if text mentions fence-related terms"""
        text_lower = text.lower()
        keywords = ['aita', 'aidat', 'aitaus', 'portti', 'verkkoaita', 'puuaita', 'fence']
        return any(keyword in text_lower for keyword in keywords)

    def google_search_scrape(self, query, max_results=20):
        """
        Scrape Google search results (public HTML)
        No API needed
        """
        companies = []

        try:
            # Google search URL
            url = f"https://www.google.com/search?q={quote(query)}&num={max_results}"

            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'fi-FI,fi;q=0.9,en;q=0.8',
            }

            response = self.session.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find search result divs
                results = soup.find_all('div', class_='g')

                for result in results:
                    try:
                        # Extract link
                        link_tag = result.find('a', href=True)
                        if not link_tag:
                            continue

                        url = link_tag['href']
                        if not url.startswith('http'):
                            continue

                        # Skip non-company sites
                        if any(skip in url for skip in ['google.', 'facebook.', 'youtube.', 'wikipedia.']):
                            continue

                        # Extract title
                        title_tag = result.find('h3')
                        title = title_tag.get_text(strip=True) if title_tag else url

                        # Check if it's fence-related
                        snippet = result.get_text()
                        if self.is_finnish_fence_company(snippet):
                            companies.append({
                                'name': title,
                                'url': url
                            })
                            logging.info(f"  Found: {title[:60]}")

                    except Exception as e:
                        continue

        except Exception as e:
            logging.error(f"Google search error: {e}")

        return companies

    def scrape_website_for_emails(self, url, company_name):
        """Scrape a company website for email addresses"""
        try:
            headers = {
                'User-Agent': self.get_random_user_agent(),
            }

            response = self.session.get(url, headers=headers, timeout=10, verify=False)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Remove scripts
                for script in soup(['script', 'style']):
                    script.decompose()

                # Get text
                text = soup.get_text()

                # Extract emails
                emails = self.extract_emails(text)

                # Also check mailto links
                for a_tag in soup.find_all('a', href=True):
                    if a_tag['href'].startswith('mailto:'):
                        email = a_tag['href'].replace('mailto:', '').split('?')[0]
                        emails.add(email)

                return emails

        except Exception as e:
            pass

        return set()

    def search_bing(self, query, max_results=10):
        """
        Bing search as alternative (no API needed)
        Often has less restrictions than Google
        """
        companies = []

        try:
            url = f"https://www.bing.com/search?q={quote(query)}&count={max_results}"

            headers = {
                'User-Agent': self.get_random_user_agent(),
            }

            response = self.session.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find search results
                results = soup.find_all('li', class_='b_algo')

                for result in results:
                    try:
                        link_tag = result.find('a', href=True)
                        if not link_tag:
                            continue

                        url = link_tag['href']
                        title = link_tag.get_text(strip=True)

                        # Skip social media
                        if any(skip in url for skip in ['facebook.', 'linkedin.', 'youtube.']):
                            continue

                        snippet = result.get_text()
                        if self.is_finnish_fence_company(snippet):
                            companies.append({
                                'name': title,
                                'url': url
                            })
                            logging.info(f"  Found: {title[:60]}")

                    except Exception as e:
                        continue

        except Exception as e:
            logging.error(f"Bing search error: {e}")

        return companies


def main():
    OUTPUT_FILE = 'SCRAPED_FINNISH_COMPANIES.csv'

    logging.info("=" * 80)
    logging.info("Scraping Finnish Fence Companies - NO API REQUIRED")
    logging.info("=" * 80)

    scraper = FinnishCompanyScraper()
    all_companies = []

    # Search Google for each term
    for i, term in enumerate(SEARCH_TERMS, 1):
        logging.info(f"\n[{i}/{len(SEARCH_TERMS)}] Searching Google: {term}")

        companies = scraper.google_search_scrape(term, max_results=15)
        all_companies.extend(companies)

        time.sleep(random.uniform(3, 6))  # Random delay to avoid blocking

        # Also try Bing as backup
        if i % 2 == 0:  # Every other search
            logging.info(f"  Also searching Bing...")
            bing_companies = scraper.search_bing(term, max_results=10)
            all_companies.extend(bing_companies)
            time.sleep(random.uniform(2, 4))

    # Remove duplicates by URL
    unique_companies = {}
    for company in all_companies:
        url = company['url']
        if url not in unique_companies:
            unique_companies[url] = company

    logging.info(f"\n\nFound {len(unique_companies)} unique companies")
    logging.info("Now scraping websites for email addresses...")

    # Scrape each website for emails
    results = []
    for i, (url, company) in enumerate(unique_companies.items(), 1):
        logging.info(f"\n[{i}/{len(unique_companies)}] {company['name'][:50]}")
        logging.info(f"  URL: {url}")

        emails = scraper.scrape_website_for_emails(url, company['name'])

        if emails:
            email_str = ', '.join(sorted(emails))
            results.append({
                'country': 'Finland',
                'website': url,
                'email': email_str
            })
            logging.info(f"  ✓ Emails: {email_str}")
        else:
            logging.info(f"  ✗ No emails found")

        time.sleep(random.uniform(2, 4))  # Be respectful

    # Save results
    logging.info(f"\n\nSaving {len(results)} companies with emails to: {OUTPUT_FILE}")

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['country', 'website', 'email'])
        writer.writeheader()
        writer.writerows(results)

    logging.info("=" * 80)
    logging.info(f"COMPLETE!")
    logging.info(f"Found: {len(results)} Finnish fence companies with emails")
    logging.info(f"Output: {OUTPUT_FILE}")
    logging.info("=" * 80)


if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
