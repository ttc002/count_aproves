from flask import Flask, request, redirect, url_for, render_template
import json
import os
from multiprocessing import Process
app = Flask(__name__)
# Путь к файлу для хранения статистики
stats_file_path = 'stats.json'

def load_stats():
    """Загрузка статистики из файла JSON."""
    if os.path.exists(stats_file_path):
        with open(stats_file_path, 'r') as f:
            return json.load(f)
    else:
        return {
            'daily': {
                'approvals': 0,
                'denials': 0,
                'total': 0,
                'denial_percentage': 0.0,  # Процент отказов
            },
            'monthly': {
                'total_approvals': 0,
                'total_denials': 0,
                'denial_percentage': 0.0,  # Процент отказов
            }
        }

def calculate_denial_percentage(approvals, denials):
    """Расчет процента отказов."""
    total = approvals + denials
    if total == 0:
        return 0.0
    return (denials / total) * 100

def save_stats(stats):
    """Сохранение статистики в файл JSON."""
    with open(stats_file_path, 'w') as f:
        json.dump(stats, f)

# Начальные данные статистики
stats = load_stats()

@app.route('/')
def index():
    stats = load_stats()
    return render_template('index.html', stats=stats)

@app.route('/approve', methods=['POST'])
def approve():
    stats['daily']['approvals'] += 1
    stats['daily']['total'] = stats['daily']['approvals'] + stats['daily']['denials']
    stats['daily']['denial_percentage'] = calculate_denial_percentage(stats['daily']['approvals'], stats['daily']['denials'])
    
    save_stats(stats)  # Сохраняем данные после обновления
    return redirect(url_for('index'))

@app.route('/deny', methods=['POST'])
def deny():
    stats['daily']['denials'] += 1
    stats['daily']['total'] = stats['daily']['approvals'] + stats['daily']['denials']
    stats['daily']['denial_percentage'] = calculate_denial_percentage(stats['daily']['approvals'], stats['daily']['denials'])
    
    save_stats(stats)  # Сохраняем данные после обновления
    return redirect(url_for('index'))

@app.route('/submit_daily', methods=['POST'])
def submit_daily():
    # Сохраняем дневные данные в месячную статистику только по нажатию кнопки
    stats['monthly']['total_approvals'] += stats['daily']['approvals']
    stats['monthly']['total_denials'] += stats['daily']['denials']
    
    # Обновляем процент отказов в месячной статистике
    stats['monthly']['denial_percentage'] = calculate_denial_percentage(stats['monthly']['total_approvals'], stats['monthly']['total_denials'])

    # Сбрасываем дневные данные
    stats['daily']['approvals'] = 0
    stats['daily']['denials'] = 0
    stats['daily']['total'] = 0
    stats['daily']['denial_percentage'] = 0.0  # Сброс процента

    save_stats(stats)  # Сохраняем данные после сброса
    return redirect(url_for('index'))





def load_data():
    if os.path.exists('stats.json'):
        with open('stats.json', 'r') as f:
            return json.load(f)
    return {}

# Удаление всех данных из stats.json
@app.route('/delete_data', methods=['GET', 'POST'])
def delete_data():
    if request.method == 'POST':
        # Удаляем файл stats.json
        if os.path.exists('stats.json'):
            print("aaa")
            os.remove('stats.json')
        return redirect(url_for('index'))  # Перенаправляем на главную страницу после удаления
    return render_template('delete.html')

# Не забудьте также добавить маршрут для главной страницы
@app.route('/delete', methods=['GET'])
def index2():
    stats = load_data()
    return render_template('delete.html', stats=stats)

if __name__ == '__main__':
    app.run(port=80,host='0.0.0.0')



    
