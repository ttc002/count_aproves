from flask import Flask, request, redirect, url_for, render_template
import json
import os
import datetime

app = Flask(__name__)
stats_file_path = 'stats.json'

def load_stats():
    """Загрузка статистики из файла JSON."""
    if os.path.exists(stats_file_path):
        with open(stats_file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}  # Если файл пуст или повреждён, используем пустой словарь
    else:
        data = {}

    # Убедимся, что все ключи присутствуют
    data.setdefault("daily", {
        "approvals": 0,
        "denials": 0,
        "total": 0,
        "denial_percentage": 0.0
    })
    data.setdefault("monthly", {
        "total_approvals": 0,
        "total_denials": 0,
        "denial_percentage": 0.0
    })
    return data


def calculate_denial_percentage(approvals, denials):
    """Расчет процента отказов."""
    total = approvals + denials
    if total == 0:
        return 0.0
    return (denials / total) * 100

def save_stats(stats):
    """Сохранение статистики в файл JSON."""
    with open(stats_file_path, 'w') as f:
        json.dump(stats, f, indent=4)

stats = load_stats()

@app.route('/')
def index():
    stats = load_stats()
    return render_template('index.html', stats=stats)

@app.route('/approve', methods=['POST'])
def approve():
    stats = load_stats()
    stats['daily']['approvals'] += 1
    stats['daily']['total'] = stats['daily']['approvals'] + stats['daily']['denials']
    stats['daily']['denial_percentage'] = calculate_denial_percentage(stats['daily']['approvals'], stats['daily']['denials'])
    stats['daily']['last_approval_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_stats(stats)
    return redirect(url_for('index'))

@app.route('/deny', methods=['POST'])
def deny():
    stats = load_stats()
    stats['daily']['denials'] += 1
    stats['daily']['total'] = stats['daily']['approvals'] + stats['daily']['denials']
    stats['daily']['denial_percentage'] = calculate_denial_percentage(stats['daily']['approvals'], stats['daily']['denials'])
    stats['daily']['last_denial_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_stats(stats)
    return redirect(url_for('index'))


@app.route('/cancel_last/<action>', methods=['POST'])
def cancel_last(action):
    stats = load_stats()
    if action == 'approval' and stats['daily']['approvals'] > 0:
        stats['daily']['approvals'] -= 1
    elif action == 'denial' and stats['daily']['denials'] > 0:
        stats['daily']['denials'] -= 1
    stats['daily']['total'] = stats['daily']['approvals'] + stats['daily']['denials']
    stats['daily']['denial_percentage'] = calculate_denial_percentage(stats['daily']['approvals'], stats['daily']['denials'])
    save_stats(stats)
    return redirect(url_for('index'))


@app.route('/submit_daily', methods=['POST'])
def submit_daily():
    """Добавляет дневные данные в общую статистику и сбрасывает дневную."""
    stats = load_stats()
    
    # Добавляем запись в массив entries
    stats.setdefault('monthly', {}).setdefault('entries', [])
    stats['monthly']['entries'].append({
        "timestamp": datetime.datetime.now().isoformat(),
        "approvals": stats['daily']['approvals'],
        "denials": stats['daily']['denials'],
        "denial_percentage": calculate_denial_percentage(
            stats['daily']['approvals'], stats['daily']['denials']
        )
    })

    # Обновляем общую статистику
    stats['monthly']['total_approvals'] += stats['daily']['approvals']
    stats['monthly']['total_denials'] += stats['daily']['denials']
    stats['monthly']['denial_percentage'] = calculate_denial_percentage(
        stats['monthly']['total_approvals'], stats['monthly']['total_denials']
    )

    # Сбрасываем дневную статистику
    stats['daily'] = {
        "approvals": 0,
        "denials": 0,
        "total": 0,
        "denial_percentage": 0.0
    }
    save_stats(stats)
    return redirect(url_for('index'))


@app.route('/delete_data', methods=['POST'])
def delete_data():
    """Удаляет все данные статистики."""
    if os.path.exists(stats_file_path):
        os.remove(stats_file_path)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0')
