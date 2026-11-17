import os
import json
from datetime import datetime, timezone, timedelta
import cloudscraper
from bs4 import BeautifulSoup

url = "https://www.pvoil.com.vn/tin-gia-xang-dau"
print(f"Đang kết nối tới: {url}")

try:
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    response = scraper.get(url, timeout=25)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Tìm bảng chứa dữ liệu giá xăng dầu trên trang PVOil
    table = soup.find('table')
    gas_items = []
    
    if table:
        rows = table.find_all('tr')
        print(f"Tìm thấy bảng dữ liệu với {len(rows)} hàng.")
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                stt = cols[0].text.strip()
                # Kiểm tra nếu là dòng chứa số thứ tự sản phẩm (1, 2, 3, 4)
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
                    print(f"Đã cào thành công: {product} | Giá: {price} | Chênh lệch: {change}")

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
            
        print(f"Đã ghi dữ liệu mới vào {json_path} thành công lúc {formatted_time}!")
    else:
        print("CẢNH BÁO: Không tìm thấy dữ liệu dòng sản phẩm nào trong bảng.")

except Exception as e:
    print(f"Lỗi khi cào dữ liệu: {e}")