# Базовый образ - мини версия Python
FROM python:3.11-slim

# Рабочая папка внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями
COPY backend/requirements.txt .

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем весь бэкенд
COPY backend/ .

# Команда для запуска приложения
CMD ["python", "app.py"]