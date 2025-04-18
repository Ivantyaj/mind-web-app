from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import get_connection, is_premium_user

async def get_premium_keyboard():
    """Создает клавиатуру с кнопкой для получения информации о премиум"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text="🌟 Получить Premium",
        callback_data="premium_info"
    ))
    return keyboard

async def handle_premium_callback(callback: types.CallbackQuery):
    """Обрабатывает нажатия на премиум-кнопки"""
    if callback.data == "premium_info":
        message_text = (
            "🌟 Premium подписка\n\n"
            "Стоимость: 299 руб/месяц\n\n"
            "Преимущества:\n"
            "✅ Доступ ко всем медитациям в приложении\n"
            "✅ Доступ ко всем психологическим тестам\n"
            "✅ Расширенная аналитика результатов\n"
            "✅ Персональные рекомендации\n"
            "✅ Приоритетная поддержка\n\n"
            "Для оформления подписки:\n"
            "1️⃣ Переведите 299 руб. по номеру карты:\n"
            "1234 5678 9012 3456\n\n"
            "2️⃣ Отправьте скриншот оплаты администратору:\n"
            "@ivantyaj\n\n"
            "После проверки оплаты вам будет активирован премиум-доступ\n"
            "и вы сможете использовать все функции в веб-приложении! 🎉"
        )
        await callback.message.answer(message_text)
    await callback.answer()

def check_premium_status(telegram_id: int) -> dict:
    """Проверяет премиум статус пользователя для веб-приложения"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT username, is_premium 
            FROM users 
            WHERE telegram_id = ?
        """, (telegram_id,))
        
        result = cursor.fetchone()
        if result:
            username, is_premium = result
            return {
                "success": True,
                "is_premium": bool(is_premium),
                "username": username
            }
        return {
            "success": False,
            "error": "User not found"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        conn.close() 