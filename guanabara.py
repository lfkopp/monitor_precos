import requests
from bs4 import BeautifulSoup
url_principal = 'https://www.supermercadosguanabara.com.br/produtos'
pagina_principal = requests.get(url_principal)
soup = BeautifulSoup(pagina_principal.content)
for link in soup.find_all('a'):
    if '/produtos/' in link['href']:
        pagina = requests.get('https://www.supermercadosguanabara.com.br/'+link['href'])
        soup = BeautifulSoup(pagina.content)
        for item in soup.find_all('div', {'class':'col item'}):
            print(item.find('div',{'class':'name'}).text,';',item.find('span',{'class':'number'}).text )
