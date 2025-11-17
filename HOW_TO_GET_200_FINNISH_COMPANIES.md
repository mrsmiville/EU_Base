# How to Get 200 Finnish Fence Companies (FREE, NO API)

## Current Status
✅ **You have:** 45 Finnish companies in `FINLAND_FENCE_COMPANIES.csv`
🎯 **Goal:** Find 155 more = **200 total**

---

## 🚀 FASTEST METHOD (Recommended)

### Batch Email Extractor (2-3 hours total)

**Step 1:** Find company websites (1-2 hours)
1. Search Google for these keywords:
   - `aita yritys suomi`
   - `aidat myynti finland`
   - `verkkoaita helsinki`
   - `puuaita tampere`
   - `metalliportti turku`
   - `aitaus palvelu suomi`
   - `rakennusaita vuokraus`
   - `betoniaita myynti`

2. Copy 150+ company website URLs
3. Save them to `urls.txt` (one URL per line)

**Step 2:** Extract emails automatically (10 minutes)
```bash
python batch_email_extractor.py
```

**Output:** `BATCH_EXTRACTED_FINNISH_COMPANIES.csv` with emails!

### urls.txt Example:
```
https://www.company1.fi
https://www.company2.fi
https://www.company3.fi
```

---

## 🛠️ ALTERNATIVE: Interactive Collector

Add companies one by one with automatic email extraction:

```bash
python manual_company_collector.py
```

**How it works:**
1. You paste a company website
2. Script automatically extracts emails
3. Saves to CSV after each entry
4. Type 'done' when finished

**Output:** `COLLECTED_FINNISH_COMPANIES.csv`

---

## 📋 Finnish Business Directories

Search these sites manually:

1. **Finder.fi** - https://www.finder.fi/
   - Search: "aita", "aidat", "aitaus"
   - Free business directory

2. **Fonecta.fi** - https://www.fonecta.fi/
   - Search: "aita yritys"
   - Yellow pages

3. **Kauppalehti** - https://www.kauppalehti.fi/
   - Business directory

4. **LinkedIn** - https://www.linkedin.com/search/
   - Search: "fence company Finland"
   - "aita yritys Suomi"

---

## 🎯 Expected Timeline

| Method | Time | Companies Found |
|--------|------|-----------------|
| Batch Extractor | 2-3 hours | 100-150 |
| Interactive Collector | 3-4 hours | 50-100 |
| Manual (directories) | 4-6 hours | 150-200 |

---

## ✅ Combining Your Data

After collecting, merge all CSVs:

```bash
# Combine all your CSVs
cat FINLAND_FENCE_COMPANIES.csv \
    BATCH_EXTRACTED_FINNISH_COMPANIES.csv \
    COLLECTED_FINNISH_COMPANIES.csv \
    > ALL_FINNISH_COMPANIES.csv

# Remove duplicates
python -c "
import pandas as pd
df = pd.read_csv('ALL_FINNISH_COMPANIES.csv')
df = df.drop_duplicates(subset=['website'])
df.to_csv('FINAL_200_FINNISH_COMPANIES.csv', index=False)
print(f'Total: {len(df)} unique companies')
"
```

---

## 📊 Tools Summary

| Tool | API Required | Automation | Best For |
|------|--------------|------------|----------|
| `batch_email_extractor.py` | ❌ No | ✅ Yes | **Fastest - RECOMMENDED** |
| `manual_company_collector.py` | ❌ No | ⚡ Semi | Interactive adding |
| `scrape_finnish_companies_no_api.py` | ❌ No | ✅ Yes | Automated (may be blocked) |
| `google_search_finnish_companies.py` | ✅ Yes | ✅ Yes | Requires Google API setup |

---

## 💡 Pro Tips

1. **Quality over quantity:** Focus on companies with real contact pages
2. **Check multiple pages:** Look for "Yhteystiedot" (Contact) pages
3. **Verify emails:** Use the ones ending in company domain (e.g., info@company.fi)
4. **Save progress:** Tools save after each company
5. **Take breaks:** Search engines may temporarily block rapid searches

---

## 🎯 My Recommendation

**For 200 companies in 2-3 hours:**

1. Spend 2 hours finding 150-160 company URLs via Google
2. Run `batch_email_extractor.py` (10 minutes)
3. Combine with your existing 45 companies
4. **Result:** 195-205 Finnish fence companies with emails!

---

## Need Help?

All scripts are ready to use:
- No API keys needed
- No setup required
- Just run and follow prompts

Good luck! 🚀
