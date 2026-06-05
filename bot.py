import os
import json
import urllib.request
from urllib.parse import quote
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def search_alternative(query: str, source: int) -> tuple:
    """Пробует разные источники поиска"""
    
    encoded_query = quote(query)
    
    # Источник 1: DDG Instant Answer (быстрые ответы)
    if source == 1:
        try:
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get('AbstractText') or data.get('Answer'):
                    text = data.get('AbstractText') or data.get('Answer')
                    url_res = data.get('AbstractURL', '')
                    return True, f"📝 {text[:300]}\n\n🔗 {url_res}" if url_res else f"📝 {text[:300]}"
            return False, ""
        except:
            return False, ""
    
    # Источник 2: Публичный SearXNG экземпляр (запасной)
    if source == 2:
        instances = [
            "https://searx.space/search",
            "https://search.whatever.social/search",
            "https://searx.baczek.me/search"
        ]
        for instance in instances:
            try:
                url = f"{instance}?q={encoded_query}&format=json"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=8) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    results = data.get('results', [])[:3]
                    if results:
                        output = []
                        for r in results:
                            title = r.get('title', '')[:80]
                            link = r.get('url', '')
                            if title and link:
                                output.append(f"🔹 [{title}]({link})")
                        if output:
                            return True, "\n\n".join(output)
            except:
                continue
        return False, ""
    
    # Источник 3: Простой словарь с ответами на частые вопросы
    if source == 3:
        answers = {
            'погода': "🌤️ Для точной погоды рекомендую сайт: https://yandex.ru/pogoda или https://www.gismeteo.ru",
            'курс доллара': "💵 Актуальный курс можно посмотреть на: https://www.cbr.ru или https://www.google.com/finance",
            'новости': "📰 Главные новости: https://www.rbc.ru, https://tass.ru, https://www.vedomosti.ru",
            'википедия': "📚 Wikipedia: https://ru.wikipedia.org",
            'ютуб': "🎬 YouTube: https://www.youtube.com",
            'telegram': "📱 Telegram: https://web.telegram.org"
        }
        for key, answer in answers.items():
            if key in query.lower():
                return True, answer
        return False, ""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Поисковый бот*\n\n"
        "Я ищу информацию разными способами.\n\n"
        "📌 *Что я умею:*\n"
        "• Отвечать на вопросы\n"
        "• Искать информацию\n"
        "• Давать полезные ссылки\n\n"
        "✅ *Примеры запросов:*\n"
        "• погода\n"
        "• курс доллара\n"
        "• новости сегодня\n"
        "• Wikipedia Россия\n\n"
        "Просто напишите, что вас интересует!",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    
    if not query:
        await update.message.reply_text("Пожалуйста, напишите что-нибудь.")
        return
    
    await update.message.reply_text(f"🔎 *Ищу:* {query}...", parse_mode="Markdown")
    
    # Пробуем разные источники по очереди
    found = False
    for source in [1, 2, 3]:
        success, result = search_alternative(query, source)
        if success:
            await update.message.reply_text(result, parse_mode="Markdown", disable_web_page_preview=True)
            found = True
            break
    
    if not found:
        await update.message.reply_text(
            "❌ *Не удалось найти информацию*\n\n"
            "Попробуйте:\n"
            "• задать вопрос иначе\n"
            "• использовать более простые слова\n"
            "• спросить о другом\n\n"
            "Например: погода, новости, курс доллара, википедия",
            parse_mode="Markdown"
        )

def main():
    if not TELEGRAM_TOKEN:
        print("❌ Ошибка: не указан TELEGRAM_TOKEN")
        return
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен с многоуровневым поиском!")
    app.run_polling()

if __name__ == "__main__":
    main()
