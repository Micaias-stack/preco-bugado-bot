import requests

TOKEN = "SEU_TOKEN_AQUI"  # @BotFather no Telegram
CHAT_ID = "SEU_CHAT_ID"   # Use @userinfobot pra descobrir

def enviar_alerta(produto):
    """Envia mensagem formatada no Telegram"""
    mensagem = f"""
🚨 **PREÇO BUGADO DETECTADO!**

📦 {produto['nome']}
💰 R$ {produto['preco']:.2f} (era R$ {produto['preco_medio']:.2f})
📉 Desconto: {produto['desconto']}%

🔗 Comprar: {produto['link']}
    """
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"})
