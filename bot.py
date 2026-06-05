import os
import json
import urllib.request
from urllib.parse import quote
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

def search_duckduckgo(query: str) -> str:
    """Поиск через DuckDuckGo Instant Answer API"""
    try:
        encoded_query = quote(query)
        # Используем официальный API DuckDuckGo
        url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        results = []
        
        # Добавляем абстрактный ответ (краткое описание)
        if data.get('AbstractText'):
            results.append(f"📝 *Кратко:* {data['AbstractText'][:500]}")
            if data.get('AbstractURL'):
                results.append(f"🔗 Источник: {data['AbstractURL']}")
        
        # Добавляем связанные темы
        if data.get('RelatedTopics'):
            topics = []
            for topic in data['RelatedTopics'][:5]:
                if isinstance(topic, dict) and topic.get('Text'):
                    text = topic['Text'][:200]
                    if topic.get('FirstURL'):
                        results.append(f"• {text}\n  Ссылка: {topic['FirstURL']}")
                    else:
                        results.append(f"• {text}")
        
        # Если есть прямые ответы (для простых вопросов)
        if data.get('Answer'):
            results.insert(0, f"✅ *Ответ:* {data['Answer']}")
        
        if not results:
            # Если ничего не нашли через API, пробуем обычный поиск
            return search_duckduckgo_fallback(query)
        
        return f"🔍 *Результаты поиска:* {query}\n\n" + "\n\n".join(results[:5])
    
    except Exception as e:
        return search_duckduckgo_fallback(query)

def search_duckduckgo_fallback(query: str) -> str:
    """Запасной метод поиска с другим User-Agent"""
    try:
        encoded_query = quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
        
        import re
        results = []
        matches = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)".*?>(.*?)</a>', html, re.DOTALL)
        
        for href, title in matches[:3]:
            title = re.sub(r'<[^>]+>', '', title).strip()
            if title and href.startswith('http'):
                results.append(f"🔹 [{title}]({href})")
        
        if not results:
            return "❌ Ничего не найдено. Попробуйте:\n1. Уточнить запрос\n2. Задать вопрос иначе\n\nПримеры запросов:\n• курс доллара к рублю 2026\n• новости сегодня\n• Wikipedia Россия"
        
        return "🔍 *Найдено через поиск:*\n\n" + "\n\n".join(results)
    
    except Exception as e:
        return f"❌ Ошибка поиска. Попробуйте позже.\nТехническая причина: {str(e)[:100]}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Поисковый бот*\n\n"
        "Я ищу информацию в интернете через DuckDuckGo.\n\n"
        "Просто напишите любой вопрос или запрос.\n\n"
        "📌 *Примеры:*\n"
        "• курс доллара 2026\n"
        "• столица Франции\n"
        "• последние новости науки\n"
        "• рецепт борща\n\n"
        "⚡ *Совет:* Чем точнее вопрос, тем лучше результат!",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text(f"🔎 *Ищу:* {query}\n\nПодождите несколько секунд...", parse_mode="Markdown")
    results = search_duckduckgo(query)
    await update.message.reply_text(results, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот успешно запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()
