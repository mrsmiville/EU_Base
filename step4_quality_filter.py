#!/usr/bin/env python3
"""
Step 4: Remove non-fence businesses (hotels, stores, rentals, etc.)
Better quality filtering to keep ONLY real fence companies
"""

import pandas as pd
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Words that indicate it's NOT a fence company
EXCLUDE_KEYWORDS = [
    # Hotels & Accommodation
    'hotel', 'motel', 'hostel', 'apartment', 'apartamente', 'villa',
    'accommodation', 'lodge', 'resort', 'camping', 'glamping', 'bungalow',

    # Storage & Luggage
    'luggage', 'storage', 'warehouse', 'varastot', 'selfstorage',

    # Rental Services
    'rent a car', 'car rental', 'bike rental', 'makina me qera',
    'iznajmljivanje', 'vuokraus', 'rental', 'hire',

    # Stores (non-fence)
    'mobile store', 'phone shop', 'electronics', 'supermarket',
    'grocery', 'convenience store',

    # Tours & Travel
    'tour', 'travel', 'adventure', 'tourist', 'visitor center',

    # Restaurants & Food
    'restaurant', 'cafe', 'bar', 'pub', 'food', 'catering',

    # Other Services
    'laundry', 'spalatorie', 'croitorie', 'tailor',
    'real estate', 'imoti', 'property', 'realty',
    'police', 'dopravný', 'traffic',

    # Generic stores
    'shopping center', 'mall', 'shopping centre',
]

# Strong fence indicators (company MUST have at least one)
FENCE_INDICATORS = [
    # Fence words
    'fence', 'fences', 'fencing', 'aita', 'aidat', 'aitaus',
    'plot', 'ploty', 'oplocení', 'ogrodzeni', 'gard', 'garduri',
    'zaun', 'clôture', 'valla', 'recinzione', 'kerítés',
    'ograde', 'ogradi',

    # Fence types
    'betonplot', 'metalliportti', 'verkkoaita', 'puuaita',
    'pletivo', 'gabion', 'betafence',

    # Gates
    'gate', 'gates', 'portti', 'brána', 'brány', 'branky',
    'bramka', 'bramy', 'poartă', 'kapije', 'kapija',
]

def should_exclude(text):
    """Check if text contains exclusion keywords"""
    if not text or pd.isna(text):
        return False

    text_lower = str(text).lower()

    for keyword in EXCLUDE_KEYWORDS:
        if keyword.lower() in text_lower:
            return True

    return False

def has_fence_indicator(text):
    """Check if text contains strong fence indicators"""
    if not text or pd.isna(text):
        return False

    text_lower = str(text).lower()

    for indicator in FENCE_INDICATORS:
        if indicator.lower() in text_lower:
            return True

    return False

def is_real_fence_company(row):
    """Determine if a company is a real fence business"""

    # Combine name and address for checking
    company_name = str(row['company_name'])
    address = str(row['address'])
    text_to_check = company_name + ' ' + address

    # Must have at least one fence indicator
    has_fence = has_fence_indicator(text_to_check)

    # If it has strong fence indicators, keep it even if it has some other words
    if has_fence:
        # Only exclude if it has VERY obvious non-fence keywords
        text_lower = text_to_check.lower()
        obvious_excludes = ['hotel', 'motel', 'luggage', 'apartment', 'apartamente',
                           'rent a car', 'mobile store', 'restaurant', 'cafe']
        for keyword in obvious_excludes:
            if keyword in text_lower:
                return False
        return True

    # If no fence indicators, exclude
    return False

def main():
    INPUT_FILE = 'CLEANED_FENCE_COMPANIES_WITH_EMAILS.csv'
    OUTPUT_FILE = 'QUALITY_FILTERED_FENCE_COMPANIES.csv'
    REMOVED_FILE = 'REMOVED_NON_FENCE_COMPANIES.csv'

    logging.info("=" * 80)
    logging.info("Filtering out non-fence businesses (hotels, stores, etc.)")
    logging.info("=" * 80)

    # Read CSV
    logging.info(f"Reading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)

    before_count = len(df)
    logging.info(f"Companies before filtering: {before_count}")

    # Apply filter
    logging.info("Filtering companies...")
    df['is_fence_company'] = df.apply(is_real_fence_company, axis=1)

    # Split into good and bad
    good_companies = df[df['is_fence_company'] == True].copy()
    bad_companies = df[df['is_fence_company'] == False].copy()

    # Remove helper column
    good_companies = good_companies.drop('is_fence_company', axis=1)
    bad_companies = bad_companies.drop('is_fence_company', axis=1)

    # Save results
    good_companies.to_csv(OUTPUT_FILE, index=False)
    bad_companies.to_csv(REMOVED_FILE, index=False)

    after_count = len(good_companies)
    removed_count = len(bad_companies)

    logging.info("=" * 80)
    logging.info("QUALITY FILTERING RESULTS")
    logging.info("=" * 80)
    logging.info(f"Before: {before_count} companies")
    logging.info(f"After: {after_count} REAL fence companies")
    logging.info(f"Removed: {removed_count} non-fence businesses")
    logging.info(f"Kept: {after_count/before_count*100:.1f}%")
    logging.info(f"")
    logging.info(f"Good companies saved to: {OUTPUT_FILE}")
    logging.info(f"Removed companies saved to: {REMOVED_FILE}")
    logging.info("=" * 80)

    # Show examples of removed companies
    if len(bad_companies) > 0:
        logging.info("\nExamples of REMOVED companies:")
        for idx, row in bad_companies.head(20).iterrows():
            logging.info(f"  ✗ {row['company_name'][:70]}")

    logging.info("\n" + "=" * 80)

if __name__ == '__main__':
    main()
