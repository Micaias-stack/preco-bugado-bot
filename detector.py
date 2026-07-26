import sqlite3
import pandas as pd

def calcular_preco_medio(produto_nome):
    """Consulta histórico do banco"""
    conn = sqlite3.connect("data/historico_precos.db")
    query = f"SELECT AVG(preco) as media FROM produtos WHERE nome LIKE '%{produto_nome[:20]}%'"
    resultado = pd.read_sql(query, conn)
    conn.close()
    return resultado["media"][0] if not resultado.empty else None

def eh_preco_bugado(preco_atual, preco_medio):
    """Regra: preço 40%+ abaixo da média = bug"""
    if preco_medio is None:
        return False
    desconto = ((preco_medio - preco_atual) / preco_medio) * 100
    return desconto >= 40

def detectar_bugs(df):
    """Filtra produtos com preços suspeitos"""
    bugs = []
    for _, row in df.iterrows():
        media = calcular_preco_medio(row["nome"])
        if eh_preco_bugado(row["preco"], media):
            bugs.append({
                **row,
                "preco_medio": media,
                "desconto": round(((media - row["preco"]) / media) * 100, 1)
            })
    return pd.DataFrame(bugs)
