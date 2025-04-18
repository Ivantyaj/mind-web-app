import sqlite3
import os

def init_db():
    conn = sqlite3.connect('mindfulness_bot.db')
    cursor = conn.cursor()
    
    # Создание таблицы пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        is_premium BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_meditation_date TIMESTAMP
    )
    ''')
    
    # Создание таблицы администраторов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Создание таблицы медитаций
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meditations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        content_type TEXT,
        content_url TEXT,
        duration INTEGER,
        is_free BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Создание таблицы достижений
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        icon TEXT,
        required_days INTEGER
    )
    ''')
    
    # Создание таблицы достижений пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        achievement_id INTEGER,
        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (achievement_id) REFERENCES achievements (id)
    )
    ''')
    
    # Создание таблицы отслеживания настроения
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mood_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        mood_score INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Создание таблицы психологических тестов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS psychological_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        questions_count INTEGER,
        is_free BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Создание таблицы вопросов тестов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER,
        question_text TEXT,
        question_number INTEGER,
        FOREIGN KEY (test_id) REFERENCES psychological_tests (id)
    )
    ''')
    
    # Создание таблицы ответов на вопросы
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER,
        answer_text TEXT,
        score INTEGER,
        FOREIGN KEY (question_id) REFERENCES test_questions (id)
    )
    ''')
    
    # Создание таблицы результатов тестов пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        test_id INTEGER,
        total_score INTEGER,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (test_id) REFERENCES psychological_tests (id)
    )
    ''')
    
    # Создание таблицы ответов пользователей на вопросы
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_test_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        test_id INTEGER,
        question_id INTEGER,
        answer_id INTEGER,
        score INTEGER,
        answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (test_id) REFERENCES psychological_tests (id),
        FOREIGN KEY (question_id) REFERENCES test_questions (id),
        FOREIGN KEY (answer_id) REFERENCES test_answers (id)
    )
    ''')
    
    # Создание таблицы интерпретаций результатов тестов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS test_interpretations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER,
        min_score INTEGER,
        max_score INTEGER,
        interpretation TEXT,
        FOREIGN KEY (test_id) REFERENCES psychological_tests (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    # Инициализация теста Бека
    init_beck_depression_test()
    init_anxiety_test()
    init_self_esteem_test()

def init_beck_depression_test():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем, существует ли уже тест Бека
        cursor.execute("""
            SELECT id FROM psychological_tests 
            WHERE title = 'Шкала депрессии Бека'
        """)
        existing_test = cursor.fetchone()
        
        if existing_test:
            print("Тест Бека уже существует в базе данных")
            return
            
        # Добавляем тест
        cursor.execute("""
            INSERT INTO psychological_tests (title, description, questions_count, is_free)
            VALUES (?, ?, ?, ?)
        """, (
            "Шкала депрессии Бека",
            "Тест предназначен для диагностики уровня депрессии. Состоит из 21 вопроса, каждый из которых содержит 4-5 утверждений, расположенных по мере нарастания степени выраженности симптома.",
            21,
            0  # Платный тест
        ))
        test_id = cursor.lastrowid
        
        # Добавляем вопросы
        questions = [
            (1, "Настроение"),
            (2, "Пессимизм"),
            (3, "Чувство несостоятельности"),
            (4, "Неудовлетворенность"),
            (5, "Чувство вины"),
            (6, "Ощущение наказания"),
            (7, "Отношение к себе"),
            (8, "Самообвинение"),
            (9, "Суицидальные мысли"),
            (10, "Слезливость"),
            (11, "Раздражительность"),
            (12, "Социальная отгороженность"),
            (13, "Нерешительность"),
            (14, "Образ тела"),
            (15, "Утрата работоспособности"),
            (16, "Нарушение сна"),
            (17, "Утомляемость"),
            (18, "Утрата аппетита"),
            (19, "Потеря веса"),
            (20, "Озабоченность здоровьем"),
            (21, "Утрата либидо")
        ]
        
        for question_number, question_text in questions:
            cursor.execute("""
                INSERT INTO test_questions (test_id, question_text, question_number)
                VALUES (?, ?, ?)
            """, (test_id, question_text, question_number))
            question_id = cursor.lastrowid
            
            # Добавляем варианты ответов
            if question_number == 1:  # Настроение
                answers = [
                    (0, "Я не чувствую себя расстроенным, печальным"),
                    (1, "Я расстроен"),
                    (2, "Я все время расстроен и не могу от этого отключиться"),
                    (3, "Я настолько расстроен и несчастлив, что не могу это выдержать")
                ]
            elif question_number == 2:  # Пессимизм
                answers = [
                    (0, "Я не тревожусь о своем будущем"),
                    (1, "Я чувствую, что озадачен будущим"),
                    (2, "Я чувствую, что меня ничего не ждет в будущем"),
                    (3, "Мое будущее безнадежно, и ничто не может измениться к лучшему")
                ]
            elif question_number == 3:  # Чувство несостоятельности
                answers = [
                    (0, "Я не чувствую себя неудачником"),
                    (1, "Я чувствую, что терпел больше неудач, чем другие люди"),
                    (2, "Когда я оглядываюсь на свою жизнь, я вижу в ней много неудач"),
                    (3, "Я чувствую, что как личность я - полный неудачник")
                ]
            elif question_number == 4:  # Неудовлетворенность
                answers = [
                    (0, "Я получаю столько же удовлетворения от жизни, как раньше"),
                    (1, "Я не получаю столько же удовлетворения от жизни, как раньше"),
                    (2, "Я больше не получаю удовлетворения ни от чего"),
                    (3, "Я полностью не удовлетворен жизнью и мне все надоело")
                ]
            elif question_number == 5:  # Чувство вины
                answers = [
                    (0, "Я не чувствую себя в чем-нибудь виноватым"),
                    (1, "Достаточно часто я чувствую себя виноватым"),
                    (2, "Большую часть времени я чувствую себя виноватым"),
                    (3, "Я постоянно чувствую себя виноватым")
                ]
            elif question_number == 6:  # Ощущение наказания
                answers = [
                    (0, "Я не чувствую, что могу быть наказанным за что-либо"),
                    (1, "Я чувствую, что могу быть наказан"),
                    (2, "Я ожидаю наказания"),
                    (3, "Я чувствую, что уже наказан")
                ]
            elif question_number == 7:  # Отношение к себе
                answers = [
                    (0, "Я не разочарован в себе"),
                    (1, "Я разочарован в себе"),
                    (2, "Я себе противен"),
                    (3, "Я себя ненавижу")
                ]
            elif question_number == 8:  # Самообвинение
                answers = [
                    (0, "Я знаю, что я не хуже других"),
                    (1, "Я критикую себя за ошибки и слабости"),
                    (2, "Я все время обвиняю себя за свои поступки"),
                    (3, "Я виню себя во всем плохом, что происходит")
                ]
            elif question_number == 9:  # Суицидальные мысли
                answers = [
                    (0, "Я не думаю о самоубийстве"),
                    (1, "Ко мне приходят мысли о самоубийстве, но я не буду их осуществлять"),
                    (2, "Я хотел бы убить себя"),
                    (3, "Я бы убил себя, если бы представился случай")
                ]
            elif question_number == 10:  # Слезливость
                answers = [
                    (0, "Я плачу не больше, чем обычно"),
                    (1, "Сейчас я плачу чаще, чем раньше"),
                    (2, "Теперь я все время плачу"),
                    (3, "Раньше я мог плакать, а сейчас не могу, даже если хочется")
                ]
            elif question_number == 11:  # Раздражительность
                answers = [
                    (0, "Сейчас я раздражителен не более, чем обычно"),
                    (1, "Я более нервничаю или раздражаюсь, чем раньше"),
                    (2, "Я все время раздражен"),
                    (3, "Я стал равнодушен к вещам, которые меня раньше раздражали")
                ]
            elif question_number == 12:  # Социальная отгороженность
                answers = [
                    (0, "Я не утратил интереса к другим людям"),
                    (1, "Я меньше интересуюсь другими людьми, чем раньше"),
                    (2, "Я утратил почти весь интерес к другим людям и почти не испытываю к ним никаких чувств"),
                    (3, "Я утратил всякий интерес к другим людям и полностью равнодушен к ним")
                ]
            elif question_number == 13:  # Нерешительность
                answers = [
                    (0, "Я принимаю решения примерно так же легко, как и всегда"),
                    (1, "Я стараюсь отложить принятие решений на потом"),
                    (2, "Принимать решения для меня трудно"),
                    (3, "Я больше совсем не могу принимать решения")
                ]
            elif question_number == 14:  # Образ тела
                answers = [
                    (0, "Я не чувствую, что выгляжу хуже, чем обычно"),
                    (1, "Меня тревожит, что я выгляжу старым и непривлекательным"),
                    (2, "Я знаю, что в моей внешности произошли существенные изменения, делающие меня непривлекательным"),
                    (3, "Я знаю, что выгляжу безобразно")
                ]
            elif question_number == 15:  # Утрата работоспособности
                answers = [
                    (0, "Я могу работать так же хорошо, как и раньше"),
                    (1, "Мне необходимо сделать дополнительное усилие, чтобы начать делать что-нибудь"),
                    (2, "Я с трудом заставляю себя делать что-либо"),
                    (3, "Я совсем не могу выполнять никакую работу")
                ]
            elif question_number == 16:  # Нарушение сна
                answers = [
                    (0, "Я сплю так же хорошо, как и раньше"),
                    (1, "Сейчас я сплю хуже, чем раньше"),
                    (2, "Я просыпаюсь на 1-2 часа раньше, и мне трудно заснуть опять"),
                    (3, "Я просыпаюсь на несколько часов раньше обычного и больше не могу заснуть")
                ]
            elif question_number == 17:  # Утомляемость
                answers = [
                    (0, "Я устаю не больше, чем обычно"),
                    (1, "Теперь я устаю быстрее, чем раньше"),
                    (2, "Я устаю почти от всего, что я делаю"),
                    (3, "Я не могу ничего делать из-за усталости")
                ]
            elif question_number == 18:  # Утрата аппетита
                answers = [
                    (0, "Мой аппетит не хуже, чем обычно"),
                    (1, "Мой аппетит стал хуже, чем раньше"),
                    (2, "Мой аппетит значительно хуже"),
                    (3, "У меня вообще нет аппетита")
                ]
            elif question_number == 19:  # Потеря веса
                answers = [
                    (0, "В последнее время я не похудел или потеря веса была незначительной"),
                    (1, "За последнее время я потерял более 2 кг"),
                    (2, "Я потерял более 5 кг"),
                    (3, "Я потерял более 7 кг")
                ]
            elif question_number == 20:  # Озабоченность здоровьем
                answers = [
                    (0, "Я беспокоюсь о своем здоровье не больше, чем обычно"),
                    (1, "Меня тревожат проблемы моего физического здоровья, такие как боли, расстройство желудка, запоры и т.д."),
                    (2, "Я очень обеспокоен своим физическим состоянием, и мне трудно думать о чем-либо другом"),
                    (3, "Я настолько обеспокоен своим физическим состоянием, что больше ни о чем не могу думать")
                ]
            elif question_number == 21:  # Утрата либидо
                answers = [
                    (0, "В последнее время я не замечал изменения своего интереса к сексу"),
                    (1, "Меня меньше занимают проблемы секса, чем раньше"),
                    (2, "Сейчас я значительно меньше интересуюсь сексуальными проблемами, чем раньше"),
                    (3, "Я полностью утратил сексуальный интерес")
                ]
            
            for score, answer_text in answers:
                cursor.execute("""
                    INSERT INTO test_answers (question_id, answer_text, score)
                    VALUES (?, ?, ?)
                """, (question_id, answer_text, score))
        
        # Добавляем интерпретации результатов
        interpretations = [
            (0, 9, "Отсутствие депрессивных симптомов"),
            (10, 15, "Легкая депрессия (субдепрессия)"),
            (16, 19, "Умеренная депрессия"),
            (20, 29, "Выраженная депрессия (средней тяжести)"),
            (30, 63, "Тяжелая депрессия")
        ]
        
        for min_score, max_score, interpretation in interpretations:
            cursor.execute("""
                INSERT INTO test_interpretations (test_id, min_score, max_score, interpretation)
                VALUES (?, ?, ?, ?)
            """, (test_id, min_score, max_score, interpretation))
        
        conn.commit()
        print("Тест Бека успешно добавлен в базу данных")
        return True
    except Exception as e:
        print(f"Ошибка при добавлении теста Бека: {e}")
        return False
    finally:
        conn.close()

def init_anxiety_test():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем, существует ли уже тест на тревожность
        cursor.execute("""
            SELECT id FROM psychological_tests 
            WHERE title = 'Шкала тревожности Спилбергера-Ханина'
        """)
        existing_test = cursor.fetchone()
        
        if existing_test:
            print("Тест на тревожность уже существует в базе данных")
            return
            
        # Добавляем тест
        cursor.execute("""
            INSERT INTO psychological_tests (title, description, questions_count, is_free)
            VALUES (?, ?, ?, ?)
        """, (
            "Шкала тревожности Спилбергера-Ханина",
            "Тест предназначен для измерения уровня тревожности. Состоит из 20 вопросов, оценивающих уровень тревожности в различных ситуациях.",
            20,
            0  # Платный тест
        ))
        test_id = cursor.lastrowid
        
        # Добавляем вопросы
        questions = [
            (1, "Я чувствую себя спокойно"),
            (2, "Мне ничто не угрожает"),
            (3, "Я нахожусь в напряжении"),
            (4, "Я испытываю сожаление"),
            (5, "Я чувствую себя свободно"),
            (6, "Я расстроен"),
            (7, "Меня волнуют возможные неудачи"),
            (8, "Я чувствую себя отдохнувшим"),
            (9, "Я встревожен"),
            (10, "Я испытываю чувство внутреннего удовлетворения"),
            (11, "Я уверен в себе"),
            (12, "Я нервничаю"),
            (13, "Я не нахожу себе места"),
            (14, "Я взвинчен"),
            (15, "Я не чувствую скованности"),
            (16, "Я доволен"),
            (17, "Я озабочен"),
            (18, "Я слишком возбужден и мне не по себе"),
            (19, "Мне радостно"),
            (20, "Мне приятно")
        ]
        
        for question_number, question_text in questions:
            cursor.execute("""
                INSERT INTO test_questions (test_id, question_text, question_number)
                VALUES (?, ?, ?)
            """, (test_id, question_text, question_number))
            question_id = cursor.lastrowid
            
            # Добавляем варианты ответов
            answers = [
                (1, "Почти никогда"),
                (2, "Иногда"),
                (3, "Часто"),
                (4, "Почти всегда")
            ]
            
            for score, answer_text in answers:
                cursor.execute("""
                    INSERT INTO test_answers (question_id, answer_text, score)
                    VALUES (?, ?, ?)
                """, (question_id, answer_text, score))
        
        # Добавляем интерпретации результатов
        interpretations = [
            (20, 30, "Низкий уровень тревожности"),
            (31, 45, "Умеренный уровень тревожности"),
            (46, 60, "Высокий уровень тревожности"),
            (61, 80, "Очень высокий уровень тревожности")
        ]
        
        for min_score, max_score, interpretation in interpretations:
            cursor.execute("""
                INSERT INTO test_interpretations (test_id, min_score, max_score, interpretation)
                VALUES (?, ?, ?, ?)
            """, (test_id, min_score, max_score, interpretation))
        
        conn.commit()
        print("Тест на тревожность успешно добавлен в базу данных")
        return True
    except Exception as e:
        print(f"Ошибка при добавлении теста на тревожность: {e}")
        return False
    finally:
        conn.close()

def init_self_esteem_test():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем, существует ли уже тест на самооценку
        cursor.execute("""
            SELECT id FROM psychological_tests 
            WHERE title = 'Шкала самооценки Розенберга'
        """)
        existing_test = cursor.fetchone()
        
        if existing_test:
            print("Тест на самооценку уже существует в базе данных")
            return
            
        # Добавляем тест
        cursor.execute("""
            INSERT INTO psychological_tests (title, description, questions_count, is_free)
            VALUES (?, ?, ?, ?)
        """, (
            "Шкала самооценки Розенберга",
            "Тест предназначен для измерения уровня самооценки. Состоит из 10 вопросов, оценивающих отношение к себе.",
            10,
            1  # Бесплатный тест
        ))
        test_id = cursor.lastrowid
        
        # Добавляем вопросы
        questions = [
            (1, "Я чувствую, что я достойный человек, по крайней мере, не менее чем другие"),
            (2, "Я склонен чувствовать, что я неудачник"),
            (3, "Мне кажется, у меня есть ряд хороших качеств"),
            (4, "Я способен кое-что делать не хуже, чем большинство"),
            (5, "Мне кажется, что мне особенно нечем гордиться"),
            (6, "Я к себе хорошо отношусь"),
            (7, "В целом я удовлетворен собой"),
            (8, "Мне бы хотелось больше уважать себя"),
            (9, "Иногда я ясно чувствую свою бесполезность"),
            (10, "Иногда я думаю, что я во всем нехорош")
        ]
        
        for question_number, question_text in questions:
            cursor.execute("""
                INSERT INTO test_questions (test_id, question_text, question_number)
                VALUES (?, ?, ?)
            """, (test_id, question_text, question_number))
            question_id = cursor.lastrowid
            
            # Добавляем варианты ответов
            answers = [
                (1, "Полностью согласен"),
                (2, "Согласен"),
                (3, "Не согласен"),
                (4, "Полностью не согласен")
            ]
            
            for score, answer_text in answers:
                cursor.execute("""
                    INSERT INTO test_answers (question_id, answer_text, score)
                    VALUES (?, ?, ?)
                """, (question_id, answer_text, score))
        
        # Добавляем интерпретации результатов
        interpretations = [
            (10, 15, "Низкий уровень самооценки"),
            (16, 25, "Средний уровень самооценки"),
            (26, 35, "Высокий уровень самооценки"),
            (36, 40, "Очень высокий уровень самооценки")
        ]
        
        for min_score, max_score, interpretation in interpretations:
            cursor.execute("""
                INSERT INTO test_interpretations (test_id, min_score, max_score, interpretation)
                VALUES (?, ?, ?, ?)
            """, (test_id, min_score, max_score, interpretation))
        
        conn.commit()
        print("Тест на самооценку успешно добавлен в базу данных")
        return True
    except Exception as e:
        print(f"Ошибка при добавлении теста на самооценку: {e}")
        return False
    finally:
        conn.close()

def get_connection():
    return sqlite3.connect('mindfulness_bot.db')

def is_admin(telegram_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM admins WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone() is not None
        print(f"Проверка прав администратора для ID {telegram_id}: {'есть права' if result else 'нет прав'}")
        return result
    except Exception as e:
        print(f"Ошибка при проверке прав администратора: {e}")
        return False
    finally:
        conn.close()

def add_admin(telegram_id, username):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Сначала проверяем, существует ли уже такой администратор
        cursor.execute("SELECT id FROM admins WHERE telegram_id = ?", (telegram_id,))
        if cursor.fetchone() is None:
            # Если администратора нет, добавляем его
            cursor.execute(
                "INSERT INTO admins (telegram_id, username) VALUES (?, ?)",
                (telegram_id, username)
            )
            conn.commit()
            print(f"Администратор {username} (ID: {telegram_id}) успешно добавлен")
            return True
        else:
            print(f"Администратор {username} (ID: {telegram_id}) уже существует")
            return True
    except Exception as e:
        print(f"Ошибка при добавлении администратора: {e}")
        return False
    finally:
        conn.close()

async def get_available_tests(self):
    """Получить список доступных тестов"""
    async with self.pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT id, title, questions_count 
                FROM psychological_tests 
                WHERE is_free = 1
            """)
            return await cur.fetchall()

async def get_test_question(self, test_id: int, question_number: int):
    """Получить вопрос теста по номеру"""
    async with self.pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT id, question_text 
                FROM test_questions 
                WHERE test_id = %s AND question_number = %s
            """, (test_id, question_number))
            return await cur.fetchone()

async def get_question_answers(self, question_id: int):
    """Получить варианты ответов для вопроса"""
    async with self.pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT id, answer_text, score 
                FROM test_answers 
                WHERE question_id = %s
            """, (question_id,))
            return await cur.fetchall()

async def get_answer_score(self, answer_id: int):
    """Получить балл за ответ"""
    async with self.pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT score 
                FROM test_answers 
                WHERE id = %s
            """, (answer_id,))
            return await cur.fetchone()

async def save_test_result(self, user_id: int, test_id: int, total_score: int):
    """Сохранить результат теста"""
    async with self.pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO user_test_results (user_id, test_id, total_score, completed_at)
                VALUES (%s, %s, %s, NOW())
            """, (user_id, test_id, total_score))
            await conn.commit()

async def get_user_test_results(self, user_id: int):
    """Получить результаты тестов пользователя"""
    async with self.pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT test_id, total_score, completed_at
                FROM user_test_results
                WHERE user_id = %s
                ORDER BY completed_at DESC
            """, (user_id,))
            return await cur.fetchall()

async def get_test_by_id(self, test_id: int):
    """Получить информацию о тесте по ID"""
    async with self.pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT title, description
                FROM psychological_tests
                WHERE id = %s
            """, (test_id,))
            return await cur.fetchone()

async def init_test_data(self):
    """Инициализация тестовых данных"""
    async with self.pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Проверяем, существует ли уже тест на уровень стресса
            await cur.execute("""
                SELECT id FROM psychological_tests 
                WHERE title = 'Тест на уровень стресса'
            """)
            existing_test = await cur.fetchone()
            
            if existing_test:
                print("Тест на уровень стресса уже существует в базе данных")
                return
            
            # Добавляем тест на определение уровня стресса
            await cur.execute("""
                INSERT INTO psychological_tests (title, description, questions_count, is_free)
                VALUES ('Тест на уровень стресса', 
                        'Этот тест поможет определить ваш текущий уровень стресса', 
                        5, 1)
            """)
            test_id = cur.lastrowid

            # Добавляем вопросы
            questions = [
                (1, "Как часто вы чувствуете себя уставшим?"),
                (2, "Насколько хорошо вы спите?"),
                (3, "Как часто у вас возникают головные боли?"),
                (4, "Насколько легко вы раздражаетесь?"),
                (5, "Как часто вы чувствуете тревогу?")
            ]

            for question_number, question_text in questions:
                await cur.execute("""
                    INSERT INTO test_questions (test_id, question_text, question_number)
                    VALUES (%s, %s, %s)
                """, (test_id, question_text, question_number))
                question_id = cur.lastrowid

                # Добавляем варианты ответов
                answers = [
                    ("Почти никогда", 1),
                    ("Иногда", 2),
                    ("Часто", 3),
                    ("Почти всегда", 4)
                ]

                for answer_text, score in answers:
                    await cur.execute("""
                        INSERT INTO test_answers (question_id, answer_text, score)
                        VALUES (%s, %s, %s)
                    """, (question_id, answer_text, score))

            await conn.commit()
            print("Тест на уровень стресса успешно добавлен в базу данных")

def add_premium_user(username: str) -> bool:
    """Добавляет пользователя в список премиум-пользователей"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Проверяем существование пользователя
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            # Создаем нового пользователя
            cursor.execute(
                "INSERT INTO users (username, is_premium) VALUES (?, 1)",
                (username,)
            )
        else:
            # Обновляем существующего пользователя
            cursor.execute(
                "UPDATE users SET is_premium = 1 WHERE username = ?",
                (username,)
            )
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding premium user: {e}")
        return False
    finally:
        conn.close()

def remove_premium_user(username: str) -> bool:
    """Удаляет пользователя из списка премиум-пользователей"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE users SET is_premium = 0 WHERE username = ?",
            (username,)
        )
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error removing premium user: {e}")
        return False
    finally:
        conn.close()

def is_premium_user(username: str) -> bool:
    """Проверяет, является ли пользователь премиум-пользователем"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT is_premium FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        
        return result and result[0] == 1
    except Exception as e:
        print(f"Error checking premium status: {e}")
        return False
    finally:
        conn.close()

def get_premium_users() -> list:
    """Возвращает список премиум-пользователей"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT username FROM users WHERE is_premium = 1"
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting premium users: {e}")
        return []
    finally:
        conn.close()

class Database:
    async def is_premium_user(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь премиум"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT is_premium FROM users WHERE id = $1',
                user_id
            )
            return row['is_premium'] if row else False

    async def set_premium_status(self, user_id: int, is_premium: bool):
        """Устанавливает премиум статус пользователя"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                '''
                INSERT INTO users (id, is_premium) 
                VALUES ($1, $2)
                ON CONFLICT (id) DO UPDATE 
                SET is_premium = $2
                ''',
                user_id, is_premium
            ) 