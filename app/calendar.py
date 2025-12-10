from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os

def create_newyear_image_styled(
    input_image,
    output_image,
    nm,
    font_path="app/fonts/arial/ARIALBD.TTF"
):
    """
    Rasm ustiga Yangi yil tabrigi va raqam qo'yish funksiyasi
    Shadow va outline style bilan.
    
    input_image: kiruvchi rasm (path)
    output_image: saqlanadigan rasm (path)
    nm: qancha kun qolgani (raqam)
    font_path: .ttf font fayl
    """
    img = Image.open(input_image)
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Font mavjudligini tekshirish
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font fayl topilmadi: {font_path}")
    
    # Matnlar va ularning parametrlarini belgilash
    texts = [
        ("YANGI YILGA", 700, 70, "red"),
        ("KUN QOLDI", 1050, 70, "red")
    ]
    
    # Shadow va outline chizish funksiyasi
    def draw_text_with_style(draw, position, text, font, fill, outline_color="black", shadow_offset=(2,2)):
        x, y = position
        
        # Shadow
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill="black")
        
        # Outline
        for dx in [-2, 0, 2]:
            for dy in [-2, 0, 2]:
                if dx != 0 or dy != 0:
                    draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
        
        # Asl matn
        draw.text((x, y), text, font=font, fill=fill)
    
    # Matnlarni chizish
    for text, pos_y, font_size, color in texts:
        font = ImageFont.truetype(font_path, font_size)  # font_path ishlatildi
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        position = ((width - text_width) // 2, pos_y)
        draw_text_with_style(draw, position, text, font, fill=color)
    
    # Raqamni chizish (katta font bilan)
    font_number = ImageFont.truetype(font_path, 200)  # font_path ishlatildi
    bbox = draw.textbbox((0, 0), str(nm), font=font_number)
    number_width = bbox[2] - bbox[0]
    number_position = ((width - number_width) // 2, 800)
    draw_text_with_style(draw, number_position, str(nm), font_number, fill="red")
    
    img.save(output_image)
    return output_image