from flask import Flask, render_template, request, g, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome to my Flask app!'


DATABASE = 'messages_db.sqlite'

def get_message_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, handle TEXT, message TEXT)")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def insert_message(request):
    db = get_message_db()
    cursor = db.cursor()
    handle = request.form['handle']
    message = request.form['message']
    cursor.execute("INSERT INTO messages (handle, message) VALUES (?, ?)", (handle, message))
    db.commit()

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        insert_message(request)
        return render_template('submit.html', thanks=True)
    return render_template('submit.html')

@app.route('/messages')
def messages():
    db = get_message_db()
    cursor = db.cursor()
    cursor.execute("SELECT handle, message FROM messages ORDER BY id DESC")
    messages = cursor.fetchall()
    return render_template('messages.html', messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
