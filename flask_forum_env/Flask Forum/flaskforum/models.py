from datetime import datetime
from flaskforum import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    forums_followed = db.Column(db.Integer, default=0) 
    display_picture = db.Column(db.String(20), nullable=False, default='default.png')
    posts = db.relationship('Post', backref='author', lazy=True)
    followed_users = db.relationship('Follow_Forum', backref='follow_user', lazy=True)
    forum_owner = db.relationship('Forum', backref='owner', lazy=True)
    comment_user = db.relationship('Comment', backref='comment_user', lazy=True)
    reply_user = db.relationship('Reply', backref='reply_user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"

class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    num_of_comments = db.Column(db.Integer, default=0) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    forum_id = db.Column(db.Integer, db.ForeignKey('forum.id'), nullable=False)
    comment_post = db.relationship('Comment', backref='comment_post', lazy=True)

    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"

class Forum(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    about = db.Column(db.Text, nullable=False)
    display_picture = db.Column(db.String(20), nullable=False, default='default.png')
    followers = db.Column(db.Integer, default=0)
    num_of_post = db.Column(db.Integer, default=0)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    forum = db.relationship('Post', backref='forum', lazy=True)
    followed_users = db.relationship('Follow_Forum', backref='follow_forum', lazy=True)

    def __repr__(self):
        return f"Forum('{self.name}','{self.date_created}')"

class Follow_Forum(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    forum_id = db.Column(db.Integer, db.ForeignKey('forum.id'), nullable=False)

    def __repr__(self):
        return f"Follow_Forum('{self.user_id}','{self.forum_id}')"

class Comment(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_commented = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    num_of_reply = db.Column(db.Integer, default=0) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    reply = db.relationship('Reply', backref='reply', lazy=True)   
    
    def __repr__(self):
        return f"Comment('{self.content}','{self.date_commented}')"

class Reply(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_reply = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)

    def __repr__(self):
        return f"Reply('{self.content}','{self.date_reply}')"
