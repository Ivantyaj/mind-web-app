// Инициализация Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand(); // Раскрываем на всю высоту

// Получаем данные о пользователе
const userId = tg.initDataUnsafe.user.id;
let isPremium = false;

// Список медитаций
const meditations = [
    {
        id: 1,
        title: "Базовая медитация",
        description: "Простая медитация для начинающих",
        duration: "10 мин",
        audioUrl: "meditations/basic.mp3",
        isPremium: false
    },
    {
        id: 2,
        title: "Глубокое дыхание",
        description: "Техника осознанного дыхания",
        duration: "15 мин",
        audioUrl: "meditations/breathing.mp3",
        isPremium: false
    },
    {
        id: 3,
        title: "Медитация для сна",
        description: "Помогает расслабиться перед сном",
        duration: "20 мин",
        audioUrl: "meditations/sleep.mp3",
        isPremium: true
    }
];

// Проверяем премиум статус
async function checkPremiumStatus() {
    try {
        const response = await fetch('http://your-server:8000/check_premium', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ telegram_id: userId })
        });
        
        const data = await response.json();
        isPremium = data.is_premium;
        renderMeditations();
    } catch (error) {
        console.error('Ошибка при проверке премиум статуса:', error);
        renderMeditations();
    }
}

// Отображаем медитации
function renderMeditations() {
    const container = document.querySelector('.meditations-list');
    container.innerHTML = '';

    meditations.forEach(meditation => {
        if (!meditation.isPremium || isPremium) {
            const card = document.createElement('div');
            card.className = 'meditation-card';
            
            card.innerHTML = `
                ${meditation.isPremium ? '<span class="premium-badge">Premium</span>' : ''}
                <h2>${meditation.title}</h2>
                <p>${meditation.description}</p>
                <div class="duration">${meditation.duration}</div>
                <button class="button" onclick="startMeditation(${meditation.id})">
                    Начать медитацию
                </button>
            `;
            
            container.appendChild(card);
        }
    });
}

// Начало медитации
function startMeditation(meditationId) {
    const meditation = meditations.find(m => m.id === meditationId);
    
    if (meditation.isPremium && !isPremium) {
        // Отправляем запрос на получение премиум
        tg.sendData(JSON.stringify({
            action: 'premium_request'
        }));
        return;
    }
    
    // Здесь будет логика воспроизведения медитации
    console.log(`Начинаем медитацию: ${meditation.title}`);
    
    // После завершения медитации отправляем данные в бот
    tg.sendData(JSON.stringify({
        action: 'meditation_completed',
        meditation_id: meditationId,
        duration: meditation.duration
    }));
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    // Применяем цветовую схему Telegram
    document.documentElement.style.setProperty('--tg-theme-bg-color', tg.backgroundColor);
    document.documentElement.style.setProperty('--tg-theme-text-color', tg.textColor);
    document.documentElement.style.setProperty('--tg-theme-button-color', tg.buttonColor);
    document.documentElement.style.setProperty('--tg-theme-button-text-color', tg.buttonTextColor);
    
    // Проверяем премиум статус и отображаем медитации
    checkPremiumStatus();
}); 