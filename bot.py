import os
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Расширенная база знаний
ANSWERS = {
    # Погода
    'погода': "🌤️ *Погода*\n\nПосмотреть погоду в вашем городе:\n• [Яндекс.Погода](https://yandex.ru/pogoda)\n• [Gismeteo](https://www.gismeteo.ru)\n• [Weather.com](https://weather.com/ru-RU)\n\n💡 *Совет:* Добавьте город в запрос, например: \"погода в Москве\"",
    
    # Курсы валют
    'курс доллара': "💵 *Курс доллара и других валют*\n\nАктуальные курсы:\n• [ЦБ РФ](https://www.cbr.ru)\n• [Google Финансы](https://www.google.com/finance)\n• [Investing.com](https://ru.investing.com/currencies/usd-rub)\n• [Rate.am](https://rate.am/ru)",
    
    'курс евро': "💶 *Курс евро*\n\nАктуальный курс:\n• [ЦБ РФ](https://www.cbr.ru)\n• [Google Финансы](https://www.google.com/finance)",
    
    # Новости
    'новости': "📰 *Главные новости*\n\n• [РИА Новости](https://ria.ru)\n• [ТАСС](https://tass.ru)\n• [РБК](https://www.rbc.ru)\n• [Ведомости](https://www.vedomosti.ru)\n• [Lenta.ru](https://lenta.ru)\n• [Meduza](https://meduza.io)",
    
    'новости мира': "🌍 *Мировые новости*\n\n• [BBC Russian](https://www.bbc.com/russian)\n• [Deutsche Welle](https://www.dw.com/ru)\n• [Euronews](https://ru.euronews.com)",
    
    'новости россии': "🇷🇺 *Новости России*\n\n• [Российская газета](https://rg.ru)\n• [Коммерсантъ](https://www.kommersant.ru)\n• [Известия](https://iz.ru)",
    
    # Википедия и энциклопедии
    'википедия': "📚 *Википедия*\n\nСвободная энциклопедия:\n[https://ru.wikipedia.org](https://ru.wikipedia.org)\n\n🔍 Чтобы найти статью, напишите: википедия [тема]\nПример: википедия кот",
    
    # Поисковые системы
    'поиск': "🔍 *Поисковые системы*\n\n• [Google](https://www.google.com)\n• [Яндекс](https://yandex.ru)\n• [DuckDuckGo](https://duckduckgo.com)\n• [Bing](https://www.bing.com)",
    
    # YouTube
    'ютуб': "🎬 *YouTube*\n\nСмотрите видео:\n[https://www.youtube.com](https://www.youtube.com)\n\n📱 Приложение для Android/iOS",
    
    # Telegram
    'телеграм': "📱 *Telegram*\n\nВеб-версия:\n[https://web.telegram.org](https://web.telegram.org)\n\nПриложения для всех платформ",
    
    # Карты
    'карты': "🗺️ *Карты и навигация*\n\n• [Google Карты](https://maps.google.com)\n• [Яндекс.Карты](https://yandex.ru/maps)\n• [2ГИС](https://2gis.ru)",
    
    # Переводчики
    'переводчик': "🌐 *Переводчики*\n\n• [Google Translate](https://translate.google.com)\n• [Яндекс.Переводчик](https://translate.yandex.ru)\n• [DeepL](https://www.deepl.com/ru/translator)",
    
    # Время
    'время': "🕐 *Точное время*\n\n• [TimeAndDate.com](https://www.timeanddate.com/worldclock/)\n• [Time100.ru](https://time100.ru)",
    
    # Фильмы и сериалы
    'фильм': "🎬 *Где смотреть фильмы и сериалы*\n\n• [Кинопоиск](https://www.kinopoisk.ru)\n• [IVI](https://ivi.ru)\n• [Okko](https://okko.tv)\n• [Кинопоиск HD](https://hd.kinopoisk.ru)",
    
    # Музыка
    'музыка': "🎵 *Музыкальные сервисы*\n\n• [Яндекс.Музыка](https://music.yandex.ru)\n• [VK Музыка](https://vk.com/music)\n• [Spotify](https://www.spotify.com)\n• [YouTube Music](https://music.youtube.com)",
    
    # Образование
    'образование': "📚 *Образовательные ресурсы*\n\n• [Stepik](https://stepik.org)\n• [Coursera](https://www.coursera.org)\n• [Открытое образование](https://openedu.ru)\n• [Arzamas](https://arzamas.academy)",
    
    # Здоровье
    'здоровье': "💊 *О здоровье*\n\n• [Здоровая Россия](https://www.takzdorovo.ru)\n• [Поликлиника.ру](https://policlinica.ru)\n• [Справочник лекарств](https://www.rlsnet.ru)",
    
    # Еда
    'рецепт': "🍳 *Кулинарные сайты*\n\n• [Povarenok](https://www.povarenok.ru)\n• [Gotovim.ru](https://www.gotovim.ru)\n• [Еда.ру](https://eda.ru)\n• [Cookpad](https://cookpad.com/ru)",
}

def extract_city(query: str) -> str:
    """Пытается извлечь название города из запроса"""
    import re
    city_match = re.search(r'(?:погода в|в городе|в)\s+([а-яА-ЯёЁ\s-]+)', query.lower())
    if city_match:
        city = city_match.group(1).strip()
        if len(city) < 30:
            return city
    return None

def get_answer(query: str) -> str:
    """Возвращает ответ на основе ключевых слов"""
    query_lower = query.lower()
    
    # Специальный случай: погода в городе
    if 'погода' in query_lower:
        city = extract_city(query)
        if city:
            return f"🌤️ *Погода в {city.title()}*\n\nПосмотреть прогноз:\n• [Яндекс.Погода](https://yandex.ru/pogoda/search?text={city})\n• [Gismeteo](https://www.gismeteo.ru/search2/?query={city})\n• [Weather.com](https://weather.com/ru-RU/weather/today/l/{city})\n\n💡 Или просто напишите \"погода\""
        return ANSWERS.get('погода')
    
    # Википедия + тема
    if 'википедия' in query_lower:
        topic_match = re.search(r'википедия\s+(.+?)(?:$|,|\.)', query_lower)
        if topic_match:
            topic = topic_match.group(1).strip()
            return f"📚 *Википедия: {topic.title()}*\n\n[https://ru.wikipedia.org/wiki/{topic.replace(' ', '_')}](https://ru.wikipedia.org/wiki/{topic.replace(' ', '_')})\n\n📌 Общая ссылка: https://ru.wikipedia.org"
        return ANSWERS.get('википедия')
    
    # Курс валют (доллар, евро, юань)
    if 'доллар' in query_lower or 'usd' in query_lower:
        return ANSWERS.get('курс доллара')
    if 'евро' in query_lower or 'eur' in query_lower:
        return ANSWERS.get('курс евро')
    
    # Категории новостей
    if 'новости мира' in query_lower or 'мировые новости' in query_lower:
        return ANSWERS.get('новости мира')
    if 'новости россии' in query_lower or 'российские новости' in query_lower:
        return ANSWERS.get('новости россии')
    if 'новости' in query_lower:
        return ANSWERS.get('новости')
    
    # Остальные ключевые слова
    for keyword, answer in ANSWERS.items():
        if keyword in query_lower:
            return answer
    
    # Если не нашли ключевое слово — предложить помощь
    return (
        "🤔 *Я не совсем понял запрос*\n\n"
        "Вот что я умею:\n\n"
        "🌤️ *Погода* — погода, погода в Москве\n"
        "💰 *Курсы валют* — курс доллара, курс евро\n"
        "📰 *Новости* — новости, новости России\n"
        "📚 *Википедия* — википедия, википедия кот\n"
        "🎬 *Развлечения* — фильмы, музыка, ютуб\n"
        "🗺️ *Карты* — карты, навигация\n"
        "🌐 *Перевод* — переводчик\n\n"
        "✍️ Попробуйте один из этих запросов!"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Помощник по интернет-сервисам*\n\n"
        "Я даю полезные ссылки на популярные сайты.\n\n"
        "📌 *Примеры запросов:*\n"
        "• погода или погода в Сочи\n"
        "• курс доллара\n"
        "• новости\n"
        "• википедия (или википедия собака)\n"
        "• фильмы, музыка, карты\n\n"
        "Просто напишите, что вас интересует!",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *Справка*\n\n"
        "Я умею отвечать на такие темы:\n\n"
        "🌤️ *Погода* — погода, погода в городе\n"
        "💰 *Финансы* — курс доллара, курс евро\n"
        "📰 *Новости* — новости, новости России\n"
        "📚 *Энциклопедия* — википедия, википедия [тема]\n"
        "🎬 *Видео/ТВ* — фильмы, ютуб, музыка\n"
        "🗺️ *Карты* — карты, навигация\n"
        "🌐 *Инструменты* — переводчик, время\n\n"
        "🔧 *Команды:*\n"
        "/start — приветствие\n"
        "/help — это сообщение",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    
    if not query:
        await update.message.reply_text("Пожалуйста, напишите что-нибудь.")
        return
    
    await update.message.reply_text(f"🔎 *Обрабатываю запрос:* {query}", parse_mode="Markdown")
    answer = get_answer(query)
    await update.message.reply_text(answer, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    if not TELEGRAM_TOKEN:
        print("❌ Ошибка: не указан TELEGRAM_TOKEN")
        return
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен с расширенной базой знаний!")
    app.run_polling()

if __name__ == "__main__":
    main()
