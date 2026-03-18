import requests
import datetime
import os
import feedparser
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

def translate_text(text):
    """将文本翻译成中文，如果翻译失败则返回原内容"""
    if not text or not any(c.isalpha() for c in text): # 判空或无字母
        return text
    try:
        # 自动检测源语言并翻译为简中
        return GoogleTranslator(source='auto', target='zh-CN').translate(text)
    except Exception as e:
        print(f"翻译失败: {e}")
        return text

def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text().strip()

def fetch_ai_news():
    sources = {
        "机器之心": "https://www.syncedreview.com/feed/",
        "TechCrunch - AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "The Verge - AI": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"
    }
    
    news_items = []
    now = datetime.datetime.now(datetime.timezone.utc)
    
    for name, url in sources.items():
        print(f"正在抓取并翻译: {name}...")
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                pub_time = None
                if hasattr(entry, 'published_parsed'):
                    pub_time = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                
                if pub_time and (now - pub_time).total_seconds() < 86400:
                    # 翻译标题
                    translated_title = translate_text(entry.title)
                    
                    # 翻译摘要
                    summary = clean_html(entry.get('summary', ''))
                    short_summary = summary[:200] if len(summary) > 200 else summary
                    translated_summary = translate_text(short_summary)
                    
                    news_items.append(
                        f"### {translated_title}\n"
                        f"- **来源**: {name}\n"
                        f"- **摘要**: {translated_summary}\n"
                        f"- 🔗 [查看详情]({entry.link})"
                    )
                    count += 1
                
                if count >= 3: break 
        except Exception as e:
            print(f"抓取 {name} 失败: {e}")

    return "\n\n---\n\n".join(news_items)

def send_to_wechat(content):
    send_key = os.getenv("SERVER_CHAN_SENDKEY")
    if not send_key: return
    url = f"https://sctapi.ftqq.com/{send_key}.send"
    data = {
        "title": f"🤖 全球 AI 资讯(已翻译) - {datetime.date.today()}",
        "desp": content if content else "今日暂无 AI 动态。"
    }
    requests.post(url, data=data)

if __name__ == "__main__":
    ai_content = fetch_ai_news()
    send_to_wechat(ai_content)
