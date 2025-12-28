import requests
import json
from datetime import datetime
import re
from html.parser import HTMLParser

# Hacker News API基础URL（免费，无需认证）
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"

# 核心AI关键词 - 高度相关
CORE_AI_KEYWORDS = [
        'AI', 'artificial intelligence', 'machine learning', 'ML', 'LLM', 
        'Claude', 'ChatGPT', 'GPT', 'Gemini', 'deep learning', 'transformer',
        'neural network', 'language model', 'foundation model', 'agent',
        'autonomous system', 'RAG', 'prompt', 'fine-tune', 'training'
]

# 相关AI关键词 - 辅助判断
RELATED_AI_KEYWORDS = [
        'data science', 'algorithm', 'neural', 'model', 'prediction',
        'classification', 'regression', 'NLP', 'vision', 'computer vision'
]

def get_top_stories():
        """获取最新的故事ID列表"""
        url = f"{HN_API_BASE}/topstories.json"
        response = requests.get(url, timeout=10)
        return response.json()[:150]  # 获取前150个确保足够数量

def get_item(item_id):
        """获取单个故事的详细信息"""
        url = f"{HN_API_BASE}/item/{item_id}.json"
        try:
                    response = requests.get(url, timeout=5)
                    return response.json()
                except:
        return None

def strip_html_tags(text):
        """移除HTML标签"""
        if not text:
                    return ""
                # 简单的HTML标签移除
    text = re.sub('<[^<]+?>', '', text)
    # 移除多个空格
    text = re.sub('\s+', ' ', text)
    return text.strip()

def extract_summary(text, max_length=200):
        """从文本中提取摘要（前几句话）"""
        if not text:
                    return "无摘要"

    text = strip_html_tags(text)

    # 按句子分割（简单方法）
    sentences = re.split(r'[。！？.!?]+', text)

    summary = ""
    for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 5:  # 避免太短的句子
                                if len(summary) + len(sentence) <= max_length:
                                                    summary += sentence + "。"
                else:
                                    break

    if not summary:
                # 如果没有句子，直接截断
                summary = text[:max_length] + "..." if len(text) > max_length else text

    return summary if summary else "无摘要"

def get_article_content(url):
        """尝试获取文章内容（可选功能）"""
        if not url or url.startswith('item?'):
                    return None

    try:
                response = requests.get(url, timeout=5)
                # 简单的内容提取
        text = response.text
        # 移除HTML标签并提取主要内容
        text = re.sub('<script[^<]*</script>', '', text, flags=re.DOTALL)
        text = re.sub('<style[^<]*</style>', '', text, flags=re.DOTALL)
        text = strip_html_tags(text)

        # 取前500字作为内容
        return text[:500]
    except:
        return None

def is_highly_ai_related(title, text=""):
        """精准判断内容是否与AI高度相关"""
        content = (title + " " + text).lower()

    # 计算核心关键词匹配数
    core_matches = sum(1 for keyword in CORE_AI_KEYWORDS if keyword.lower() in content)

    # 计算相关关键词匹配数
    related_matches = sum(1 for keyword in RELATED_AI_KEYWORDS if keyword.lower() in content)

    # 排除非AI相关的假阳性词汇
    exclusions = [
                'mushroom', 'hallucination', 'parasite', 'spain', 'gold', 
                'gaming', 'game', 'rainbow six', 'video game',
                'history', 'ancient', 'public domain'
    ]

    for exclusion in exclusions:
                if exclusion.lower() in content:
                                return False

    # 判断逻辑：需要至少1个核心关键词，或2个相关关键词
    is_related = core_matches >= 1 or related_matches >= 2

    return is_related

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
        url = item.get('url', '')

        # 检查是否与AI高度相关
        if is_highly_ai_related(title, text):
                        # 尝试获取文章内容作为摘要
                        summary = None
                        if url:
                                            content = get_article_content(url)
                                            if content:
                                                                    summary = extract_summary(content)

            # 如果没有获取到，尝试使用文章中的text字段
            if not summary:
                                if text:
                                                        summary = extract_summary(text)
            else:
                    summary = f"暂无摘要 - {title[:100]}"

            ai_stories.append({
                                'id': item['id'],
                                'title': title,
                                'url': url,
                                'score': item.get('score', 0),
                                'by': item.get('by', 'Unknown'),
                                'time': item.get('time', 0),
                                'comments': item.get('descendants', 0),
                                'summary': summary,
                                'hn_url': f"https://news.ycombinator.com/item?id={item['id']}"
            })

        # 显示进度
        if (idx + 1) % 20 == 0:
                        print(f"  已检查 {idx + 1}/{len(story_ids)} 个故事，已找到 {len(ai_stories)} 篇AI相关内容...")

    return ai_stories

def format_results(ai_stories):
        """格式化结果为Markdown"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = f"""# 🤖 Hacker News AI相关内容筛选结果

    **更新时间**: {timestamp}  
    **找到**: {len(ai_stories)} 篇高度相关AI内容

    ---

    """

    # 按分数排序
    ai_stories.sort(key=lambda x: x['score'], reverse=True)

    for idx, story in enumerate(ai_stories, 1):
                content += f"""## {idx}. {story['title']}

                **来源**: [Hacker News](https://news.ycombinator.com/item?id={story['id']})  
                **评分**: {story['score']} 👍 | **评论**: {story['comments']} 💬  
                **作者**: {story['by']}

                **摘要**: {story['summary']}

                """

        if story['url']:
                        content += f"**原文链接**: [{story['url'][:60]}...]({story['url']})\n\n"

        content += "---\n\n"

    return content

def main():
        print("🚀 开始获取Hacker News AI相关内容...")

    # 获取AI相关的新闻
    ai_stories = fetch_ai_news()

    print(f"\n✅ 找到 {len(ai_stories)} 篇高度相关的AI内容")

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
