import os
import json
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import AsyncGroq

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = AsyncGroq(api_key=GROQ_API_KEY)

def search_duckduckgo(query: str) -> str:
    """Бесплатный поиск через DuckDuckGo HTML API"""
    try:
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = httpx.post(url, data=params, headers=headers, timeout=15)
        
        # Простой парсинг результатов
        import re
        results = []
        matches = re.findall(r'<a rel="nofollow" class="result__a" href="([^"]+)".*?>(.*?)</a>', response.text, re.DOTALL)
        
        for href, title in matches[:3]:
            title = re.sub(r'<[^>]+>', '', title).strip()
            if title and href.startswith('http'):
                results.append(f"• [{title}]({href})")
        
        if not results:
            return "По вашему запросу ничего не найдено."
        
        return "\n".join(results) + "\n\n🔍 *Источник:* DuckDuckGo"
    except Exception as e:
        return f"Ошибка поиска: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Я бот с поиском в интернете!*\n\n"
        "Просто задайте вопрос, и я найду актуальную информацию.\n"
        "Например:\n"
        "• Курс доллара на сегодня\n"
        "• Новости науки 2026\n"
        "• Как приготовить пиццу\n\n"
        "Команды:\n"
        "/search <запрос> — поиск без ИИ\n"
        "/reset — очистить историю",
        parse_mode="Markdown"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("История диалога очищена ✅")

async def search_only(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напишите: /search <ваш запрос>")
        return
    query = " ".join(context.args)
    await update.message.reply_text(f"🔎 Ищу: *{query}*...", parse_mode="Markdown")
    results = search_duckduckgo(query)
    await update.message.reply_text(results, parse_mode="Markdown", disable_web_page_preview=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.reply_text("🤔 Думаю и ищу в интернете...")
    
    # Сохраняем историю (последние 5 сообщений)
    if "history" not in context.user_data:
        context.user_data["history"] = []
    context.user_data["history"].append({"role": "user", "content": user_text})
    
    # Делаем поиск в интернете
    search_results = search_duckduckgo(user_text)
    
    # Формируем промпт для ИИ
    system_prompt = """Ты полезный ассистент. Отвечай на русском языке, используя информацию из поиска.
    Если в поиске нет точного ответа — честно скажи об этом и предложи уточнить вопрос.
    Будь кратким, но информативным."""
    
    user_prompt = f"""Вопрос пользователя: {user_text}

Результаты поиска:
{search_results}

Дай ответ, основанный на этих результатах."""
    
    try:
        response = await groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                *context.user_data["history"][-5:],
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        reply = response.choices[0].message.content
        context.user_data["history"].append({"role": "assistant", "content": reply})
        
        # Отправляем ответ + ссылки на источники
        full_reply = f"{reply}\n\n{search_results}"
        await update.message.reply_text(full_reply, parse_mode="Markdown", disable_web_page_preview=True)
        
    except Exception as e:
        await update.message.reply_text(f"Ошибка ИИ: {str(e)}\n\nВот что нашёл поиск:\n{search_results}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("search", search_only))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()