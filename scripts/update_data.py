import json
import datetime
import os
import urllib.request

# Configuration
DATA_FILE = '../data/conferences.json'

# 这只是一个示例，实际的爬虫需要针对每个源（如 ccf-deadlines, ai-deadlines）编写解析逻辑
# 这里我们模拟一个简单的更新检查：如果日期已过，就尝试推测下一年（简单+1年）
# 在实际生产中，你应该抓取 https://raw.githubusercontent.com/ccf-ddl/ccf-deadlines/main/conference/all.yml 等

def load_data():
    file_path = os.path.join(os.path.dirname(__file__), DATA_FILE)
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f), file_path

def save_data(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Updated data saved to {file_path}")

def update_deadlines(conferences):
    today = datetime.date.today()
    updated_count = 0

    for conf in conferences:
        deadline_str = conf.get('next_deadline')
        if not deadline_str:
            continue
        
        try:
            deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d").date()
            
            # 如果截稿日期已过超过 30 天，且还没有更新，我们可以在这里通过爬虫去抓取新日期
            # 这里暂时用 placeholder 逻辑：提示需要手动/自动更新
            if deadline < today:
                print(f"Warning: {conf['title']} deadline ({deadline}) has passed.")
                # TODO: Implement real fetching logic here
                # e.g. fetch_from_ccf_deadlines(conf['id'])
                
                # 简单模拟：如果过期很久，假设下一年周期
                # days_passed = (today - deadline).days
                # if days_passed > 30:
                #    new_year = deadline.year + 1
                #    conf['next_deadline'] = deadline.replace(year=new_year).strftime("%Y-%m-%d")
                #    conf['deadline_note'] = f"{new_year} Cycle (Est)"
                #    updated_count += 1
                
        except ValueError:
            continue

    return updated_count

if __name__ == "__main__":
    try:
        data, path = load_data()
        print(f"Loaded {len(data)} conferences.")
        
        count = update_deadlines(data)
        
        if count > 0:
            save_data(data, path)
            print(f"Successfully updated {count} conferences.")
        else:
            print("No updates needed based on current logic.")
            
    except Exception as e:
        print(f"Error: {e}")
