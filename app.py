from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os
import csv
from io import StringIO

app = Flask(__name__)

DB_PATH = 'records.db'

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            q1 TEXT, q2 TEXT, q3 TEXT, q4 TEXT, q5 TEXT,
            q6 TEXT, q7 TEXT, q8 TEXT, q9 TEXT, q10 TEXT, q11 TEXT
        )
        """)
        conn.commit()
        conn.close()

@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', active='home')

@app.route('/30day-plan')
def plan():
    return render_template('index.html', active='plan')

@app.route('/records', methods=['GET', 'POST'])
def records():
    if request.method == 'POST':
        # Save submitted record to SQLite
        values = [request.form.get(f'q{i}') for i in range(1, 12)]
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO records (q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, values)
        conn.commit()
        conn.close()
        return redirect(url_for('records'))
    # Show all records
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11 FROM records")
    all_records = c.fetchall()
    conn.close()
    return render_template('index.html', active='records', records=all_records)

@app.route('/download-csv')
def download_csv():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11 FROM records")
    rows = c.fetchall()
    conn.close()
    headers = [
        "Morning Mood", "Bed Time", "Coffee", "Masturbation", "YouTube",
        "Pray", "Exercise/Meditation", "Energy Level", "Motivation Content",
        "Task Done", "Notes"
    ]
    proxy = StringIO()
    writer = csv.writer(proxy)
    writer.writerow(headers)
    writer.writerows(rows)
    mem = StringIO(proxy.getvalue())
    proxy.close()
    mem.seek(0)
    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name='records.csv'
    )

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
