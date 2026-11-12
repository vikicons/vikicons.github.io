import feedparser
import json
import os
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

rss_url = "https://baoxaydung.vn/rss/xay-dung.rss"
feed = feedparser.parse(rss_url)

VN_TZ = timezone(timedelta(hours=7))
DEFAULT_IMG = "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80"

# Khởi tạo bộ dịch tự động từ Tiếng Việt sang Tiếng Anh
translator = GoogleTranslator(source='vi', target='en')

def translate_text(text):
    """Hàm dịch an toàn, nếu lỗi tự động trả về văn bản gốc"""
    if not text:
        return ""
    try:
        # Giới hạn ký tự dịch nếu cần, deep-translator xử lý tốt tiêu đề báo chí
        translated = translator.translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"Lỗi dịch thuật: {e}")
        return text

def get_date(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        dt = datetime(*parsed[:6], tzinfo=timezone.utc).astimezone(VN_TZ)
    else:
        dt = datetime.now(VN_TZ)
    return dt.strftime("%d/%m/%Y")

def get_image(entry):
    if entry.get("enclosures"):
        url = entry.enclosures[0].get("href")
        if url:
            return url.strip()
    if entry.get("media_content"):
        url = entry.media_content[0].get("url")
        if url:
            return url.strip()
    soup = BeautifulSoup(entry.get("description", ""), "html.parser")
    img_tag = soup.find("img")
    if img_tag and img_tag.get("src"):
        return img_tag["src"]
    return DEFAULT_IMG

if feed.entries:
    news_list = []
    for entry in feed.entries[:5]:
        title_vi = entry.title.strip()
        print(f"Đang dịch tiêu đề trang chủ: {title_vi[:30]}...")
        title_en = translate_text(title_vi)
        
        news_list.append({
            "title": title_vi,             # Tiêu đề tiếng Việt hiển thị khi ở chế độ VN
            "title_en": title_en,         # Tiêu đề tiếng Anh hiển thị khi đổi sang EN
            "link": entry.link,
            "date": get_date(entry),
            "category": "Tin Xây Dựng",
            "category_en": "Construction News",
            "image": get_image(entry),
        })

    os.makedirs("src/data", exist_ok=True)
    with open("src/data/latest_news.json", "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=4)
    print(f"Đã cập nhật thành công {len(news_list)} bài viết trang chủ kèm bản dịch!")
else:
    print("Cảnh báo: Không đọc được RSS, giữ nguyên file JSON cũ.")