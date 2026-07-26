import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_alerta(produto):
    emoji_plataforma = {
        '🛒 Mercado Livre': '🛒',
        '🛍️ Shopee': '🛍️',
        '🎵 TikTok Shop': '🎵'
    }
    
    emoji = emoji_plataforma.get(produto['plataforma'], '🔥')
    
    mensagem = f"""
{emoji} *PREÇO BUGADO!*

📦 {produto['nome'][:80]}
💰 R$ {produto['preco']:.2f} (era R$ {produto['preco_medio']:.2f})
📉 Desconto: {produto['desconto']}%
🏪 {produto['plataforma']}

🔗 [COMPRAR]({produto['link']})
"""
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Erro Telegram: {e}")
        return None
