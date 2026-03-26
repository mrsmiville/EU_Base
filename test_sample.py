#!/usr/bin/env python3
"""
Test script to validate the scraper on a small sample
"""

import pandas as pd
from clean_companies import CompanyWebsiteScraper
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    # Read CSV
    df = pd.read_csv('MAIN_EU_ALL_14K_COMPANIES_WITH_EMAILS_UPDATED.csv')

    # Take first 10 companies with websites
    sample_df = df[df['website'] != 'N/A'].head(10)

    scraper = CompanyWebsiteScraper(timeout=10, max_retries=2)

    print("Testing on sample companies:")
    print("=" * 80)

    for idx, row in sample_df.iterrows():
        company_name = row['company_name']
        website = row['website']

        print(f"\nCompany: {company_name}")
        print(f"Website: {website}")

        result = scraper.scrape_website(website)

        print(f"Has fence content: {result['has_fence_content']}")
        print(f"Emails found: {result['emails']}")
        print(f"Error: {result['error']}")
        print("-" * 80)

    scraper.close()
    print("\nTest complete!")

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
