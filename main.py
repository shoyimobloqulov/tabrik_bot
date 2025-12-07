import telebot
from telebot import types
from datetime import datetime
from app.calendar import create_newyear_image_styled
import os

BOT_TOKEN = "8422556946:AAHfJPljk9em_6Uz8wWKnkEY7n73MItV_vc"   # BotFather bergan tokenni qo'ying
bot = telebot.TeleBot(BOT_TOKEN)


# /start komandasi
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("🎄 Yangi yilga necha kun qoldi?")
    btn2 = types.KeyboardButton("🎉 Tabriklar")
    btn3 = types.KeyboardButton("📘 Qo'llanma")
    btn4 = types.KeyboardButton("👨‍💻 Admin")

    markup.row(btn1)
    markup.row(btn2, btn3)
    markup.row(btn4)

    user = message.from_user

    # Foydalanuvchi nomi
    full_name = user.first_name
    if user.last_name:
        full_name += f" {user.last_name}"

    # Agar username bo'lsa
    if user.username:
        profile_link = f"https://t.me/{user.username}"
    else:
        # Agar username bo'lmasa ID orqali link
        profile_link = f"tg://user?id={user.id}"

    # Clickable name
    clickable_name = f'<a href="{profile_link}">{full_name}</a>'

    text = f"Assalomu alaykum, {clickable_name}! 👋\nProfilingizga o‘tish uchun ismingizni bosing."

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda m: m.text == "🎄 Yangi yilga necha kun qoldi?")
def new_year_info(message):
    today = datetime.now()
    new_year = datetime(today.year + 1, 1, 1)

    # Qolgan kunlar
    days_left = (new_year - today).days

    # Rasm nomi chat_id orqali
    output_image = f"logs/newyear_{message.chat.id}.jpg"

    # Rasmni yaratish
    create_newyear_image_styled(
        input_image="app/images/calendar.jpg",
        output_image=output_image,
        nm=days_left
    )

    # Matn
    info_text = (
        f"🎄 *YANGI YILGA QOLGAN VAQT*\n\n"
        f"📆 Bugungi sana: {today.strftime('%d-%m-%Y')}\n"
        f"🎉 Yangi yil: 01-01-{today.year + 1}\n"
        f"⏳ Qolgan kunlar: *{days_left} kun*\n"
        f"✨ Yangi yilga oz qoldi, tayyorgarlikni boshlang!"
    )

    # Rasmni jonatish
    with open(output_image, "rb") as photo:
        bot.send_photo(
            message.chat.id,
            photo,
            caption=info_text,
            parse_mode="Markdown"
        )

    # Optional: rasmni yuborganidan keyin o'chirish (diskni tozalash uchun)
    if os.path.exists(output_image):
        os.remove(output_image)

# Admin haqida ma'lumot
@bot.message_handler(func=lambda m: m.text == "👨‍💻 Admin")
def admin_info(message):
    bot.send_message(
        message.chat.id,
        "🧑‍💻 *Dasturchi:* @shoyimobloqulov\n\n"
        "🔷 *Biz bilan o'z virtual olamingizni yarating!*",
        parse_mode="Markdown"
    )

# Qo'llanma haqida ma'lumot
@bot.message_handler(func=lambda m: m.text == "📘 Qo'llanma")
def guide_info(message):
    text = (
        "📘 ***BOT QO'LLANMASI***\n\n"
        "_- Tabriklar bo'limida siz ismingizga tabrik yozishingiz mumkin._\n"
        "_- Sertifikatlar bo'limida siz ismingizga sertifikat yozishingiz mumkin._\n"
        "_- Yangi yilgacha nechi kun qolganini bot orqali chiroyli rasmda yozib olishingiz mumkin._\n\n"
        "🎄 ***Yangi yil sizga bir olam quvonch olib kelsin!***"
    )

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="Markdown"
    )

# Tabriklar bo'limi
@bot.message_handler(func=lambda m: m.text == "🎉 Tabriklar")
def open_tabrik_webapp(message):
    webapp_url = "../tabrik"   # <-- sahifangiz URL
    
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        text="🎉 Tabrik yozish",
        web_app=types.WebAppInfo(url=webapp_url)
    )

    markup.add(btn)

    bot.send_message(
        message.chat.id,
        "Quyidagi tugmani bosing va tabrik yarating:",
        reply_markup=markup
    )

bot.infinity_polling()
