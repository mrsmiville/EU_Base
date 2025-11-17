#!/usr/bin/env python3
"""
Step 3: Clean fake/placeholder emails from the results
"""

import pandas as pd
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Patterns for fake/placeholder emails
FAKE_EMAIL_PATTERNS = [
    r'xxx@',
    r'yyy@',
    r'test@',
    r'example@',
    r'placeholder@',
    r'dummy@',
    r'noreply@',
    r'no-reply@',
    r'@example\.',
    r'@test\.',
    r'@dummy\.',
    r'@placeholder\.',
    r'durmitor1@t-com\.me',  # Specific fake email found
]

# Suspicious domains
SUSPICIOUS_DOMAINS = [
    'example.com',
    'test.com',
    'dummy.com',
    'placeholder.com',
    'yoursite.com',
    'yourdomain.com',
    'domain.com',
]

def is_fake_email(email):
    """Check if an email is fake/placeholder"""
    if not email or pd.isna(email):
        return True

    email = str(email).strip().lower()

    # Check against fake patterns
    for pattern in FAKE_EMAIL_PATTERNS:
        if re.search(pattern, email, re.IGNORECASE):
            return True

    # Check against suspicious domains
    for domain in SUSPICIOUS_DOMAINS:
        if domain.lower() in email:
            return True

    # Check for obviously fake patterns
    if email.count('@') != 1:
        return True

    return False

def clean_email_list(email_string):
    """Clean a comma-separated list of emails"""
    if not email_string or pd.isna(email_string):
        return ''

    emails = str(email_string).split(',')
    clean_emails = []

    for email in emails:
        email = email.strip()
        if email and not is_fake_email(email):
            clean_emails.append(email)

    # Remove duplicates while preserving order
    seen = set()
    unique_emails = []
    for email in clean_emails:
        email_lower = email.lower()
        if email_lower not in seen:
            seen.add(email_lower)
            unique_emails.append(email)

    return ', '.join(unique_emails)

def main():
    INPUT_FILE = 'FINAL_FENCE_COMPANIES_WITH_EMAILS.csv'
    OUTPUT_FILE = 'CLEANED_FENCE_COMPANIES_WITH_EMAILS.csv'

    logging.info("=" * 80)
    logging.info("Cleaning fake/placeholder emails")
    logging.info("=" * 80)

    # Read CSV
    logging.info(f"Reading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)

    total_companies = len(df)
    logging.info(f"Total companies: {total_companies}")

    # Count before
    before_with_emails = df['all_emails'].notna().sum()
    logging.info(f"Companies with emails (before): {before_with_emails}")

    # Clean emails
    logging.info("Cleaning email addresses...")
    df['all_emails_cleaned'] = df['all_emails'].apply(clean_email_list)

    # Replace empty strings with NaN for proper counting
    df['all_emails_cleaned'] = df['all_emails_cleaned'].replace('', pd.NA)

    # Keep only companies with valid emails
    df_cleaned = df[df['all_emails_cleaned'].notna()].copy()

    # Rename column
    df_cleaned = df_cleaned.drop('all_emails', axis=1)
    df_cleaned = df_cleaned.rename(columns={'all_emails_cleaned': 'all_emails'})

    # Save cleaned results
    df_cleaned.to_csv(OUTPUT_FILE, index=False)

    # Count after
    after_with_emails = len(df_cleaned)
    removed = before_with_emails - after_with_emails

    logging.info("=" * 80)
    logging.info("CLEANING RESULTS")
    logging.info("=" * 80)
    logging.info(f"Before cleaning: {before_with_emails} companies with emails")
    logging.info(f"After cleaning: {after_with_emails} companies with valid emails")
    logging.info(f"Removed: {removed} companies with fake/placeholder emails")
    logging.info(f"Final output: {OUTPUT_FILE}")
    logging.info("=" * 80)

    # Show some examples of what was removed
    logging.info("\nExamples of removed fake emails:")
    fake_examples = df[df['all_emails'].notna() & df['all_emails_cleaned'].isna()][['company_name', 'all_emails']].head(10)
    for idx, row in fake_examples.iterrows():
        logging.info(f"  - {row['company_name']}: {row['all_emails']}")

if __name__ == '__main__':
    main()
