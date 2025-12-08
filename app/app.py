from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
from datetime import datetime
from new_year_data import congratulations, templates

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "static", "certificate_template.png")
FONT_PATH = os.path.join(BASE_DIR, "static", "fonts", "Roboto-Bold.ttf")  # o'zgartiring

def draw_centered_text(draw, text, font, box_center_x, y, max_width=None):
    """
    Matnni markazlashtirib chizish uchun yordamchi funksiya.
    Agar max_width berilsa, kerak bo'lsa shriftni kichraytiradi.
    """
    if max_width:
        # agar juda uzun bo'lsa, shrift o'lchamini kamaytirishga harakat qilamiz
        current_font = font
        w, h = draw.textsize(text, font=current_font)
        while w > max_width and current_font.size > 12:
            # fontni kichiklashtirish
            current_font = ImageFont.truetype(FONT_PATH, current_font.size - 2)
            w, h = draw.textsize(text, font=current_font)
        font = current_font

    w, h = draw.textsize(text, font=font)
    x = box_center_x - w // 2
    draw.text((x, y), text, font=font, fill=(20, 20, 20))  # fill => qoraiga yaqin rang

@app.route("/", methods=["GET"])
def index():

    return render_template("index.html",congratulations=congratulations,templates=templates)

# =======================  GENERATION  =========================
@app.route("/generate", methods=["POST"])
def generate():
    name = request.form.get("name")
    info = request.form.get("info", "")
    date = request.form.get("date", "")
    template_file = request.form.get("template")

    print(f"Generating certificate for: {name}, {info}, {date}, template: {template_file}")

    if not name or not template_file:
        return "Xato: Ism yoki shablon tanlanmagan!"

    # --- Shablon rasmni yuklash ---
    template_path = f"static/templates/{template_file}"
    image = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(image)

    # --- Fontlar ---
    font_name = ImageFont.truetype("arial.ttf", 80)
    font_info = ImageFont.truetype("arial.ttf", 40)
    font_date = ImageFont.truetype("arial.ttf", 40)

    # --- Matnni rasmga yozish ---
    draw.text((300, 300), name, fill="black", font=font_name)
    draw.text((300, 420), info, fill="black", font=font_info)
    draw.text((300, 520), date, fill="black", font=font_date)

    # --- QR-KOD yaratish ---
    bot_link = "https://t.me/YOUR_BOT"   # YOU BOT LINK HERE
    qr = qrcode.make(bot_link)
    qr = qr.resize((180, 180))
    image.paste(qr, (image.width - 250, image.height - 250))

    # --- Rasmni yuborish ---
    img_io = io.BytesIO()
    image.save(img_io, "PNG")
    img_io.seek(0)

    return send_file(
        img_io,
        mimetype="image/png",
        as_attachment=True,
        download_name="sertifikat.png"
    )
\
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)