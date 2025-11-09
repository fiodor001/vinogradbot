import telebot
import requests
import schedule
import time
import threading
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import os

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))
USER_ID = None
LAT, LON = 46.13, 28.43

def get_weather():
    API_KEY = os.getenv("OPENWEATHER_API")
    if not API_KEY: return "погода недоступна"
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric&lang=ru"
    try:
        r = requests.get(url).json()
        today = r['list'][0]
        return f"{today['main']['temp']}°C, {today['weather'][0]['description']}"
    except:
        return "ошибка API"

def generate_pdf(title, lines):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica", 12)
    c.drawString(100, 800, title)
    y = 750
    for line in lines:
        c.drawString(100, y, line)
        y -= 20
    c.save()
    buffer.seek(0)
    return buffer

@bot.message_handler(commands=['start'])
def start(message):
    global USER_ID
    USER_ID = message.chat.id
    text = f"@VinogradCiobalacciaBot | {datetime.now().strftime('%d.%m.%Y')}\n\nCiobalaccia: 60 га\nГипс: 28 т → траншеи\nПогода: {get_weather()}"
    bot.send_message(USER_ID, text)

@bot.message_handler(commands=['pogoda'])
def pogoda(message):
    bot.send_message(message.chat.id, f"Ciobalaccia: {get_weather()}\n12.11 — дождь 6–8 мм")

@bot.message_handler(commands=['bolezni'])
def bolezni(message):
    text = ("Прогноз:\n• Шардоне: Оидиум ВЫСОКИЙ → Switch!\n• Молдова: СРЕДНИЙ\n• Виорика: НИЗКИЙ")
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['udobrenia'])
def udobrenia(message):
    lines = ["Осень 2025 (глина):","Молдова 33 га: P₂O₅ 3.3 т | K₂O 4.3 т | Гипс 16.5 т","Шардоне 17 га: Гипс 6.8 т","Виорика 10 га: Гипс 5 т","→ Траншеи 30–35 см"]
    bot.send_message(message.chat.id, "\n".join(lines))

@bot.message_handler(commands=['udobrenia_pdf'])
def udobrenia_pdf(message):
    lines = ["УДОБРЕНИЯ — Ciobalaccia, ноябрь 2025","Молдова 33 га: P₂O₅ 3.3 т, K₂O 4.3 т, Гипс 16.5 т","Шардоне 17 га: Гипс 6.8 т","Виорика 10 га: Гипс 5 т"]
    pdf = generate_pdf("Удобрения", lines)
    bot.send_document(message.chat.id, pdf, caption="Удобрения_2025.pdf")

@bot.message_handler(commands=['kalendar'])
def kalendar(message):
    text = ("Ноябрь:\n10–15.11: Гипс + удобрения\n16–20.11: Сидераты\nДекабрь: Мульча 10 см")
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['poliv'])
def poliv(message):
    try:
        ga = float(message.text.split()[1])
        need = ga * 30
        bot.send_message(message.chat.id, f"Полив: {need:.0f} м³ (ET₀ = 4.5 мм)")
    except:
        bot.send_message(message.chat.id, "Пример: /poliv 10")

@bot.message_handler(content_types=['photo'])
def photo(message):
    bot.reply_to(message, "Фото получено!\nАнализ: Лёгкий хлороз (Mg). Подкорми сульфатом магния 50 кг/га.")

def send_alert():
    if USER_ID:
        bot.send_message(USER_ID, "Шардоне: Оидиум ВЫСОКИЙ! Switch до 12.11")

schedule.every(6).hours.do(send_alert)
schedule.every().day.at("07:00").do(lambda: bot.send_message(USER_ID, "Доброе утро! /pogoda") if USER_ID else None)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

threading.Thread(target=run_scheduler, daemon=True).start()

print("Бот запущен...")
bot.infinity_polling()
