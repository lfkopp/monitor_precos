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
    '_fbp': 'fb.2.1759422199763.20541570871641954.Bg',
    'VtexWorkspace': 'master%3A-',
    'vtex-search-session': '0bcbe2ddeee74e2aaa6d42ee68b3b22c',
    'vtex_session': 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjljZTY1YTc3LWNmNzMtNGM4Ni1hZGYzLWUyY2IzMWRhYjZiZiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50LmlkIjpbXSwiaWQiOiI5ZjQzNDdkOC1iOGM5LTQ0NzktYjE3My0zNjM0ZmZhZTU2ZDciLCJ2ZXJzaW9uIjoyLCJzdWIiOiJzZXNzaW9uIiwiYWNjb3VudCI6InNlc3Npb24iLCJleHAiOjE3NjE1NzgzODgsImlhdCI6MTc2MDg4NzE4OCwianRpIjoiYTA0ZThkNmMtNTMxNC00NmRkLWE1ODgtMGZjMDVjOGUwZmYxIiwiaXNzIjoic2Vzc2lvbi9kYXRhLXNpZ25lciJ9._sRhb8Ltk_RomIqvCkcf6W59G4GAeIfijK8GhwHgjo1JlV7G7gHzLZiaBKqqdPCS1FRMSZo1idwAIIvsjUpI4A',
    'vtex_segment': 'eyJjYW1wYWlnbnMiOm51bGwsImNoYW5uZWwiOiIxIiwicHJpY2VUYWJsZXMiOm51bGwsInJlZ2lvbklkIjpudWxsLCJ1dG1fY2FtcGFpZ24iOm51bGwsInV0bV9zb3VyY2UiOm51bGwsInV0bWlfY2FtcGFpZ24iOm51bGwsImN1cnJlbmN5Q29kZSI6IkJSTCIsImN1cnJlbmN5U3ltYm9sIjoiUiQiLCJjb3VudHJ5Q29kZSI6IkJSQSIsImN1bHR1cmVJbmZvIjoicHQtQlIiLCJjaGFubmVsUHJpdmFjeSI6InB1YmxpYyJ9',
    'sp-variant': '68f272e09c5530284c150a2e-variantNull',
    '_vss': '5DD86BF58350A03D169BC69D70A15BC2F3EF8AA6E6473F89FA1760AD02493CDC',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0',
    'Accept': '*/*',
    'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://www.zonasul.com.br/matinais/d',
    'content-type': 'application/json',
    'DNT': '1',
    'Sec-GPC': '1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Connection': 'keep-alive',
    # 'Cookie': 'vtex-search-anonymous=1a9c5fd8336049e7b5d07bcae56ca508; checkout.vtex.com=__ofid=537e4eca01f040448ed142e728d5ecd0; vtex_binding_address=zonasul.myvtex.com/; _fbp=fb.2.1759422199763.20541570871641954.Bg; VtexWorkspace=master%3A-; vtex-search-session=0bcbe2ddeee74e2aaa6d42ee68b3b22c; vtex_session=eyJhbGciOiJFUzI1NiIsImtpZCI6IjljZTY1YTc3LWNmNzMtNGM4Ni1hZGYzLWUyY2IzMWRhYjZiZiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50LmlkIjpbXSwiaWQiOiI5ZjQzNDdkOC1iOGM5LTQ0NzktYjE3My0zNjM0ZmZhZTU2ZDciLCJ2ZXJzaW9uIjoyLCJzdWIiOiJzZXNzaW9uIiwiYWNjb3VudCI6InNlc3Npb24iLCJleHAiOjE3NjE1NzgzODgsImlhdCI6MTc2MDg4NzE4OCwianRpIjoiYTA0ZThkNmMtNTMxNC00NmRkLWE1ODgtMGZjMDVjOGUwZmYxIiwiaXNzIjoic2Vzc2lvbi9kYXRhLXNpZ25lciJ9._sRhb8Ltk_RomIqvCkcf6W59G4GAeIfijK8GhwHgjo1JlV7G7gHzLZiaBKqqdPCS1FRMSZo1idwAIIvsjUpI4A; vtex_segment=eyJjYW1wYWlnbnMiOm51bGwsImNoYW5uZWwiOiIxIiwicHJpY2VUYWJsZXMiOm51bGwsInJlZ2lvbklkIjpudWxsLCJ1dG1fY2FtcGFpZ24iOm51bGwsInV0bV9zb3VyY2UiOm51bGwsInV0bWlfY2FtcGFpZ24iOm51bGwsImN1cnJlbmN5Q29kZSI6IkJSTCIsImN1cnJlbmN5U3ltYm9sIjoiUiQiLCJjb3VudHJ5Q29kZSI6IkJSQSIsImN1bHR1cmVJbmZvIjoicHQtQlIiLCJjaGFubmVsUHJpdmFjeSI6InB1YmxpYyJ9; sp-variant=68f272e09c5530284c150a2e-variantNull; _vss=5DD86BF58350A03D169BC69D70A15BC2F3EF8AA6E6473F89FA1760AD02493CDC',
}

params = {
    'workspace': 'master',
    'maxAge': 'short',
    'appsEtag': 'remove',
    'domain': 'store',
    'locale': 'pt-BR',
    'operationName': 'productSearchV3',
    'variables': '{}',
    'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"efcfea65b452e9aa01e820e140a5b4a331adfce70470d2290c08bc4912b45212","sender":"vtex.store-resources@0.x","provider":"vtex.search-graphql@0.x"},"variables":"eyJoaWRlVW5hdmFpbGFibGVJdGVtcyI6dHJ1ZSwic2t1c0ZpbHRlciI6IkFMTCIsInNpbXVsYXRpb25CZWhhdmlvciI6ImRlZmF1bHQiLCJpbnN0YWxsbWVudENyaXRlcmlhIjoiTUFYX1dJVEhPVVRfSU5URVJFU1QiLCJwcm9kdWN0T3JpZ2luVnRleCI6dHJ1ZSwibWFwIjoiYyIsInF1ZXJ5IjoibWF0aW5haXMiLCJvcmRlckJ5IjoiT3JkZXJCeVNjb3JlREVTQyIsImZyb20iOjAsInRvIjo0Nywic2VsZWN0ZWRGYWNldHMiOlt7ImtleSI6ImMiLCJ2YWx1ZSI6Im1hdGluYWlzIn1dLCJmYWNldHNCZWhhdmlvciI6IlN0YXRpYyIsImNhdGVnb3J5VHJlZUJlaGF2aW9yIjoiZGVmYXVsdCIsIndpdGhGYWNldHMiOmZhbHNlLCJ2YXJpYW50IjoiNjhmMjcyZTA5YzU1MzAyODRjMTUwYTJlLXZhcmlhbnROdWxsIiwiYWR2ZXJ0aXNlbWVudE9wdGlvbnMiOnsic2hvd1Nwb25zb3JlZCI6dHJ1ZSwic3BvbnNvcmVkQ291bnQiOjMsImFkdmVydGlzZW1lbnRQbGFjZW1lbnQiOiJ0b3Bfc2VhcmNoIiwicmVwZWF0U3BvbnNvcmVkUHJvZHVjdHMiOnRydWV9fQ=="}',
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

encoded_vars = "eyJoaWRlVW5hdmFpbGFibGVJdGVtcyI6dHJ1ZSwic2t1c0ZpbHRlciI6IkFMTF9BVkFJTEFCTEUiLCJzaW11bGF0aW9uQmVoYXZpb3IiOiJkZWZhdWx0IiwiaW5zdGFsbG1lbnRDcml0ZXJpYSI6Ik1BWF9XSVRIT1VUX0lOVEVSRVNUIiwicHJvZHVjdE9yaWdpblZ0ZXgiOnRydWUsIm1hcCI6InByb2R1Y3RDbHVzdGVySWRzIiwicXVlcnkiOiIxNjQiLCJvcmRlckJ5IjoiT3JkZXJCeVRvcFNhbGVERVNDIiwiZnJvbSI6OTYsInRvIjoxNDMsInNlbGVjdGVkRmFjZXRzIjpbeyJrZXkiOiJwcm9kdWN0Q2x1c3RlcklkcyIsInZhbHVlIjoiMTY0In1dLCJvcGVyYXRvciI6ImFuZCIsImZ1enp5IjoiMCIsInNlYXJjaFN0YXRlIjpudWxsLCJmYWNldHNCZWhhdmlvciI6IlN0YXRpYyIsIndpdGhGYWNldHMiOmZhbHNlLCJhZHZlcnRpc2VtZW50T3B0aW9ucyI6eyJzaG93U3BvbnNvcmVkIjp0cnVlLCJzcG9uc29yZWRDb3VudCI6MywiYWR2ZXJ0aXNlbWVudFBsYWNlbWVudCI6InRvcF9zZWFyY2giLCJyZXBlYXRTcG9uc29yZWRQcm9kdWN0cyI6dHJ1ZX19"
decoded_vars = base64.b64decode(encoded_vars)
print(json.loads(decoded_vars))
todos = []


#%%
for j in [49, 89]:
    for cluster in ['2364','1131','7350', '164', '1604','7350','868','238']:
        erro = 0
        i=0
        total = 1
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
                    'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"00ce3d1c420a53a8424cc20b7b6af2102022062f60c0189357526a57c21443e6","sender":"vtex.store-resources@0.x","provider":"vtex.search-graphql@0.x"},"variables":"'+reencoded+'"}',
}
                url = 'https://www.zonasul.com.br/_v/segment/graphql/v1'
                response = requests.get(url, params=params, cookies=cookies, headers=headers)
                #url = f'https://www.zonasul.com.br/_v/segment/graphql/v1?extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22c351315ecde7f473587b710ac8b97f147ac0ac0cd3060c27c695843a72fd3903%22%2C%22sender%22%3A%22vtex.store-resources%400.x%22%2C%22provider%22%3A%22vtex.search-graphql%400.x%22%7D%2C%22variables%22%3A%22{reencoded}%22%7D'
                #response = requests.get(url, cookies=cookies, headers=headers)
                produtos = response.json().get('data', {}).get('productSearch', {}).get('products', [])
                total = response.json().get('data', {}).get('productSearch', {}).get('recordsFiltered')
                #print('i',i,'tam',len(produtos),'total',total,'todos',len(todos),[x.get('productName') for x in produtos])  
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
df2 = df[['linkText','product_name','selling_price','measurement_unit','unit_multiplier','sku_id','product_id','brand']]
df2['data'] = hoje
# %%
with open('zsul.txt', 'a+', encoding='utf-8') as f:
    for index, row in df2.iterrows():
        f.write(f"{row['data']};{row['linkText']};{row['product_name']};{row['selling_price']};{row['measurement_unit']};{row['unit_multiplier']};{row['sku_id']};{row['product_id']};{row['brand']}\n")
# %%

