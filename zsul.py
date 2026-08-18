import datetime
import requests
from time import sleep
import pandas as pd
import base64
import json
from os import listdir


def simplify_product_data(products):
    simplified = []
    for product in products:
        price_range = product.get("priceRange", {})
        selling = price_range.get("sellingPrice", {})
        listing = price_range.get("listPrice", {})
        items = product.get("items", [])
        item0 = items[0] if items else {}
        sellers = item0.get("sellers", [])
        offer = sellers[0].get("commertialOffer", {}) if sellers else {}
        images = item0.get("images", [])
        ref_id_list = item0.get("referenceId", [])
        simplified.append({
            'linkText': product.get("linkText", ""),
            "product_name": product.get("productName", ""),
            'product_reference': product.get("productReference", ""),
            "description": product.get("description", ""),
            "selling_price": selling.get("lowPrice", 0),
            "list_price": listing.get("lowPrice", 0),
            "categories": " > ".join(product.get("categories", [])),
            "release_date": product.get("releaseDate", ""),
            "image_url": images[0].get("imageUrl", "") if images else "",
            "measurement_unit": item0.get("measurementUnit", ""),
            "unit_multiplier": item0.get("unitMultiplier", 0),
            "sku_id": item0.get("itemId", ""),
            "product_id": product.get("productId", ""),
            "brand": product.get("brand", ""),
            "ean": item0.get("ean", ""),
            "ref_id": ref_id_list[0].get("Value", "") if ref_id_list else "",
            "available_quantity": offer.get("AvailableQuantity", 0),
        })
    return simplified


STORE_NAME = "ZonaSul"
BASE_URL = "https://www.zonasul.com.br"
GRAPHQL_URL = f"{BASE_URL}/_v/segment/graphql/v1"
CATALOG_URL = f"{BASE_URL}/api/catalog_system/pub/products/search"

SHA256 = "b869cb20f1b9f801396a9999b09f67a678f85687ee97d63da8a17127527c4616"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'pt-BR,pt;q=0.9',
})

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


def fetch_graphql(session, termo, from_idx, to_idx):
    variables = {
        "query": termo,
        "map": "",
        "category": "",
        "priceRange": "",
        "collection": "",
        "salesChannel": "1",
        "orderBy": "OrderByScoreDESC",
        "from": from_idx,
        "to": to_idx,
        "hideUnavailableItems": True,
        "simulationBehavior": "default"
    }
    encoded_vars = base64.b64encode(json.dumps(variables).encode()).decode()
    extensions = json.dumps({
        "persistedQuery": {
            "version": 1,
            "sha256Hash": SHA256,
            "sender": "zonasul.resources@0.x",
            "provider": "vtex.search-graphql@0.x"
        },
        "variables": encoded_vars
    })
    params = {
        'workspace': 'master',
        'maxAge': 'short',
        'appsEtag': 'remove',
        'domain': 'store',
        'locale': 'pt-BR',
        'operationName': 'products',
        'variables': '{}',
        'extensions': extensions,
    }
    r = session.get(GRAPHQL_URL, params=params, timeout=15)
    data = r.json().get('data', {})
    products = data.get('products', [])
    if products is None:
        products = []
    return products


print(f'[{STORE_NAME}] Obtendo sessao...')
try:
    session.get(BASE_URL, timeout=15)
    sleep(0.3)
    session.get(f'{BASE_URL}/api/checkout/pub/orderForm', timeout=10)
    print(f'[{STORE_NAME}] Sessao OK, cookies={len(session.cookies)}')
except Exception as e:
    print(f'[{STORE_NAME}] Erro sessao: {e}')

print(f'[{STORE_NAME}] Iniciando coleta via GraphQL (products hash)...')

for termo in buscas:
    from_idx = 0
    to_idx = 49
    erro = 0
    while True:
        try:
            produtos = fetch_graphql(session, termo, from_idx, to_idx)
            if not produtos:
                break
            todos += simplify_product_data(produtos)
            print(f'  [{STORE_NAME}] "{termo}" from={from_idx} +{len(produtos)} total={len(todos)}')
            if len(produtos) < 50:
                break
            from_idx = to_idx + 1
            to_idx = from_idx + 49
            erro = 0
            sleep(0.3)
        except Exception as e:
            erro += 1
            print(f'  [{STORE_NAME}] Erro "{termo}" from={from_idx}: {e}')
            if erro > 2:
                break
            sleep(1)
    sleep(0.2)

print(f'\n[{STORE_NAME}] GraphQL total: {len(todos)} produtos')

if not todos:
    print(f'[{STORE_NAME}] GraphQL retornou 0. Tentando VTEX catalog API...')
    for termo in buscas:
        i = 0
        tentativa = 0
        while tentativa < 3:
            try:
                r = session.get(CATALOG_URL, params={'ft': termo, '_from': i, '_to': i + 49}, timeout=15)
                if r.status_code in [200, 206]:
                    produtos = r.json()
                    if not produtos:
                        break
                    for p in produtos:
                        items = p.get("items", [])
                        sellers = items[0].get("sellers", []) if items else []
                        offer = sellers[0].get("commertialOffer", {}) if sellers else {}
                        images = items[0].get("images", []) if items else []
                        ref_id_list = items[0].get("referenceId", []) if items else []
                        todos.append({
                            'linkText': p.get("linkText", ""),
                            "product_name": p.get("productName", ""),
                            'product_reference': p.get("productReference", ""),
                            "description": p.get("description", ""),
                            "selling_price": offer.get("Price", 0),
                            "list_price": offer.get("ListPrice", 0),
                            "categories": " > ".join(p.get("categories", [])),
                            "release_date": p.get("releaseDate", ""),
                            "image_url": images[0].get("imageUrl", "") if images else "",
                            "measurement_unit": items[0].get("measurementUnit", "") if items else "",
                            "unit_multiplier": items[0].get("unitMultiplier", 0) if items else 0,
                            "sku_id": items[0].get("itemId", "") if items else "",
                            "product_id": p.get("productId", ""),
                            "brand": p.get("brand", ""),
                            "ean": items[0].get("ean", "") if items else "",
                            "ref_id": ref_id_list[0].get("Value", "") if ref_id_list else "",
                            "available_quantity": offer.get("AvailableQuantity", 0),
                        })
                    print(f'  [{STORE_NAME}] "{termo}": {len(produtos)} (from={i}, total={len(todos)})')
                    if len(produtos) < 50:
                        break
                    i += 50
                    tentativa = 0
                    sleep(0.5)
                elif r.status_code == 429:
                    sleep(5)
                    tentativa += 1
                else:
                    tentativa += 1
                    sleep(2)
            except Exception as e:
                tentativa += 1
                sleep(2)
        sleep(0.3)

if not todos:
    print(f'[{STORE_NAME}] Nenhum produto coletado. Abortando.')
else:
    df = pd.DataFrame(todos)
    df.drop_duplicates(subset=['linkText'], keep='first', inplace=True)

    if 'description' in df.columns:
        df['description'] = df['description'].fillna('').str.replace(r'<[^>]+>', '', regex=True)
        df['description'] = df['description'].str.replace(r'\s+', ' ', regex=True).str.strip()

    hoje = datetime.datetime.now().strftime('%Y-%m-%d')
    mes = datetime.datetime.now().strftime('%Y%m')
    df2 = df[['linkText', 'product_name', 'selling_price', 'measurement_unit',
              'unit_multiplier', 'sku_id', 'product_id', 'brand', 'ean', 'ref_id']].copy()
    df2['data'] = hoje

    filename = f'zsul_{mes}.txt'
    if filename not in listdir():
        print(f'Criando arquivo {filename}')
        with open(filename, 'w+', encoding='utf-8') as f:
            f.write("data;cod;produto;preco;unidade;fator_unid;cod_id;cod_sku;marca;ean;ref_id\n")

    with open(filename, 'a+', encoding='utf-8') as f:
        for _, row in df2.iterrows():
            f.write(f"{row['data']};{row['linkText']};{row['product_name']};{row['selling_price']};{row['measurement_unit']};{row['unit_multiplier']};{row['sku_id']};{row['product_id']};{row['brand']};{row['ean']};{row['ref_id']}\n")

    print(f'[{STORE_NAME}] {len(df2)} produtos gravados em {filename}')
