#%%
import datetime
import requests
from time import sleep
import pandas as pd



#%%
def simplify_product_data(products):
    simplified = []
    for product in products:
        simplified_product = {
            'linkText':  product["linkText"],
            "product_name": product["productName"],
            'product_reference': product["productReference"],
            "description": product.get("description", ""),
            "selling_price": product["priceRange"]["sellingPrice"]["lowPrice"],
            "list_price": product["priceRange"]["listPrice"]["lowPrice"],
            "categories_id": product["categoryId"],
            "release_date": product["releaseDate"],
            "image_url": product["items"][0]["images"][0]["imageUrl"] if product["items"] and product["items"][0]["images"] else None,
            "measurement_unit": product["items"][0]["measurementUnit"] if product["items"] else None,
            "unit_multiplier": product["items"][0]["unitMultiplier"] if product["items"] else None,
            "sku_id": product["items"][0]["itemId"] if product["items"] else None,
            "product_id": product["productId"],
            "brand": product["brand"],
            "brand_id": product["brandId"],
            "available_quantity": product["items"][0]["sellers"][0]["commertialOffer"]["AvailableQuantity"] if product["items"] and product["items"][0]["sellers"] else None
        }
        simplified.append(simplified_product)
    return simplified


cookies = {
    'vtex-search-anonymous': '1a9c5fd8336049e7b5d07bcae56ca508',
    'checkout.vtex.com': '__ofid=537e4eca01f040448ed142e728d5ecd0',
    'vtex_binding_address': 'zonasul.myvtex.com/',
    'VtexWorkspace': 'master%3A-',
    '_fbp': 'fb.2.1769266254008.126342954208711991.AQYBAQIA',
    'vtex-search-session': 'd4829ef037cf46d5a974310c4e03547c',
    'vtex_session': 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjFjY2M0ZDM2LTc5MDgtNDAwYy1iYmY4LTM5ZWM2MzM1MTI0YyIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50LmlkIjpbXSwiaWQiOiJjMjVjYzAzOC0zYjRjLTQ3ZDQtODVhNS1mOTk0MzMzYjAwMzciLCJ2ZXJzaW9uIjoyLCJzdWIiOiJzZXNzaW9uIiwiYWNjb3VudCI6InNlc3Npb24iLCJleHAiOjE3Njk5NTc0NTQsImlhdCI6MTc2OTI2NjI1NCwianRpIjoiOTM5YTRhMjgtYWY1Ni00NjA4LTk3NjUtZjM3Yzg3MjA4YjAwIiwiaXNzIjoic2Vzc2lvbi9kYXRhLXNpZ25lciJ9.HXqbMX3l21tPdAdEg1GHik_4M1KgwW-PegOvNYXBbLOEc7Y0UhenGHrzb41W22Jvopa8zPVvx--pJ-9gUIoPfA',
    'vtex_segment': 'eyJjYW1wYWlnbnMiOm51bGwsImNoYW5uZWwiOiIxIiwicHJpY2VUYWJsZXMiOm51bGwsInJlZ2lvbklkIjpudWxsLCJ1dG1fY2FtcGFpZ24iOm51bGwsInV0bV9zb3VyY2UiOm51bGwsInV0bWlfY2FtcGFpZ24iOm51bGwsImN1cnJlbmN5Q29kZSI6IkJSTCIsImN1cnJlbmN5U3ltYm9sIjoiUiQiLCJjb3VudHJ5Q29kZSI6IkJSQSIsImN1bHR1cmVJbmZvIjoicHQtQlIiLCJjaGFubmVsUHJpdmFjeSI6InB1YmxpYyJ9',
    'sp-variant': 'null-null',
    'CheckoutOrderFormOwnership': 'bArPA1TGRk2zt8bB4dKPV/eQmeS4co2KJO8WRBTAF9lep2RH57EZm+Vp2JhyBkj4',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0',
    'Accept': '*/*',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    'Referer': 'https://www.zonasul.com.br/hortifruti/d',
    'content-type': 'application/json',
    'DNT': '1',
    'Sec-GPC': '1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Connection': 'keep-alive',
}

params = {
    'workspace': 'master',
    'maxAge': 'short',
    'appsEtag': 'remove',
    'domain': 'store',
    'locale': 'pt-BR',
    'operationName': 'productSearchV3',
    'variables': '{}',
    'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"31d3fa494df1fc41efef6d16dd96a96e6911b8aed7a037868699a1f3f4d365de","sender":"vtex.store-resources@0.x","provider":"vtex.search-graphql@0.x"},"variables":"eyJoaWRlVW5hdmFpbGFibGVJdGVtcyI6dHJ1ZSwic2t1c0ZpbHRlciI6IkFMTCIsInNpbXVsYXRpb25CZWhhdmlvciI6ImRlZmF1bHQiLCJpbnN0YWxsbWVudENyaXRlcmlhIjoiTUFYX1dJVEhPVVRfSU5URVJFU1QiLCJwcm9kdWN0T3JpZ2luVnRleCI6dHJ1ZSwibWFwIjoiYyIsInF1ZXJ5IjoiaG9ydGlmcnV0aSIsIm9yZGVyQnkiOiJPcmRlckJ5U2NvcmVERVNDIiwiZnJvbSI6MCwidG8iOjQ3LCJzZWxlY3RlZEZhY2V0cyI6W3sia2V5IjoiYyIsInZhbHVlIjoiaG9ydGlmcnV0aSJ9XSwiZmFjZXRzQmVoYXZpb3IiOiJTdGF0aWMiLCJjYXRlZ29yeVRyZWVCZWhhdmlvciI6ImRlZmF1bHQiLCJ3aXRoRmFjZXRzIjpmYWxzZSwidmFyaWFudCI6Im51bGwtbnVsbCJ9"}',
}



url = 'https://www.zonasul.com.br/_v/segment/graphql/v1'
response = requests.get(url, params=params, cookies=cookies, headers=headers)
response.json()
#%%
produtos = response.json().get('data', {}).get('productSearch', {}).get('products', [])
print(len(produtos))
print([x.get('productName') for x in produtos])  
total = response.json().get('data', {}).get('productSearch', {}).get('recordsFiltered')
print('Total de produtos:', total)
# %%
import base64
import json

encoded_vars = "eyJoaWRlVW5hdmFpbGFibGVJdGVtcyI6dHJ1ZSwic2t1c0ZpbHRlciI6IkFMTF9BVkFJTEFCTEUiLCJzaW11bGF0aW9uQmVoYXZpb3IiOiJkZWZhdWx0IiwiaW5zdGFsbG1lbnRDcml0ZXJpYSI6Ik1BWF9XSVRIT1VUX0lOVEVSRVNUIiwicHJvZHVjdE9yaWdpblZ0ZXgiOnRydWUsIm1hcCI6InByb2R1Y3RDbHVzdGVySWRzIiwicXVlcnkiOiIxNjA0Iiwib3JkZXJCeSI6Ik9yZGVyQnlTY29yZURFU0MiLCJmcm9tIjowLCJ0byI6NDcsInNlbGVjdGVkRmFjZXRzIjpbeyJrZXkiOiJwcm9kdWN0Q2x1c3RlcklkcyIsInZhbHVlIjoiMTYwNCJ9XSwiZmFjZXRzQmVoYXZpb3IiOiJTdGF0aWMiLCJ3aXRoRmFjZXRzIjpmYWxzZSwidmFyaWFudCI6Im51bGwtbnVsbCJ9"
decoded_vars = base64.b64decode(encoded_vars)
print(json.loads(decoded_vars))
todos = []


#%%
for j in [49, 89]:
    for cluster in ['2364','1131','7350', '164', '1604','7350','868','238']:
        erro = 0
        i=0
        total = 100
        while (i < total):
            decoded_vars2 = json.loads(decoded_vars)
            decoded_vars2['selectedFacets'] = [{'key': 'productClusterIds', 'value': cluster}]
            decoded_vars2['from'] = i
            decoded_vars2['to'] =  i+j
            try:
                reencoded = base64.b64encode(json.dumps(decoded_vars2).encode('utf-8')).decode('utf-8'  )
                params = {
                    'workspace': 'master',
                    'maxAge': 'short',
                    'appsEtag': 'remove',
                    'domain': 'store',
                    'locale': 'pt-BR',
                    'operationName': 'productSearchV3',
                    'variables': '{}',
                    'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"31d3fa494df1fc41efef6d16dd96a96e6911b8aed7a037868699a1f3f4d365de","sender":"vtex.store-resources@0.x","provider":"vtex.search-graphql@0.x"},"variables":"eyJoaWRlVW5hdmFpbGFibGVJdGVtcyI6dHJ1ZSwic2t1c0ZpbHRlciI6IkFMTF9BVkFJTEFCTEUiLCJzaW11bGF0aW9uQmVoYXZpb3IiOiJkZWZhdWx0IiwiaW5zdGFsbG1lbnRDcml0ZXJpYSI6Ik1BWF9XSVRIT1VUX0lOVEVSRVNUIiwicHJvZHVjdE9yaWdpblZ0ZXgiOnRydWUsIm1hcCI6InByb2R1Y3RDbHVzdGVySWRzIiwicXVlcnkiOiIxNjQiLCJvcmRlckJ5IjoiT3JkZXJCeVRvcFNhbGVERVNDIiwiZnJvbSI6NDgsInRvIjo5NSwic2VsZWN0ZWRGYWNldHMiOlt7ImtleSI6InByb2R1Y3RDbHVzdGVySWRzIiwidmFsdWUiOiIxNjQifV0sIm9wZXJhdG9yIjoiYW5kIiwiZnV6enkiOiIwIiwic2VhcmNoU3RhdGUiOm51bGwsImZhY2V0c0JlaGF2aW9yIjoiU3RhdGljIiwid2l0aEZhY2V0cyI6ZmFsc2UsInZhcmlhbnQiOiJudWxsLW51bGwifQ=="}',
                }
                url = 'https://www.zonasul.com.br/_v/segment/graphql/v1'
                response = requests.get(url, params=params, cookies=cookies, headers=headers)
                produtos = response.json().get('data', {}).get('productSearch', {}).get('products', [])
                total = response.json().get('data', {}).get('productSearch', {}).get('recordsFiltered')
                print('i',i,'tam',len(produtos),'total',total,'todos',len(todos),[x.get('productName') for x in produtos])  
                todos += simplify_product_data(produtos)
                i+= 50
                erro = 0
                sleep(.2)
            except Exception as e:
                print('Erro na iteração', i, e,'i',i,'tam',len(produtos),'total',total,'todos',len(todos))
                erro += 1
                if erro > 2:
                    print('Muitos erros consecutivos, parando a execução.')
                    break
                sleep(1)
    
    df = pd.DataFrame(todos)
    df.drop_duplicates(subset=['linkText'], keep='first', inplace=True)
    print(cluster,df.shape)
# %%

df = pd.DataFrame(todos)
df.drop_duplicates(subset=['linkText'], keep='first', inplace=True)
df

#%%
df.shape
# %%
df['description'] = df['description'].str.replace(r'<[^>]+>', '', regex=True)
df['description'] = df['description'].str.replace(r'\s+', ' ', regex=True).str.strip()
df['description'] = df['description'].str.replace(r'\n', ' ', regex=True).str.strip()
df['description'] = df['description'].str.replace(r'\r', ' ', regex=True).str.strip()
df['description'] = df['description'].str.replace(r'\t', ' ', regex=True).str.strip()
df['description'] = df['description'].str.replace(r'\xa0', ' ', regex=True).str.strip()

# %%
df.to_excel('zonasul.xlsx', index=False,engine='openpyxl')

# %%

hoje = datetime.datetime.now().strftime('%Y-%m-%d')
mes = datetime.datetime.now().strftime('%Y%m')
df2 = df[['linkText','product_name','selling_price','measurement_unit','unit_multiplier','sku_id','product_id','brand']]
df2['data'] = hoje
# %%

from os import listdir


filename = f'zsul_{mes}.txt'

if filename not in listdir():
    print('Criando arquivo', filename)
    with open(filename, 'w+', encoding='utf-8') as f:
        f.write("data;cod;produto;preco;unidade;faot_unid;cod_id;cod_sku;marca\n")

with open(filename, 'a+', encoding='utf-8') as f:
    for index, row in df2.iterrows():
        f.write(f"{row['data']};{row['linkText']};{row['product_name']};{row['selling_price']};{row['measurement_unit']};{row['unit_multiplier']};{row['sku_id']};{row['product_id']};{row['brand']}\n")
# %%


# %%
