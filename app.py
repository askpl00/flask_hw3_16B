from flask import Flask, render_template, request, g, redirect, url_for
import sqlite3, random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


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


def random_messages(n):
    db = get_message_db()
    cursor = db.cursor()
    cursor.execute("SELECT handle, message FROM messages")
    all_messages = cursor.fetchall()
    db.close()  # Don't forget to close the connection
    return random.sample(all_messages, min(n, len(all_messages)))


@app.route('/view')
def view():
    msgs = random_messages(5)  # Change the number to how many messages you want to display
    return render_template('view.html', messages=msgs)
