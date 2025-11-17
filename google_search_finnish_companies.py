#!/usr/bin/env python3
"""
Find Finnish fence companies using Google Custom Search API
FREE: 100 searches per day

Setup:
1. Go to: https://developers.google.com/custom-search/v1/overview
2. Get API key: https://console.cloud.google.com/apis/credentials
3. Create Custom Search Engine: https://programmablesearchengine.google.com/
4. Set to search the entire web
5. Add API key and Search Engine ID below
"""

import requests
import csv
import time
import re
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# ===== CONFIGURATION =====
# Get these from Google Cloud Console (FREE)
API_KEY = "YOUR_API_KEY_HERE"  # Get from: https://console.cloud.google.com/apis/credentials
SEARCH_ENGINE_ID = "YOUR_SEARCH_ENGINE_ID_HERE"  # Get from: https://programmablesearchengine.google.com/

# Finnish fence keywords
KEYWORDS = [
    "aita yritys Finland",
    "aidat myynti Suomi",
    "verkkoaita Helsinki",
    "puuaita yritys",
    "metalliportti Finland",
    "aitaus palvelu Suomi",
]

def google_search(query, api_key, cse_id, num_results=10):
    """
    Search using Google Custom Search API
    Free tier: 100 queries/day
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query,
        'num': num_results,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Search error: {e}")
        return None

def extract_email_from_website(url):
    """Extract email from a website"""
    try:
        response = requests.get(url, timeout=10, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find mailto links
        emails = set()
        for a_tag in soup.find_all('a', href=True):
            if a_tag['href'].startswith('mailto:'):
                email = a_tag['href'].replace('mailto:', '').split('?')[0]
                emails.add(email)

        # Find emails in text
        text = soup.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        found = re.findall(email_pattern, text)
        emails.update(found)

        return list(emails)
    except:
        return []

def main():
    if API_KEY == "YOUR_API_KEY_HERE" or SEARCH_ENGINE_ID == "YOUR_SEARCH_ENGINE_ID_HERE":
        print("\n" + "=" * 80)
        print("ERROR: Please configure your Google API credentials")
        print("=" * 80)
        print("\nSteps:")
        print("1. Get API Key: https://console.cloud.google.com/apis/credentials")
        print("2. Create Search Engine: https://programmablesearchengine.google.com/")
        print("3. Update API_KEY and SEARCH_ENGINE_ID in this script")
        print("\nFREE TIER: 100 searches per day")
        print("=" * 80)
        return

    OUTPUT_FILE = 'GOOGLE_FOUND_FINNISH_COMPANIES.csv'
    companies = []
    seen_urls = set()

    logging.info("Starting Google search for Finnish fence companies...")

    for keyword in KEYWORDS:
        logging.info(f"\nSearching: {keyword}")

        results = google_search(keyword, API_KEY, SEARCH_ENGINE_ID, num_results=10)

        if not results or 'items' not in results:
            continue

        for item in results['items']:
            url = item.get('link', '')
            title = item.get('title', '')

            if url and url not in seen_urls:
                seen_urls.add(url)
                logging.info(f"  Found: {title}")

                # Try to extract email
                emails = extract_email_from_website(url)

                if emails:
                    companies.append({
                        'name': title,
                        'website': url,
                        'email': ', '.join(emails)
                    })
                    logging.info(f"    Emails: {', '.join(emails)}")

                time.sleep(1)  # Be respectful

        time.sleep(2)  # Between keyword searches

    # Save results
    logging.info(f"\n\nSaving {len(companies)} companies to {OUTPUT_FILE}")

    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['country', 'website', 'email'])

        for company in companies:
            writer.writerow(['Finland', company['website'], company['email']])

    logging.info(f"COMPLETE: Found {len(companies)} Finnish companies")

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
