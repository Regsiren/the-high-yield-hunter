import os
import threading
import time
import feedparser
import requests
import pandas as pd
from flask import Flask
from anthropic import Anthropic

app = Flask(__name__)

# --- CONFIGURATION (Set these in Railway Variables) ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CH_API_KEY = os.getenv("COMPANIES_HOUSE_KEY")
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")

def send_telegram(message, mode="HTML"):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": mode}
    requests.post(url, json=payload)

# --- BOT 2: THE NEWS CURATOR ---
@app.route('/run')
def run_curator_route():
    threading.Thread(target=run_curator).start()
    return "<h1>Intelligence Triggered</h1>", 200

def run_curator():
    # ... (Your successful Chief of Staff logic from before goes here)
    pass 

# --- BOT 3: THE LONDON ENRICHER ---
@app.route('/scout')
def scout_leads():
    threading.Thread(target=run_enricher).start()
    return "<h1>Scout Engine Active</h1><p>Checking London Property SPVs...</p>", 200

def run_enricher():
    try:
        send_telegram("🔍 <b>Bot 3:</b> Searching London for Property SPVs...")
        # 1. Search Companies House for London Property Firms
        ch_url = "https://api.company-information.service.gov.uk/advanced-search/companies"
        ch_params = {"location": "London", "sic_codes": "68209", "company_status": "active", "size": 5}
        res = requests.get(ch_url, params=ch_params, auth=(CH_API_KEY, ''))
        
        companies = res.json().get('items', [])
        for co in companies:
            name = co.get('company_name')
            
            # 2. Use Apollo to find the Director for this Company
            apollo_url = "https://api.apollo.io/v1/people/match"
            apollo_payload = {
                "api_key": APOLLO_API_KEY,
                "organization_name": name,
                "person_titles": ["Director", "Owner", "Founder"]
            }
            
            apollo_res = requests.post(apollo_url, json=apollo_payload)
            person = apollo_res.json().get('person', {})
            
            if person:
                lead_msg = (
                    f"🎯 <b>NEW LEAD FOUND</b><br>"
                    f"Company: {name}<br>"
                    f"Director: {person.get('first_name')} {person.get('last_name')}<br>"
                    f"Title: {person.get('title')}<br>"
                    f"LinkedIn: {person.get('linkedin_url', 'Not found')}"
                )
                send_telegram(lead_msg)
            
            time.sleep(1) # Safety delay
            
    except Exception as e:
        send_telegram(f"❌ Scout Error: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
