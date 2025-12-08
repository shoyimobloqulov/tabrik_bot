import telebot
from telebot import types
from datetime import datetime
from app.calendar import create_newyear_image_styled
from app.new_year_data import templates,congratulations
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap
import re

BOT_TOKEN = "8422556946:AAEj6H7aqSi4yc5k5rPuxCgv6Khwl61MB9o"   # BotFather bergan tokenni qo'ying
bot = telebot.TeleBot(BOT_TOKEN)

user_page = {}  # foydalanuvchi hozirgi page indexini saqlaydi
user_data = {}  # foydalanuvchi tanlagan template va tabrikni saqlash

def send_template_slider(chat_id, index):
    template = templates[index]

    # Inline tugmalar
    keyboard = types.InlineKeyboardMarkup()
    prev_btn = types.InlineKeyboardButton("⬅️ Oldingi", callback_data=f"prev_{index}")
    select_btn = types.InlineKeyboardButton("✔ Tanlash", callback_data=f"select_{index}")
    next_btn = types.InlineKeyboardButton("➡️ Keyingi", callback_data=f"next_{index}")
    keyboard.row(prev_btn, select_btn, next_btn)

    # Rasm yo'li
    template_path = f"static/templates/{template['preview']}"

    # Rasmni ochish va Telegram uchun maksimal o'lchamga moslash
    MAX_WIDTH = 1280
    MAX_HEIGHT = 1280

    img = Image.open(template_path)
    img_format = img.format  # JPEG yoki PNG bo'lishi kerak

    # Rasm juda katta bo'lsa, kamaytirish
    img.thumbnail((MAX_WIDTH, MAX_HEIGHT))

    # Telegramga yuborish uchun vaqtinchalik saqlash
    temp_path = f"static/templates/_temp_{template['preview']}"
    img.save(temp_path, format=img_format)

    with open(temp_path, "rb") as img_file:
        bot.send_photo(
            chat_id,
            img_file,
            caption=f"📄 *{template['title']}* shablon\n{index+1}/{len(templates)}",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

def send_congratulations_slider(chat_id, index):
    text = congratulations[index]

    keyboard = types.InlineKeyboardMarkup()
    prev_btn = types.InlineKeyboardButton("⬅️ Oldingi", callback_data=f"prev_congr_{index}")
    select_btn = types.InlineKeyboardButton("✔ Tanlash", callback_data=f"select_congr_{index}")
    next_btn = types.InlineKeyboardButton("➡️ Keyingi", callback_data=f"next_congr_{index}")
    keyboard.row(prev_btn, select_btn, next_btn)

    bot.send_message(
        chat_id,
        f"📄 *Tabrik:* {text}\n{index+1}/{len(congratulations)}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

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

    text = f"<b>👋 Assalomu alaykum {clickable_name} botimizga xush kelibsiz.\n\n🔹 Kerakli bo'limni tanlang.</b>"

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
        """🧑‍💻 *Dasturchi:* @shoyimobloqulov\n🧑‍💻 *Dastur dizayneri:* Visoliddin Jaloliy\n\n🔷 *Biz bilan o'z virtual olamingizni yarating!*""",
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
    chat_id = message.chat.id
    user_page[chat_id] = 0  # birinchi slayd
    send_template_slider(chat_id, 0)

@bot.callback_query_handler(func=lambda call: True)
def callback_slider(call):
    chat_id = call.message.chat.id
    data = call.data

    # TEMPLATE SLIDER
    if data.startswith("next_") and not data.startswith("next_congr_"):
        index = int(data.split("_")[1])
        index = (index + 1) % len(templates)
        user_page[chat_id] = index
        bot.delete_message(chat_id, call.message.message_id)
        send_template_slider(chat_id, index)

    elif data.startswith("prev_") and not data.startswith("prev_congr_"):
        index = int(data.split("_")[1])
        index = (index - 1) % len(templates)
        user_page[chat_id] = index
        bot.delete_message(chat_id, call.message.message_id)
        send_template_slider(chat_id, index)

    elif data.startswith("select_") and not data.startswith("select_congr_"):
        index = int(data.split("_")[1])
        chosen = templates[index]
        user_data[chat_id] = {"template": chosen}
        bot.answer_callback_query(call.id, "Template tanlandi!")
        bot.edit_message_caption(
            chat_id=chat_id,
            message_id=call.message.message_id,
            caption=f"✔ Siz *{chosen['title']}* shablonni tanladingiz!",
            parse_mode="Markdown"
        )

        # Tabrik slider boshlash
        user_page[chat_id] = 0
        send_congratulations_slider(chat_id, 0)

    # CONGRATULATIONS SLIDER
    elif data.startswith("next_congr_"):
        index = int(data.split("_")[2])
        index = (index + 1) % len(congratulations)
        user_page[chat_id] = index
        bot.delete_message(chat_id, call.message.message_id)
        send_congratulations_slider(chat_id, index)

    elif data.startswith("prev_congr_"):
        index = int(data.split("_")[2])
        index = (index - 1) % len(congratulations)
        user_page[chat_id] = index
        bot.delete_message(chat_id, call.message.message_id)
        send_congratulations_slider(chat_id, index)

    elif data.startswith("select_congr_"):
        index = int(data.split("_")[2])
        chosen_congr = congratulations[index]
        user_data[chat_id]["congr"] = chosen_congr
        bot.answer_callback_query(call.id, "Tabrik tanlandi!")
        bot.send_message(chat_id, "🎉 Iltimos, ismingizni kiriting:")
        bot.register_next_step_handler_by_chat_id(chat_id, add_name_to_template)

def add_name_to_template(message):
    chat_id = message.chat.id
    user_name = message.text.strip()
    data = user_data.get(chat_id)

    if not data:
        bot.send_message(chat_id, "Xatolik yuz berdi, iltimos boshidan boshlang.")
        return

    template = data["template"]
    text = data["congr"]

    # ========================
    # Rasmni ochish va RGBA rejimida ishlash
    # ========================
    template_path = f"static/templates/{template['preview']}"
    img = Image.open(template_path)
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    img_format = img.format
    MAX_SIZE = (1280, 1280)
    img.thumbnail(MAX_SIZE)

    # Overlay yaratish (rangli emoji uchun)
    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # ========================
    # Fontlar
    # ========================
    font_name = ImageFont.truetype("app/fonts/arial/ARIAL.ttf", template.get('name_font_size', 60))
    font_text = ImageFont.truetype("app/fonts/arial/ARIAL.ttf", template.get('info_font_size', 40))
    font_emoji = ImageFont.truetype("app/fonts/seguiemj.ttf", template.get('info_font_size', 40))

    # ========================
    # Emoji ajratish funksiyasi
    # ========================
    def split_text_and_emoji(text):
        """Matnni oddiy matn va emoji qismlariga ajratadi"""
        # Emoji pattern (keng range)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "]+", 
            flags=re.UNICODE
        )
        
        parts = []
        last_end = 0
        
        for match in emoji_pattern.finditer(text):
            # Emoji oldidagi matn
            if match.start() > last_end:
                parts.append(('text', text[last_end:match.start()]))
            # Emoji
            parts.append(('emoji', match.group()))
            last_end = match.end()
        
        # Oxirgi matn
        if last_end < len(text):
            parts.append(('text', text[last_end:]))
        
        return parts

    # ========================
    # Aralash matn chizish funksiyasi
    # ========================
    def draw_mixed_text(draw, text, x, y, text_font, emoji_font, color):
        """Matn va emojini aralash holda chizadi"""
        parts = split_text_and_emoji(text)
        current_x = x
        
        for part_type, content in parts:
            if part_type == 'text':
                draw.text((current_x, y), content, font=text_font, fill=color)
                bbox = draw.textbbox((current_x, y), content, font=text_font)
                current_x = bbox[2]
            else:  # emoji
                draw.text((current_x, y), content, font=emoji_font, embedded_color=True)
                bbox = draw.textbbox((current_x, y), content, font=emoji_font)
                current_x = bbox[2]
        
        return current_x

    # ========================
    # Greeting
    # ========================
    greeting = "Assalomu alaykum"
    bbox = draw.textbbox((0, 0), greeting, font=font_text)
    w = bbox[2] - bbox[0]
    draw.text(
        (template['name_pos'][0] - w // 2, template['name_pos'][1] - 60),
        greeting,
        font=font_text,
        fill=template.get('name_color', 'black')
    )

    # ========================
    # Ism markazda
    # ========================
    bbox = draw.textbbox((0, 0), user_name, font=font_name)
    w = bbox[2] - bbox[0]
    draw.text(
        (template['name_pos'][0] - w // 2, template['name_pos'][1]),
        user_name,
        font=font_name,
        fill=template.get('name_color', 'black')
    )

    # ========================
    # Text + emoji multi-line (RANGLI)
    # ========================
    max_chars_per_line = 25
    lines = textwrap.wrap(text, width=max_chars_per_line)
    y_text = template['info_pos'][1]

    for line in lines:
        # Har bir qatorning kengligini hisoblash (markazlash uchun)
        parts = split_text_and_emoji(line)
        total_width = 0
        
        for part_type, content in parts:
            if part_type == 'text':
                bbox = draw.textbbox((0, 0), content, font=font_text)
            else:
                bbox = draw.textbbox((0, 0), content, font=font_emoji)
            total_width += (bbox[2] - bbox[0])
        
        # Markazlangan x koordinata
        start_x = template['info_pos'][0] - total_width // 2
        
        # Aralash matn va emoji chizish
        draw_mixed_text(
            draw, 
            line, 
            start_x, 
            y_text, 
            font_text, 
            font_emoji, 
            template.get('info_color', 'black')
        )
        
        # Keyingi qatorga o'tish
        bbox = draw.textbbox((0, 0), line, font=font_text)
        y_text += (bbox[3] - bbox[1]) + 10
    # ================================
    # PASTKI O‘NGDA @tabrik2026bot YOZUVINI CHIQARISH
    # ================================
    bot_text = "@tabrik2026bot"
    bot_font = ImageFont.truetype("app/fonts/arial/ARIAL.ttf", 24)
    padding = 10

    bbox = draw.textbbox((0, 0), bot_text, font=bot_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = img.width - text_width - padding
    y = img.height - text_height - padding

    bg_padding = 10
    bg_x1 = x - bg_padding
    bg_y1 = y - bg_padding
    bg_x2 = x + text_width + bg_padding
    bg_y2 = y + text_height + bg_padding

    draw.rectangle(
        [bg_x1, bg_y1, bg_x2, bg_y2],
        fill=(0, 0, 0, 150)
    )

    draw.text((x, y), bot_text, font=bot_font, fill="white")

    img = Image.alpha_composite(img, overlay)

    # Temp fayl nomi
    temp_path = f"out/final_{chat_id}.png"

    # Rasmni saqlash
    img.save(temp_path, format="PNG")

    # Telegramga yuborish
    with open(temp_path, "rb") as img_file:
        bot.send_photo(chat_id, img_file, caption="🎊 Sizga yoqadigan tabrik tayyor! 🎊")

    # Agar kerak bo‘lsa faylni o‘chirib tashlash
    if os.path.exists(temp_path):
        os.remove(temp_path)


bot.infinity_polling()
