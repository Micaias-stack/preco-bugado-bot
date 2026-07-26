import streamlit as st
import pandas as pd
import sqlite3
from scraper import buscar_produtos
from detector import detectar_bugs
from notificador import enviar_alerta

st.set_page_config(page_title="🔍 Caçador de Bugs", layout="wide")

st.title("🔍 Detector de Preços Bugados")

# --- BUSCA ---
termo = st.text_input("🔎 O que você procura?", "iphone 15")
if st.button("🕷️ Varrer Mercado Livre"):
    with st.spinner("Coletando dados..."):
        df = buscar_produtos(termo)
        
        # Salva no banco
        conn = sqlite3.connect("data/historico_precos.db")
        df.to_sql("produtos", conn, if_exists="append", index=False)
        conn.close()
        
        # Detecta bugs
        bugs = detectar_bugs(df)
        
        if not bugs.empty:
            st.success(f"🎯 {len(bugs)} bugs encontrados!")
            
            for _, bug in bugs.iterrows():
                with st.expander(f"💥 {bug['nome'][:50]}..."):
                    col1, col2 = st.columns(2)
                    col1.metric("Preço Atual", f"R$ {bug['preco']:.2f}")
                    col2.metric("Média Histórica", f"R$ {bug['preco_medio']:.2f}", 
                               delta=f"-{bug['desconto']}%", delta_color="inverse")
                    
                    st.markdown(f"🔗 [**Comprar Agora**]({bug['link']})")
                    
                    if st.button("📱 Enviar pro Telegram", key=bug['link']):
                        enviar_alerta(bug)
                        st.success("✅ Alerta enviado!")
        else:
            st.warning("😕 Nenhum bug detectado dessa vez")

# --- HISTÓRICO ---
st.divider()
st.subheader("📊 Histórico de Detecções")
conn = sqlite3.connect("data/historico_precos.db")
historico = pd.read_sql("SELECT * FROM produtos ORDER BY timestamp DESC LIMIT 50", conn)
conn.close()
st.dataframe(historico, use_container_width=True)
# Adicione no app.py
import time
import threading

def monitorar_continuamente():
    while True:
        df = buscar_produtos("notebook gamer")
        bugs = detectar_bugs(df)
        for _, bug in bugs.iterrows():
            enviar_alerta(bug)
        time.sleep(600)  # A cada 10 min

if st.sidebar.button("🤖 Ativar Modo Vigilante"):
    threading.Thread(target=monitorar_continuamente, daemon=True).start()
    st.sidebar.success("Bot rodando em background!")
