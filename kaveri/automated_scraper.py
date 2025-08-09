#!/usr/bin/env python3
"""
Automated Kaveri Data Scraper
Automatically scrapes and updates Karnataka administrative hierarchy data.
"""

import json
import requests
import time
import os
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KaveriScraper:
    def __init__(self):
        # Load configuration
        self.load_config()
        
        self.backup_dir = "backups"
        self.data_files = [
            "district_talukas.json",
            "taluk_hoblis.json", 
            "hobli_villages.json",
            "remap.json",
            "village_mapping.json"
        ]
        
        self.districts = {
            "11": "Bagalkot", "2": "Bangalore Rural", "1": "Basavanagudi",
            "7": "Belgaum", "8": "Bellary", "9": "Bidar", "10": "Bijapur",
            "14": "Chamarajanagar", "38": "Chikkaballapura", "12": "Chikkamagalur",
            "13": "Chitradurga", "15": "Davangere", "16": "Dharwad", "18": "Gadag",
            "35": "Gandhinagar", "17": "Gulbarga", "19": "Hassan", "20": "Haveri",
            "36": "Jayanagar", "22": "Karwar", "23": "Kodagu", "21": "Kolar",
            "31": "Koppal", "25": "Mandya", "24": "Mangalore", "26": "Mysore",
            "27": "Raichur", "34": "Rajajinagar", "37": "Ramanagara", "28": "Shimoga",
            "33": "Shivajinagar", "29": "Tumkur", "30": "Udupi", "40": "Vijayanagara",
            "39": "Yadagiri"
        }
        
        self.ensure_backup_dir()
    
    def load_config(self):
        """Load configuration from config.json file."""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            # Extract configuration values
            scraper_config = config.get('scraper_config', {})
            credentials = config.get('credentials', {})
            
            self.base_url = scraper_config.get('base_url', 'https://kaveri.karnataka.gov.in/api')
            self.rate_limit_delay = scraper_config.get('rate_limit_delay', 1)
            self.max_retries = scraper_config.get('max_retries', 3)
            
            # Set up headers with credentials from config
            self.headers = {
                "_append": "3ccbc2d56099f3f6a380b8d4a8763c5d",
                "accept": "application/json",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                "authorization": credentials.get('authorization', 'YOUR_AUTH_TOKEN_HERE'),
                "content-type": "application/json",
                "cookie": credentials.get('cookie', 'YOUR_COOKIE_HERE'),
                "origin": "https://kaveri.karnataka.gov.in",
                "referer": "https://kaveri.karnataka.gov.in/",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            logger.info("Configuration loaded successfully from config.json")
            
        except FileNotFoundError:
            logger.warning("config.json not found, using default values")
            self.use_default_config()
        except json.JSONDecodeError:
            logger.error("Invalid JSON in config.json, using default values")
            self.use_default_config()
    
    def use_default_config(self):
        """Use default configuration when config.json is not available."""
        self.base_url = "https://kaveri.karnataka.gov.in/api"
        self.rate_limit_delay = 1
        self.max_retries = 3
        
        self.headers = {
            "_append": "3ccbc2d56099f3f6a380b8d4a8763c5d",
            "accept": "application/json",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "authorization": "YOUR_AUTH_TOKEN_HERE",  # Update this
            "content-type": "application/json",
            "cookie": "YOUR_COOKIE_HERE",  # Update this
            "origin": "https://kaveri.karnataka.gov.in",
            "referer": "https://kaveri.karnataka.gov.in/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def ensure_backup_dir(self):
        """Create backup directory if it doesn't exist."""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def backup_existing_files(self):
        """Backup existing data files with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for file_name in self.data_files:
            if os.path.exists(file_name):
                backup_name = f"{self.backup_dir}/{timestamp}_{file_name}"
                shutil.copy2(file_name, backup_name)
                logger.info(f"Backed up {file_name} to {backup_name}")
    
    def get_file_hash(self, file_path: str) -> str:
        """Get MD5 hash of a file."""
        if not os.path.exists(file_path):
            return ""
        
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def make_request(self, endpoint: str, data: dict, max_retries: int = None) -> Optional[dict]:
        """Make API request with retry logic and rate limiting."""
        if max_retries is None:
            max_retries = self.max_retries
            
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=self.headers, json=data)
                
                if response.status_code == 429:
                    sleep_time = 5 * (attempt + 1)  # Exponential backoff
                    logger.warning(f"Rate limited. Sleeping for {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    continue
                
                response.raise_for_status()
                return response.json()
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {endpoint}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"All attempts failed for {endpoint}")
                    return None
        
        return None
    
    def scrape_talukas(self) -> Dict:
        """Scrape all talukas for each district."""
        logger.info("Starting taluka scraping...")
        district_talukas = {}
        
        for district_code, district_name in self.districts.items():
            logger.info(f"Fetching talukas for {district_name}...")
            
            result = self.make_request("GetTalukaAsync", {"districtCode": str(district_code)})
            if result:
                district_talukas[district_name] = result
            
            time.sleep(self.rate_limit_delay)  # Rate limiting from config
        
        return district_talukas
    
    def scrape_hoblis(self, district_talukas: Dict) -> Dict:
        """Scrape all hoblis for each taluka."""
        logger.info("Starting hobli scraping...")
        taluk_hoblis = {}
        
        # Build taluka mapping
        talukas = {}
        for district_data in district_talukas.values():
            for taluk in district_data:
                talukas[taluk['talukCode']] = taluk['talukNamee']
        
        for taluk_code, taluk_name in talukas.items():
            logger.info(f"Fetching hoblis for {taluk_name}...")
            
            result = self.make_request("GetHobliAsync", {"talukaCode": str(taluk_code)})
            if result:
                taluk_hoblis[taluk_name] = result
            
            time.sleep(self.rate_limit_delay)  # Rate limiting from config
        
        return taluk_hoblis
    
    def scrape_villages(self, taluk_hoblis: Dict) -> Dict:
        """Scrape all villages for each hobli."""
        logger.info("Starting village scraping...")
        hobli_villages = {}
        
        # Build hobli mapping
        hoblis = {}
        for hobli_data in taluk_hoblis.values():
            for hobli in hobli_data:
                hoblis[hobli['hoblicode']] = hobli['hoblinamee']
        
        total_hoblis = len(hoblis)
        for i, (hobli_code, hobli_name) in enumerate(hoblis.items(), 1):
            logger.info(f"Fetching villages for {hobli_name} ({i}/{total_hoblis})...")
            
            result = self.make_request("GetVillageAsync", {"hobliCode": str(hobli_code)})
            if result:
                hobli_villages[hobli_name] = result
            
            time.sleep(self.rate_limit_delay)  # Rate limiting from config
        
        return hobli_villages
    
    def create_reverse_mapping(self, district_talukas: Dict, taluk_hoblis: Dict, hobli_villages: Dict) -> List[Dict]:
        """Create reverse mapping from village to administrative hierarchy."""
        logger.info("Creating reverse mapping...")
        village_mapping = []
        seen = set()
        
        for district_name, talukas in district_talukas.items():
            for taluka in talukas:
                taluk_name = taluka['talukNamee']
                
                if taluk_name in taluk_hoblis:
                    hoblis = taluk_hoblis[taluk_name]
                    
                    for hobli in hoblis:
                        hobli_name = hobli['hoblinamee']
                        
                        if hobli_name in hobli_villages:
                            villages = hobli_villages[hobli_name]
                            
                            for village in villages:
                                village_name = village['villageName']
                                
                                # Avoid duplicates
                                key = (village_name, hobli_name, taluk_name, district_name)
                                if key not in seen:
                                    seen.add(key)
                                    village_mapping.append({
                                        "village": village_name,
                                        "hoblinamee": hobli_name,
                                        "talukNamee": taluk_name,
                                        "districtNamee": district_name
                                    })
        
        return village_mapping
    
    def save_data(self, district_talukas: Dict, taluk_hoblis: Dict, hobli_villages: Dict, village_mapping: List[Dict]):
        """Save all scraped data to JSON files."""
        logger.info("Saving data files...")
        
        data_to_save = [
            ("district_talukas.json", district_talukas),
            ("taluk_hoblis.json", taluk_hoblis),
            ("hobli_villages.json", hobli_villages),
            ("remap.json", village_mapping),
            ("village_mapping.json", village_mapping)
        ]
        
        for filename, data in data_to_save:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {filename}")
    
    def check_for_changes(self) -> bool:
        """Check if any data files have changed."""
        # Store old hashes
        old_hashes = {}
        for file_name in self.data_files:
            old_hashes[file_name] = self.get_file_hash(file_name)
        
        # Run scraping
        success = self.run_scraping()
        if not success:
            return False
        
        # Check new hashes
        changes_detected = False
        for file_name in self.data_files:
            new_hash = self.get_file_hash(file_name)
            if old_hashes[file_name] != new_hash:
                logger.info(f"Changes detected in {file_name}")
                changes_detected = True
        
        return changes_detected
    
    def run_scraping(self) -> bool:
        """Run the complete scraping process."""
        try:
            logger.info("Starting automated scraping process...")
            
            # Backup existing files
            self.backup_existing_files()
            
            # Scrape data
            district_talukas = self.scrape_talukas()
            if not district_talukas:
                logger.error("Failed to scrape district-taluka data")
                return False
            
            taluk_hoblis = self.scrape_hoblis(district_talukas)
            if not taluk_hoblis:
                logger.error("Failed to scrape taluk-hobli data")
                return False
            
            hobli_villages = self.scrape_villages(taluk_hoblis)
            if not hobli_villages:
                logger.error("Failed to scrape hobli-village data")
                return False
            
            # Create reverse mapping
            village_mapping = self.create_reverse_mapping(district_talukas, taluk_hoblis, hobli_villages)
            
            # Save data
            self.save_data(district_talukas, taluk_hoblis, hobli_villages, village_mapping)
            
            logger.info(f"Scraping completed successfully! Found {len(village_mapping)} villages.")
            return True
            
        except Exception as e:
            logger.error(f"Scraping failed: {str(e)}")
            return False

def main():
    scraper = KaveriScraper()
    
    # Check if changes are detected
    if scraper.check_for_changes():
        logger.info("Data changes detected and updated!")
    else:
        logger.info("No changes detected in the data.")

if __name__ == "__main__":
    main()
