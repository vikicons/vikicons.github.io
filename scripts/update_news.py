import feedparser
import json
import os
from bs4 import BeautifulSoup

rss_url = "https://baoxaydung.vn/rss/xay-dung.rss"
feed = feedparser.parse(rss_url)

# CHỈ CẬP NHẬT KHI THỰC SỰ CÓ BÀI VIẾT TỪ RSS
if feed.entries:
    news_list = []
    for entry in feed.entries[:6]:
        description_html = entry.get("description", "")
        soup = BeautifulSoup(description_html, "html.parser")
        img_tag = soup.find("img")
        img_url = img_tag["src"] if img_tag else "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80"
        
        news_item = {
            "title": entry.title.strip(),
            "link": entry.link,
            "date": "29/10/2026", # Hoặc giữ logic bóc ngày tháng của bạn
            "category": "Tin Xây Dựng",
            "image": img_url
        }
        news_list.append(news_item)

    os.makedirs("src/data", exist_ok=True)
    json_path = "src/data/latest_news.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=4)
    print(f"Đã cập nhật thành công {len(news_list)} bài viết!")
else:
    print("Cảnh báo: Không thể đọc dữ liệu từ RSS, giữ nguyên file JSON cũ.")