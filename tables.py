from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Dummy database for users
users_db = {}

# Dummy database for user progress
progress_db = {}

# Function to initialize progress for a user
def initialize_progress(username):
    if username not in progress_db:
        progress_db[username] = {'global': 0, 'choose': 0, 'fill': 0}

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login_signup', next='index'))

    username = session['user']
    initialize_progress(username)

    global_progress = progress_db[username]['global']
    
    return render_template('index.html', username=username, global_progress=global_progress)

@app.route('/get_table', methods=['POST'])
def get_table():
    number = int(request.form['number'])
    table = [f"{number} x {i} = {number * i}" for i in range(1, 11)]
    return jsonify({'table': table})

@app.route('/login_signup', methods=['GET', 'POST'])
def login_signup():
    next_page = request.args.get('next', 'index')  # default 'index' if nothing
    if request.method == 'POST':
        action = request.form['action']
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            return render_template('login_signup.html', error="Username and password required!", next=next_page)

        if action == 'signup':
            if username in users_db:
                return render_template('login_signup.html', error="Username already exists!", next=next_page)
            users_db[username] = password
            session['user'] = username
            initialize_progress(username)
            return redirect(url_for(next_page))

        elif action == 'login':
            if username in users_db and users_db[username] == password:
                session['user'] = username
                initialize_progress(username)
                return redirect(url_for(next_page))
            else:
                return render_template('login_signup.html', error="Invalid username or password!", next=next_page)

    return render_template('login_signup.html', error=None, next=next_page)

@app.route('/choose')
def choose():
    if 'user' not in session:
        return redirect(url_for('login_signup', next='choose'))

    username = session['user']
    initialize_progress(username)

    progress_db[username]['choose'] = min(progress_db[username]['choose'] + 10, 100)
    progress_db[username]['global'] = min(progress_db[username]['global'] + 5, 100)

    return render_template('choose.html', username=username, progress=progress_db[username])

@app.route('/fill')
def fill():
    if 'user' not in session:
        return redirect(url_for('login_signup', next='fill'))

    username = session['user']
    initialize_progress(username)

    progress_db[username]['fill'] = min(progress_db[username]['fill'] + 10, 100)
    progress_db[username]['global'] = min(progress_db[username]['global'] + 5, 100)

    return render_template('fill.html', username=username, progress=progress_db[username])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login_signup', next='index'))

if __name__ == "__main__":
    app.run(debug=True)
