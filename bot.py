import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== НАСТРОЙКИ ==========
TOKEN = "8900701358:AAEizc7UClRl-VoG28DEBC8Wand4gMEoETw"
TAVILY_API_KEY = "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"
SEARCH_ENGINE = "tavily"  # используем Tavily

def search_web(query: str) -> str:
    if not TAVILY_API_KEY:
        return "⚠️ API ключ Tavily не найден. Добавьте переменную TAVILY_API_KEY."
    
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": f"Ответь на русском языке: {query}",
    "include_answer": True,
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
            return "🤔 Ты какую-то хуйню спросил"
    except Exception as e:
        return f"❌ Ошибка поиска: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 Привет! Я сам ищу ответы в интернете.\n"
        "Просто напиши вопрос — и я отвечу своими словами, без ссылок.\n\n"
        "Примеры:\n"
        "• Погода в Москве\n"
        "• Курс доллара\n"
        "• Кто такие пидоры?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_query = update.message.text
    await update.message.chat.send_action(action="typing")
    answer = search_web(user_query)
    await update.message.reply_text(answer)

def main():
    if not TOKEN:
        print("❌ Ошибка: не найден TELEGRAM_BOT_TOKEN")
        return
    
    if not TAVILY_API_KEY:
        print("⚠️ Предупреждение: не найден TAVILY_API_KEY")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен и ищет ответы самостоятельно!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
