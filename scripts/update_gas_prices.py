import os
import json
import requests
from bs4 import BeautifulSoup

url = "https://www.pvoil.com.vn/tin-gia-xang-dau"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print(f"Đang lấy giá xăng dầu từ: {url}")

try:
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Tìm bảng (table) chứa dữ liệu giá xăng dầu trên trang PVOil
    table = soup.find('table')
    
    gas_prices = []
    effective_date = "Mới nhất"
    
    if table:
        rows = table.find_all('tr')
        for row in rows[1:]: # Bỏ qua dòng tiêu đề (header)
            cols = row.find_all('td')
            if len(cols) >= 4:
                stt = cols[0].text.strip()
                product = cols[1].text.strip()
                price = cols[2].text.strip()
                change = cols[3].text.strip()
                
                gas_prices.append({
                    "stt": stt,
                    "product": product,
                    "price": price,
                    "change": change
                })

    # Nếu cào được dữ liệu, ghi vào file JSON
    if gas_prices:
        os.makedirs("src/data", exist_ok=True)
        json_path = "src/data/gas_prices.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(gas_prices, f, ensure_ascii=False, indent=4)
        print(f"Đã cập nhật thành công {len(gas_prices)} bản ghi giá xăng dầu vào {json_path}!")
    else:
        print("Không tìm thấy dữ liệu bảng giá trong trang PVOil.")

except Exception as e:
    print(f"Lỗi khi cào giá xăng dầu: {e}")