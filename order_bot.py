import telebot
import html

# 🆔 Твій точний Telegram ID
ADMIN_CHAT_ID = 0 

# 🔑 ТОКЕН НОВОГО БОТА (створи його в @BotFather і встав сюди замість тексту нижче)
ORDERS_BOT_TOKEN = 'ВСТАВТЕ_ТОКЕН_ОСНОВНОГО_БОТА_СЮДИ'
order_bot = telebot.TeleBot(ORDERS_BOT_TOKEN)

def send_order_to_admin(order_data):
    """Функція для надсилання замовлення в адмінку з клікабельним ID"""
    try:
        chat_id = order_data['chat_id']
        
        # 🛡️ Захист від зламу HTML-розмітки (екрануємо всі символи)
        safe_prod = html.escape(order_data['prod_name'])
        safe_size = html.escape(order_data['size'])
        safe_price = html.escape(order_data['price'])
        safe_name = html.escape(order_data['name'])
        safe_phone = html.escape(order_data['phone'])
        safe_ship = html.escape(order_data['shipping'])

        # Шаблон повідомлення з клікабельним посиланням на користувача tg://user?id=
        admin_invoice = (
            "🚨 <b>НОВЕ ЗАМОВЛЕННЯ В МАГАЗИНІ!</b> 🚨\n\n"
            f"🛍️ Товар: <b>{safe_prod}</b>\n"
            f"📏 Розмір: <b>{safe_size}</b>\n"
            f"💵 Сума: <b>{safe_price}</b>\n"
            "-------------------------\n"
            f"👤 Клієнт: <a href='tg://user?id={chat_id}'>{safe_name}</a>\n"
            f"📞 Тел: <code>{safe_phone}</code>\n"
            f"📍 Куди: {safe_ship}\n"
            f"💬 Чат-ID юзера: <code>{chat_id}</code>\n\n"
            f"🔗 <a href='tg://user?id={chat_id}'>👉 Натисніть сюди, щоб написати клієнту</a>"
        )
        
        order_bot.send_message(ADMIN_CHAT_ID, admin_invoice, parse_mode="HTML")
        print("💡 [Order Bot] Замовлення успішно надіслано в адмінку!")
    except Exception as e:
        print(f"❌ [Order Bot] Помилка відправки: {e}")