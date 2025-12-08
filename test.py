from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
import re

# Foydalanuvchi ma'lumotlari
chat_id = 123456789
user_name = "Shoyim Obloqulov"
template = {
        "preview": 'ce8af1daf9cfe11503e9bb15efdb9a9f.jpg',
        "title": "Black Classic",
        "title_color": "white",
        "name_pos": (340, 500),
        "info_pos": (330, 570),
        "name_color": "white",
        "info_color": "white",
        'name_font_size': 40,
        'info_font_size': 30
    }
text = "🎄 Yangi yil muborak! Yangi yil sizga quvonch, omad va mustahkam sog'liq olib kelsin! 🌟"

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

# Overlay yaratish
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
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"
        "]+",
        flags=re.UNICODE
    )
    
    parts = []
    last_end = 0
    
    for match in emoji_pattern.finditer(text):
        if match.start() > last_end:
            parts.append(('text', text[last_end:match.start()]))
        parts.append(('emoji', match.group()))
        last_end = match.end()
    
    if last_end < len(text):
        parts.append(('text', text[last_end:]))
    
    return parts

# ========================
# Aralash matn chizish funksiyasi
# ========================
def draw_mixed_text(draw, text, x, y, text_font, emoji_font, color):
    parts = split_text_and_emoji(text)
    current_x = x
    
    for part_type, content in parts:
        if part_type == 'text':
            draw.text((current_x, y), content, font=text_font, fill=color)
            bbox = draw.textbbox((current_x, y), content, font=text_font)
        else:
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
# Text + emoji multi-line
# ========================
max_chars_per_line = 25
lines = textwrap.wrap(text, width=max_chars_per_line)
y_text = template['info_pos'][1]

for line in lines:
    parts = split_text_and_emoji(line)
    total_width = 0
    
    for part_type, content in parts:
        if part_type == 'text':
            bbox = draw.textbbox((0, 0), content, font=font_text)
        else:
            bbox = draw.textbbox((0, 0), content, font=font_emoji)
        total_width += (bbox[2] - bbox[0])
    
    start_x = template['info_pos'][0] - total_width // 2
    
    draw_mixed_text(
        draw,
        line,
        start_x,
        y_text,
        font_text,
        font_emoji,
        template.get('info_color', 'black')
    )
    
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

# ========================
# Overlay va rasmni birlashtirish
# ========================
img = Image.alpha_composite(img, overlay)

# ========================
# Saqlash
# ========================
output_dir = "out"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"final_{chat_id}.png")

if img_format == 'JPEG':
    img = img.convert('RGB')

img.save(output_path, format=img_format if img_format else 'PNG')
print(f"✅ Rasm saqlandi: {output_path}")
