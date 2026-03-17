import requests
import datetime
import os

def fetch_tech_news():
    # 示例：抓取 Hacker News 的 Top Stories
    # 你也可以替换为 36Kr RSS (https://36kr.com/feed) 或其他 API
    api_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    item_url = "https://hacker-news.firebaseio.com/v0/item/{}.json"
    
    response = requests.get(api_url)
    story_ids = response.json()[:15]  # 取前15条
    
    news_list = []
    now = datetime.datetime.now(datetime.timezone.utc)
    
    for sid in story_ids:
        item = requests.get(item_url.format(sid)).json()
        # 转换发布时间，仅保留过去24小时内的
        pub_time = datetime.datetime.fromtimestamp(item.get('time', 0), datetime.timezone.utc)
        if (now - pub_time).total_seconds() < 86400:
            title = item.get('title')
            link = item.get('url', f"https://news.ycombinator.com/item?id={sid}")
            news_list.append(f"- **{title}** \n  [阅读全文]({link})")
            
    return "\n\n".join(news_list)

def send_to_wechat(content):
    send_key = os.getenv("SERVER_CHAN_SENDKEY")
    if not send_key:
        print("Error: SERVER_CHAN_SENDKEY not found.")
        return

    url = f"https://sctapi.ftqq.com/{send_key}.send"
    data = {
        "title": f"今日科技资讯 - {datetime.date.today()}",
        "desp": content if content else "今日暂无重大科技更新。"
    }
    res = requests.post(url, data=data)
    print(f"推送状态: {res.status_code}, 响应: {res.text}")

if __name__ == "__main__":
    content = fetch_tech_news()
    send_to_wechat(content)
