#!/usr/bin/env python3
"""
Batch Email Extractor for Finnish Companies

FASTEST METHOD:
1. Find 150 Finnish fence company websites (Google search)
2. Save URLs to urls.txt (one per line)
3. Run this script
4. Get CSV with all emails!

Time: Find 150 URLs in 1-2 hours, extract emails in 10 minutes
"""

import requests
from bs4 import BeautifulSoup
import re
import csv
import time
from pathlib import Path

def extract_emails_from_website(url):
    """Extract emails from a website"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10, verify=False)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            for script in soup(['script', 'style']):
                script.decompose()

            text = soup.get_text()

            # Extract emails
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = set(re.findall(email_pattern, text))

            # Check mailto
            for a_tag in soup.find_all('a', href=True):
                if a_tag['href'].startswith('mailto:'):
                    email = a_tag['href'].replace('mailto:', '').split('?')[0]
                    emails.add(email)

            # Filter
            real_emails = {e for e in emails if not any(
                skip in e.lower() for skip in ['example.', 'test.', 'noreply@']
            )}

            return list(real_emails)

    except:
        return []

    return []


def main():
    input_file = 'urls.txt'

    print("\n" + "=" * 80)
    print("BATCH EMAIL EXTRACTOR")
    print("=" * 80)

    # Check if urls.txt exists
    if not Path(input_file).exists():
        print(f"\n❌ Error: {input_file} not found!")
        print("\nCreate urls.txt with one URL per line:")
        print("  https://www.company1.fi")
        print("  https://www.company2.fi")
        print("  https://www.company3.fi")
        print("\nThen run this script again.")
        print("=" * 80)
        return

    # Read URLs
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]

    if not urls:
        print(f"\n❌ No valid URLs found in {input_file}")
        print("Make sure each line contains a URL starting with http:// or https://")
        return

    print(f"\n📝 Found {len(urls)} URLs to process")
    print(f"⏱️  Estimated time: {len(urls) * 3} seconds (~{len(urls) * 3 / 60:.1f} minutes)")
    print("\n" + "=" * 80)

    results = []

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")

        emails = extract_emails_from_website(url)

        if emails:
            email_str = ', '.join(emails)
            print(f"  ✓ Emails: {email_str}")

            results.append({
                'country': 'Finland',
                'website': url,
                'email': email_str
            })
        else:
            print(f"  ✗ No emails found")

        time.sleep(2)  # Be respectful

    # Save results
    output_file = 'BATCH_EXTRACTED_FINNISH_COMPANIES.csv'

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['country', 'website', 'email'])
        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 80)
    print(f"✅ COMPLETE!")
    print(f"  Processed: {len(urls)} websites")
    print(f"  Found emails: {len(results)} companies")
    print(f"  Success rate: {len(results)/len(urls)*100:.1f}%")
    print(f"  Output: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
