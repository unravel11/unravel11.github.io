import json
import os
import datetime
import requests
import xml.etree.ElementTree as ET
import time

# Configuration
DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/papers.json')
MAX_PAPERS = 50  # Keep latest 50 papers

# arXiv Categories
# cs.CR: Cryptography and Security
# cs.SE: Software Engineering
# cs.AI: Artificial Intelligence
# cs.LG: Machine Learning
# cs.AR: Hardware Architecture
# quant-ph: Quantum Physics (for superconducting/quantum computing)
CATEGORIES = ['cs.CR', 'cs.SE', 'cs.AI', 'cs.AR', 'quant-ph']

# Search keywords to filter relevant papers from these categories
# We want: AI+Security, Arch+Superconducting/Hardware
KEYWORDS_AI_SEC = ['adversarial', 'backdoor', 'large language model', 'llm', 'jailbreak', 'prompt injection', 'robustness', 'privacy', 'vulnerability']
KEYWORDS_ARCH = ['accelerator', 'superconducting', 'quantum', 'microarchitecture', 'hardware security', 'fpga', 'asic']

def load_papers():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_papers(papers):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(papers)} papers to {DATA_FILE}")

def fetch_arxiv_papers():
    print("Fetching papers from arXiv...")
    base_url = 'http://export.arxiv.org/api/query?'
    
    # Construct query: (cat:cs.CR OR cat:cs.SE ... ) AND (submittedDate:[NOW-2DAYS TO NOW])
    # For simplicity, we just query by category and sort by submittedDate descending
    # Then we filter manually by keywords and date
    
    # Query for the last 100 papers in these categories
    cat_query = ' OR '.join([f'cat:{c}' for c in CATEGORIES])
    query = f'search_query={cat_query}&sortBy=submittedDate&sortOrder=descending&start=0&max_results=100'
    
    try:
        response = requests.get(base_url + query, timeout=20)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error fetching arXiv: {e}")
        return None

def parse_arxiv_response(xml_data):
    if not xml_data:
        return []
    
    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
    
    new_papers = []
    today = datetime.datetime.now(datetime.timezone.utc)
    
    for entry in root.findall('atom:entry', ns):
        try:
            id_url = entry.find('atom:id', ns).text
            paper_id = id_url.split('/')[-1]
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
            summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
            published = entry.find('atom:published', ns).text
            authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
            author_str = ', '.join(authors[:3]) + (' et al.' if len(authors) > 3 else '')
            link = entry.find("atom:link[@title='pdf']", ns)
            pdf_link = link.attrib['href'] if link is not None else id_url
            
            # Filter by keywords
            text_to_search = (title + ' ' + summary).lower()
            
            tags = []
            is_relevant = False
            
            # Check AI+Sec relevance
            if any(k in text_to_search for k in KEYWORDS_AI_SEC):
                tags.append("AI+Security")
                is_relevant = True
            
            # Check Arch relevance
            if any(k in text_to_search for k in KEYWORDS_ARCH):
                tags.append("Arch/Hardware")
                is_relevant = True
                
            if not is_relevant:
                continue
                
            # Simple AI Summary placeholder (since we don't have LLM API key here)
            # In production, call OpenAI/DeepSeek API here
            ai_summary = f"[AI 摘要] {summary[:150]}..." 
            
            paper_obj = {
                "id": f"arxiv-{paper_id}",
                "title": title,
                "authors": author_str,
                "source": "arXiv",
                "date": published[:10],
                "link": id_url,
                "summary": ai_summary,
                "tags": tags
            }
            new_papers.append(paper_obj)
            
        except Exception as e:
            print(f"Error parsing entry: {e}")
            continue
            
    return new_papers

def merge_papers(existing, new_ones):
    # Use a set of IDs to avoid duplicates
    existing_ids = {p['id'] for p in existing}
    merged = []
    
    # Add new ones first
    for p in new_ones:
        if p['id'] not in existing_ids:
            merged.append(p)
            existing_ids.add(p['id'])
            
    # Add old ones
    merged.extend(existing)
    
    # Sort by date descending
    merged.sort(key=lambda x: x['date'], reverse=True)
    
    return merged[:MAX_PAPERS]

if __name__ == "__main__":
    xml_data = fetch_arxiv_papers()
    new_papers = parse_arxiv_response(xml_data)
    print(f"Found {len(new_papers)} relevant papers from arXiv.")
    
    if new_papers:
        current_papers = load_papers()
        updated_papers = merge_papers(current_papers, new_papers)
        save_papers(updated_papers)
    else:
        print("No new relevant papers found.")
