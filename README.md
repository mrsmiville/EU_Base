# EU Company Email Scraper and Fence Filter

This project filters a dataset of ~14,000 European companies to keep only those that have fence-related content on their websites, and scrapes all email addresses from their websites.

## Files

- `MAIN_EU_ALL_14K_COMPANIES_WITH_EMAILS.csv` - Original dataset
- `MAIN_EU_ALL_14K_COMPANIES_WITH_EMAILS_UPDATED.csv` - Updated dataset with more websites
- `clean_companies.py` - Main script to filter and scrape
- `test_sample.py` - Test script for validation on small sample
- `requirements.txt` - Python dependencies

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Test on Sample Data

First, test on a small sample to verify everything works:

```bash
python test_sample.py
```

### Run Full Processing

Process all companies (this may take several hours):

```bash
python clean_companies.py
```

## Output

The script creates:
- `FILTERED_COMPANIES_WITH_FENCE_CONTENT.csv` - Filtered companies with fence content
- `scraping.log` - Detailed log of the scraping process

## Features

- **Multi-language fence detection**: Detects fence-related keywords in 10+ European languages (Czech, Polish, German, French, Spanish, Italian, Hungarian, Dutch, Romanian, English)
- **Email scraping**: Extracts all emails from website content and mailto links
- **Duplicate removal**: Merges original and scraped emails
- **Concurrent processing**: Uses threading for faster processing
- **Error handling**: Robust retry logic and timeout handling
- **Rate limiting**: Respectful delays to avoid overwhelming servers
- **SSL handling**: Works with sites that have SSL certificate issues

## Process

1. Read company data from CSV
2. For each company with a website:
   - Scrape website content
   - Check for fence-related keywords
   - Extract all email addresses
3. Filter out companies without fence content
4. Merge original and scraped emails
5. Save filtered results to new CSV

## Statistics

The script provides:
- Total companies processed
- Companies with fence content (kept)
- Companies removed
- Companies with emails
- Newly scraped emails

## Free Tools Used

- **pandas**: CSV manipulation
- **requests**: HTTP requests
- **BeautifulSoup4**: HTML parsing
- **re**: Email extraction via regex
- **urllib3**: URL handling
