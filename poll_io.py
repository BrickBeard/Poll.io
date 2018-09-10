from flask import (
    Flask, render_template, request, flash, redirect, url_for, session, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from models import db, Users, Polls, Topics, Options, UserPolls
from flask_admin import Admin
from admin import AdminView, TopicView

poll_io = Flask(__name__)

# Load config setting from config.py
poll_io.config.from_object('config')

# Initialize and create Database
db.init_app(poll_io)
#db.create_all(app=poll_io)

migrate = Migrate(poll_io, db, render_as_batch=True)


admin = Admin(poll_io, name='Dashboard', index_view=TopicView(Topics, db.session, url='/admin', endpoint='admin'))
admin.add_view(AdminView(Polls, db.session))
admin.add_view(AdminView(Options, db.session))
admin.add_view(AdminView(Users, db.session))
admin.add_view(AdminView(UserPolls, db.session))


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
    
    return redirect(request.args.get('next') or url_for('home'))

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
        polls = Topics.query.filter_by(status=1).join(Polls).order_by(Topics.id.desc()).all()
        all_polls = {'Polls': [poll.to_json() for poll in polls]}
        
        return jsonify(all_polls)

@poll_io.route('/api/polls/options')
def api_polls_options():
    all_options = [option.to_json() for option in Options.query.all()]
    return jsonify(all_options)

@poll_io.route('/api/poll/vote', methods=['PATCH'])
def api_poll_vote():
    poll = request.get_json()

    poll_title, option = (poll['poll_title'], poll['option'])

    join_tables = Polls.query.join(Topics).join(Options)
    
    # get topic and username from the database
    topic = Topics.query.filter_by(title=poll_title).first()
    user = Users.query.filter_by(username=session['user']).first()
    
    #filter options
    option = join_tables.filter(Topics.title.like(poll_title)).filter(Options.name.like(option)).first()
    
    #check if user has voted on this poll
    poll_count = UserPolls.query.filter_by(topic_id=topic.id).filter_by(user_id=user.id).count()
    if poll_count > 0:
        return jsonify({'message': 'Sorry! Multiple votes are not allowed.'})
    #increment vote_count by 1 if the option was found
    if option:
        user_poll = UserPolls(topic_id=topic.id, user_id=user.id)
        db.session.add(user_poll)

        option.vote_count += 1
        db.session.commit()

        return jsonify({'message': 'Thank you for voting'})
    
    return jsonify({'message': 'Option or poll was not found.  Please try again. '})

@poll_io.route('/polls/<poll_name>')
def poll(poll_name):
    return render_template('index.html')

@poll_io.route('/api/poll/<poll_name>')
def api_poll(poll_name):
    poll = Topics.query.filter(Topics.title.like(poll_name)).first()

    return jsonify({'Polls': [poll.to_json()]}) if poll else jsonify({'message': 'poll not found'})


# if __name__ == '__main__':
#     poll_io.run(port='5001')
