from flask import (
    Flask, render_template, request, flash, redirect, url_for, session, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from models import db, Users, Polls, Topics, Options

poll_io = Flask(__name__)

# Load config setting from config.py
poll_io.config.from_object('config')

# Initialize and create Database
db.init_app(poll_io)
db.create_all(app=poll_io)

migrate = Migrate(poll_io, db, render_as_batch=True)


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

@poll_io.route('/polls', methods=['GET'])
def polls():
    return render_template('polls.html')

@poll_io.route('/api/polls', methods=['GET', 'POST'])
def api_polls():
    if request.method == 'POST':
        
        poll = request.get_json()
        
        for key, value in poll.items():
            if not value:
                return jsonify({'error': 'value for {} is empty.'.format(key)})
        
        title = poll['title']
        options_query = lambda option : Options.query.filter(Options.name.like(option))
        
        options = [Polls(option=Options(name=option))
                        if options_query(option).count() == 0
                        else Polls(option=options_query(option).first()) for option in poll['options']]
        
        new_topic = Topics(title=title, options=options)

        db.session.add(new_topic)
        db.session.commit()
        
        return jsonify({'message': 'Poll was created successfully'})
    else:
        polls = Topics.query.join(Polls).all()
        all_polls = {'Polls': [poll.to_json() for poll in polls]}
        
        return jsonify(all_polls)

@poll_io.route('/api/polls/options')
def api_polls_options():
    all_options = [option.to_json() for option in Options.query.all()]
    return jsonify(all_options)

# if __name__ == '__main__':
#     poll_io.run(port='5001')
