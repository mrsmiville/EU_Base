#!/usr/bin/env python3
"""
Step 2: Scrape emails from pre-filtered fence companies
Much faster since we only process ~1,500 companies instead of 14,000
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
import logging
from urllib.parse import urlparse
from typing import Set, Optional
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping_step2.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

class EmailScraper:
    def __init__(self, timeout=10, max_retries=2):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def get_user_agent(self, index=0):
        """Get a user agent from the rotation list"""
        return USER_AGENTS[index % len(USER_AGENTS)]

    def normalize_url(self, url: str) -> Optional[str]:
        """Normalize and validate URL"""
        if pd.isna(url) or not url or url == 'N/A':
            return None

        url = str(url).strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            parsed = urlparse(url)
            if parsed.netloc:
                return url
        except:
            pass
        return None

    def extract_emails(self, text: str) -> Set[str]:
        """Extract all email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = set(re.findall(email_pattern, text))

        # Filter out common false positives
        filtered_emails = set()
        for email in emails:
            email_lower = email.lower()
            if not any(skip in email_lower for skip in ['example.com', 'test.com', 'domain.com', 'yoursite.com']):
                filtered_emails.add(email)

        return filtered_emails

    def scrape_website_emails(self, url: str, user_agent_index: int = 0) -> dict:
        """Scrape website and return emails found"""
        result = {
            'emails': set(),
            'error': None
        }

        normalized_url = self.normalize_url(url)
        if not normalized_url:
            result['error'] = 'Invalid URL'
            return result

        for attempt in range(self.max_retries):
            try:
                headers = {
                    'User-Agent': self.get_user_agent(user_agent_index),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }

                response = self.session.get(
                    normalized_url,
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=True,
                    verify=False
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Remove script and style elements
                    for script in soup(['script', 'style']):
                        script.decompose()

                    # Get text content
                    text = soup.get_text(separator=' ')

                    # Extract emails from text
                    emails_from_text = self.extract_emails(text)

                    # Extract emails from href attributes
                    emails_from_links = set()
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag['href']
                        if href.startswith('mailto:'):
                            email = href.replace('mailto:', '').split('?')[0]
                            emails_from_links.add(email)

                    result['emails'] = emails_from_text | emails_from_links
                    return result

                elif response.status_code == 403:
                    result['error'] = f'Access forbidden (403)'
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                else:
                    result['error'] = f'HTTP {response.status_code}'
                    return result

            except requests.exceptions.Timeout:
                result['error'] = f'Timeout'
                if attempt < self.max_retries - 1:
                    time.sleep(1)
            except requests.exceptions.SSLError:
                result['error'] = 'SSL Error'
                return result
            except requests.exceptions.ConnectionError:
                result['error'] = 'Connection Error'
                return result
            except Exception as e:
                result['error'] = f'Error: {str(e)}'
                return result

        return result

    def close(self):
        """Close the session"""
        self.session.close()


def process_company(row, index, scraper):
    """Process a single company"""
    website = row['website']
    company_name = row['company_name']

    if pd.isna(website) or not website or website == 'N/A':
        return {
            'index': index,
            'emails': set(),
            'error': 'No website',
        }

    logging.info(f"[{index}] Scraping: {company_name} - {website}")

    result = scraper.scrape_website_emails(website, index)

    return {
        'index': index,
        'emails': result['emails'],
        'error': result.get('error'),
    }


def main():
    INPUT_FILE = 'PRE_FILTERED_FENCE_COMPANIES.csv'
    OUTPUT_FILE = 'FINAL_FENCE_COMPANIES_WITH_EMAILS.csv'
    MAX_WORKERS = 10  # Increased since we have fewer companies
    DELAY_BETWEEN_BATCHES = 0.5

    logging.info("=" * 80)
    logging.info("Starting Email Scraping for Pre-Filtered Fence Companies")
    logging.info("=" * 80)

    # Read pre-filtered CSV
    logging.info(f"Reading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    total_companies = len(df)
    logging.info(f"Total companies to scrape: {total_companies}")

    # Initialize
    results = []
    scraper = EmailScraper(timeout=10, max_retries=2)

    try:
        # Process companies with threading
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []

            for idx, row in df.iterrows():
                future = executor.submit(process_company, row, idx, scraper)
                futures.append(future)

                if (idx + 1) % (MAX_WORKERS * 10) == 0:
                    time.sleep(DELAY_BETWEEN_BATCHES)

            # Collect results
            for i, future in enumerate(as_completed(futures)):
                try:
                    result = future.result()
                    results.append(result)

                    if (i + 1) % 50 == 0:
                        logging.info(f"Progress: {i + 1}/{total_companies} companies")

                except Exception as e:
                    logging.error(f"Error processing future: {str(e)}")

    finally:
        scraper.close()

    # Update dataframe with results
    logging.info("Updating dataframe with scraped emails...")

    df['scraped_emails'] = ''
    df['scraping_error'] = ''

    for result in results:
        idx = result['index']
        df.at[idx, 'scraped_emails'] = ', '.join(result['emails']) if result['emails'] else ''
        df.at[idx, 'scraping_error'] = result['error'] if result['error'] else ''

    # Merge original and scraped emails
    def merge_emails(row):
        emails = set()
        # Handle original email
        if pd.notna(row['email']) and row['email'] and row['email'] != 'N/A':
            emails.add(str(row['email']))
        # Handle scraped emails
        if pd.notna(row['scraped_emails']) and row['scraped_emails']:
            for email in row['scraped_emails'].split(', '):
                if email:
                    emails.add(email)
        return ', '.join(sorted(emails))

    df['all_emails'] = df.apply(merge_emails, axis=1)

    # Save results
    logging.info(f"Saving results to: {OUTPUT_FILE}")
    df.to_csv(OUTPUT_FILE, index=False)

    # Statistics
    logging.info("=" * 80)
    logging.info("SUMMARY STATISTICS")
    logging.info("=" * 80)
    logging.info(f"Total fence companies processed: {total_companies}")

    companies_with_emails = df[df['all_emails'] != ''].shape[0]
    logging.info(f"Companies with emails: {companies_with_emails} ({companies_with_emails/total_companies*100:.1f}%)")

    newly_scraped = df[
        (df['scraped_emails'] != '') &
        ((df['email'] == 'N/A') | (df['email'] == ''))
    ].shape[0]
    logging.info(f"Companies with newly scraped emails: {newly_scraped}")

    errors = df[df['scraping_error'] != ''].shape[0]
    logging.info(f"Companies with errors: {errors}")

    logging.info("=" * 80)
    logging.info("Processing complete!")
    logging.info(f"Final output: {OUTPUT_FILE}")
    logging.info("=" * 80)


if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
