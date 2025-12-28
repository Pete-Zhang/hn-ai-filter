import requests
import json
from datetime import datetime

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"

def main():
    print("Getting top stories...")
    url = f"{HN_API_BASE}/topstories.json"
    stories = requests.get(url, timeout=10).json()[:50]
    
    ai_keywords = ['AI', 'machine learning', 'Claude', 'ChatGPT', 'neural', 'deep learning']
    results = []
    
    for story_id in stories:
        try:
            item_url = f"{HN_API_BASE}/item/{story_id}.json"
            item = requests.get(item_url, timeout=5).json()
            
            title = item.get('title', '').lower()
            text = item.get('text', '').lower()
            content = title + " " + text
            
            if any(keyword.lower() in content for keyword in ai_keywords):
                results.append({
                    'title': item.get('title', ''),
                    'score': item.get('score', 0),
                    'by': item.get('by', ''),
                    'url': item.get('url', ''),
                    'comments': item.get('descendants', 0)
                })
        except:
            pass
    
    # Save markdown
    md = f"# AI News\\n\\nUpdated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\nFound: {len(results)}\\n\\n"
    for i, r in enumerate(sorted(results, key=lambda x: x['score'], reverse=True), 1):
        md += f"## {i}. {r['title']}\\n"
        md += f"Score: {r['score']} | Comments: {r['comments']}\\n"
        md += f"Author: {r['by']}\\n"
        if r['url']:
            md += f"Link: {r['url']}\\n"
        md += "\\n---\\n\\n"
    
    with open('AI_NEWS.md', 'w', encoding='utf-8') as f:
        f.write(md)
    
    with open('ai_news.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
