import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from dotenv import load_dotenv
import os
from database import init_db, get_connection, is_admin, add_admin, add_premium_user, remove_premium_user, get_premium_users, is_premium_user
from premium_handlers import get_premium_keyboard, handle_premium_callback
import json
from aiogram import F

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
TOKEN = "7046522560:AAHXlYcX5UUarUQfbWwQsAzMog0xkNP56XA"
ADMIN_ID = 729190790  # Ваш Telegram ID
ADMIN_USERNAME = "ivantyaj"  # Ваш username в Telegram

bot = Bot(token=TOKEN)

# Создание клавиатуры главного меню
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧘‍♂️ Медитации", web_app=WebAppInfo(url="https://your-meditation-app.com"))],
            [KeyboardButton(text="🎧 Бесплатные медитации")],
            [KeyboardButton(text="🌟 21-дневный курс")],
            [KeyboardButton(text="🏆 Мои достижения")],
            [KeyboardButton(text="📊 Мое состояние")],
            [KeyboardButton(text="📝 Психологические тесты")],
        ],
        resize_keyboard=True
    )
    return keyboard

# Создание клавиатуры для тестов
def get_tests_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="📊 Пройти тест"))
    keyboard.add(KeyboardButton(text="📋 Мои результаты"))
    keyboard.add(KeyboardButton(text="🔙 Назад"))
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True)

# Создание клавиатуры для администраторов
def get_admin_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Результаты тестов")],
            [KeyboardButton(text="👥 Статистика пользователей")],
            [KeyboardButton(text="⭐ Премиум пользователи")],
            [KeyboardButton(text="📋 Детальные результаты")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

# Создание клавиатуры для управления премиум пользователями
def get_premium_management_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить премиум")],
            [KeyboardButton(text="➖ Удалить премиум")],
            [KeyboardButton(text="📋 Список премиум")],
            [KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True
    )
    return keyboard

def get_test_question_keyboard(question_number: int, total_questions: int):
    """Создание клавиатуры для вопроса теста с прогрессом"""
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(
        text="❌ Прервать тест",
        callback_data="cancel_test"
    ))
    keyboard.adjust(1)
    return keyboard.as_markup()

# Состояния тестов для пользователей
user_test_states = {}

# Состояния управления премиум-пользователями
premium_management_states = {}

async def start_bot():
    # Инициализация базы данных
    init_db()
    
    # Добавление администратора
    add_admin(ADMIN_ID, ADMIN_USERNAME)
    
    # Создание диспетчера
    dp = Dispatcher()
    
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Проверяем существование пользователя
        cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (message.from_user.id,))
        user = cursor.fetchone()
        
        if not user:
            # Создаем нового пользователя
            cursor.execute(
                "INSERT INTO users (telegram_id, username) VALUES (?, ?)",
                (message.from_user.id, message.from_user.username)
            )
            conn.commit()
        
        # Проверяем, является ли пользователь администратором
        if is_admin(message.from_user.id):
            await message.answer(
                "Добро пожаловать в панель администратора!",
                reply_markup=get_admin_keyboard()
            )
        else:
            await message.answer(
                "Добро пожаловать в бот для mindfulness медитаций! 🧘‍♂️\n\n"
                "Здесь вы найдете медитации, практики и психологические тесты для улучшения вашего ментального здоровья.\n"
                "Выберите интересующий вас раздел:",
                reply_markup=get_main_keyboard()
            )
        
        conn.close()

    @dp.message(Command("admin"))
    async def cmd_admin(message: types.Message):
        if is_admin(message.from_user.id):
            await message.answer(
                "Выберите действие:",
                reply_markup=get_admin_keyboard()
            )
        else:
            await message.answer("У вас нет прав администратора.")

    @dp.message(lambda message: message.text == "📊 Результаты тестов")
    async def show_test_statistics(message: types.Message):
        if not is_admin(message.from_user.id):
            await message.answer("У вас нет прав администратора.")
            return
            
        conn = get_connection()
        cursor = conn.cursor()
        
        # Получаем статистику по тестам
        cursor.execute("""
            SELECT 
                t.title,
                COUNT(DISTINCT r.user_id) as users_count,
                AVG(r.total_score) as avg_score,
                MIN(r.total_score) as min_score,
                MAX(r.total_score) as max_score
            FROM user_test_results r
            JOIN psychological_tests t ON r.test_id = t.id
            GROUP BY t.id
        """)
        test_stats = cursor.fetchall()
        
        if not test_stats:
            await message.answer("Пока нет результатов тестов.")
            return
        
        response = "📊 Статистика по тестам:\n\n"
        for title, users_count, avg_score, min_score, max_score in test_stats:
            response += f"📝 {title}\n"
            response += f"👥 Прошло пользователей: {users_count}\n"
            response += f"📈 Средний балл: {avg_score:.1f}\n"
            response += f"📉 Минимальный балл: {min_score}\n"
            response += f"📈 Максимальный балл: {max_score}\n\n"
        
        await message.answer(response)
        
        # Получаем детальные результаты по каждому пользователю
        cursor.execute("""
            SELECT 
                u.username,
                t.title,
                r.total_score,
                r.completed_at
            FROM user_test_results r
            JOIN users u ON r.user_id = u.telegram_id
            JOIN psychological_tests t ON r.test_id = t.id
            ORDER BY r.completed_at DESC
            LIMIT 10
        """)
        recent_results = cursor.fetchall()
        
        if recent_results:
            response = "📋 Последние результаты:\n\n"
            for username, title, score, completed_at in recent_results:
                response += f"👤 {username}\n"
                response += f"📝 {title}\n"
                response += f"📊 Баллы: {score}\n"
                response += f"📅 Дата: {completed_at}\n\n"
            
            await message.answer(response)
        
        conn.close()

    @dp.message(lambda message: message.text == "👥 Статистика пользователей")
    async def show_user_statistics(message: types.Message):
        if not is_admin(message.from_user.id):
            await message.answer("У вас нет прав администратора.")
            return
            
        conn = get_connection()
        cursor = conn.cursor()
        
        # Получаем общую статистику пользователей
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                COUNT(CASE WHEN is_premium = 1 THEN 1 END) as premium_users,
                COUNT(DISTINCT r.user_id) as users_with_tests
            FROM users u
            LEFT JOIN user_test_results r ON u.telegram_id = r.user_id
        """)
        stats = cursor.fetchone()
        
        response = "👥 Статистика пользователей:\n\n"
        response += f"Всего пользователей: {stats[0]}\n"
        response += f"Премиум пользователей: {stats[1]}\n"
        response += f"Пользователей, прошедших тесты: {stats[2]}\n\n"
        
        # Получаем список последних активных пользователей
        cursor.execute("""
            SELECT 
                u.username,
                COUNT(r.id) as tests_count,
                MAX(r.completed_at) as last_test_date
            FROM users u
            LEFT JOIN user_test_results r ON u.telegram_id = r.user_id
            GROUP BY u.telegram_id
            ORDER BY last_test_date DESC NULLS LAST
            LIMIT 10
        """)
        recent_users = cursor.fetchall()
        
        response += "📋 Последние активные пользователи:\n\n"
        for username, tests_count, last_test_date in recent_users:
            response += f"👤 {username}\n"
            response += f"📊 Пройдено тестов: {tests_count}\n"
            if last_test_date:
                response += f"📅 Последний тест: {last_test_date}\n\n"
            else:
                response += "📅 Тесты не пройдены\n\n"
        
        await message.answer(response)
        conn.close()

    @dp.message(lambda message: message.text == "🔙 Назад")
    async def back_to_main_menu(message: types.Message):
        if is_admin(message.from_user.id):
            await message.answer(
                "Выберите действие:",
                reply_markup=get_admin_keyboard()
            )
        else:
            await message.answer(
                "Выберите раздел:",
                reply_markup=get_main_keyboard()
            )

    @dp.message(lambda message: message.text == "📝 Психологические тесты")
    async def show_tests_menu(message: types.Message):
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📊 Пройти тест")],
                [KeyboardButton(text="📋 Мои результаты")],
                [KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True
        )
        await message.answer(
            "Выберите действие:",
            reply_markup=keyboard
        )

    @dp.message(lambda message: message.text == "⭐ Премиум пользователи")
    async def show_premium_management(message: types.Message):
        if not is_admin(message.from_user.id):
            await message.answer("У вас нет прав администратора.")
            return
            
        await message.answer(
            "Управление премиум пользователями:",
            reply_markup=get_premium_management_keyboard()
        )

    @dp.message(lambda message: message.text == "➕ Добавить премиум")
    async def add_premium(message: types.Message):
        if not is_admin(message.from_user.id):
            await message.answer("У вас нет прав администратора.")
            return
            
        await message.answer(
            "Отправьте username пользователя, которого хотите добавить в премиум.\n"
            "Username должен начинаться с @, например: @username"
        )
        # Устанавливаем состояние ожидания username пользователя
        premium_management_states[message.from_user.id] = "waiting_premium_username"

    @dp.message(lambda message: message.text == "➖ Удалить премиум")
    async def remove_premium(message: types.Message):
        if not is_admin(message.from_user.id):
            await message.answer("У вас нет прав администратора.")
            return
            
        await message.answer(
            "Отправьте username пользователя, которого хотите удалить из премиум.\n"
            "Username должен начинаться с @, например: @username"
        )
        # Устанавливаем состояние ожидания username пользователя
        premium_management_states[message.from_user.id] = "waiting_premium_remove_username"

    @dp.message(lambda message: message.text == "📋 Список премиум")
    async def show_premium_list(message: types.Message):
        if not is_admin(message.from_user.id):
            await message.answer("У вас нет прав администратора.")
            return
            
        premium_users = get_premium_users()
        if not premium_users:
            await message.answer("Нет премиум пользователей.")
            return
            
        response = "📋 Список премиум пользователей:\n\n"
        for username in premium_users:
            response += f"👤 @{username[0]}\n"
        
        await message.answer(response)

    @dp.message(lambda message: message.from_user.id in premium_management_states and 
                premium_management_states[message.from_user.id] in ["waiting_premium_username", "waiting_premium_remove_username"])
    async def process_premium_action(message: types.Message):
        if not is_admin(message.from_user.id):
            await message.answer("У вас нет прав администратора.")
            return
            
        try:
            username = message.text.strip()
            if not username.startswith('@'):
                await message.answer("Username должен начинаться с @, например: @username")
                return
                
            # Убираем @ из начала username
            username = username[1:]
            
            action = premium_management_states[message.from_user.id]
            
            if action == "waiting_premium_username":
                if add_premium_user(username):
                    await message.answer(f"Пользователь @{username} успешно добавлен в премиум.")
                else:
                    await message.answer("Ошибка при добавлении пользователя в премиум.")
            else:
                if remove_premium_user(username):
                    await message.answer(f"Пользователь @{username} успешно удален из премиум.")
                else:
                    await message.answer("Ошибка при удалении пользователя из премиум.")
            
            # Очищаем состояние
            del premium_management_states[message.from_user.id]
            
        except Exception as e:
            await message.answer("Произошла ошибка. Пожалуйста, проверьте правильность username и попробуйте снова.")

    @dp.message(lambda message: message.text == "📊 Пройти тест")
    async def show_available_tests(message: types.Message):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, description, is_free FROM psychological_tests")
        tests = cursor.fetchall()
        
        if not tests:
            await message.answer("На данный момент нет доступных тестов.")
            return
        
        keyboard = InlineKeyboardBuilder()
        for test_id, title, description, is_free in tests:
            if is_free or is_premium_user(message.from_user.username):
                keyboard.add(types.InlineKeyboardButton(
                    text=title,
                    callback_data=f"start_test_{test_id}"
                ))
            else:
                keyboard.add(types.InlineKeyboardButton(
                    text=f"{title} 🔒",
                    callback_data=f"premium_test_{test_id}"
                ))
        keyboard.adjust(1)
        
        await message.answer(
            "Выберите тест для прохождения:",
            reply_markup=keyboard.as_markup()
        )
        conn.close()

    @dp.callback_query(lambda c: c.data.startswith("premium_test_"))
    async def handle_premium_test(callback: types.CallbackQuery):
        test_id = int(callback.data.split("_")[2])
        username = callback.from_user.username
        
        if not username:
            await callback.message.answer(
                "Для доступа к платным тестам необходимо установить username в настройках Telegram."
            )
            return
            
        if is_premium_user(username):
            # Если пользователь премиум, начинаем тест
            new_callback = types.CallbackQuery(
                id=callback.id,
                from_user=callback.from_user,
                message=callback.message,
                chat_instance=callback.chat_instance,
                data=f"start_test_{test_id}"
            )
            await start_test(new_callback)
        else:
            # Если пользователь не премиум, показываем информацию о получении премиум-доступа
            message_text = (
                "🔒 Этот тест доступен только для Premium пользователей\n\n"
                "Стоимость Premium: 299 руб/месяц\n\n"
                "Преимущества Premium:\n"
                "✅ Доступ ко всем психологическим тестам\n"
                "✅ Расширенная аналитика результатов\n"
                "✅ Персональные рекомендации\n"
                "✅ Приоритетная поддержка\n\n"
                "Для оформления подписки:\n"
                "1️⃣ Переведите 299 руб. по номеру карты:\n"
                "1234 5678 9012 3456\n\n"
                "2️⃣ Отправьте скриншот оплаты администратору:\n"
                "@ivantyaj\n\n"
                "После проверки оплаты вам будет активирован премиум-доступ!"
            )
            await callback.message.answer(message_text)
            
        await callback.answer()

    @dp.callback_query(lambda c: c.data.startswith("start_test_"))
    async def start_test(callback: types.CallbackQuery):
        test_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        username = callback.from_user.username or f"user_{user_id}"
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Проверяем существование пользователя и создаем, если его нет
            cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO users (telegram_id, username, is_premium)
                    VALUES (?, ?, ?)
                """, (user_id, username, 0))
                conn.commit()
            
            # Получаем информацию о тесте
            cursor.execute("""
                SELECT title, questions_count 
                FROM psychological_tests 
                WHERE id = ?
            """, (test_id,))
            test_info = cursor.fetchone()
            
            if not test_info:
                await callback.message.answer("Ошибка: тест не найден.")
                return
            
            title, total_questions = test_info
            
            # Получаем первый вопрос теста
            cursor.execute("""
                SELECT id, question_text 
                FROM test_questions 
                WHERE test_id = ? 
                ORDER BY question_number 
                LIMIT 1
            """, (test_id,))
            question = cursor.fetchone()
            
            if not question:
                await callback.message.answer("Ошибка: вопросы теста не найдены.")
                return
            
            # Получаем варианты ответов
            cursor.execute("""
                SELECT id, answer_text 
                FROM test_answers 
                WHERE question_id = ? 
                ORDER BY score
            """, (question[0],))
            answers = cursor.fetchall()
            
            # Создаем клавиатуру с вариантами ответов
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="❌ Прервать тест")]
                ],
                resize_keyboard=True
            )
            
            # Создаем inline клавиатуру с вариантами ответов
            inline_keyboard = InlineKeyboardBuilder()
            
            # Формируем сообщение с вопросом и вариантами ответов
            message_text = f"📝 Тест: {title}\n\n"
            message_text += f"Вопрос 1 из {total_questions}:\n{question[1]}\n\n"
            message_text += "Варианты ответа:\n"
            
            for i, (answer_id, answer_text) in enumerate(answers, 1):
                message_text += f"{i}. {answer_text}\n"
                inline_keyboard.add(types.InlineKeyboardButton(
                    text=str(i),
                    callback_data=f"answer_{test_id}_{question[0]}_{answer_id}"
                ))
            
            inline_keyboard.adjust(4)  # Размещаем кнопки по 4 в ряд
            
            # Сохраняем состояние теста для пользователя
            user_test_states[user_id] = {
                "test_id": test_id,
                "current_question": 1,
                "total_questions": total_questions,
                "total_score": 0,
                "test_title": title
            }
            
            await callback.message.answer(
                message_text,
                reply_markup=keyboard
            )
            
            # Отправляем кнопки с номерами вариантов ответа
            await callback.message.answer(
                "Выберите номер ответа:",
                reply_markup=inline_keyboard.as_markup()
            )
        except Exception as e:
            print(f"Ошибка при начале теста: {e}")
            await callback.message.answer("Произошла ошибка при начале теста. Пожалуйста, попробуйте позже.")
        finally:
            conn.close()

    @dp.message(lambda message: message.text == "❌ Прервать тест")
    async def cancel_test(message: types.Message):
        user_id = message.from_user.id
        
        if user_id not in user_test_states:
            await message.answer("Нет активного теста для прерывания.")
            return
        
        # Удаляем состояние теста
        del user_test_states[user_id]
        
        # Показываем меню тестов
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📊 Пройти тест")],
                [KeyboardButton(text="📋 Мои результаты")],
                [KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True
        )
        
        await message.answer(
            "Тест прерван. Вы можете начать новый тест в любое время.",
            reply_markup=keyboard
        )

    @dp.callback_query(lambda c: c.data.startswith("answer_"))
    async def process_answer(callback: types.CallbackQuery):
        _, test_id, question_id, answer_id = callback.data.split("_")
        test_id = int(test_id)
        question_id = int(question_id)
        answer_id = int(answer_id)
        user_id = callback.from_user.id
        username = callback.from_user.username or f"user_{user_id}"
        
        if user_id not in user_test_states:
            await callback.message.answer("Ошибка: состояние теста не найдено.")
            return
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Проверяем существование пользователя и создаем, если его нет
            cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (user_id,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO users (telegram_id, username, is_premium)
                    VALUES (?, ?, ?)
                """, (user_id, username, 0))
                conn.commit()
            
            # Получаем балл за ответ
            cursor.execute("SELECT score FROM test_answers WHERE id = ?", (answer_id,))
            score = cursor.fetchone()[0]
            
            # Сохраняем ответ пользователя
            cursor.execute("""
                INSERT INTO user_test_answers (user_id, test_id, question_id, answer_id, score)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, test_id, question_id, answer_id, score))
            conn.commit()
            
            # Обновляем общий балл
            user_test_states[user_id]["total_score"] += score
            
            # Получаем следующий вопрос
            cursor.execute("""
                SELECT id, question_text 
                FROM test_questions 
                WHERE test_id = ? AND question_number > ? 
                ORDER BY question_number 
                LIMIT 1
            """, (test_id, user_test_states[user_id]["current_question"]))
            next_question = cursor.fetchone()
            
            if next_question:
                # Получаем варианты ответов для следующего вопроса
                cursor.execute("""
                    SELECT id, answer_text 
                    FROM test_answers 
                    WHERE question_id = ? 
                    ORDER BY score
                """, (next_question[0],))
                answers = cursor.fetchall()
                
                # Создаем inline клавиатуру с вариантами ответов
                inline_keyboard = InlineKeyboardBuilder()
                
                # Формируем сообщение с вопросом и вариантами ответов
                message_text = f"📝 Тест: {user_test_states[user_id]['test_title']}\n\n"
                message_text += f"Вопрос {user_test_states[user_id]['current_question'] + 1} из {user_test_states[user_id]['total_questions']}:\n{next_question[1]}\n\n"
                message_text += "Варианты ответа:\n"
                
                for i, (answer_id, answer_text) in enumerate(answers, 1):
                    message_text += f"{i}. {answer_text}\n"
                    inline_keyboard.add(types.InlineKeyboardButton(
                        text=str(i),
                        callback_data=f"answer_{test_id}_{next_question[0]}_{answer_id}"
                    ))
                
                inline_keyboard.adjust(4)  # Размещаем кнопки по 4 в ряд
                
                # Обновляем состояние
                user_test_states[user_id]["current_question"] += 1
                
                # Отправляем новый вопрос с вариантами ответов
                await callback.message.answer(message_text)
                
                # Отправляем кнопки с номерами вариантов ответа
                await callback.message.answer(
                    "Выберите номер ответа:",
                    reply_markup=inline_keyboard.as_markup()
                )
            else:
                # Тест завершен
                total_score = user_test_states[user_id]["total_score"]
                test_title = user_test_states[user_id]["test_title"]
                
                # Получаем интерпретацию результата
                cursor.execute("""
                    SELECT interpretation 
                    FROM test_interpretations 
                    WHERE test_id = ? AND ? BETWEEN min_score AND max_score
                """, (test_id, total_score))
                interpretation = cursor.fetchone()[0]
                
                # Сохраняем общий результат теста
                cursor.execute("""
                    INSERT INTO user_test_results (user_id, test_id, total_score, completed_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (user_id, test_id, total_score))
                conn.commit()
                
                # Удаляем состояние теста
                del user_test_states[user_id]
                
                # Показываем меню тестов
                keyboard = ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="📊 Пройти тест")],
                        [KeyboardButton(text="📋 Мои результаты")],
                        [KeyboardButton(text="🔙 Назад")]
                    ],
                    resize_keyboard=True
                )
                
                await callback.message.answer(
                    f"📝 Тест: {test_title}\n\n"
                    f"Тест завершен!\n\n"
                    f"Ваш результат: {total_score} баллов\n"
                    f"Интерпретация: {interpretation}",
                    reply_markup=keyboard
                )
        except Exception as e:
            print(f"Ошибка при обработке ответа: {e}")
            await callback.message.answer("Произошла ошибка при обработке ответа. Пожалуйста, попробуйте пройти тест снова.")
        finally:
            conn.close()

    @dp.message(lambda message: message.text == "📋 Мои результаты")
    async def show_my_results(message: types.Message):
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                t.title,
                r.total_score,
                r.completed_at
            FROM user_test_results r
            JOIN psychological_tests t ON r.test_id = t.id
            WHERE r.user_id = ?
            ORDER BY r.completed_at DESC
        """, (message.from_user.id,))
        results = cursor.fetchall()
        
        if not results:
            await message.answer("У вас пока нет результатов тестов.")
            return
        
        response = "📋 Ваши результаты тестов:\n\n"
        for title, score, completed_at in results:
            response += f"📝 {title}\n"
            response += f"📊 Баллы: {score}\n"
            response += f"📅 Дата: {completed_at}\n\n"
        
        await message.answer(response)
        conn.close()

    @dp.message(lambda message: message.text == "📋 Детальные результаты")
    async def show_detailed_results(message: types.Message):
        if not is_admin(message.from_user.id):
            await message.answer("У вас нет прав администратора.")
            return
            
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Получаем список пользователей, которые проходили тесты
            cursor.execute("""
                SELECT DISTINCT u.telegram_id, u.username
                FROM users u
                JOIN user_test_results r ON u.telegram_id = r.user_id
                ORDER BY u.username
            """)
            users = cursor.fetchall()
            
            if not users:
                await message.answer("Нет пользователей, прошедших тесты.")
                return
                
            # Создаем inline клавиатуру с пользователями
            keyboard = InlineKeyboardBuilder()
            for user_id, username in users:
                keyboard.add(types.InlineKeyboardButton(
                    text=f"@{username}",
                    callback_data=f"user_{user_id}"
                ))
            keyboard.adjust(1)
            
            await message.answer(
                "Выберите пользователя для просмотра результатов:",
                reply_markup=keyboard.as_markup()
            )
        except Exception as e:
            print(f"Ошибка при получении списка пользователей: {e}")
            await message.answer("Произошла ошибка при получении списка пользователей.")
        finally:
            conn.close()

    @dp.callback_query(lambda c: c.data.startswith("user_"))
    async def show_user_tests(callback: types.CallbackQuery):
        if not is_admin(callback.from_user.id):
            await callback.message.answer("У вас нет прав администратора.")
            return
            
        user_id = int(callback.data.split("_")[1])
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Получаем username пользователя
            cursor.execute("SELECT username FROM users WHERE telegram_id = ?", (user_id,))
            username = cursor.fetchone()[0]
            
            # Получаем список тестов пользователя
            cursor.execute("""
                SELECT DISTINCT
                    t.id,
                    t.title,
                    r.completed_at,
                    r.id as result_id
                FROM user_test_results r
                JOIN psychological_tests t ON r.test_id = t.id
                WHERE r.user_id = ?
                ORDER BY r.completed_at DESC
            """, (user_id,))
            tests = cursor.fetchall()
            
            if not tests:
                await callback.message.answer(f"У пользователя @{username} нет результатов тестов.")
                return
                
            # Создаем inline клавиатуру с тестами
            keyboard = InlineKeyboardBuilder()
            for test_id, title, completed_at, result_id in tests:
                keyboard.add(types.InlineKeyboardButton(
                    text=f"{title} ({completed_at})",
                    callback_data=f"test_{user_id}_{test_id}_{result_id}"
                ))
            keyboard.adjust(1)
            
            # Добавляем кнопку "Назад к пользователям"
            keyboard.add(types.InlineKeyboardButton(
                text="🔙 Назад к пользователям",
                callback_data="back_to_users"
            ))
            
            await callback.message.answer(
                f"Выберите тест пользователя @{username} для просмотра ответов:",
                reply_markup=keyboard.as_markup()
            )
        except Exception as e:
            print(f"Ошибка при получении списка тестов: {e}")
            await callback.message.answer("Произошла ошибка при получении списка тестов.")
        finally:
            conn.close()

    @dp.callback_query(lambda c: c.data == "back_to_users")
    async def back_to_users(callback: types.CallbackQuery):
        if not is_admin(callback.from_user.id):
            await callback.message.answer("У вас нет прав администратора.")
            return
            
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Получаем список пользователей, которые проходили тесты
            cursor.execute("""
                SELECT DISTINCT u.telegram_id, u.username
                FROM users u
                JOIN user_test_results r ON u.telegram_id = r.user_id
                ORDER BY u.username
            """)
            users = cursor.fetchall()
            
            if not users:
                await callback.message.answer("Нет пользователей, прошедших тесты.")
                return
                
            # Создаем inline клавиатуру с пользователями
            keyboard = InlineKeyboardBuilder()
            for user_id, username in users:
                keyboard.add(types.InlineKeyboardButton(
                    text=f"@{username}",
                    callback_data=f"user_{user_id}"
                ))
            keyboard.adjust(1)
            
            await callback.message.answer(
                "Выберите пользователя для просмотра результатов:",
                reply_markup=keyboard.as_markup()
            )
        except Exception as e:
            print(f"Ошибка при получении списка пользователей: {e}")
            await callback.message.answer("Произошла ошибка при получении списка пользователей.")
        finally:
            conn.close()

    @dp.callback_query(lambda c: c.data.startswith("test_"))
    async def show_test_answers(callback: types.CallbackQuery):
        if not is_admin(callback.from_user.id):
            await callback.message.answer("У вас нет прав администратора.")
            return
            
        # Разбираем callback_data
        parts = callback.data.split("_")
        if len(parts) != 4:
            await callback.message.answer("Ошибка: неверный формат данных.")
            return
            
        user_id = int(parts[1])
        test_id = int(parts[2])
        result_id = int(parts[3])
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Получаем информацию о пользователе и тесте
            cursor.execute("SELECT username FROM users WHERE telegram_id = ?", (user_id,))
            user_result = cursor.fetchone()
            if not user_result:
                await callback.message.answer("Пользователь не найден.")
                return
            username = user_result[0]
            
            cursor.execute("SELECT title FROM psychological_tests WHERE id = ?", (test_id,))
            test_result = cursor.fetchone()
            if not test_result:
                await callback.message.answer("Тест не найден.")
                return
            test_title = test_result[0]
            
            # Получаем результат конкретной попытки теста
            cursor.execute("""
                SELECT total_score, completed_at
                FROM user_test_results
                WHERE id = ?
            """, (result_id,))
            result = cursor.fetchone()
            if not result:
                await callback.message.answer("Результаты теста не найдены.")
                return
            total_score, completed_at = result
            
            # Получаем все ответы пользователя для конкретной попытки
            cursor.execute("""
                SELECT 
                    q.question_text,
                    a.answer_text,
                    ua.score
                FROM user_test_answers ua
                JOIN test_questions q ON q.id = ua.question_id
                JOIN test_answers a ON a.id = ua.answer_id
                JOIN user_test_results r ON r.user_id = ua.user_id 
                    AND r.test_id = ua.test_id
                    AND r.completed_at = ?
                WHERE ua.user_id = ? 
                    AND ua.test_id = ?
                ORDER BY q.question_number
            """, (completed_at, user_id, test_id))
            answers = cursor.fetchall()
            
            if not answers:
                await callback.message.answer("Ответы на вопросы не найдены.")
                return
            
            response = f"📊 Результаты теста '{test_title}'\n\n"
            response += f"👤 Пользователь: @{username}\n"
            response += f"📅 Дата прохождения: {completed_at}\n"
            response += f"📈 Общий балл: {total_score}\n\n"
            response += "📝 Ответы:\n\n"
            
            for question, answer, score in answers:
                response += f"❓ {question}\n"
                response += f"✅ Ответ: {answer}\n"
                response += f"📊 Баллы: {score}\n\n"
            
            # Добавляем кнопку "Назад к тестам"
            keyboard = InlineKeyboardBuilder()
            keyboard.add(types.InlineKeyboardButton(
                text="🔙 Назад к тестам",
                callback_data=f"user_{user_id}"
            ))
            
            await callback.message.answer(
                response,
                reply_markup=keyboard.as_markup()
            )
        except Exception as e:
            print(f"Ошибка при получении ответов: {e}")
            await callback.message.answer("Произошла ошибка при получении ответов.")
        finally:
            conn.close()

    @dp.message(Command("check_db"))
    async def check_database(message: types.Message):
        if not is_admin(message.from_user.id):
            await message.answer("У вас нет прав администратора.")
            return
            
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Проверяем результаты тестов
            cursor.execute("SELECT * FROM user_test_results")
            test_results = cursor.fetchall()
            
            response = "📊 Результаты тестов:\n\n"
            if test_results:
                for result in test_results:
                    response += f"ID: {result[0]}\n"
                    response += f"User ID: {result[1]}\n"
                    response += f"Test ID: {result[2]}\n"
                    response += f"Score: {result[3]}\n"
                    response += f"Date: {result[4]}\n\n"
            else:
                response += "Нет результатов тестов\n\n"
            
            # Проверяем ответы пользователей
            cursor.execute("SELECT * FROM user_test_answers")
            test_answers = cursor.fetchall()
            
            response += "📝 Ответы пользователей:\n\n"
            if test_answers:
                for answer in test_answers:
                    response += f"ID: {answer[0]}\n"
                    response += f"User ID: {answer[1]}\n"
                    response += f"Test ID: {answer[2]}\n"
                    response += f"Question ID: {answer[3]}\n"
                    response += f"Answer ID: {answer[4]}\n"
                    response += f"Score: {answer[5]}\n"
                    response += f"Date: {answer[6]}\n\n"
            else:
                response += "Нет ответов пользователей\n\n"
            
            # Проверяем связи между таблицами
            cursor.execute("""
                SELECT r.*, u.username, t.title 
                FROM user_test_results r
                JOIN users u ON r.user_id = u.telegram_id
                JOIN psychological_tests t ON r.test_id = t.id
            """)
            joined_results = cursor.fetchall()
            
            response += "🔗 Связи между таблицами:\n\n"
            if joined_results:
                for result in joined_results:
                    response += f"Result ID: {result[0]}\n"
                    response += f"User: @{result[6]}\n"
                    response += f"Test: {result[7]}\n"
                    response += f"Score: {result[3]}\n"
                    response += f"Date: {result[4]}\n\n"
            else:
                response += "Нет связанных данных\n"
            
            await message.answer(response)
        except Exception as e:
            await message.answer(f"Ошибка при проверке базы данных: {str(e)}")
        finally:
            conn.close()

    @dp.message(Command("check_tables"))
    async def check_tables(message: types.Message):
        if not is_admin(message.from_user.id):
            await message.answer("У вас нет прав администратора.")
            return
            
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Проверяем таблицу users
            cursor.execute("SELECT * FROM users WHERE telegram_id = 686534625")
            user = cursor.fetchone()
            
            response = "👤 Информация о пользователе:\n\n"
            if user:
                response += f"ID: {user[0]}\n"
                response += f"Telegram ID: {user[1]}\n"
                response += f"Username: {user[2]}\n"
                response += f"Premium: {user[3]}\n"
            else:
                response += "Пользователь не найден\n"
            
            # Проверяем таблицу psychological_tests
            cursor.execute("SELECT * FROM psychological_tests WHERE id = 3")
            test = cursor.fetchone()
            
            response += "\n📝 Информация о тесте:\n\n"
            if test:
                response += f"ID: {test[0]}\n"
                response += f"Title: {test[1]}\n"
                response += f"Description: {test[2]}\n"
                response += f"Questions count: {test[3]}\n"
            else:
                response += "Тест не найден\n"
            
            # Проверяем вопросы теста
            cursor.execute("SELECT * FROM test_questions WHERE test_id = 3")
            questions = cursor.fetchall()
            
            response += "\n❓ Вопросы теста:\n\n"
            if questions:
                for q in questions:
                    response += f"ID: {q[0]}\n"
                    response += f"Question: {q[2]}\n"
                    response += f"Number: {q[3]}\n\n"
            else:
                response += "Вопросы не найдены\n"
            
            await message.answer(response)
        except Exception as e:
            await message.answer(f"Ошибка при проверке таблиц: {str(e)}")
        finally:
            conn.close()

    # Обработчик данных от веб-приложения
    @dp.message(F.web_app_data)
    async def handle_webapp_data(message: types.Message):
        """
        Обрабатывает данные, полученные от веб-приложения
        """
        try:
            # Получаем данные из веб-приложения
            data = json.loads(message.web_app_data.data)
            
            # Обрабатываем различные типы данных от веб-приложения
            if 'action' in data:
                if data['action'] == 'meditation_completed':
                    # Пользователь завершил медитацию
                    meditation_id = data.get('meditation_id')
                    duration = data.get('duration')
                    await message.answer(f"🎉 Поздравляем! Вы завершили медитацию.\nПродолжительность: {duration} минут")
                
                elif data['action'] == 'favorite_added':
                    # Пользователь добавил медитацию в избранное
                    meditation_id = data.get('meditation_id')
                    await message.answer("✨ Медитация добавлена в избранное!")
                
                elif data['action'] == 'premium_request':
                    # Пользователь запросил информацию о премиум
                    await message.answer(
                        "🌟 Premium подписка\n\n"
                        "Стоимость: 299 руб/месяц\n\n"
                        "Преимущества:\n"
                        "✅ Доступ ко всем медитациям\n"
                        "✅ Персональные рекомендации\n"
                        "✅ Отслеживание прогресса\n"
                        "✅ Приоритетная поддержка\n\n"
                        "Для оформления подписки:\n"
                        "1️⃣ Переведите 299 руб. по номеру карты:\n"
                        "1234 5678 9012 3456\n\n"
                        "2️⃣ Отправьте скриншот оплаты администратору:\n"
                        "@ivantyaj\n\n"
                        "После проверки оплаты вам будет активирован премиум-доступ!"
                    )
        except Exception as e:
            print(f"Ошибка при обработке данных от веб-приложения: {e}")
            await message.answer("Произошла ошибка при обработке данных.")

    # Регистрируем обработчики
    dp.callback_query.register(handle_premium_callback, F.data.startswith('premium_'))

    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start_bot()) 