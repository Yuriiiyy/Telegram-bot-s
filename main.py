import telebot
from telebot import types
import re
import html

# 📦 Імпортуємо функцію відправки з нашого сусіднього файлу order_bot.py
from order_bot import send_order_to_admin

# 🆔 Твій точний Telegram ID
ADMIN_CHAT_ID = 0

# 🔑 ТОКЕН ОСНОВНОГО БОТА (для покупців)
TOKEN = 'ВСТАВТЕ_ТОКЕН_ОСНОВНОГО_БОТА_СЮДИ'
bot = telebot.TeleBot(TOKEN)

# 👕 Стартовий каталог товарів
PRODUCTS = {
    "zip_hoodie": {
        "name": "Зипка Nike Vintage", 
        "price": "1450 грн", 
        "sizes": ["S", "M", "L", "XL"],
        "desc": "Оверсайз крій, щільна тканина, вишитий логотип."
    },
    "text_sweatshirt": {
        "name": "Світшот Champion", 
        "price": "1200 грн", 
        "sizes": ["M", "L", "XL"],
        "desc": "Класичний світшот, м'який фліс, ідеальний на кожен день."
    },
    "shorts": {
        "name": "Шорти Jordan Diamond", 
        "price": "850 грн", 
        "sizes": ["S", "M", "L"],
        "desc": "Легкі спортивні шорти, брендований принт."
    }
}

user_orders = {}
admin_adding_product = {}

# --- ГОЛОВНЕ МЕНЮ (/start) ---
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("📦 Каталог товарів")
    item2 = types.KeyboardButton("ℹ️ Про магазин")
    markup.add(item1, item2)
    
    if message.chat.id == ADMIN_CHAT_ID:
        item_admin = types.KeyboardButton("➕ Додати товар")
        markup.add(item_admin)
    
    bot.send_message(
        message.chat.id,
        f"Привіт, {html.escape(message.from_user.first_name)}! 👋\nВітаємо у нашому маркетплейсі одягу. Обирай розділ у меню нижче:",
        reply_markup=markup
    )

# --- ОБРОБКА КНОПОК НИЖНЬОГО МЕНЮ ---
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "📦 Каталог товарів":
        if not PRODUCTS:
            bot.send_message(message.chat.id, "📭 Каталог наразі порожній.")
            return
            
        markup = types.InlineKeyboardMarkup(row_width=1)
        for key, prod in PRODUCTS.items():
            markup.add(types.InlineKeyboardButton(
                text=f"{prod['name']} — {prod['price']}", 
                callback_data=f"prod:{key}"
            ))
        bot.send_message(message.chat.id, "👕 Доступні товари в наявності:", reply_markup=markup)
        
    elif message.text == "ℹ️ Про магазин":
        bot.send_message(message.chat.id, "🏪 Швидка доставка Новою Поштою по всій Україні.\nТільки оригінальний стаф!")

    elif message.text == "➕ Додати товар":
        if message.chat.id != ADMIN_CHAT_ID:
            bot.send_message(message.chat.id, "❌ У вас немає доступу до цієї команди.")
            return
            
        bot.send_message(message.chat.id, "📝 <b>[Адмін-панель]</b> Введіть НАЗВУ товару:", parse_mode="HTML")
        bot.register_next_step_handler(message, admin_get_name)

# --- АДМІН-ПАНЕЛЬ: ДОДАВАННЯ ТОВАРУ ---
def admin_get_name(message):
    if message.text and message.text.startswith('/'):
        start_command(message)
        return
    if not message.text:
        bot.send_message(message.chat.id, "❌ Назва має бути текстовою. Введіть знову:")
        bot.register_next_step_handler(message, admin_get_name)
        return

    admin_adding_product[message.chat.id] = {"name": message.text.strip()}
    bot.send_message(message.chat.id, "💰 Введіть ЦІНУ товару (наприклад: 1500 грн):")
    bot.register_next_step_handler(message, admin_get_price)

def admin_get_price(message):
    if message.text and message.text.startswith('/'):
        start_command(message)
        return
    if not message.text:
        bot.send_message(message.chat.id, "❌ Введіть ціну знову:")
        bot.register_next_step_handler(message, admin_get_price)
        return

    admin_adding_product[message.chat.id]["price"] = message.text.strip()
    bot.send_message(message.chat.id, "📏 Введіть РОЗМІРИ через кому (наприклад: S, M, L):")
    bot.register_next_step_handler(message, admin_get_sizes)

def admin_get_sizes(message):
    if message.text and message.text.startswith('/'):
        start_command(message)
        return
    if not message.text:
        bot.send_message(message.chat.id, "❌ Введіть розміри:")
        bot.register_next_step_handler(message, admin_get_sizes)
        return

    raw_sizes = message.text.split(",")
    sizes_list = [size.strip().upper() for size in raw_sizes if size.strip()]
    
    if not sizes_list:
        bot.send_message(message.chat.id, "❌ Неправильний формат. Введіть розміри через кому знову:")
        bot.register_next_step_handler(message, admin_get_sizes)
        return

    admin_adding_product[message.chat.id]["sizes"] = sizes_list
    bot.send_message(message.chat.id, "📝 Введіть ОПИС товару:")
    bot.register_next_step_handler(message, admin_get_desc)

def admin_get_desc(message):
    if message.text and message.text.startswith('/'):
        start_command(message)
        return
    if not message.text:
        bot.send_message(message.chat.id, "❌ Введіть опис знову:")
        bot.register_next_step_handler(message, admin_get_desc)
        return

    admin_adding_product[message.chat.id]["desc"] = message.text.strip()
    
    prod_data = admin_adding_product[message.chat.id]
    slug = f"custom_{int(message.date)}"
    
    PRODUCTS[slug] = {
        "name": prod_data["name"],
        "price": prod_data["price"],
        "sizes": prod_data["sizes"],
        "desc": prod_data["desc"]
    }
    
    del admin_adding_product[message.chat.id]
    bot.send_message(message.chat.id, f"✅ <b>Товар успішно додано!</b> Назва: {html.escape(prod_data['name'])}", parse_mode="HTML")

# --- ІНЛАЙН-КНОПКИ (КАТАЛОГ ТА ВИБІР РОЗМІРУ) ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("prod:"):
        prod_key = call.data.split(":")[1]
        if prod_key not in PRODUCTS:
            bot.answer_callback_query(call.id, "❌ Цього товару немає в базі.")
            return
            
        prod = PRODUCTS[prod_key]
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = [types.InlineKeyboardButton(text=f"Розмір {s}", callback_data=f"size:{prod_key}:{s}") for s in prod['sizes']]
        markup.add(*buttons)
        markup.add(types.InlineKeyboardButton(text="⬅️ Назад в каталог", callback_data="back_to_catalog"))
        
        caption = f"🔥 <b>{html.escape(prod['name'])}</b>\n💰 Ціна: {html.escape(prod['price'])}\n\n📝 Опис: {html.escape(prod['desc'])}\n\nОбери свій розмір:"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=caption, reply_markup=markup, parse_mode="HTML")

    elif call.data.startswith("size:"):
        _, prod_key, size = call.data.split(":")
        if prod_key not in PRODUCTS:
            bot.answer_callback_query(call.id, "❌ Помилка сесії.")
            return
            
        user_orders[call.message.chat.id] = {
            "prod_name": PRODUCTS[prod_key]["name"],
            "price": PRODUCTS[prod_key]["price"],
            "size": size
        }
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"👌 Обрано розмір: <b>{html.escape(size)}</b>.\n\nПочинаємо оформлення. Введіть ваше Ім'я та Прізвище (тільки літери):", parse_mode="HTML")
        bot.register_next_step_handler(call.message, get_user_name)
        
    elif call.data == "back_to_catalog":
        # Штучно викликаємо перехід до каталогу
        fake_msg = types.Message(message_id=0, from_user=call.from_user, date=0, chat=call.message.chat, content_type='text', text="📦 Каталог товарів", json_string="")
        handle_text(fake_msg)

# --- КЛІЄНТСЬКИЙ ХІД: ОФОРМЛЕННЯ + ВАЛІДАЦІЯ ДАНИХ ---

# Крок 1: Валідація ПІБ
def get_user_name(message):
    name = message.text.strip() if message.text else ""
    if name.startswith('/'):
        start_command(message)
        return

    # Перевірка: тільки літери, пробіли, апостроф та довжина не менше 4 символів
    if not re.match(r"^[a-zA-Zа-яА-ЯёЁіІїЇєЄґҐ'\s]+$", name) or len(name) < 4:
        msg = bot.send_message(message.chat.id, "❌ Недійсне ім'я! Будь ласка, введіть Прізвище та Ім'я літерами:")
        bot.register_next_step_handler(msg, get_user_name)
        return
        
    user_orders[message.chat.id]["name"] = name
    bot.send_message(message.chat.id, "📱 Тепер введіть ваш номер телефону для зв'язку (10 цифр, наприклад: 0931234567):")
    bot.register_next_step_handler(message, get_user_phone)

# Крок 2: Валідація телефону (ЯК НА СКРІНІ)
def get_user_phone(message):
    phone = message.text.strip() if message.text else ""
    if phone.startswith('/'):
        start_command(message)
        return

    # Залишаємо лише цифри для перевірки
    clean_phone = re.sub(r"[\s\-()]", "", phone)
    
    # Регулярка на 10 цифр, що починаються з нуля
    if not re.match(r"^0\d{9}$", clean_phone):
        msg = bot.send_message(message.chat.id, "❌ Введіть правильний номер мобільного (10 цифр, починаючи з 0):")
        bot.register_next_step_handler(msg, get_user_phone)
        return
        
    user_orders[message.chat.id]["phone"] = clean_phone
    bot.send_message(message.chat.id, "📍 Вкажіть місто та номер відділення Нової Пошти (наприклад: Самбір, відділення №1):")
    bot.register_next_step_handler(message, get_user_shipping)

# Крок 3: Валідація адреси та відправка
def get_user_shipping(message):
    shipping = message.text.strip() if message.text else ""
    if shipping.startswith('/'):
        start_command(message)
        return

    if len(shipping) < 4:
        msg = bot.send_message(message.chat.id, "❌ Вкажіть коректну адресу доставки та номер відділення:")
        bot.register_next_step_handler(msg, get_user_shipping)
        return
        
    chat_id = message.chat.id
    user_orders[chat_id]["shipping"] = shipping
    
    order = user_orders[chat_id]
    order["chat_id"] = chat_id # прикріплюємо ID клієнта

    # 1. Надсилаємо гарний екранований чек клієнту
    invoice = (
        "🎉 <b>Замовлення успішно сформовано!</b>\n\n"
        f"👕 Товар: <b>{html.escape(order['prod_name'])}</b>\n"
        f"📏 Розмір: <b>{html.escape(order['size'])}</b>\n"
        f"💰 Ціна: <b>{html.escape(order['price'])}</b>\n\n"
        "Менеджер зв'яжеться з вами найближчим часом! 🚀"
    )
    bot.send_message(chat_id, invoice, parse_mode="HTML")
    
    # 🚀 2. Передаємо пак даних нашому другому боту-сповіщувачу
    send_order_to_admin(order)

    # Очищуємо кошик сесії
    if chat_id in user_orders:
        del user_orders[chat_id]

print("🚀 Головний бот магазину повністю запущено й готово до тестів!")
bot.polling(none_stop=True)