import requests
from bs4 import BeautifulSoup
import pandas as pd
import random

def buscar_produtos(termo):
    """Coleta produtos do Mercado Livre via requests"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    url = f"https://lista.mercadolivre.com.br/{termo.replace(' ', '-')}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        produtos = []
        items = soup.find_all('li', class_='ui-search-layout__item')[:15]
        
        for item in items:
            try:
                nome_elem = item.find('h2', class_='ui-search-item__title')
                preco_elem = item.find('span', class_='andes-money-amount__fraction')
                link_elem = item.find('a', class_='ui-search-link')
                
                if nome_elem and preco_elem and link_elem:
                    nome = nome_elem.text.strip()
                    preco_texto = preco_elem.text.replace('.', '').replace(',', '.')
                    preco = float(preco_texto)
                    link = link_elem['href'].split('?')[0]  # Remove parâmetros
                    
                    produtos.append({
                        'nome': nome,
                        'preco': preco,
                        'link': link,
                        'timestamp': pd.Timestamp.now()
                    })
            except Exception as e:
                continue
        
        return pd.DataFrame(produtos)
    
    except Exception as e:
        print(f"Erro ao buscar: {e}")
        return pd.DataFrame()
