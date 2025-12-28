import requests
import json
from datetime import datetime
import re

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"

AI_KEYWORDS = {
            'AI', 'artificial intelligence', 'machine learning', 'ML', 'LLM',
            'Claude', 'ChatGPT', 'GPT', 'Gemini', 'deep learning', 'transformer',
            'neural', 'LLM', 'language model', 'foundation model'
}

def get_top_stories():
            url = f"{HN_API_BASE}/topstories.json"
            response = requests.get(url, timeout=10)
            return response.json()[:100]

def get_item(item_id):
            url = f"{HN_API_BASE}/item/{item_id}.json"
            try:
                            response = requests.get(url, timeout=5)
                            return response.json()
                        except:
        return None

def extract_summary(text):
            if not text:
                            return "无摘要"
                        text = re.sub('<[^<]+?>', '', text)
    text = text.strip()
    if len(text) > 150:
                    return text[:150] + "..."
                return text

def is_ai_related(title, text=""):
            content = (title + " " + text).lower()
    match_count = sum(1 for keyword in AI_KEYWORDS if keyword.lower() in content)
    return match_count >= 1

def fetch_ai_news():
            ai_stories = []
    print("获取最新故事...")
    story_ids = get_top_stories()

    for idx, story_id in enumerate(story_ids):
                    item = get_item(story_id)
                    if not item:
                                        continue
                                    if item.get('deleted') or item.get('dead'):
                                                        continue

        title = item.get('title', '')
        text = item.get('text', '')
        url = item.get('url', '')

        if is_ai_related(title, text):
                            summary = extract_summary(text) if text else "无摘要"

            ai_stories.append({
                                    'id': item['id'],
                                    'title': title,
                                    'url': url,
                                    'score': item.get('score', 0),
                                    'by': item.get('by', 'Unknown'),
                                    'comments': item.get('descendants', 0),
                                    'summary': summary
            })

        if (idx + 1) % 20 == 0:
                            print(f"已检查{idx+1}个故事，找到{len(ai_stories)}篇...")

    return ai_stories

def format_markdown(stories):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"# 🤖 Hacker News AI相关内容\n\n**更新**: {timestamp}\n**找到**: {len(stories)} 篇\n\n---\n\n"

    stories = sorted(stories, key=lambda x: x['score'], reverse=True)

    for idx, story in enumerate(stories, 1):
                    content += f"## {idx}. {story['title']}\n\n"
        content += f"**评分**: {story['score']} | **评论**: {story['comments']}\n"
        content += f"**作者**: {story['by']}\n\n"
        content += f"**摘要**: {story['summary']}\n\n"
        if story['url']:
                            content += f"**链接**: {story['url']}\n\n"
                        content += "---\n\n"

    return content

def main():
            print("开始获取Hacker News AI相关内容...")
    ai_stories = fetch_ai_news()
    print(f"找到{len(ai_stories)}篇AI相关内容")

    markdown = format_markdown(ai_stories)

    with open('AI_NEWS.md', 'w', encoding='utf-8') as f:
                    f.write(markdown)
    print("已保存到AI_NEWS.md")

    with open('ai_news.json', 'w', encoding='utf-8') as f:
                    json.dump(ai_stories, f, ensure_ascii=False, indent=2)
    print("已保存到ai_news.json")

if __name__ == "__main__":
            main()
