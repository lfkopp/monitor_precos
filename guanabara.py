#%%
import requests
from bs4 import BeautifulSoup
from time import sleep
import datetime
hoje = datetime.datetime.now().strftime('%Y-%m-%d')
#%%
url_principal = 'https://www.supermercadosguanabara.com.br/produtos'
pagina_principal = requests.get(url_principal)
soup = BeautifulSoup(pagina_principal.content, 'lxml')
secoes = [(x['href'], x.text.strip()) for x in soup.find('div', {'class':'products-menu menu-bar'}).find_all('a')]
print('numero de secoes: ',len(secoes))
#%%
with open('guanabara.txt', 'a+', encoding='utf-8') as f:
    for link,secao in secoes:
        pagina = requests.get('https://www.supermercadosguanabara.com.br'+link)
        soup = BeautifulSoup(pagina.content, 'lxml')
        itens = soup.find_all('div', {'class':'col item'})
        print(secao,len(itens))
        for item in itens:
            produto = item.find('div',{'class':'name'}).text
            preco = item.find('span',{'class':'number'}).text
            f.write(f'{hoje};{link};{secao};{produto};{preco}\n')
        sleep(2.3)
# %%
