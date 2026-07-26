import streamlit as st
import pandas as pd
import sqlite3
import time
import threading
from datetime import datetime
from raspador import buscar_em_todas_plataformas
from detector import detectar_bugs, salvar_historico, inicializar_bd
from notificador import enviar_alerta

st.set_page_config(
    page_title="🔥 Caçador de Preços",
    page_icon="🔥",
    layout="wide"
)

db_path = inicializar_bd()

if 'bot_ativo' not in st.session_state:
    st.session_state.bot_ativo = False
if 'ultima_busca' not in st.session_state:
    st.session_state.ultima_busca = None

def executar_busca_automatica(termo, intervalo, desconto_minimo):
    while st.session_state.bot_ativo:
        try:
            st.session_state.ultima_busca = datetime.now().strftime('%d/%m %H:%M')
            df = buscar_em_todas_plataformas(termo)
            
            if not df.empty:
                salvar_historico(df, db_path)
                bugs = detectar_bugs(df, db_path, limite=desconto_minimo)
                
                for _, bug in bugs.iterrows():
                    enviar_alerta(bug)
                    time.sleep(2)
            
            time.sleep(intervalo * 60)
        except:
            time.sleep(60)

st.title("🔥 Caçador de Preços Bugados")
st.caption("Mercado Livre • Shopee • Monitoramento 24/7")

tab1, tab2, tab3 = st.tabs(["🤖 Bot Automático", "🔍 Busca Manual", "📊 Histórico"])

with tab1:
    st.subheader("⚙️ Configurar Bot Automático")
    
    col1, col2 = st.columns(2)
    with col1:
        termo_auto = st.text_input("🔎 Produto para monitorar", "iphone 15", key="termo_auto")
        intervalo = st.number_input("⏰ Buscar a cada (minutos)", 15, 180, 30)
    with col2:
        desconto_auto = st.number_input("📉 Desconto mínimo (%)", 20, 90, 40, key="desc_auto")
        st.write("")
        st.write("")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if not st.session_state.bot_ativo:
            if st.button("🚀 INICIAR BOT", type="primary", use_container_width=True):
                st.session_state.bot_ativo = True
                thread = threading.Thread(
                    target=executar_busca_automatica,
                    args=(termo_auto, intervalo, desconto_auto),
                    daemon=True
                )
                thread.start()
                st.success("✅ Bot iniciado!")
                st.rerun()
    
    with col_btn2:
        if st.session_state.bot_ativo:
            if st.button("🛑 PARAR BOT", type="secondary", use_container_width=True):
                st.session_state.bot_ativo = False
                st.warning("⏸️ Bot pausado")
                st.rerun()
    
    if st.session_state.bot_ativo:
        st.success(f"✅ Bot rodando • Última busca: {st.session_state.ultima_busca or 'Aguardando...'}")
        st.info(f"🔄 Próxima busca em {intervalo} minutos • Buscando: **{termo_auto}**")
    else:
        st.info("⏸️ Bot pausado • Clique em INICIAR para ativar")

with tab2:
    st.subheader("🔍 Busca Manual")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        termo_manual = st.text_input("🔎 Buscar produto", "notebook gamer", key="termo_manual")
    with col2:
        desconto_manual = st.number_input("📉 Desconto mínimo", 20, 90, 40, key="desc_manual")
    with col3:
        st.write("")
        buscar_btn = st.button("🕷️ BUSCAR AGORA", type="primary", use_container_width=True)
    
    if buscar_btn:
        with st.spinner("🔍 Vasculhando todas as plataformas..."):
            df = buscar_em_todas_plataformas(termo_manual)
            
            if df.empty:
                st.error("❌ Nenhum produto encontrado")
            else:
                st.success(f"✅ {len(df)} produtos encontrados")
                salvar_historico(df, db_path)
                
                bugs = detectar_bugs(df, db_path, limite=desconto_manual)
                
                if bugs.empty:
                    st.warning("⚠️ Nenhum bug detectado nesta busca")
                    with st.expander("📦 Ver todos os produtos"):
                        st.dataframe(df, use_container_width=True)
                else:
                    st.error(f"🚨 {len(bugs)} PREÇOS BUGADOS ENCONTRADOS!")
                    
                    for _, bug in bugs.iterrows():
                        with st.container():
                            col_info, col_btn = st.columns([4, 1])
                            
                            with col_info:
                                st.markdown(f"### {bug['plataforma']} {bug['nome'][:60]}...")
                                col_preco1, col_preco2, col_desc = st.columns(3)
                                col_preco1.metric("💰 Preço Atual", f"R$ {bug['preco']:.2f}")
                                col_preco2.metric("📊 Preço Médio", f"R$ {bug['preco_medio']:.2f}")
                                col_desc.metric("📉 Desconto", f"{bug['desconto']}%", delta=f"-{bug['desconto']}%")
                            
                            with col_btn:
                                st.write("")
                                st.write("")
                                if st.button("📱 Enviar", key=f"enviar_{bug['link'][:20]}"):
                                    resultado = enviar_alerta(bug)
                                    if resultado and resultado.get("ok"):
                                        st.success("✅ Enviado!")
                                    else:
                                        st.error("❌ Erro")
                                
                                st.link_button("🔗 Ver", bug['link'])
                            
                            st.divider()

with tab3:
    st.subheader("📊 Histórico de Preços")
    
    try:
        conn = sqlite3.connect(db_path)
        historico = pd.read_sql(
            "SELECT * FROM produtos ORDER BY timestamp DESC LIMIT 100",
            conn
        )
        conn.close()
        
        if historico.empty:
            st.info("📭 Nenhum histórico ainda. Faça uma busca primeiro!")
        else:
            col_filtro1, col_filtro2 = st.columns(2)
            with col_filtro1:
                plataforma_filtro = st.multiselect(
                    "🏪 Filtrar por plataforma",
                    historico['plataforma'].unique(),
                    default=historico['plataforma'].unique()
                )
            with col_filtro2:
                limite_preco = st.slider("💰 Preço máximo", 0, int(historico['preco'].max()), int(historico['preco'].max()))
            
            historico_filtrado = historico[
                (historico['plataforma'].isin(plataforma_filtro)) &
                (historico['preco'] <= limite_preco)
            ]
            
            st.metric("📦 Total de produtos", len(historico_filtrado))
            st.dataframe(
                historico_filtrado[['nome', 'preco', 'plataforma', 'timestamp']],
                use_container_width=True,
                hide_index=True
            )
    except:
        st.info("📭 Banco vazio")

st.divider()
st.caption("💡 Dica: Deixe o bot rodando na aba 'Bot Automático' e receberá alertas no Telegram automaticamente")
