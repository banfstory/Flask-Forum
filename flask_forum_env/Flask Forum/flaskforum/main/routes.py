from flask import Blueprint
from flask import render_template, request
from flaskforum.forums.forms import SearchForm
from flaskforum.models import Post, Comment, User
from flask_login import current_user
from flaskforum import db

main = Blueprint('main', __name__)

@main.route("/")
def home():
    searchForm = SearchForm()
    follow = User.query.filter_by(id=current_user.id).first().follow.all() if current_user.is_authenticated else None
    page = request.args.get('page',1,type=int) #represented as a '?page='
    # get the data from the post field and count the amount of comments and amount of hours since post was made
    posts = db.session.query(Post,(db.func.julianday('now')-db.func.julianday(Post.date_posted))*24,db.func.count(Comment.post_id)).order_by(Post.date_posted.desc())\
        .outerjoin(Comment, Post.id==Comment.post_id).group_by(Post.id).group_by(Post.id).paginate(page=page, per_page=10)
    #posts = db.session.query(Post,(db.func.julianday('now')-db.func.julianday(Post.date_posted))*24).order_by(Post.date_posted.desc()).paginate(page=page, per_page=10)
    return render_template('home.html', follow=follow, posts=posts, searchForm=searchForm, title="Homepage")