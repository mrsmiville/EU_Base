#!/usr/bin/env python3
"""
Interactive tool to help collect Finnish fence companies
YOU search manually, this tool helps organize the data

HOW IT WORKS:
1. You search Google manually for each keyword
2. You paste company websites one by one
3. Script automatically extracts emails
4. Saves everything to CSV

This is the FASTEST free way to get 150+ companies!
"""

import requests
from bs4 import BeautifulSoup
import re
import csv
from urllib.parse import urlparse

def extract_emails_from_website(url):
    """Try to extract emails from a website"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove scripts
            for script in soup(['script', 'style']):
                script.decompose()

            text = soup.get_text()

            # Extract emails
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = set(re.findall(email_pattern, text))

            # Check mailto links
            for a_tag in soup.find_all('a', href=True):
                if a_tag['href'].startswith('mailto:'):
                    email = a_tag['href'].replace('mailto:', '').split('?')[0]
                    emails.add(email)

            # Filter fake emails
            real_emails = set()
            for email in emails:
                if not any(skip in email.lower() for skip in [
                    'example.', 'test.', 'noreply@', 'privacy@', 'webmaster@'
                ]):
                    real_emails.add(email)

            return list(real_emails)

    except Exception as e:
        return []

    return []


def main():
    print("\n" + "=" * 80)
    print("FINNISH FENCE COMPANY COLLECTOR")
    print("Semi-Automated Email Extraction")
    print("=" * 80)

    print("\nSTEPS:")
    print("1. Search Google manually for: 'aita yritys suomi'")
    print("2. Copy company websites and paste here")
    print("3. Script extracts emails automatically")
    print("4. Repeat for more companies")
    print("\nType 'done' when finished, 'skip' to skip current URL")
    print("=" * 80)

    companies = []
    count = 0

    # Search keywords for user reference
    keywords = [
        "aita yritys suomi",
        "aidat myynti finland",
        "verkkoaita helsinki",
        "puuaita tampere",
        "metalliportti turku",
        "aitaus palvelu",
        "rakennusaita vuokraus",
        "betoniaita myynti",
    ]

    print(f"\n📋 SUGGESTED SEARCH KEYWORDS (search these in Google):")
    for i, kw in enumerate(keywords, 1):
        print(f"   {i}. {kw}")

    print("\n" + "=" * 80)
    print("START ADDING COMPANIES")
    print("=" * 80)

    while True:
        print(f"\n[Company #{count + 1}]")
        url = input("Enter company website (or 'done' to finish): ").strip()

        if url.lower() == 'done':
            break

        if url.lower() == 'skip' or not url:
            continue

        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        print(f"  Checking: {url}")

        # Try to extract emails
        emails = extract_emails_from_website(url)

        if emails:
            email_str = ', '.join(emails)
            print(f"  ✓ Found emails: {email_str}")

            companies.append({
                'country': 'Finland',
                'website': url,
                'email': email_str
            })
            count += 1

            # Save after each company (in case of interruption)
            with open('COLLECTED_FINNISH_COMPANIES.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['country', 'website', 'email'])
                writer.writeheader()
                writer.writerows(companies)

            print(f"  ✓ Saved! Total companies: {count}")

        else:
            print(f"  ✗ No emails found on this website")
            add_anyway = input("    Add without email? (y/n): ").strip().lower()

            if add_anyway == 'y':
                email = input("    Enter email manually (or press Enter to skip): ").strip()
                if email:
                    companies.append({
                        'country': 'Finland',
                        'website': url,
                        'email': email
                    })
                    count += 1
                    print(f"  ✓ Added! Total companies: {count}")

    print("\n" + "=" * 80)
    print(f"COMPLETE! Collected {count} Finnish companies")
    print("Saved to: COLLECTED_FINNISH_COMPANIES.csv")
    print("=" * 80)


if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted! Your progress is saved in COLLECTED_FINNISH_COMPANIES.csv")
