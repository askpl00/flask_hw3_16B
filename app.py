from flask import Flask, render_template, request, g, redirect, url_for
import sqlite3, random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')


def get_message_db():
    """
    This function gets a connection to the database with the messages.
    It first tries to return a database connection from the Flask g object,
    which is a global namespace for holding any data you want during a single app context.
    If a connection does not already exist, it creates a new connection and initializes
    the messages table if it does not exist.
    
    Returns:
        A sqlite3 connection to the messages database.
    """
    try:
        # Try to return the database connection if it already exists
        return g.message_db
    except:
        # If it doesn't exist, create a new database connection
        g.message_db = sqlite3.connect("messages_db.sqlite")
        
        # Command to create a messages table if it does not already exist
        cmd = """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            handle TEXT,
            message TEXT
        )
        """
        
        # Create a cursor to execute the SQL command
        cursor = g.message_db.cursor()
        cursor.execute(cmd)
        
        # Return the database connection
        return g.message_db


def insert_message(request):
    """
    Insert a new message into the messages database.

    Args:
        request: The Flask request object containing form data.
    """
    # Get a database connection
    db = get_message_db()
    cursor = db.cursor()
    
    # Extract the handle and message from the form data
    handle = request.form['handle']
    message = request.form['message']
    
    # Insert the new message into the messages table
    cursor.execute("INSERT INTO messages (handle, message) VALUES (?, ?)", (handle, message))
    db.commit()
    cursor.close()


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
    db.close()  
    msgs = random.sample(all_messages, min(n, len(all_messages)))
    return msgs


@app.route('/view')
def view():
    msgs = random_messages(5)  
    return render_template('view.html', messages=msgs)
