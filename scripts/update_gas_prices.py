import os
import json
from datetime import datetime, timezone, timedelta
import cloudscraper
from bs4 import BeautifulSoup

url = "https://www.pvoil.com.vn/tin-gia-xang-dau"

print(f"Đang khởi tạo bộ vượt rào Cloudflare để lấy dữ liệu từ: {url}")

try:
    # Tạo scraper giả lập trình duyệt Chrome thật trên Windows để vượt qua Cloudflare
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    response = scraper.get(url, timeout=20)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Tìm bảng chứa dữ liệu giá xăng dầu
    container = soup.find(class_='oilpricescontainer')
    table = container.find('table') if container else soup.find('table')
    
    gas_items = []
    
    if table:
        rows = table.find_all('tr')
        print(f"Đã vượt rào thành công! Tìm thấy bảng dữ liệu với {len(rows)} dòng.")
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                stt = cols[0].text.strip()
                if stt.isdigit():
                    product = cols[1].text.strip()
                    price = cols[2].text.strip()
                    change = cols[3].text.strip()
                    
                    gas_items.append({
                        "stt": stt,
                        "product": product,
                        "price": price,
                        "change": change
                    })
                    print(f"Đã đọc: {product} - {price} (Chênh lệch: {change})")

    if gas_items:
        os.makedirs("src/data", exist_ok=True)
        json_path = "src/data/gas_prices.json"
        
        vn_time = datetime.now(timezone(timedelta(hours=7)))
        formatted_time = vn_time.strftime("%d/%m/%Y lúc %H:%M:%S")

        output_data = {
            "last_updated": formatted_time,
            "prices": gas_items
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
            
        print(f"Đã cập nhật thành công {len(gas_items)} bản ghi vào {json_path} lúc {formatted_time}!")
    else:
        print("CẢNH BÁO: Đã vào được trang nhưng không tìm thấy dữ liệu bảng sản phẩm.")

except Exception as e:
    print(f"Lỗi khi cào dữ liệu qua Cloudflare: {e}")