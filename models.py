from flask_sqlalchemy import SQLAlchemy

# Create a new SQLAlchemy object
db = SQLAlchemy()

# Base model that other models can inherit from
class Base(db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    date_created = db.Column(db.DateTime, default = db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default = db.func.current_timestamp(), 
                              onupdate = db.func.current_timestamp())
    
# Model for poll topics
class Topics(Base):
    title = db.Column(db.String(500))
    
    # User friendly way to display the object
    def __repr__(self):
        return self.title
    
    def to_json(self):
        return {
            'title': self.title,
            'options':
                [{'name': option.option.name, 'vote_count': option.vote_count}
                    for option in self.options.all()]
        }
    
# Model for poll options
class Options(Base):
    name = db.Column(db.String(200))
    
# Polls model to connect topics and options together
class Polls(Base):
    #Columns declaration
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    option_id = db.Column(db.Integer, db.ForeignKey('options.id'))
    vote_count = db.Column(db.Integer, default = 0)
    status = db.Column(db.Boolean)  # to mark poll as open or closed
    
    # Relationship declaration (makes accessing the polls model from other 
    # related models easier
    topic = db.relationship('Topics', foreign_keys = [topic_id], backref = 
                            db.backref('options', lazy = 'dynamic'))
    option = db.relationship('Options', foreign_keys = [option_id])
    
    def __repr__(self):
        return self.option.name
    
class Users(Base):
    email = db.Column(db.String(100), unique = True)
    username = db.Column(db.String(50), unique = True)
    password = db.Column(db.String(200))
    

    