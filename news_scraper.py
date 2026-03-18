import requests
import datetime
import os
import feedparser

def fetch_ai_news():
    # 定义新闻源 (RSS 链接)
    sources = {
        "机器之心 (Synced)": "https://www.syncedreview.com/feed/",
        "36Kr - 人工智能": "https://36kr.com/feed-category/37",
        "ArXiv - AI 论文": "http://rss.arxiv.org/rss/cs.AI",
        "TechCrunch - AI": "https://techcrunch.com/category/artificial-intelligence/feed/"
    }
    
    news_items = []
    now = datetime.datetime.now(datetime.timezone.utc)
    
    for name, url in sources.items():
        print(f"正在抓取: {name}...")
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                # 只取过去 24 小时的新闻
                # 某些 RSS 源的日期格式不一，这里做简单兼容处理
                pub_time = None
                if hasattr(entry, 'published_parsed'):
                    pub_time = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                
                if pub_time and (now - pub_time).total_seconds() < 86400:
                    title = entry.title
                    link = entry.link
                    news_items.append(f"### [{name}] {title}\n🔗 [点击阅读]({link})")
                    count += 1
                
                if count >= 5: break # 每个源最多取 5 条，防止消息太长
        except Exception as e:
            print(f"抓取 {name} 失败: {e}")

    return "\n\n---\n\n".join(news_items)

def send_to_wechat(content):
    send_key = os.getenv("SERVER_CHAN_SENDKEY")
    if not send_key: return

    url = f"https://sctapi.ftqq.com/{send_key}.send"
    data = {
        "title": f"🤖 AI 深度资讯 - {datetime.date.today()}",
        "desp": content if content else "过去 24 小时暂无关注的 AI 动态。"
    }
    requests.post(url, data=data)

if __name__ == "__main__":
    ai_content = fetch_ai_news()
    send_to_wechat(ai_content)
