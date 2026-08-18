import datetime
import requests
from time import sleep
import pandas as pd
from os import listdir


def simplify_product_data(products):
    simplified = []
    for product in products:
        items = product.get("items", [])
        sellers = items[0].get("sellers", []) if items else []
        offer = sellers[0].get("commertialOffer", {}) if sellers else {}
        images = items[0].get("images", []) if items else []

        ref_id_list = items[0].get("referenceId", []) if items else []
        simplified_product = {
            'linkText': product.get("linkText", ""),
            "product_name": product.get("productName", ""),
            'product_reference': product.get("productReference", ""),
            "description": product.get("description", ""),
            "selling_price": offer.get("Price", 0),
            "list_price": offer.get("ListPrice", 0),
            "categories": " > ".join(product.get("categories", [])),
            "release_date": product.get("releaseDate", ""),
            "image_url": images[0].get("imageUrl", "") if images else "",
            "measurement_unit": items[0].get("measurementUnit", "") if items else "",
            "unit_multiplier": items[0].get("unitMultiplier", 0) if items else 0,
            "sku_id": items[0].get("itemId", "") if items else "",
            "product_id": product.get("productId", ""),
            "brand": product.get("brand", ""),
            "ean": items[0].get("ean", "") if items else "",
            "ref_id": ref_id_list[0].get("Value", "") if ref_id_list else "",
            "available_quantity": offer.get("AvailableQuantity", 0),
            "seller": offer.get("seller", ""),
        }
        simplified.append(simplified_product)
    return simplified


STORE_NAME = "Atacadao"
BASE_URL = "https://www.atacadao.com.br"
SEARCH_URL = f"{BASE_URL}/api/catalog_system/pub/products/search"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'pt-BR,pt;q=0.9',
    'Referer': f'{BASE_URL}/',
}

buscas = [
    'arroz', 'feijao', 'acucar', 'oleo', 'cafe', 'leite', 'farinha',
    'macarrao', 'molho de tomate', 'sal', 'ovo', 'frango', 'carne',
    'porco', 'peixe', 'cebola', 'tomate', 'batata', 'banana',
    'laranja', 'maca', 'alface', 'cenoura', 'repolho',
    'sabao', 'detergente', 'papel higienico', 'shampoo', 'creme dental',
    'cerveja', 'refrigerante', 'suco', 'agua',
    'pao', 'presunto', 'queijo', 'manteiga', 'margarina',
    'iogurte', 'requeijao',
]

todos = []
session = requests.Session()
session.headers.update(headers)

for termo in buscas:
    i = 0
    max_tentativas = 3
    tentativa = 0
    while tentativa < max_tentativas:
        try:
            params = {
                'ft': termo,
                '_from': i,
                '_to': i + 49,
            }
            response = session.get(SEARCH_URL, params=params, timeout=15)
            if response.status_code in [200, 206]:
                produtos = response.json()
                if not produtos:
                    print(f'  [{STORE_NAME}] "{termo}": 0 produtos (from={i})')
                    break
                todos += simplify_product_data(produtos)
                print(f'  [{STORE_NAME}] "{termo}": {len(produtos)} produtos (from={i}, total={len(todos)})')
                if len(produtos) < 50:
                    break
                i += 50
                tentativa = 0
                sleep(0.5)
            elif response.status_code == 429:
                print(f'  [{STORE_NAME}] Rate limit em "{termo}", aguardando...')
                sleep(5)
                tentativa += 1
            else:
                print(f'  [{STORE_NAME}] Erro {response.status_code} em "{termo}" (from={i})')
                tentativa += 1
                sleep(2)
        except Exception as e:
            print(f'  [{STORE_NAME}] Exceção em "{termo}" (from={i}): {e}')
            tentativa += 1
            sleep(2)

    sleep(0.3)

print(f'\n[{STORE_NAME}] Total coletado: {len(todos)} registros brutos')

df = pd.DataFrame(todos)
if df.empty:
    print(f'[{STORE_NAME}] Nenhum produto coletado.')
else:
    df.drop_duplicates(subset=['sku_id'], keep='first', inplace=True)
    df['description'] = df['description'].str.replace(r'<[^>]+>', '', regex=True)
    df['description'] = df['description'].str.replace(r'\s+', ' ', regex=True).str.strip()

    hoje = datetime.datetime.now().strftime('%Y-%m-%d')
    mes = datetime.datetime.now().strftime('%Y%m')

    filename = f'atacadao_{mes}.txt'

    if filename not in listdir():
        print(f'Criando arquivo {filename}')
        with open(filename, 'w+', encoding='utf-8') as f:
            f.write("data;cod;produto;preco;preco_lista;unidade;fator_unid;cod_id;cod_sku;marca;ean;ref_id;disponivel\n")

    with open(filename, 'a+', encoding='utf-8') as f:
        for _, row in df.iterrows():
            f.write(f"{hoje};{row['linkText']};{row['product_name']};{row['selling_price']};{row['list_price']};{row['measurement_unit']};{row['unit_multiplier']};{row['product_id']};{row['sku_id']};{row['brand']};{row['ean']};{row['ref_id']};{row['available_quantity']}\n")

    print(f'[{STORE_NAME}] {len(df)} produtos gravados em {filename}')
