import os
import json
import urllib.request
from urllib.parse import quote
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# ВАШ АДРЕС SearXNG на Railway (без слеша в конце)
SEARXNG_URL = os.getenv("SEARXNG_URL", "https://your-app-name.up.railway.app")

def search_searxng(query: str) -> str:
    """Поиск через СВОЙ экземпляр SearXNG на Railway"""
    try:
        encoded_query = quote(query)
        # Используем JSON API вашего собственного сервера
        url = f"{SEARXNG_URL}/search?q={encoded_query}&format=json"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        results = []
        
        for item in data.get('results', [])[:5]:
            title = item.get('title', 'Без названия')
            url_result = item.get('url', '')
            content = item.get('content', '')[:200]
            
            if title and url_result:
                results.append(f"🔹 *{title}*\n{content}\n[Ссылка]({url_result})")
        
        if not results:
            return f"❌ По запросу \"{query}\" ничего не найдено."
        
        return f"🔍 *Результаты поиска:* {query}\n\n" + "\n\n".join(results)
    
    except Exception as e:
        return f"❌ Ошибка поиска: {str(e)[:150]}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Поисковый бот*\n\n"
        "Я ищу информацию через собственный поисковый сервер.\n\n"
        "📌 *Как использовать:*\n"
        "Просто напишите любой вопрос\n\n"
        "✅ *Примеры:*\n"
        "• курс доллара 2026\n"
        "• погода в Москве\n"
        "• новости сегодня",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    
    if not query:
        await update.message.reply_text("Пожалуйста, напишите что-нибудь для поиска.")
        return
    
    await update.message.reply_text(f"🔎 *Ищу:* {query}...", parse_mode="Markdown")
    results = search_searxng(query)
    await update.message.reply_text(results, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    if not TELEGRAM_TOKEN:
        print("❌ Ошибка: не указан TELEGRAM_TOKEN")
        return
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print(f"✅ Бот запущен с SearXNG: {SEARXNG_URL}")
    app.run_polling()

if __name__ == "__main__":
    main()
