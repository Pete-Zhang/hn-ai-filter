import requests
import json
from datetime import datetime
import re

# Hacker News API基础URL（免费，无需认证）
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"

# AI相关关键词（可根据需要扩展）
AI_KEYWORDS = [
    'AI', 'artificial intelligence', 'machine learning', 'ML', 'LLM', 'Claude',
    'ChatGPT', 'GPT', 'Gemini', 'neural', 'deep learning', 'transformer',
    'agent', 'autonomous', 'language model', 'foundation model', 'RAG'
]

def get_top_stories():
    """获取最新的故事ID列表"""
    url = f"{HN_API_BASE}/topstories.json"
    response = requests.get(url, timeout=10)
    return response.json()[:100]  # 获取前100个

def get_item(item_id):
    """获取单个故事的详细信息"""
    url = f"{HN_API_BASE}/item/{item_id}.json"
    try:
        response = requests.get(url, timeout=5)
        return response.json()
    except:
        return None

def is_ai_related(title, text=""):
    """判断内容是否与AI高度相关"""
    content = (title + " " + text).lower()
    
    # 计算匹配的关键词数量
    matched_keywords = sum(1 for keyword in AI_KEYWORDS if keyword.lower() in content)
    
    # 如果匹配2个或以上关键词，则认为高度相关
    return matched_keywords >= 1

def fetch_ai_news():
    """获取所有AI相关的新闻"""
    ai_stories = []
    
    print("🔍 正在获取最新故事...")
    story_ids = get_top_stories()
    
    for idx, story_id in enumerate(story_ids):
        item = get_item(story_id)
        if not item:
            continue
            
        # 跳过已删除的项目
        if item.get('deleted') or item.get('dead'):
            continue
            
        title = item.get('title', '')
        text = item.get('text', '')
        
        # 检查是否与AI相关
        if is_ai_related(title, text):
            ai_stories.append({
                'id': item['id'],
                'title': title,
                'url': item.get('url', ''),
                'score': item.get('score', 0),
                'by': item.get('by', 'Unknown'),
                'time': item.get('time', 0),
                'comments': item.get('descendants', 0),
                'hn_url': f"https://news.ycombinator.com/item?id={item['id']}"
            })
        
        # 显示进度
        if (idx + 1) % 10 == 0:
            print(f"  已检查 {idx + 1}/{len(story_ids)} 个故事...")
    
    return ai_stories

def format_results(ai_stories):
    """格式化结果为Markdown"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""# 🤖 Hacker News AI相关内容筛选结果

**更新时间**: {timestamp}  
**找到**: {len(ai_stories)} 篇AI相关内容

---

"""
    
    # 按分数排序
    ai_stories.sort(key=lambda x: x['score'], reverse=True)
    
    for idx, story in enumerate(ai_stories, 1):
        content += f"""## {idx}. {story['title']}

- **来源**: [Hacker News](https://news.ycombinator.com/item?id={story['id']})
- **分数**: {story['score']} 👍
- **评论**: {story['comments']} 💬
- **作者**: {story['by']}
- **链接**: [{story['url'][:50]}...]({story['url']}) (如果有)

---

"""
    
    return content

def main():
    print("🚀 开始获取Hacker News AI相关内容...")
    
    # 获取AI相关的新闻
    ai_stories = fetch_ai_news()
    
    print(f"\\n✅ 找到 {len(ai_stories)} 篇AI相关内容")
    
    # 格式化为Markdown
    markdown_content = format_results(ai_stories)
    
    # 保存到文件
    with open('AI_NEWS.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print("💾 结果已保存到 AI_NEWS.md")
    
    # 同时保存JSON格式（用于其他处理）
    with open('ai_news.json', 'w', encoding='utf-8') as f:
        json.dump(ai_stories, f, ensure_ascii=False, indent=2)
    
    print("📊 JSON数据已保存到 ai_news.json")

if __name__ == "__main__":
    main()
