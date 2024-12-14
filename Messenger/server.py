from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

HISTORY_FILE = 'history.json'

def load_history():
    """Загружаем историю чатов из файла, если он существует"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(history):
    """Сохраняем историю чатов в файл"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

@app.route('/send_message', methods=['POST'])
def send_message():
    """Получаем и сохраняем сообщение"""
    data = request.get_json()
    username = data.get('username')
    message = data.get('message')
    
    if not username or not message:
        return jsonify({"status": "error", "message": "Invalid input"}), 400
    
    history = load_history()
    
    history.append({"username": username, "message": message})
    
    save_history(history)
    
    return jsonify({"status": "success"}), 200

@app.route('/get_history', methods=['GET'])
def get_history():
    """Получаем историю чатов"""
    history = load_history()
    return jsonify({"history": history}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
