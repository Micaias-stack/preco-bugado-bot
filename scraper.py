from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

def buscar_produtos(termo):
    """Varre Mercado Livre em busca do termo"""
    url = f"https://lista.mercadolivre.com.br/{termo}"
    
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)
    
    produtos = []
    items = driver.find_elements(By.CLASS_NAME, "ui-search-result__content")
    
    for item in items[:20]:  # Limita a 20 produtos
        try:
            nome = item.find_element(By.CLASS_NAME, "ui-search-item__title").text
            preco_texto = item.find_element(By.CLASS_NAME, "andes-money-amount__fraction").text
            link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            preco = float(preco_texto.replace(".", "").replace(",", "."))
            
            produtos.append({
                "nome": nome,
                "preco": preco,
                "link": link,
                "timestamp": pd.Timestamp.now()
            })
        except:
            continue
    
    driver.quit()
    return pd.DataFrame(produtos)
