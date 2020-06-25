from flask import Blueprint
from flaskforum import db, bcrypt
from flaskforum.users.utils import save_picture
from flask import render_template, url_for, flash, redirect, request
from flaskforum.users.forms import LoginForm, RegistrationForm, AccountForm
from flaskforum.forums.forms import SearchForm
from flaskforum.models import User, Post, Forum, Comment
from flask_login import login_user, current_user, logout_user, login_required

users = Blueprint('users', __name__)

@users.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            next_page = request.args.get('next')
            login_user(user) #create the session for the user with the user's details
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('That password was incorrect. Please try again.')
    searchForm = SearchForm()
    return render_template('login.html', form=form, searchForm=searchForm, title="Login")

@users.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hash_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.home'))
    searchForm = SearchForm()
    return render_template('register.html', form=form, searchForm=searchForm, title="Register")

@users.route("/account", methods=['GET','POST'])
@login_required
def account():
    form = AccountForm()  
    image_file = url_for('static', filename='display_pics/' + current_user.display_picture)
    if form.validate_on_submit():
        if form.picture.data: # if user has not attached a file into the picture form than dont do anything with the picture
            picture_file=save_picture(form.picture.data, 'display_pics')
            current_user.display_picture = picture_file #update picture path field for user
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        return redirect(url_for('users.account'))
    elif request.method == 'GET':  # prevent post from been changed if it is a POST and form is invalid as it needs to show the data that was typed in
        form.username.data = current_user.username
        form.email.data = current_user.email
    follow = User.query.filter_by(id=current_user.id).first().follow.all() if current_user.is_authenticated else None
    searchForm = SearchForm()
    return render_template('account.html', form=form, searchForm=searchForm, follow=follow, image_file=image_file, title="Account")

@users.route("/account/remove_picture/<int:id>", methods=['POST'])
@login_required
def account_remove_pic(id):
    if current_user.is_authenticated and current_user.id == id:
        current_user.display_picture = 'default.png'
        db.session.commit()
    return redirect(url_for('users.account'))
        
@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/follow/<int:id>', methods=['POST'])
@login_required
def follow(id):
    forum = Forum.query.filter_by(id=id).first()
    follow_forum = User.query.filter_by(id=current_user.id).first().follow.filter_by(id=id).first() if current_user.is_authenticated else None
    if not follow_forum:
        Forum.query.filter_by(id=forum.id).first().follow_forum.append(current_user) if current_user.is_authenticated else None
        db.session.commit()
    return redirect(url_for('forums.forum', name=forum.name))

@users.route('/unfollow/<int:id>', methods=['POST'])
@login_required
def unfollow(id):
     forum = Forum.query.filter_by(id=id).first()
     follow_forum = User.query.filter_by(id=current_user.id).first().follow.filter_by(id=id).first() if current_user.is_authenticated else None
     if follow_forum:
        user = User.query.filter_by(id=current_user.id).first()
        if user.follow.filter_by(id=forum.id).first():
            user.follow.remove(forum)
        db.session.commit()
     return redirect(url_for('forums.forum', name=forum.name))

@users.route("/user/<string:username>/posts")
def user_posts(username):
    searchForm = SearchForm()
    follow = User.query.filter_by(id=current_user.id).first().follow.all() if current_user.is_authenticated else None
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int) #represented as a '?page='
    # get the data from the post field and count the amount of comments and amount of hours since post was made
    posts = db.session.query(Post,(db.func.julianday('now')-db.func.julianday(Post.date_posted))*24,db.func.count(Comment.post_id)).order_by(Post.date_posted.desc()).outerjoin(Comment, Post.id==Comment.post_id).group_by(Post.id).filter(Post.user_id==user.id).group_by(Post.id).paginate(page=page, per_page=10)
    #posts = db.session.query(Post,(db.func.julianday('now')-db.func.julianday(Post.date_posted))*24).order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template('user_posts.html', follow=follow, posts=posts, user=user, searchForm=searchForm, title=user.username + " posts")

@users.route("/user/<string:username>/comments")
def user_comments(username):
    searchForm = SearchForm()
    follow = User.query.filter_by(id=current_user.id).first().follow.all() if current_user.is_authenticated else None
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int) #represented as a '?page='
    comments = Comment.query.order_by(Comment.date_commented.desc()).filter_by(comment_user=user).paginate(page=page, per_page=10) 
    return render_template('user_comments.html', follow=follow, comments=comments, user=user, searchForm=searchForm, title=user.username + " comments")