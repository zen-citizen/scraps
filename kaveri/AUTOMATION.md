# Automated Kaveri Data Collection

This automation system keeps the Karnataka administrative hierarchy data (Districts → Taluks → Hoblis → Villages) up-to-date by automatically scraping the Kaveri website.

## 🚀 Quick Setup
### Option: GitHub Actions

1. **Set up repository secrets:**
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `KAVERI_AUTH_TOKEN`: Authorization header from browser
     - `KAVERI_COOKIE`: Cookie header from browser

2. **The workflow runs automatically:**
   - Weekly full scrape on Sundays at 3 AM UTC
   - Manual trigger available in Actions tab


## 🔧 Configuration

Edit `config.json` to customize:

```json
{
  "scraper_config": {
    "rate_limit_delay": 1,
    "max_retries": 3,
    "backup_retention_days": 30
  },
  "schedule": {
    "daily_check": "02:00",
    "weekly_full_scrape": "Sunday 03:00"
  }
}
```

## 🔐 Authentication

The scraper requires authentication headers from a logged-in browser session:

### Getting Credentials

1. **Log into Kaveri website:**
   - Visit https://kaveri.karnataka.gov.in
   - Complete the login process

2. **Extract headers:**
   - Open Developer Tools (F12)
   - Go to Network tab
   - Select any dropdown (District, Taluka, etc.)
   - Find the API request (e.g., `GetTalukaAsync`)
   - Copy the `authorization` and `cookie` headers

3. **Update credentials:**
   - **Local**: Run `python3 update_credentials.py`
   - **GitHub**: Update repository secrets

### Credential Expiry

- Credentials typically expire after 24-48 hours
- The system will log authentication errors
- Update credentials when you see auth failures

### GitHub Actions Monitoring

- **Workflow runs**: Check the Actions tab
- **Failed runs**: Issues are automatically created
- **Data releases**: Weekly releases with updated data

## 🛠 Manual Operations

### Force Full Scrape
```bash
cd kaveri
python3 automated_scraper.py --force-full-scrape
```

### Test API Connectivity
```bash
cd kaveri
python3 -c "
from automated_scraper import KaveriScraper
scraper = KaveriScraper()
result = scraper.make_request('GetTalukaAsync', {'districtCode': '11'})
print('✓ API working' if result else '✗ API failed')
"
```

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Update credentials using `update_credentials.py`
   - Check if you're still logged into Kaveri website

2. **Rate Limiting**
   - The scraper handles this automatically
   - Increase delays in config if needed

3. **Missing Data**
   - Check logs for specific API failures
   - Some regions might not have data

4. **Cron Jobs Not Running**
   - Verify cron service: `sudo service cron status`
   - Check cron logs: `grep CRON /var/log/syslog`

### Getting Help

- Check logs: `scraper.log` and `automation.log`
- Run status check: `./check_status.sh`
- Test manually: `./run_scraper.sh`

## 📄 Legal Notice

This automation system:
- Respects the Kaveri website's rate limits
- Is intended for educational and research purposes
- Users are responsible for compliance with terms of service
- Should not overload the government servers

## 🔄 Data Updates

The system maintains these data files:
- `district_talukas.json` - District to Taluka mappings
- `taluk_hoblis.json` - Taluka to Hobli mappings
- `hobli_villages.json` - Hobli to Village mappings
- `remap.json` - Village to hierarchy reverse mapping
- `village_mapping.json` - Complete village data

Updates are only applied when actual changes are detected, minimizing unnecessary writes and commits.
