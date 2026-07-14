from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os  # Добавляем импорт os для работы с переменными окружения

# Создаём приложение
app = Flask(__name__)
CORS(app)  # Разрешаем запросы с других сайтов

# Настраиваем базу данных
# Используем Railway PostgreSQL, если есть, иначе SQLite
database_url = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
# Railway передает DATABASE_URL с префиксом postgres://, но SQLAlchemy требует postgresql://
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Создаём модель задачи (что будет храниться в базе)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'completed': self.completed,
            'created_at': self.created_at.isoformat()
        }

# Создаём таблицы в базе данных
with app.app_context():
    db.create_all()

# Маршрут для получения всех задач
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

# Маршрут для создания новой задачи
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Нужно указать название'}), 400
    
    task = Task(title=data['title'])
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201

# Маршрут для удаления задачи
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Задача удалена'})

# Маршрут для обновления задачи
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    if 'completed' in data:
        task.completed = data['completed']
    
    db.session.commit()
    return jsonify(task.to_dict())

# Маршрут для проверки здоровья (для Railway)
@app.route('/health')
def health():
    return 'OK', 200

# Запуск приложения - ИСПРАВЛЕНО для Railway
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Берём порт из переменной окружения
    app.run(debug=False, host='0.0.0.0', port=port)  # Слушаем все интерфейсы