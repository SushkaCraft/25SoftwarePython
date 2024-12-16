from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "auction.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_price REAL NOT NULL,
            current_price REAL NOT NULL,
            end_time TEXT NOT NULL,
            winner TEXT
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS bids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_id INTEGER NOT NULL,
            bidder TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (lot_id) REFERENCES lots (id)
        )''')
        conn.commit()

@app.route('/create_lot', methods=['POST'])
def create_lot():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    start_price = data.get('start_price')
    end_time = data.get('end_time')

    if not name or not start_price or not end_time:
        return jsonify({"error": "Invalid input"}), 400

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO lots (name, description, start_price, current_price, end_time) 
                          VALUES (?, ?, ?, ?, ?)''',
                       (name, description, start_price, start_price, end_time))
        conn.commit()
    return jsonify({"message": "Lot created successfully"}), 200

@app.route('/get_lots', methods=['GET'])
def get_lots():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lots WHERE end_time > ?', (datetime.now().isoformat(),))
        lots = cursor.fetchall()
    return jsonify({"lots": lots}), 200

@app.route('/place_bid', methods=['POST'])
def place_bid():
    data = request.get_json()
    lot_id = data.get('lot_id')
    bidder = data.get('bidder')
    amount = data.get('amount')

    if not lot_id or not bidder or not amount:
        return jsonify({"error": "Invalid input"}), 400

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT current_price FROM lots WHERE id = ?', (lot_id,))
        lot = cursor.fetchone()
        if not lot or amount <= lot[0]:
            return jsonify({"error": "Bid must be higher than current price"}), 400

        cursor.execute('UPDATE lots SET current_price = ? WHERE id = ?', (amount, lot_id))
        cursor.execute('INSERT INTO bids (lot_id, bidder, amount) VALUES (?, ?, ?)', (lot_id, bidder, amount))
        conn.commit()
    return jsonify({"message": "Bid placed successfully"}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
