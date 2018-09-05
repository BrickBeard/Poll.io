from flask import (
    Flask, render_template, request, flash, redirect, url_for, session, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Users, Polls, Topics, Options

poll_io = Flask(__name__)

# Load config setting from config.py
poll_io.config.from_object('config')

# Initialize and create Database
db.init_app(poll_io)
db.create_all(app=poll_io)

# Map routes

@poll_io.route('/')
def home():
    return render_template('index.html')

@poll_io.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get the user details from the form
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        # Hash the password
        password = generate_password_hash(password)
        
        user = Users(email=email, username=username, password=password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Thanks for signing up! Please log in.')
        
        return redirect(url_for('home'))
    
    # If GET request, render template
    return render_template('signup.html')

@poll_io.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Search the database for the user
    user = Users.query.filter_by(username=username).first()
    
    if user:
        password_hash = user.password
        
        if check_password_hash(password_hash, password):
            # The hash matches the password in the database
            session['user'] = username
            
            flash('Login was successful')
    else:
        # User wasn't found in the database
        flash('Username or password was incorrect.  Please try again.', 'error')
    
    return redirect(url_for('home'))

@poll_io.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
        flash('We hope to see you again soon!')
    
    return redirect(url_for('home'))

@poll_io.route('/api/polls', methods=['GET', 'POST'])
def api_polls():
    if request.method == 'POST':
        poll = request.get_json()
        return "The title of the poll is {} and the options are {} and {}".format(poll['title'], *poll['options'])
    else:
        all_polls = {}
        
        topics = Topics.query.all()
        for topic in topics:
            all_polls[topic.title] = {'options': [poll.option.name for poll in Polls.query.filter_by(topic=topic)]}
        return jsonify(all_polls)
    


if __name__ == '__main__':
    poll_io.run(port='5001')
    