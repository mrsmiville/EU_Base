#!/usr/bin/env python3
"""
Step 1: Pre-filter companies by name to identify fence-related businesses
This dramatically reduces the number of websites to scrape
"""

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Fence-related keywords in multiple European languages
FENCE_KEYWORDS = [
    # English
    'fence', 'fences', 'fencing', 'gate', 'gates',
    # Czech
    'plot', 'ploty', 'oplocení', 'brána', 'brány', 'branky', 'pletivo',
    # Polish
    'ogrodzenie', 'ogrodzenia', 'płot', 'płoty', 'bramka', 'bramy',
    # German
    'zaun', 'zäune', 'umzäunung', 'gartenzaun', 'tor', 'tore',
    # French
    'clôture', 'clôtures', 'palissade', 'grillage', 'portail', 'barrière',
    # Spanish
    'valla', 'vallas', 'cerca', 'cercado', 'vallado', 'cerco',
    # Italian
    'recinzione', 'recinzioni', 'steccato', 'cancello', 'cancelli',
    # Hungarian
    'kerítés', 'kerítések', 'kapu', 'kapuk',
    # Dutch
    'hek', 'hekwerk', 'omheining', 'schutting', 'poort',
    # Romanian
    'gard', 'garduri', 'împrejmuire', 'poartă',
    # Additional related terms
    'gabion', 'gabiony', 'betonplot', 'mobilní oplocení',
]

def has_fence_keyword(text):
    """Check if text contains any fence-related keyword"""
    if pd.isna(text):
        return False
    text_lower = str(text).lower()
    for keyword in FENCE_KEYWORDS:
        if keyword.lower() in text_lower:
            return True
    return False

def main():
    INPUT_FILE = 'MAIN_EU_ALL_14K_COMPANIES_WITH_EMAILS_UPDATED.csv'
    OUTPUT_FILE = 'PRE_FILTERED_FENCE_COMPANIES.csv'

    logging.info("=" * 80)
    logging.info("Pre-filtering companies by name for fence-related keywords")
    logging.info("=" * 80)

    # Read CSV
    logging.info(f"Reading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    total_companies = len(df)
    logging.info(f"Total companies: {total_companies}")

    # Filter by company name containing fence keywords
    logging.info("Filtering by company name...")
    df['is_fence_company'] = df['company_name'].apply(has_fence_keyword)

    # Also check address for fence keywords (some companies include it there)
    df['fence_in_address'] = df['address'].apply(has_fence_keyword)

    # Keep companies with fence keywords in name or address
    filtered_df = df[df['is_fence_company'] | df['fence_in_address']].copy()

    # Remove the helper columns
    filtered_df = filtered_df.drop(['is_fence_company', 'fence_in_address'], axis=1)

    # Save filtered results
    filtered_df.to_csv(OUTPUT_FILE, index=False)

    logging.info("=" * 80)
    logging.info("FILTERING RESULTS")
    logging.info("=" * 80)
    logging.info(f"Original companies: {total_companies}")
    logging.info(f"Fence-related companies: {len(filtered_df)}")
    logging.info(f"Reduction: {total_companies - len(filtered_df)} companies removed")
    logging.info(f"Kept: {len(filtered_df) / total_companies * 100:.1f}%")
    logging.info(f"Saved to: {OUTPUT_FILE}")

    # Show sample
    logging.info("\nSample of filtered companies:")
    for idx, row in filtered_df.head(10).iterrows():
        logging.info(f"  - {row['company_name']} ({row['country']})")

    logging.info("=" * 80)

if __name__ == '__main__':
    main()
