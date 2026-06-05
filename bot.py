import os
import re
import urllib.request
from urllib.parse import quote
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def search_duckduckgo(query: str) -> str:
    """Поиск в DuckDuckGo"""
    try:
        encoded_query = quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
        
        results = []
        matches = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)".*?>(.*?)</a>', html, re.DOTALL)
        
        for href, title in matches[:5]:
            title = re.sub(r'<[^>]+>', '', title).strip()
            if title and href.startswith('http'):
                results.append(f"🔹 [{title}]({href})")
        
        if not results:
            return "❌ Ничего не найдено"
        
        return f"🔍 *Результаты для:* {query}\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"⚠️ Ошибка: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Поисковый бот*\n\nОтправьте любой запрос, и я найду информацию в интернете.",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text(f"🔎 Ищу: *{query}*...", parse_mode="Markdown")
    results = search_duckduckgo(query)
    await update.message.reply_text(results, parse_mode="Markdown", disable_web_page_preview=False)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
