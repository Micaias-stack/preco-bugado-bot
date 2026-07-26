import sqlite3
import pandas as pd
import os

def inicializar_bd():
    db_path = "/tmp/historico_precos.db"
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            nome TEXT,
            preco REAL,
            link TEXT,
            plataforma TEXT,
            timestamp DATETIME
        )
    """)
    conn.commit()
    conn.close()
    return db_path

def calcular_preco_medio(produto_nome, db_path="/tmp/historico_precos.db"):
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    query = """
        SELECT AVG(preco) as media 
        FROM produtos 
        WHERE nome LIKE ?
    """
    resultado = pd.read_sql(query, conn, params=(f'%{produto_nome[:30]}%',))
    conn.close()
    
    if resultado.empty or pd.isna(resultado["media"][0]):
        return None
    return resultado["media"][0]

def eh_preco_bugado(preco_atual, preco_medio, limite=40):
    if preco_medio is None or preco_medio == 0:
        return False
    desconto = ((preco_medio - preco_atual) / preco_medio) * 100
    return desconto >= limite

def detectar_bugs(dataframe, db_path="/tmp/historico_precos.db", limite=40):
    bugs = []
    for _, linha in dataframe.iterrows():
        media = calcular_preco_medio(linha["nome"], db_path)
        if eh_preco_bugado(linha["preco"], media, limite):
            bugs.append({
                **linha,
                "preco_medio": media,
                "desconto": round(((media - linha["preco"]) / media) * 100, 1)
            })
    return pd.DataFrame(bugs)

def salvar_historico(dataframe, db_path="/tmp/historico_precos.db"):
    conn = sqlite3.connect(db_path)
    dataframe.to_sql("produtos", conn, if_exists="append", index=False)
    conn.close()
