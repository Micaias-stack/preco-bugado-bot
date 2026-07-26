import streamlit as st
import pandas as pd
import sqlite3
import time
import threading
from datetime import datetime
from raspador import buscar_em_todas_plataformas
from detector import detectar_bugs, salvar_historico, inicializar_bd
from notificador import enviar_alerta

# Configuração da página
st.set_page_config(
    page_title="🔥 Caçador de Preços",
    page_icon="🔥",
    layout="wide"
)

# Inicializa banco
db_path = inicializar_bd()

# Estado do bot automático
if 'bot_ativo' not in st.session_state:
    st.session_state.bot_ativo = False
if 'ultima_busca' not in st.session_state:
    st.session_state.ultima_busca = None

def executar_busca_automatica(termo, intervalo_minutos, desconto_minimo):
    """Função que roda em loop no background"""
    while st.session_state.bot_ativo:
        try:
            st.session_state.ultima_busca = datetime.now().strftime('%H:%M:%S')
            
            # Busca produtos
            df = buscar_em_todas_plataformas(termo)
            
            if not df.empty:
                salvar_historico(df, db_path)
                bugs = detectar_bugs(df, db_path, limite=desconto_minimo)
                
                # Envia alertas
                for _, bug in bugs.iterrows():
                    enviar_alerta(bug)
                    time.sleep(2)
            
            # Aguarda próximo ciclo
            time.sleep(intervalo_minutos * 60)
        
        except Exception as e:
            print(f"Erro no bot: {e}")
            time.sleep(60)

# Interface
st.title("🔥 Caçador de Preços Bugados")
st.caption("Mercado Livre • Shopee • Automático 24/7")

# Tabs
tab1, tab2, tab3 = st.tabs(["🤖 Bot Automático", "🔍 Busca Manual", "📊 Histórico"])

# TAB 1: BOT AUTOMÁTICO
with tab1:
    st.subheader("🤖 Monitoramento Automático")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        termo_auto = st.text_input("Produto a monitorar", "iphone 15", key="termo_auto")
    
    with col2:
        intervalo = st.number_input("Intervalo (minutos)", 10, 120, 30)
    
    with col3:
        desconto_auto = st.number_input("Desconto mín (%)", 20, 90, 40, key="desc_auto")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("🚀 Iniciar Bot", type="primary", disabled=st.session_state.bot_ativo):
            st.session_state.bot_ativo = True
            threading.Thread(
                target=executar_busca_automatica,
                args=(termo_auto, intervalo, desconto_auto),
                daemon=True
            ).start()
            st.success("✅ Bot iniciado!")
            st.rerun()
    
    with col_btn2:
        if st.button("🛑 Parar Bot", disabled=not st.session_state.bot_ativo):
            st.session_state.bot_ativo = False
            st.warning("⏸️ Bot parado")
            st.rerun()
    
    # Status
    if st.session_state.bot_ativo:
        st.success(f"🟢 **Bot ATIVO** | Última busca: {st.session_state.ultima_busca or 'Aguardando...'}")
        st.info(f"🔄 Próxima busca em ~{intervalo} minutos")
    else:
        st.error("🔴 **Bot INATIVO**")

# TAB 2: BUSCA MANUAL
with tab2:
    st.subheader("🔍 Busca Manual")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        termo_manual = st.text_input("O que procura?", "notebook gamer")
    
    with col2:
        desconto_manual = st.number_input("Desconto mín (%)", 20, 90, 40)
    
    if st.button("🕷️ Buscar Agora", type="primary"):
        with st.spinner("Varrendo..."):
            df = buscar_em_todas_plataformas(termo_manual)
            
            if df.empty:
                st.warning("Nenhum produto encontrado")
            else:
                salvar_historico(df, db_path)
                bugs = detectar_bugs(df, db_path, limite=desconto_manual)
                
                if not bugs.empty:
                    st.success(f"🎯 **{len(bugs)} bugs encontrados!**")
                    
                    for idx, bug in bugs.iterrows():
                        with st.expander(f"💥 {bug['nome'][:60]}..."):
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Preço", f"R$ {bug['preco']:.2f}")
                            col2.metric("Média", f"R$ {bug['preco_medio']:.2f}")
                            col3.metric("Desconto", f"{bug['desconto']}%")
                            
                            st.markdown(f"**{bug['plataforma']}**")
                            st.link_button("🛒 Comprar", bug['link'])
                            
                            if st.button("📱 Enviar Telegram", key=f"btn_{idx}"):
                                resultado = enviar_alerta(bug)
                                if resultado and resultado.get("ok"):
                                    st.success("✅ Enviado!")
                else:
                    st.info("Nenhum bug detectado")

# TAB 3: HISTÓRICO
with tab3:
    st.subheader("📊 Produtos Monitorados")
    
    try:
        conn = sqlite3.connect(db_path)
        historico = pd.read_sql("SELECT * FROM produtos ORDER BY timestamp DESC LIMIT 100", conn)
        conn.close()
        
        if not historico.empty:
            st.dataframe(historico, use_container_width=True)
        else:
            st.info("Nenhum produto no histórico")
    except:
        st.info("Histórico vazio")
