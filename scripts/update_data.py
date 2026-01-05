import json
import datetime
import os
import requests
import yaml
import re

# Configuration
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/conferences.json')
CCF_DEADLINES_URL = "https://raw.githubusercontent.com/ccf-ddl/ccf-deadlines/main/conference/all.yml"

def load_local_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_local_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved to {DATA_FILE}")

def fetch_ccf_data():
    print("Fetching data from ccf-deadlines...")
    try:
        response = requests.get(CCF_DEADLINES_URL, timeout=10)
        response.raise_for_status()
        # CCF YAML is a list of objects
        return yaml.safe_load(response.text)
    except Exception as e:
        print(f"Error fetching CCF data: {e}")
        return []

def parse_date(date_str):
    if not date_str:
        return None
    # Handle various formats if necessary, but CCF usually uses YYYY-MM-DD
    # Sometimes it might have time, we strip it
    try:
        return datetime.datetime.strptime(str(date_str).split()[0], "%Y-%m-%d").date()
    except:
        return None

def get_future_deadline(ccf_entry):
    """
    Extract the most relevant deadline from a CCF entry.
    CCF entry structure example:
    - title: ICSE
      confs:
        - year: 2024
          timeline:
            - deadline: '2023-10-01'
    """
    if not ccf_entry or 'confs' not in ccf_entry:
        return None, None, None

    # Sort confs by year descending
    confs = sorted(ccf_entry['confs'], key=lambda x: x.get('year', 0), reverse=True)
    
    today = datetime.date.today()
    
    for conf in confs:
        timeline = conf.get('timeline', [])
        if not timeline:
            continue
            
        # Try to find the latest deadline in this year's cycle
        # Usually we want the 'abstract' or 'full paper' deadline
        # CCF data is simple, usually just 'deadline'
        
        for item in timeline:
            deadline_str = item.get('deadline')
            deadline = parse_date(deadline_str)
            
            if deadline and deadline >= today:
                # Found a future deadline!
                return deadline, conf.get('date'), conf.get('place')
    
    # If no future deadline found, return the latest past one for reference (to predict next year)
    if confs:
        latest_conf = confs[0]
        timeline = latest_conf.get('timeline', [])
        if timeline:
            last_deadline = parse_date(timeline[0].get('deadline'))
            return last_deadline, latest_conf.get('date'), latest_conf.get('place')

    return None, None, None

def predict_next_deadline(last_deadline):
    if not last_deadline:
        return None
    # Simple logic: +365 days
    # Adjust to same weekday? For now, just +365 is good enough estimation
    next_date = last_deadline + datetime.timedelta(days=365)
    return next_date

def update_conferences():
    local_data = load_local_data()
    ccf_data = fetch_ccf_data()
    
    # Create a lookup map for CCF data by title (uppercase)
    ccf_map = {entry['title'].upper(): entry for entry in ccf_data if 'title' in entry}
    
    today = datetime.date.today()
    updates_count = 0
    
    for conf in local_data:
        conf_id = conf.get('title', '').upper()
        # Some mapping fixes if ids differ
        if conf_id == 'S&P (OAKLAND)': conf_id = 'SP'
        if conf_id == 'USENIX SEC': conf_id = 'USENIX-SECURITY'
        if conf_id == 'FSE': conf_id = 'ESEC/FSE' # CCF often uses ESEC/FSE
        
        ccf_entry = ccf_map.get(conf_id)
        
        if ccf_entry:
            deadline, conf_date, location = get_future_deadline(ccf_entry)
            
            if deadline:
                deadline_str = deadline.strftime("%Y-%m-%d")
                
                # Logic:
                # 1. If we found a FUTURE deadline from CCF, use it directly.
                # 2. If the deadline from CCF is PAST, we predict next year.
                
                if deadline >= today:
                    if conf.get('next_deadline') != deadline_str:
                        conf['next_deadline'] = deadline_str
                        conf['deadline_note'] = "Verified (Source: CCF)"
                        if location: conf['location'] = location
                        if conf_date: conf['conference_date'] = str(conf_date)
                        updates_count += 1
                        print(f"Updated {conf['title']} to {deadline_str} (Source)")
                else:
                    # The latest data in CCF is already past.
                    # We check if our local data is also past.
                    local_deadline = parse_date(conf.get('next_deadline'))
                    
                    if local_deadline and local_deadline < today:
                        # Both local and CCF are past -> Predict next year based on CCF last date
                        predicted = predict_next_deadline(deadline)
                        predicted_str = predicted.strftime("%Y-%m-%d")
                        
                        if conf.get('next_deadline') != predicted_str:
                            conf['next_deadline'] = predicted_str
                            conf['deadline_note'] = "Expected (Auto-predicted)"
                            updates_count += 1
                            print(f"Predicted {conf['title']} to {predicted_str} (Based on last: {deadline})")
            else:
                print(f"No deadline found in CCF for {conf['title']}")
        else:
            # Fallback for conferences not in CCF DB or named differently
            # Check if local deadline is past, if so, predict +1 year
            local_deadline = parse_date(conf.get('next_deadline'))
            if local_deadline and local_deadline < today:
                predicted = predict_next_deadline(local_deadline)
                conf['next_deadline'] = predicted.strftime("%Y-%m-%d")
                conf['deadline_note'] = "Expected (Auto-predicted)"
                updates_count += 1
                print(f"Predicted {conf['title']} (Local-based) to {conf['next_deadline']}")

    if updates_count > 0:
        save_local_data(local_data)
        print(f"Total updates: {updates_count}")
    else:
        print("No updates needed.")

if __name__ == "__main__":
    update_conferences()
