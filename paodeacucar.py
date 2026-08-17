import datetime
import requests
from time import sleep
import pandas as pd
from os import listdir
import json


STORE_NAME = "PaoDeAcucar"
API_URL = "https://api.vendas.gpa.digital/pa/search/category-page"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:153.0) Gecko/20100101 Firefox/153.0',
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
    'Origin': 'https://www.paodeacucar.com',
    'Referer': 'https://www.paodeacucar.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
}

STORE_ID_RJ = 461

categorias = [
    'alimentos',
    'limpeza',
    'higiene',
    'bebidas',
    'bazar',
]

todos = []
session = requests.Session()
session.headers.update(headers)

print(f'[{STORE_NAME}] Iniciando coleta (loja RJ storeId={STORE_ID_RJ})...')

for cat in categorias:
    page = 1
    total_paginas = 1
    while page <= total_paginas:
        payload = {
            'partner': 'linx',
            'page': page,
            'resultsPerPage': 21,
            'multiCategory': cat,
            'sortBy': 'relevance',
            'department': 'ecom',
            'storeId': STORE_ID_RJ,
            'customerPlus': True,
        }
        try:
            response = session.post(API_URL, json=payload, timeout=15)
            if response.status_code == 200:
                data = response.json()
                total_paginas = data.get('totalPages', 1)
                produtos = data.get('products', [])
                if not produtos:
                    print(f'  [{STORE_NAME}] {cat} p{page}: 0 produtos')
                    break
                for p in produtos:
                    todos.append({
                        'sku_id': str(p.get('sku', '')),
                        'product_name': p.get('name', ''),
                        'selling_price': p.get('price', 0),
                        'list_price': p.get('price', 0),
                        'brand': p.get('brand', ''),
                        'available': p.get('stock', False),
                        'category': cat,
                        'seller': p.get('sellerName', ''),
                        'url': p.get('urlDetails', ''),
                    })
                print(f'  [{STORE_NAME}] {cat} p{page}/{total_paginas}: +{len(produtos)} (total={len(todos)})')
                page += 1
                sleep(0.3)
            else:
                print(f'  [{STORE_NAME}] {cat} p{page}: Erro {response.status_code}')
                break
        except Exception as e:
            print(f'  [{STORE_NAME}] {cat} p{page}: Excecao {e}')
            break

print(f'\n[{STORE_NAME}] Total coletado: {len(todos)} registros brutos')

df = pd.DataFrame(todos)
if df.empty:
    print(f'[{STORE_NAME}] Nenhum produto coletado.')
else:
    df.drop_duplicates(subset=['sku_id'], keep='first', inplace=True)

    hoje = datetime.datetime.now().strftime('%Y-%m-%d')
    mes = datetime.datetime.now().strftime('%Y%m')

    filename = f'paodeacucar_{mes}.txt'

    if filename not in listdir():
        print(f'Criando arquivo {filename}')
        with open(filename, 'w+', encoding='utf-8') as f:
            f.write("data;cod;produto;preco;preco_lista;marca;disponivel;categoria;vendedor;url\n")

    with open(filename, 'a+', encoding='utf-8') as f:
        for _, row in df.iterrows():
            f.write(f"{hoje};{row['sku_id']};{row['product_name']};{row['selling_price']};{row['list_price']};{row['brand']};{row['available']};{row['category']};{row['seller']};{row['url']}\n")

    print(f'[{STORE_NAME}] {len(df)} produtos gravados em {filename}')
