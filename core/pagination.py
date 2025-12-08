ITEMS_PER_PAGE = 5

def get_templates_page(page):
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    return templates[start:end]

def templates_markup(page=0):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    page_items = get_templates_page(page)
    
    for t in page_items:
        markup.add(types.InlineKeyboardButton(
            text=f"{t['title']}",
            callback_data=f"select_{t['id']}"
        ))
    
    nav_row = []
    if page > 0:
        nav_row.append(types.InlineKeyboardButton("⬅️ Oldingi", callback_data=f"page_{page-1}"))
    if (page + 1) * ITEMS_PER_PAGE < len(templates):
        nav_row.append(types.InlineKeyboardButton("Keyingi ➡️", callback_data=f"page_{page+1}"))
    
    if nav_row:
        markup.row(*nav_row)

    return markup
