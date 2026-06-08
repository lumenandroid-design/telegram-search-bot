print("TELEGRAM_BOT_TOKEN exists:", bool(os.getenv("TELEGRAM_BOT_TOKEN")))
print("TAVILY_API_KEY exists:", bool(os.getenv("TAVILY_API_KEY")))
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== НАСТРОЙКИ ==========
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Токен из переменных окружения

# ВАРИАНТ 1: Tavily (рекомендуется, сам даёт ответ без ссылок)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # Получить бесплатно на app.tavily.com

# ВАРИАНТ 2: Brave Search (альтернатива, нужно брать описание)
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")  # Получить на brave.com/search/api/

# Какой поисковик использовать? (пишем "tavily" или "brave")
SEARCH_ENGINE = "tavily"  # поменяйте на "brave", если получили ключ Brave

# ========== ФУНКЦИИ ПОИСКА (без ссылок) ==========
def search_web(query: str) -> str:
    """Ищет в интернете и возвращает ТОЛЬКО текст ответа (без ссылок)"""
    
    if SEARCH_ENGINE == "tavily" and TAVILY_API_KEY:
        return _search_tavily(query)
    elif SEARCH_ENGINE == "brave" and BRAVE_API_KEY:
        return _search_brave(query)
    else:
        return "⚠️ Поиск не настроен. Добавьте API-ключ в переменные окружения."

def _search_tavily(query: str) -> str:
    """Tavily сам возвращает готовый ответ без ссылок"""
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "include_answer": True,      # КЛЮЧЕВОЙ параметр!
        "include_raw_content": False,
        "max_results": 3
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        answer = data.get("answer", "")
        
        if answer:
            return answer
        else:
            return "🤔 Не нашёл точного ответа. Попробуйте переформулировать вопрос."
    except Exception as e:
        return f"❌ Ошибка поиска: {str(e)}"

def _search_brave(query: str) -> str:
    """Brave — собираем только описания, ссылки отбрасываем"""
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    params = {"q": query, "count": 5}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        
        snippets = []
        for item in data.get("web", {}).get("results", []):
            desc = item.get("description", "")
            if desc:
                snippets.append(desc)
        
        if snippets:
            # Просто склеиваем описания (можно передать в GPT, если есть)
            return "\n\n".join(snippets[:3])
        else:
            return "🔍 Ничего не найдено."
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

# ========== ОБРАБОТЧИКИ КОМАНД ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 Привет! Я сам ищу ответы в интернете.\n"
        "Просто напиши вопрос — и я отвечу своими словами, без ссылок.\n\n"
        "Примеры:\n"
        "• Погода в Москве\n"
        "• Курс доллара\n"
        "• Кто такой Пушкин"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    
    # Показываем индикатор "печатает..."
    await update.message.chat.send_action(action="typing")
    
    # Ищем ответ
    answer = search_web(user_query)
    
    # Отправляем результат (только текст, без ссылок!)
    await update.message.reply_text(answer)

# ========== ЗАПУСК БОТА ==========
def main():
    if not TOKEN:
        print("❌ Ошибка: не найден TELEGRAM_BOT_TOKEN")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен и ищет ответы самостоятельно!")
    app.run_polling()

if __name__ == "__main__":
    main()
