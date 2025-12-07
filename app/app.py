from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import os
from datetime import datetime

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
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    name = request.form.get("name", "").strip()
    info = request.form.get("info", "").strip()
    date_text = request.form.get("date", "").strip()

    if not name:
        flash("Iltimos, ismni kiriting.")
        return redirect(url_for("index"))

    # Agar foydalanuvchi sana bermagan bo'lsa, hozirgi sanani qo'yamiz
    if not date_text:
        date_text = datetime.now().strftime("%d %B %Y")  # 07 December 2025 kabi

    # Ochiq certificate template
    try:
        base = Image.open(TEMPLATE_PATH).convert("RGBA")
    except FileNotFoundError:
        flash("Sertifikat shabloni topilmadi (static/certificate_template.png).")
        return redirect(url_for("index"))

    image = base.copy()
    draw = ImageDraw.Draw(image)

    # Font o'lchamlari (sertifikat o'lchamiga qarab sozlang)
    img_w, img_h = image.size
    # nom va info uchun dinamik bazaviy o'lcham
    name_font_size = max(36, img_w // 15)
    info_font_size = max(20, img_w // 40)
    date_font_size = max(16, img_w // 60)

    try:
        name_font = ImageFont.truetype(FONT_PATH, name_font_size)
        info_font = ImageFont.truetype(FONT_PATH, info_font_size)
        date_font = ImageFont.truetype(FONT_PATH, date_font_size)
    except OSError:
        # Agar shrift yuklab bo'lmasa, default shriftga qaytamiz
        name_font = ImageFont.load_default()
        info_font = ImageFont.load_default()
        date_font = ImageFont.load_default()

    center_x = img_w // 2

    # Joylashuvlar - rasmga qarab moslashtiring
    # Misol: ismi markazda va biroz tepada
    name_y = int(img_h * 0.45)
    info_y = name_y + int(img_h * 0.06)
    date_y = info_y + int(img_h * 0.06)

    # Matnni markazga chiziq bo'yicha chizish (ba'zi holatlarda max_width bilan siqish)
    max_text_width = int(img_w * 0.8)

    draw_centered_text(draw, name, name_font, center_x, name_y, max_width=max_text_width)
    draw_centered_text(draw, info, info_font, center_x, info_y, max_width=max_text_width)
    draw_centered_text(draw, date_text, date_font, center_x, date_y, max_width=max_text_width)

    # Outputni BytesIO ga yozamiz va yuboramiz
    img_io = io.BytesIO()
    # PNG - shaffoflik yoki yuqori sifat uchun
    image = image.convert("RGB")  # ba'zi brauzerlar uchun
    image.save(img_io, "PNG", quality=95)
    img_io.seek(0)

    # Foydalanuvchi uchun mos fayl nomi
    filename = f"certificate_{name.replace(' ', '_')}.png"

    return send_file(
        img_io,
        mimetype="image/png",
        as_attachment=True,
        download_name=filename
    )

if __name__ == "__main__":
    app.run(debug=True)
