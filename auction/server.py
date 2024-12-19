from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "auction.db"

def execute_query(query, params=None, fetchall=False, fetchone=False):
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        if fetchall:
            return cursor.fetchall()
        if fetchone:
            return cursor.fetchone()
        conn.commit()

def init_db():
    execute_query('''
        CREATE TABLE IF NOT EXISTS lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            owner TEXT NOT NULL,
            start_price REAL NOT NULL,
            current_price REAL NOT NULL,
            min_step REAL NOT NULL,
            end_time TEXT NOT NULL,
            winner TEXT
        )
    ''')

    execute_query('''
        CREATE TABLE IF NOT EXISTS bids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_id INTEGER NOT NULL,
            bidder TEXT NOT NULL,
            amount REAL NOT NULL,
            bid_time TEXT NOT NULL,
            FOREIGN KEY (lot_id) REFERENCES lots (id)
        )
    ''')

@app.route('/create_lot', methods=['POST'])
def create_lot():
    data = request.get_json()
    try:
        name = data['name']
        description = data.get('description', '')
        owner = data['owner']
        start_price = float(data['start_price'])
        min_step = float(data['min_step'])
        end_time = data['end_time']

        try:
            datetime.strptime(end_time, "%Y-%m-%d %H:%M")
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD HH:MM."}), 400

        query = '''INSERT INTO lots (name, description, owner, start_price, current_price, min_step, end_time) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)'''
        execute_query(query, (name, description, owner, start_price, start_price, min_step, end_time))
        return jsonify({"message": "Lot created successfully"}), 200

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except ValueError:
        return jsonify({"error": "Invalid input data."}), 400

@app.route('/get_lots', methods=['GET'])
def get_lots():
    query = '''SELECT id, name, description, owner, current_price, end_time, 
                      COALESCE(winner, '') AS winner, min_step 
               FROM lots WHERE end_time > ?'''
    lots = execute_query(query, (datetime.now().isoformat(),), fetchall=True)
    return jsonify({"lots": [dict(lot) for lot in lots]}), 200

@app.route('/place_bid', methods=['POST'])
def place_bid():
    data = request.get_json()
    try:
        lot_id = int(data['lot_id'])
        bidder = data['bidder']
        amount = float(data['amount'])

        lot = execute_query('SELECT * FROM lots WHERE id = ?', (lot_id,), fetchone=True)
        if not lot:
            return jsonify({"error": "Lot not found."}), 404

        if datetime.now() > datetime.fromisoformat(lot['end_time']):
            return jsonify({"error": "Auction for this lot has ended."}), 400

        if amount <= lot['current_price'] + lot['min_step']:
            return jsonify({"error": "Bid must be at least the current price plus the minimum step."}), 400

        execute_query('UPDATE lots SET current_price = ? WHERE id = ?', (amount, lot_id))
        execute_query('INSERT INTO bids (lot_id, bidder, amount, bid_time) VALUES (?, ?, ?, ?)',
                      (lot_id, bidder, amount, datetime.now().isoformat()))

        return jsonify({"message": "Bid placed successfully"}), 200

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except ValueError:
        return jsonify({"error": "Invalid input data."}), 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
