import json
import sys
import time
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

BASE_URL = 'https://www.ifood.com.br'

MERCHANTS = [
    {
        'id': '3907a7c5-6256-4f37-b76d-9fed9dd628e8',
        'slug': 'super-prix---ipanema-ipanema',
        'name': 'Super Prix - Ipanema',
        'city': 'rio-de-janeiro-rj',
        'file_prefix': 'ifood_superprix',
    },
    {
        'id': 'f2d53594-1510-41ae-90a8-c85ffdaa5ba6',
        'slug': 'zona-sul---loja-22---sao-conrado-sao-conrado',
        'name': 'Zona Sul - São Conrado',
        'city': 'rio-de-janeiro-rj',
        'file_prefix': 'ifood_zonasul',
    },
]


def scrape_merchant(context, merchant):
    collected = []
    page = context.new_page()

    def handle_response(response):
        if response.status != 200:
            return
        ct = response.headers.get('content-type', '')
        if 'json' not in ct:
            return
        url = response.url
        if '/multicategory/' not in url or '/catalog' not in url:
            return
        try:
            body = response.text()
            if len(body) < 500:
                return
            data = json.loads(body)
            menu = data.get('data', {}).get('menu', [])
            for m in menu:
                cat_name = m.get('name', '')
                for item in m.get('itens', []):
                    collected.append({
                        'categoria': cat_name,
                        'id': item.get('id', ''),
                        'produto': item.get('description', ''),
                        'detalhes': item.get('details', ''),
                        'preco': item.get('unitPrice', 0),
                    })
        except:
            pass

    page.on('response', handle_response)

    merchant_url = f'{BASE_URL}/delivery/{merchant["city"]}/{merchant["slug"]}/{merchant["id"]}'

    for attempt in range(3):
        try:
            page.goto(merchant_url, wait_until='networkidle', timeout=25000)
            break
        except:
            time.sleep(2)

    time.sleep(3)

    page.evaluate('''() => {
        for (const b of document.querySelectorAll('button, a')) {
            if (b.textContent.trim() === 'Ignorar') { b.click(); return; }
        }
    }''')
    time.sleep(5)

    page.close()
    return collected


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale='pt-BR',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            geolocation={'latitude': -22.9984669, 'longitude': -43.2680693},
            permissions=['geolocation'],
        )

        for merchant in MERCHANTS:
            print(f'\nScraping {merchant["name"]}...')
            items = scrape_merchant(context, merchant)
            print(f'  Collected {len(items)} items')

            if not items:
                print(f'  RETRY with fresh context...')
                context.close()
                context = browser.new_context(
                    locale='pt-BR',
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    geolocation={'latitude': -22.9984669, 'longitude': -43.2680693},
                    permissions=['geolocation'],
                )
                items = scrape_merchant(context, merchant)
                print(f'  Retry collected {len(items)} items')

            if not items:
                print(f'  SKIP - no items')
                continue

            today = datetime.now().strftime('%Y-%m-%d')
            filename = f'{merchant["file_prefix"]}_{datetime.now().strftime("%Y%m")}.txt'
            header_needed = not (merchant.get('_file_exists', False))
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    header_needed = False
            except FileNotFoundError:
                header_needed = True

            with open(filename, 'a', encoding='utf-8') as f:
                if header_needed:
                    f.write('data;id;produto;detalhes;preco;categoria\n')
                for item in items:
                    line = f'{today};{item["id"]};{item["produto"]};{item["detalhes"]};{item["preco"]};{item["categoria"]}\n'
                    f.write(line)

            print(f'  Saved {len(items)} items to {filename}')

        browser.close()


if __name__ == '__main__':
    main()
