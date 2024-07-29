import requests, json
from bs4 import BeautifulSoup


def sjc_gold_price():
    url = "https://sjc.com.vn/giavang/textContent.php"

    response = requests.get(url)

    if response.status_code != 200:
        return f"Status code: {response.status_code}"
    

    soup = BeautifulSoup(response.content, 'html.parser')
    updated_time = soup.find('div', class_='w350').get_text(strip=True)
    currency = soup.find('div', class_='float_left ylo_text').get_text(strip=True)

    main_table = soup.find('table')

    new_soup = BeautifulSoup(f"<div>Cập nhật: {updated_time} | {currency}</div><table></table>", 'html.parser')
    tb = new_soup.find('table')
    for row in main_table.find_all('tr'):
        tr = new_soup.new_tag('tr')
        for j, col in enumerate(row.find_all('td')):
            txt = col.get_text()
            txt = txt.replace('99,99', '99.99% |')
            if '0.5 chỉ' in txt:
                txt = "Vàng nhẫn SJC 99.99% | 0.3 chỉ, 0.5 chỉ"
            if j != 0:
                txt = txt.replace(',', '.')
            td = new_soup.new_tag('td')
            td.string = txt.upper()
            tr.append(td)
        
        tb.append(tr)
        
    return new_soup
