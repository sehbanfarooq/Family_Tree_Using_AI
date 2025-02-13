from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Set upload folder and allowed image extensions
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Initialize the database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Create family_members table
    c.execute('''
        CREATE TABLE IF NOT EXISTS family_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            relationship TEXT NOT NULL,
            parent_id INTEGER,
            photo TEXT,
            FOREIGN KEY (parent_id) REFERENCES family_members(id)
        );
    ''')

    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
    ''')

    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

@app.route('/')
def home():
    return redirect(url_for('login'))  # Redirect to login page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM family_members')
    members = c.fetchall()
    conn.close()
    return render_template('dashboard.html', members=members)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_family_member', methods=['GET', 'POST'])
def add_family_member():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        relationship = request.form['relationship']
        parent_id = request.form['parent_id']
        photo = None

        # Handle image upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                photo = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(photo)

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO family_members (name, relationship, parent_id, photo)
            VALUES (?, ?, ?, ?)
        ''', (name, relationship, parent_id, photo))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))

    return render_template('add_family_member.html')

@app.route('/edit_family_member/<int:member_id>', methods=['GET', 'POST'])
def edit_family_member(member_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        relationship = request.form['relationship']
        parent_id = request.form['parent_id']
        photo = None

        # Handle image upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                photo = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(photo)

        c.execute('''
            UPDATE family_members
            SET name = ?, relationship = ?, parent_id = ?, photo = ?
            WHERE id = ?
        ''', (name, relationship, parent_id, photo, member_id))

        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    # Fetch the member details to pre-fill the form
    c.execute('SELECT * FROM family_members WHERE id = ?', (member_id,))
    member = c.fetchone()
    conn.close()

    return render_template('edit_member.html', member=member)

@app.route('/delete_family_member/<int:member_id>', methods=['POST'])
def delete_family_member(member_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Get the photo file path to delete it from the file system
    c.execute('SELECT photo FROM family_members WHERE id = ?', (member_id,))
    member = c.fetchone()
    if member and member[0]:
        os.remove(member[0])  # Remove the image file from the server

    c.execute('DELETE FROM family_members WHERE id = ?', (member_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
