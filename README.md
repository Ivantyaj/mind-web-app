# Mindfulness Meditation Web App

Веб-приложение для Telegram бота с медитациями. Интегрируется с Telegram Web App API для предоставления удобного интерфейса для медитаций.

## Особенности

- Интеграция с Telegram Web App
- Адаптивный дизайн
- Поддержка премиум-контента
- Автоматическая синхронизация с ботом

## Установка

1. Склонируйте репозиторий:
```bash
git clone https://github.com/your-username/mindfulness-webapp.git
```

2. Перейдите в директорию проекта:
```bash
cd mindfulness-webapp
```

3. Откройте `index.html` в браузере для локального тестирования.

## Развертывание

1. Создайте новый репозиторий на GitHub
2. Переименуйте его в `your-username.github.io`
3. Загрузите файлы в репозиторий:
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

4. Перейдите в настройки репозитория -> Pages
5. Выберите ветку main и папку root
6. Нажмите Save

Ваше приложение будет доступно по адресу: `https://your-username.github.io`

## Настройка

1. В файле `app.js` замените URL сервера на ваш:
```javascript
const response = await fetch('http://your-server:8000/check_premium', ...
```

2. В боте замените URL веб-приложения на ваш:
```python
WebAppInfo(url="https://your-username.github.io")
```

## Лицензия

MIT 