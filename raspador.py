import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

def buscar_mercado_livre(termo):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = f"https://lista.mercadolivre.com.br/{termo.replace(' ', '-')}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        produtos = []
        
        for item in soup.find_all('li', class_='ui-search-layout__item')[:10]:
            try:
                nome = item.find('h2', class_='ui-search-item__title').text.strip()
                preco_texto = item.find('span', class_='andes-money-amount__fraction').text
                preco = float(preco_texto.replace('.', '').replace(',', '.'))
                link = item.find('a', class_='ui-search-link')['href'].split('?')[0]
                
                produtos.append({
                    'nome': nome,
                    'preco': preco,
                    'link': link,
                    'plataforma': '🛒 Mercado Livre',
                    'timestamp': pd.Timestamp.now()
                })
            except:
                continue
        
        return produtos
    except Exception as e:
        print(f"Erro ML: {e}")
        return []

def buscar_shopee(termo):
    headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://shopee.com.br/'}
    url = f"https://shopee.com.br/api/v4/search/search_items?by=relevancy&keyword={termo.replace(' ', '%20')}&limit=10"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        dados = response.json()
        produtos = []
        
        for item in dados.get('items', []):
            try:
                info = item.get('item_basic', {})
                nome = info.get('name', '')
                preco = info.get('price', 0) / 100000
                item_id = info.get('itemid')
                shop_id = info.get('shopid')
                link = f"https://shopee.com.br/product/{shop_id}/{item_id}"
                
                if nome and preco > 0:
                    produtos.append({
                        'nome': nome,
                        'preco': preco,
                        'link': link,
                        'plataforma': '🛍️ Shopee',
                        'timestamp': pd.Timestamp.now()
                    })
            except:
                continue
        
        return produtos
    except Exception as e:
        print(f"Erro Shopee: {e}")
        return []

def buscar_em_todas_plataformas(termo):
    todos_produtos = []
    todos_produtos.extend(buscar_mercado_livre(termo))
    todos_produtos.extend(buscar_shopee(termo))
    return pd.DataFrame(todos_produtos)
